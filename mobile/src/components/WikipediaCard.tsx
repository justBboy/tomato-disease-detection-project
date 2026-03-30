import * as Linking from "expo-linking";
import { Image, StyleSheet, Text, TouchableOpacity } from "react-native";

import SectionCard from "@/components/SectionCard";
import type { WikipediaSummary } from "@/services/disease-info";

type WikipediaCardProps = {
  summary: WikipediaSummary | null;
  isLoading: boolean;
  diseaseTerm: string;
};

export default function WikipediaCard({ summary, isLoading, diseaseTerm }: WikipediaCardProps) {
  if (isLoading) {
    return (
      <SectionCard title="Learn More" subtitle="Pulling additional public information from Wikipedia.">
        <Text style={styles.note}>Loading article summary...</Text>
      </SectionCard>
    );
  }

  if (!summary) {
    return (
      <SectionCard title="Learn More" subtitle="Pulling additional public information from Wikipedia.">
        <Text style={styles.note}>No Wikipedia summary found for &quot;{diseaseTerm}&quot; yet.</Text>
      </SectionCard>
    );
  }

  return (
    <SectionCard title="Learn More" subtitle={summary.title}>
      {summary.thumbnailUrl ? <Image source={{ uri: summary.thumbnailUrl }} style={styles.thumbnail} /> : null}
      <Text style={styles.extract}>{summary.extract}</Text>
      <TouchableOpacity onPress={() => Linking.openURL(summary.url)} style={styles.button}>
        <Text style={styles.buttonText}>Open Full Article</Text>
      </TouchableOpacity>
    </SectionCard>
  );
}

const styles = StyleSheet.create({
  note: {
    color: "#567867",
  },
  thumbnail: {
    width: "100%",
    height: 150,
    borderRadius: 12,
    marginBottom: 10,
    backgroundColor: "#dfeae2",
  },
  extract: {
    color: "#3d6251",
    lineHeight: 19,
  },
  button: {
    marginTop: 12,
    backgroundColor: "#e9f7ef",
    borderWidth: 1,
    borderColor: "#b8d7c5",
    borderRadius: 10,
    paddingVertical: 10,
    alignItems: "center",
  },
  buttonText: {
    color: "#1b4f35",
    fontWeight: "700",
  },
});
