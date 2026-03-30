import { useQuery } from "@tanstack/react-query";
import { useFocusEffect } from "@react-navigation/native";
import { LinearGradient } from "expo-linear-gradient";
import { useCallback, useMemo, useState } from "react";
import { Alert, Image, ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";

import DiseaseInsightsCard from "@/components/DiseaseInsightsCard";
import SectionCard from "@/components/SectionCard";
import WikipediaCard from "@/components/WikipediaCard";
import { fetchWikipediaSummary, getDiseaseProfile, getWikipediaTerms, type WikipediaSummary } from "@/services/disease-info";
import { formatConfidence, formatSeverity, formatTimestamp } from "@/services/formatting";
import { clearHistoryStorage, loadHistory } from "@/services/history-storage";
import type { AnalysisHistoryItem } from "@/types/history";

export default function HistoryScreen() {
  const [items, setItems] = useState<AnalysisHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const loadItems = useCallback(async () => {
    setLoading(true);
    const history = await loadHistory();
    setItems(history);
    if (history.length > 0) {
      setSelectedId((previous) => previous ?? history[0].id);
    } else {
      setSelectedId(null);
    }
    setLoading(false);
  }, []);

  useFocusEffect(
    useCallback(() => {
      void loadItems();
    }, [loadItems])
  );

  const selectedItem = useMemo(() => items.find((item) => item.id === selectedId) || items[0] || null, [items, selectedId]);
  const selectedProfile = useMemo(() => (selectedItem ? getDiseaseProfile(selectedItem.rawClass) : null), [selectedItem]);
  const wikiTerms = useMemo(() => (selectedProfile ? getWikipediaTerms(selectedProfile) : []), [selectedProfile]);

  const { data: wikipediaSummary, isFetching: wikiLoading } = useQuery<WikipediaSummary | null>({
    queryKey: ["history_wikipedia_summary", wikiTerms.join("|")],
    queryFn: () => fetchWikipediaSummary(wikiTerms),
    enabled: wikiTerms.length > 0,
    staleTime: 1000 * 60 * 60 * 24,
  });

  function clearHistory() {
    Alert.alert("Clear History", "Delete all saved leaf checks from this device?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Clear",
        style: "destructive",
        onPress: () => {
          void (async () => {
            await clearHistoryStorage();
            await loadItems();
          })();
        },
      },
    ]);
  }

  return (
    <View style={styles.screen}>
      <LinearGradient colors={["#0f4b2e", "#256e47"]} style={styles.hero}>
        <Text style={styles.heroEyebrow}>CHECK HISTORY</Text>
        <Text style={styles.heroTitle}>Recent Leaf Checks</Text>
        <Text style={styles.heroSubtitle}>Review previous results and care suggestions.</Text>
      </LinearGradient>

      <ScrollView contentContainerStyle={styles.container}>
        <SectionCard
          title="Saved Checks"
          subtitle="Stored locally on this phone."
          rightSlot={
            items.length > 0 ? (
              <TouchableOpacity onPress={clearHistory}>
                <Text style={styles.clearText}>Clear All</Text>
              </TouchableOpacity>
            ) : null
          }
        >
          {loading ? <Text style={styles.emptyText}>Loading history...</Text> : null}
          {!loading && items.length === 0 ? <Text style={styles.emptyText}>No saved checks yet.</Text> : null}
          {!loading &&
            items.map((item) => {
              const selected = selectedItem?.id === item.id;
              return (
                <TouchableOpacity
                  key={item.id}
                  style={[styles.historyItem, selected ? styles.historyItemSelected : null]}
                  onPress={() => setSelectedId(item.id)}
                >
                  <Image source={{ uri: item.sourceUri }} style={styles.historyImage} />
                  <View style={styles.historyBody}>
                    <Text style={styles.historyTitle}>{item.displayName}</Text>
                    <Text style={styles.historyMeta}>
                      Certainty: {formatConfidence(item.confidence)} | Affected Area: {formatSeverity(item.severityPercent)}
                    </Text>
                    <Text style={styles.historyTime}>{formatTimestamp(item.timestamp)}</Text>
                  </View>
                </TouchableOpacity>
              );
            })}
        </SectionCard>

        {selectedItem && selectedProfile ? (
          <SectionCard title="Selected Check" subtitle={`Saved on ${formatTimestamp(selectedItem.timestamp)}`}>
            <Text style={styles.selectedTitle}>{selectedItem.displayName}</Text>
            <Text style={styles.selectedMeta}>This is the condition detected for the selected leaf photo.</Text>
          </SectionCard>
        ) : null}

        {selectedItem && selectedProfile ? (
          <DiseaseInsightsCard
            profile={selectedProfile}
            confidence={selectedItem.confidence}
            severityPercent={selectedItem.severityPercent}
          />
        ) : null}

        {selectedItem && selectedProfile ? (
          <WikipediaCard
            summary={wikipediaSummary || null}
            isLoading={wikiLoading}
            diseaseTerm={selectedProfile.displayName}
          />
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
  clearText: {
    color: "#306247",
    fontSize: 12,
    fontWeight: "700",
  },
  emptyText: {
    color: "#5e7d6d",
    fontSize: 13,
  },
  historyItem: {
    flexDirection: "row",
    marginTop: 10,
    backgroundColor: "#ffffff",
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#d5e8dc",
    padding: 8,
  },
  historyItemSelected: {
    borderColor: "#81b89b",
    backgroundColor: "#f2faf5",
  },
  historyImage: {
    width: 62,
    height: 62,
    borderRadius: 9,
    backgroundColor: "#e2ede5",
  },
  historyBody: {
    flex: 1,
    marginLeft: 9,
  },
  historyTitle: {
    color: "#1d412f",
    fontWeight: "700",
    fontSize: 14,
  },
  historyMeta: {
    color: "#466656",
    fontSize: 12,
    marginTop: 2,
  },
  historyTime: {
    color: "#5d7a6b",
    fontSize: 11,
    marginTop: 3,
  },
  selectedTitle: {
    color: "#173928",
    fontSize: 19,
    fontWeight: "800",
  },
  selectedMeta: {
    color: "#517362",
    marginTop: 4,
  },
});
