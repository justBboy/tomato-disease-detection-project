import { LinearGradient } from "expo-linear-gradient";
import { useMemo, useState } from "react";
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";

import SectionCard from "@/components/SectionCard";
import { getAllKnownDiseaseProfiles } from "@/services/disease-info";

export default function CareGuideScreen() {
  const profiles = useMemo(() => getAllKnownDiseaseProfiles(), []);
  const [selectedRawClass, setSelectedRawClass] = useState<string>(profiles[0]?.rawClass || "");
  const selectedProfile = profiles.find((item) => item.rawClass === selectedRawClass) || profiles[0];

  return (
    <View style={styles.screen}>
      <LinearGradient colors={["#0f4b2e", "#2a7a4f"]} style={styles.hero}>
        <Text style={styles.heroEyebrow}>GUIDANCE</Text>
        <Text style={styles.heroTitle}>Causes And Management</Text>
        <Text style={styles.heroSubtitle}>Quick agronomy notes for common tomato leaf conditions.</Text>
      </LinearGradient>

      <ScrollView contentContainerStyle={styles.container}>
        <SectionCard title="Disease Library" subtitle="Tap any condition to review likely causes and treatment approach.">
          <View style={styles.chipWrap}>
            {profiles.map((profile) => {
              const selected = selectedProfile?.rawClass === profile.rawClass;
              return (
                <TouchableOpacity
                  key={profile.rawClass}
                  onPress={() => setSelectedRawClass(profile.rawClass)}
                  style={[styles.chip, selected ? styles.chipActive : null]}
                >
                  <Text style={[styles.chipText, selected ? styles.chipTextActive : null]}>{profile.shortLabel}</Text>
                </TouchableOpacity>
              );
            })}
          </View>
        </SectionCard>

        {selectedProfile ? (
          <SectionCard title={selectedProfile.displayName} subtitle={`Type: ${selectedProfile.kind.toUpperCase()}`}>
            <Text style={styles.description}>{selectedProfile.description}</Text>

            <Text style={styles.blockTitle}>Likely Causes</Text>
            {selectedProfile.likelyCauses.map((cause) => (
              <View key={cause} style={styles.bulletRow}>
                <Text style={styles.bulletDot}>-</Text>
                <Text style={styles.bulletText}>{cause}</Text>
              </View>
            ))}

            <Text style={styles.blockTitle}>How To Manage</Text>
            {selectedProfile.managementTips.map((tip) => (
              <View key={tip} style={styles.bulletRow}>
                <Text style={styles.bulletDot}>-</Text>
                <Text style={styles.bulletText}>{tip}</Text>
              </View>
            ))}
          </SectionCard>
        ) : null}

        <SectionCard title="Important Note" subtitle="Decision support, not a replacement for local agronomic diagnosis.">
          <Text style={styles.noteText}>
            Use this app to prioritize scouting and early intervention. Always validate high-risk cases with local
            extension guidelines or an agronomist before applying treatment.
          </Text>
        </SectionCard>
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
    paddingBottom: 22,
    paddingHorizontal: 18,
  },
  heroEyebrow: {
    color: "#add8c1",
    letterSpacing: 1.1,
    fontSize: 11,
    fontWeight: "700",
  },
  heroTitle: {
    marginTop: 6,
    color: "#f4fff8",
    fontSize: 31,
    fontWeight: "800",
  },
  heroSubtitle: {
    marginTop: 5,
    color: "#d6f0df",
    fontSize: 14,
  },
  container: {
    paddingHorizontal: 16,
    paddingTop: 14,
    paddingBottom: 32,
  },
  chipWrap: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  chip: {
    paddingHorizontal: 10,
    paddingVertical: 7,
    borderRadius: 999,
    backgroundColor: "#edf7f0",
    borderWidth: 1,
    borderColor: "#c7ddcf",
  },
  chipActive: {
    backgroundColor: "#177245",
    borderColor: "#177245",
  },
  chipText: {
    color: "#244c38",
    fontSize: 12,
    fontWeight: "700",
  },
  chipTextActive: {
    color: "#ffffff",
  },
  description: {
    color: "#3d6251",
    lineHeight: 19,
    marginBottom: 10,
  },
  blockTitle: {
    color: "#234937",
    fontWeight: "800",
    marginBottom: 5,
    marginTop: 6,
  },
  bulletRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 6,
    marginBottom: 5,
  },
  bulletDot: {
    color: "#2e6649",
    marginTop: 1,
  },
  bulletText: {
    flex: 1,
    color: "#3d6251",
    lineHeight: 18,
  },
  noteText: {
    color: "#3d6251",
    lineHeight: 19,
  },
});
