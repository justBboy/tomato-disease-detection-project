import { StyleSheet, Text, View } from "react-native";

import SectionCard from "@/components/SectionCard";
import { confidenceBand, severityBand, type DiseaseProfile } from "@/services/disease-info";
import { formatConfidence, formatSeverity } from "@/services/formatting";

type DiseaseInsightsCardProps = {
  profile: DiseaseProfile;
  confidence: number | null;
  severityPercent: number | null;
};

function Row({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.row}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>{value}</Text>
    </View>
  );
}

function BulletList({ title, items }: { title: string; items: string[] }) {
  return (
    <View style={styles.block}>
      <Text style={styles.blockTitle}>{title}</Text>
      {items.map((item) => (
        <View key={`${title}_${item}`} style={styles.bulletRow}>
          <Text style={styles.bulletDot}>-</Text>
          <Text style={styles.bulletText}>{item}</Text>
        </View>
      ))}
    </View>
  );
}

export default function DiseaseInsightsCard({ profile, confidence, severityPercent }: DiseaseInsightsCardProps) {
  return (
    <SectionCard title="What This Means" subtitle="Simple explanation, likely causes, and practical next steps.">
      <Text style={styles.condition}>{profile.displayName}</Text>
      <Text style={styles.description}>{profile.description}</Text>

      <Row label="Result Certainty" value={`${formatConfidence(confidence)} (${confidenceBand(confidence)})`} />
      <Row label="Infection Level" value={`${formatSeverity(severityPercent)} (${severityBand(severityPercent)})`} />
      <Row label="Condition Type" value={profile.kind.toUpperCase()} />

      <BulletList title="Likely Causes" items={profile.likelyCauses} />
      <BulletList title="What You Can Do" items={profile.managementTips} />
    </SectionCard>
  );
}

const styles = StyleSheet.create({
  condition: {
    color: "#173928",
    fontSize: 20,
    fontWeight: "800",
    marginBottom: 6,
  },
  description: {
    color: "#466857",
    fontSize: 13,
    lineHeight: 19,
    marginBottom: 12,
  },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 7,
    gap: 8,
  },
  label: {
    color: "#355846",
    fontWeight: "600",
  },
  value: {
    color: "#143425",
    fontWeight: "700",
    textAlign: "right",
    flexShrink: 1,
  },
  block: {
    marginTop: 11,
  },
  blockTitle: {
    color: "#244a37",
    fontWeight: "700",
    marginBottom: 5,
  },
  bulletRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginBottom: 5,
    gap: 6,
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
});
