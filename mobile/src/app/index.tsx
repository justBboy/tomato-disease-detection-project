import { StatusBar } from "expo-status-bar";
import * as ImagePicker from "expo-image-picker";
import type { ImagePickerAsset } from "expo-image-picker";
import { LinearGradient } from "expo-linear-gradient";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Image,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

import DiseaseInsightsCard from "@/components/DiseaseInsightsCard";
import SectionCard from "@/components/SectionCard";
import WikipediaCard from "@/components/WikipediaCard";
import { DEFAULT_API_BASE_URL } from "@/config/api";
import { predictFull, type FullPredictionResponse } from "@/services/api";
import { fetchWikipediaSummary, getDiseaseProfile, getWikipediaTerms, type DiseaseProfile, type WikipediaSummary } from "@/services/disease-info";
import { formatConfidence, formatSeverity } from "@/services/formatting";
import { appendHistoryEntry } from "@/services/history-storage";

type ActionButtonProps = {
  label: string;
  onPress: () => void;
  disabled?: boolean;
  variant?: "primary" | "secondary" | "ghost";
};

type LeafCheckResult = {
  rawClass: string;
  confidence: number | null;
  severityPercent: number | null;
  classProbabilities: Record<string, number>;
};

function ActionButton({ label, onPress, disabled = false, variant = "primary" }: ActionButtonProps) {
  return (
    <TouchableOpacity
      style={[
        styles.button,
        variant === "secondary" ? styles.buttonSecondary : styles.buttonPrimary,
        variant === "ghost" ? styles.buttonGhost : null,
        disabled && styles.buttonDisabled,
      ]}
      onPress={onPress}
      disabled={disabled}
    >
      <Text style={[styles.buttonText, variant === "primary" ? styles.buttonTextPrimary : styles.buttonTextSecondary]}>
        {label}
      </Text>
    </TouchableOpacity>
  );
}

function ResultRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={styles.rowValue}>{value}</Text>
    </View>
  );
}

function buildLeafCheckResult(fullResult: FullPredictionResponse | null): LeafCheckResult | null {
  const predictedClass = fullResult?.classification?.predicted_class || fullResult?.segmentation?.predicted_class;
  if (!predictedClass) {
    return null;
  }

  return {
    rawClass: predictedClass,
    confidence: fullResult?.classification?.confidence ?? fullResult?.segmentation?.confidence ?? null,
    severityPercent: fullResult?.segmentation?.severity_percent ?? null,
    classProbabilities: fullResult?.classification?.class_probabilities || {},
  };
}

function toFriendlyErrorMessage(error: unknown): string {
  const rawMessage = error instanceof Error ? error.message : "Something went wrong.";
  const message = rawMessage.toLowerCase();

  if (
    message.includes("network request failed") ||
    message.includes("failed to fetch") ||
    message.includes("econnrefused")
  ) {
    return "We could not reach the plant health service. Make sure your phone and server are on the same Wi-Fi, then try again.";
  }

  if (message.includes("422") || message.includes("400")) {
    return "Please use a clear photo of one tomato leaf and try again.";
  }

  return "We could not check this leaf right now. Please try again.";
}

function overallLeafStatus(profile: DiseaseProfile | null): string {
  if (!profile) {
    return "Unknown";
  }
  return profile.kind === "healthy" ? "Healthy" : "Needs Attention";
}

export default function ScanScreen() {
  const [imageAsset, setImageAsset] = useState<ImagePickerAsset | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [fullResult, setFullResult] = useState<FullPredictionResponse | null>(null);

  const leafCheckResult = useMemo(() => buildLeafCheckResult(fullResult), [fullResult]);
  const diseaseProfile = useMemo(() => {
    if (!leafCheckResult) {
      return null;
    }
    return getDiseaseProfile(leafCheckResult.rawClass);
  }, [leafCheckResult]);

  const wikiTerms = useMemo(() => {
    if (!diseaseProfile) {
      return [];
    }
    return getWikipediaTerms(diseaseProfile);
  }, [diseaseProfile]);

  const { data: wikipediaSummary, isFetching: isWikipediaLoading } = useQuery<WikipediaSummary | null>({
    queryKey: ["wikipedia_summary", wikiTerms.join("|")],
    queryFn: () => fetchWikipediaSummary(wikiTerms),
    enabled: wikiTerms.length > 0,
    staleTime: 1000 * 60 * 60 * 24,
  });

  const segmentationMaskUri = useMemo(() => {
    const maskBase64 = fullResult?.segmentation?.segmentation_mask_base64;
    return maskBase64 ? `data:image/png;base64,${maskBase64}` : null;
  }, [fullResult]);

  const topAlternatives = useMemo(() => {
    if (!leafCheckResult) {
      return [];
    }

    return Object.entries(leafCheckResult.classProbabilities)
      .sort((a, b) => b[1] - a[1])
      .filter(([rawClass]) => rawClass !== leafCheckResult.rawClass)
      .slice(0, 2)
      .map(([rawClass, value]) => ({
        label: getDiseaseProfile(rawClass).shortLabel,
        value,
      }));
  }, [leafCheckResult]);

  function clearSession() {
    setImageAsset(null);
    setFullResult(null);
    setError("");
  }

  async function handlePickImage() {
    setError("");
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      setError("Please allow gallery access to upload a leaf photo.");
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
      quality: 0.9,
    });
    if (!result.canceled) {
      setImageAsset(result.assets[0]);
      setFullResult(null);
    }
  }

  async function handleCaptureImage() {
    setError("");
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (!permission.granted) {
      setError("Please allow camera access to scan a leaf.");
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ["images"],
      cameraType: ImagePicker.CameraType.back,
      quality: 0.9,
    });
    if (!result.canceled) {
      setImageAsset(result.assets[0]);
      setFullResult(null);
    }
  }

  async function checkLeafHealth() {
    if (!imageAsset) {
      setError("Add a leaf photo first.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const result = await predictFull(DEFAULT_API_BASE_URL, imageAsset);
      setFullResult(result);

      const parsed = buildLeafCheckResult(result);
      if (parsed) {
        const profile = getDiseaseProfile(parsed.rawClass);
        await appendHistoryEntry(
          "full",
          imageAsset.uri,
          parsed.rawClass,
          profile.displayName,
          parsed.confidence,
          parsed.severityPercent
        );
      }
    } catch (requestError) {
      setError(toFriendlyErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  }

  function confirmClearSession() {
    Alert.alert("Clear Current Check", "Remove the selected photo and result?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Clear",
        style: "destructive",
        onPress: clearSession,
      },
    ]);
  }

  return (
    <View style={styles.screen}>
      <StatusBar style="light" />
      <LinearGradient colors={["#0f4b2e", "#1d7246"]} style={styles.hero}>
        <Text style={styles.heroEyebrow}>TOMATO LEAF CARE ASSISTANT</Text>
        <Text style={styles.heroTitle}>Leaf Check</Text>
        <Text style={styles.heroSubtitle}>Take or upload a photo to quickly check leaf health and get care tips.</Text>
      </LinearGradient>

      <ScrollView contentContainerStyle={styles.container}>
        <SectionCard title="1. Add a Leaf Photo" subtitle="Use your camera in the field or upload from gallery.">
          <View style={styles.inlineActions}>
            <View style={styles.inlineActionItem}>
              <ActionButton label="Capture Leaf" onPress={handleCaptureImage} disabled={loading} />
            </View>
            <View style={styles.inlineActionItem}>
              <ActionButton label="Upload Photo" variant="secondary" onPress={handlePickImage} disabled={loading} />
            </View>
          </View>
          {imageAsset?.uri ? <Image source={{ uri: imageAsset.uri }} style={styles.preview} /> : null}
          {imageAsset?.uri ? (
            <Text style={styles.readyText}>Photo ready.</Text>
          ) : (
            <Text style={styles.readyTextMuted}>No photo selected yet.</Text>
          )}
        </SectionCard>

        <SectionCard title="2. Check Leaf Health" subtitle="Run a full check and get easy-to-understand guidance.">
          <ActionButton label="Check Leaf Health" onPress={checkLeafHealth} disabled={loading || !imageAsset} />
          <ActionButton label="Clear Current Check" variant="ghost" onPress={confirmClearSession} disabled={loading} />
        </SectionCard>

        {loading ? (
          <View style={styles.loadingBox}>
            <ActivityIndicator size="large" color="#1b7a43" />
            <Text style={styles.loadingText}>Checking leaf health...</Text>
          </View>
        ) : null}

        {error ? <Text style={styles.errorText}>{error}</Text> : null}

        {leafCheckResult && diseaseProfile ? (
          <SectionCard title="Leaf Health Result" subtitle="Summary from your latest leaf photo.">
            <ResultRow label="Leaf Status" value={overallLeafStatus(diseaseProfile)} />
            <ResultRow label="Detected Condition" value={diseaseProfile.displayName} />
            <ResultRow label="Result Certainty" value={formatConfidence(leafCheckResult.confidence)} />
            <ResultRow label="Estimated Affected Area" value={formatSeverity(leafCheckResult.severityPercent)} />
          </SectionCard>
        ) : null}

        {topAlternatives.length > 0 ? (
          <SectionCard title="Other Possible Matches" subtitle="Less likely conditions based on this photo.">
            {topAlternatives.map((item, index) => (
              <ResultRow key={`${item.label}_${index}`} label={`${index + 1}. ${item.label}`} value={formatConfidence(item.value)} />
            ))}
          </SectionCard>
        ) : null}

        {diseaseProfile ? (
          <DiseaseInsightsCard
            profile={diseaseProfile}
            confidence={leafCheckResult?.confidence ?? null}
            severityPercent={leafCheckResult?.severityPercent ?? null}
          />
        ) : null}

        {diseaseProfile ? (
          <WikipediaCard
            summary={wikipediaSummary || null}
            isLoading={isWikipediaLoading}
            diseaseTerm={diseaseProfile.displayName}
          />
        ) : null}

        {segmentationMaskUri ? (
          <SectionCard title="Affected Areas Map" subtitle="Highlighted parts of the leaf that appear infected.">
            <Image source={{ uri: segmentationMaskUri }} style={styles.maskPreview} />
          </SectionCard>
        ) : null}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: "#e9f4ed",
  },
  hero: {
    paddingTop: 56,
    paddingBottom: 24,
    paddingHorizontal: 18,
  },
  heroEyebrow: {
    color: "#acd8bf",
    fontSize: 11,
    letterSpacing: 1.2,
    fontWeight: "700",
  },
  heroTitle: {
    marginTop: 6,
    color: "#f4fff8",
    fontSize: 34,
    fontWeight: "800",
  },
  heroSubtitle: {
    marginTop: 6,
    color: "#d6f0df",
    fontSize: 14,
    maxWidth: 340,
  },
  container: {
    paddingHorizontal: 16,
    paddingTop: 14,
    paddingBottom: 30,
  },
  inlineActions: {
    flexDirection: "row",
    gap: 8,
    marginBottom: 4,
  },
  inlineActionItem: {
    flex: 1,
  },
  button: {
    borderRadius: 12,
    paddingVertical: 11,
    paddingHorizontal: 12,
    marginBottom: 8,
    alignItems: "center",
  },
  buttonPrimary: {
    backgroundColor: "#177245",
  },
  buttonSecondary: {
    backgroundColor: "#f0faf3",
    borderWidth: 1,
    borderColor: "#b6d4c0",
  },
  buttonGhost: {
    backgroundColor: "#edf7f0",
    borderWidth: 1,
    borderColor: "#c3dccb",
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonText: {
    fontWeight: "700",
    fontSize: 14,
  },
  buttonTextPrimary: {
    color: "#ffffff",
  },
  buttonTextSecondary: {
    color: "#18442f",
  },
  preview: {
    width: "100%",
    height: 220,
    borderRadius: 14,
    marginTop: 8,
    resizeMode: "cover",
    backgroundColor: "#dbe9de",
  },
  readyText: {
    marginTop: 8,
    color: "#195b37",
    fontSize: 12,
    fontWeight: "600",
  },
  readyTextMuted: {
    marginTop: 8,
    color: "#6d8979",
    fontSize: 12,
  },
  loadingBox: {
    alignItems: "center",
    justifyContent: "center",
    marginTop: 8,
    marginBottom: 12,
  },
  loadingText: {
    marginTop: 8,
    color: "#1f4f38",
    fontSize: 13,
  },
  errorText: {
    color: "#962121",
    fontWeight: "600",
    backgroundColor: "#f9e9e9",
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderRadius: 10,
    marginBottom: 12,
  },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 7,
    gap: 8,
  },
  rowLabel: {
    fontWeight: "600",
    color: "#315645",
  },
  rowValue: {
    color: "#173a2b",
    maxWidth: "68%",
    textAlign: "right",
  },
  maskPreview: {
    width: "100%",
    height: 220,
    borderRadius: 14,
    resizeMode: "contain",
    backgroundColor: "#dbe9de",
  },
});
