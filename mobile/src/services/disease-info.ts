type DiseaseKind = "healthy" | "fungal" | "bacterial" | "viral" | "pest" | "unknown";

export type DiseaseProfile = {
  rawClass: string;
  displayName: string;
  shortLabel: string;
  kind: DiseaseKind;
  wikipediaTerm?: string;
  wikipediaFallbackTerms?: string[];
  description: string;
  likelyCauses: string[];
  managementTips: string[];
};

export type WikipediaSummary = {
  title: string;
  extract: string;
  url: string;
  thumbnailUrl?: string;
};

const diseaseProfiles: Record<string, Omit<DiseaseProfile, "rawClass">> = {
  Tomato___healthy: {
    displayName: "Healthy Tomato Leaf",
    shortLabel: "Healthy",
    kind: "healthy",
    wikipediaTerm: "Tomato",
    description: "No major disease signature detected on the leaf image.",
    likelyCauses: ["Leaf tissue appears normal in color and texture."],
    managementTips: [
      "Continue preventive scouting at least 2-3 times per week.",
      "Maintain balanced nutrition and avoid overhead irrigation late in the day.",
      "Remove lower senescent leaves to improve airflow around the canopy.",
    ],
  },
  Tomato___Bacterial_spot: {
    displayName: "Tomato Bacterial Spot",
    shortLabel: "Bacterial Spot",
    kind: "bacterial",
    wikipediaTerm: "Bacterial spot",
    description: "Bacterial disease causing dark lesions on leaves and fruit.",
    likelyCauses: [
      "Warm temperatures combined with frequent leaf wetness.",
      "Splash spread from infected crop residues or contaminated seed/transplants.",
    ],
    managementTips: [
      "Use disease-free seed/transplants and resistant varieties where available.",
      "Avoid overhead irrigation and reduce leaf wetness duration.",
      "Remove heavily infected foliage and sanitize field tools regularly.",
    ],
  },
  Tomato___Early_blight: {
    displayName: "Tomato Early Blight",
    shortLabel: "Early Blight",
    kind: "fungal",
    wikipediaTerm: "Alternaria solani",
    description: "Fungal disease that produces target-like concentric lesions.",
    likelyCauses: [
      "Alternaria infection favored by warm, humid conditions.",
      "Stress factors such as nutrient imbalance and older lower leaves.",
    ],
    managementTips: [
      "Practice crop rotation and remove infected plant debris after harvest.",
      "Improve airflow and avoid prolonged leaf wetness.",
      "Apply fungicide programs early when risk conditions begin.",
    ],
  },
  Tomato___Late_blight: {
    displayName: "Tomato Late Blight",
    shortLabel: "Late Blight",
    kind: "fungal",
    wikipediaTerm: "Late blight",
    description: "Aggressive disease that can spread rapidly under cool, wet weather.",
    likelyCauses: [
      "Pathogen pressure during cool temperatures and persistent humidity.",
      "Wind-driven spread from nearby infected fields.",
    ],
    managementTips: [
      "Scout frequently and remove infected plants quickly to reduce spread.",
      "Improve drainage and canopy airflow to lower humidity around leaves.",
      "Use preventive fungicide programs in high-risk weather windows.",
    ],
  },
  Tomato___Leaf_Mold: {
    displayName: "Tomato Leaf Mold",
    shortLabel: "Leaf Mold",
    kind: "fungal",
    wikipediaTerm: "Cladosporium fulvum",
    description: "Fungal disease often seen in humid greenhouse or dense canopy conditions.",
    likelyCauses: [
      "High relative humidity and poor ventilation.",
      "Leaf wetness and dense canopy trapping moisture.",
    ],
    managementTips: [
      "Ventilate greenhouse structures and reduce prolonged humidity.",
      "Prune for better airflow and avoid wetting leaves during irrigation.",
      "Use resistant cultivars and remove infected lower leaves.",
    ],
  },
  Tomato___Septoria_leaf_spot: {
    displayName: "Tomato Septoria Leaf Spot",
    shortLabel: "Septoria Leaf Spot",
    kind: "fungal",
    wikipediaTerm: "Septoria lycopersici",
    description: "Common foliar fungal disease with many small circular spots.",
    likelyCauses: [
      "Extended moisture on leaves from rain or irrigation splash.",
      "Survival of inoculum on infected debris and nearby solanaceous weeds.",
    ],
    managementTips: [
      "Remove lower infected leaves and crop debris.",
      "Use mulching to reduce soil splash and inoculum spread.",
      "Follow protective fungicide schedules when disease pressure increases.",
    ],
  },
  "Tomato___Spider_mites Two-spotted_spider_mite": {
    displayName: "Tomato Two-Spotted Spider Mite",
    shortLabel: "Spider Mite",
    kind: "pest",
    wikipediaTerm: "Tetranychus urticae",
    description: "Mite infestation that causes stippling, bronzing, and webbing on leaves.",
    likelyCauses: [
      "Hot and dry microclimate conditions.",
      "Rapid population growth when natural predators are absent.",
    ],
    managementTips: [
      "Monitor leaf undersides and intervene early when populations are low.",
      "Use integrated pest management with biological control where possible.",
      "Avoid broad-spectrum sprays that disrupt beneficial insects.",
    ],
  },
  Tomato___Target_Spot: {
    displayName: "Tomato Target Spot",
    shortLabel: "Target Spot",
    kind: "fungal",
    wikipediaTerm: "Target spot",
    description: "Fungal disease causing necrotic leaf lesions and foliage decline.",
    likelyCauses: [
      "High humidity and warm weather in dense canopies.",
      "Pathogen carry-over from infected residues.",
    ],
    managementTips: [
      "Increase spacing and prune to improve airflow.",
      "Minimize prolonged leaf wetness in irrigation scheduling.",
      "Use disease monitoring and fungicide rotations as needed.",
    ],
  },
  Tomato___Tomato_Yellow_Leaf_Curl_Virus: {
    displayName: "Tomato Yellow Leaf Curl Virus",
    shortLabel: "TYLCV",
    kind: "viral",
    wikipediaTerm: "Tomato yellow leaf curl virus",
    wikipediaFallbackTerms: ["Tomato yellow leaf curl disease", "TYLCV"],
    description: "Viral disease often associated with whitefly vectors.",
    likelyCauses: [
      "Virus transmission by whiteflies between infected and healthy plants.",
      "High vector pressure and presence of alternate hosts.",
    ],
    managementTips: [
      "Use vector management (whitefly suppression) and reflective mulches.",
      "Rogue severely symptomatic plants early to lower spread.",
      "Prefer tolerant/resistant varieties in endemic areas.",
    ],
  },
  Tomato___Tomato_mosaic_virus: {
    displayName: "Tomato Mosaic Virus",
    shortLabel: "ToMV",
    kind: "viral",
    wikipediaTerm: "Tomato mosaic virus",
    description: "Mechanically transmitted virus causing mosaic and leaf distortion.",
    likelyCauses: [
      "Spread through contaminated tools, hands, and plant material.",
      "Persistent virus survival on surfaces and residues.",
    ],
    managementTips: [
      "Disinfect tools and hands between plant blocks.",
      "Remove infected plants and avoid handling wet plants.",
      "Use certified clean seed and sanitize greenhouse work areas.",
    ],
  },
};

function prettifyFallbackLabel(rawClass: string): string {
  const withoutPrefix = rawClass.replace(/^Tomato___/, "");
  const normalized = withoutPrefix.replace(/_/g, " ").replace(/\s+/g, " ").trim();
  if (!normalized) {
    return "Unknown Condition";
  }
  return normalized.replace(/\b\w/g, (char) => char.toUpperCase());
}

export function severityBand(severityPercent: number | null): string {
  if (severityPercent == null) {
    return "Not Available";
  }
  if (severityPercent < 10) {
    return "Low";
  }
  if (severityPercent < 30) {
    return "Moderate";
  }
  return "High";
}

export function confidenceBand(confidence: number | null): string {
  if (confidence == null) {
    return "Not Available";
  }
  if (confidence >= 0.85) {
    return "High";
  }
  if (confidence >= 0.65) {
    return "Medium";
  }
  return "Low";
}

export function getDiseaseProfile(rawClass: string): DiseaseProfile {
  const known = diseaseProfiles[rawClass];
  if (known) {
    return { rawClass, ...known };
  }

  const fallbackDisplay = prettifyFallbackLabel(rawClass);
  return {
    rawClass,
    displayName: fallbackDisplay,
    shortLabel: fallbackDisplay,
    kind: "unknown",
    description: "Condition recognized by model but no curated agronomic note is available yet.",
    likelyCauses: ["Image may represent a less common pattern or class alias."],
    managementTips: [
      "Collect additional clear images from different leaves for confirmation.",
      "Cross-check symptoms with local agronomy guidance before intervention.",
    ],
  };
}

export function getAllKnownDiseaseProfiles(): DiseaseProfile[] {
  return Object.entries(diseaseProfiles)
    .map(([rawClass, profile]) => ({ rawClass, ...profile }))
    .sort((a, b) => a.displayName.localeCompare(b.displayName));
}

export function getWikipediaTerms(profile: DiseaseProfile): string[] {
  const terms = [
    profile.wikipediaTerm,
    ...(profile.wikipediaFallbackTerms || []),
    profile.displayName,
    profile.shortLabel,
  ]
    .map((item) => (item || "").trim())
    .filter((item) => item.length > 0);

  return Array.from(new Set(terms));
}

type SearchResponse = {
  query?: {
    search?: { title?: string }[];
  };
};

type SummaryResponse = {
  title?: string;
  extract?: string;
  content_urls?: {
    desktop?: {
      page?: string;
    };
  };
  thumbnail?: {
    source?: string;
  };
};

type ActionQueryResponse = {
  query?: {
    pages?: Record<
      string,
      {
        title?: string;
        extract?: string;
        fullurl?: string;
        thumbnail?: { source?: string };
        missing?: boolean;
      }
    >;
  };
};

const WIKIPEDIA_HEADERS = {
  Accept: "application/json",
  "Api-User-Agent": "TomatoLeafCompanion/1.0 (student project app)",
  "User-Agent": "TomatoLeafCompanion/1.0 (student project app)",
};

async function fetchSummaryByTitle(title: string): Promise<WikipediaSummary | null> {
  const summaryUrl = `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(title)}`;
  const response = await fetch(summaryUrl, { headers: WIKIPEDIA_HEADERS });
  if (!response.ok) {
    return null;
  }

  const data = (await response.json()) as SummaryResponse;
  if (!data.extract || !data.title) {
    return null;
  }

  return {
    title: data.title,
    extract: data.extract,
    url: data.content_urls?.desktop?.page || `https://en.wikipedia.org/wiki/${encodeURIComponent(data.title)}`,
    thumbnailUrl: data.thumbnail?.source,
  };
}

async function fetchActionSummaryByTitle(title: string): Promise<WikipediaSummary | null> {
  const actionUrl =
    "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts|pageimages|info" +
    "&inprop=url&exintro=1&explaintext=1&piprop=thumbnail&pithumbsize=400&redirects=1&origin=*&titles=" +
    encodeURIComponent(title);

  const response = await fetch(actionUrl, { headers: WIKIPEDIA_HEADERS });
  if (!response.ok) {
    return null;
  }

  const data = (await response.json()) as ActionQueryResponse;
  const pages = data.query?.pages || {};
  const firstPage = Object.values(pages)[0];

  if (!firstPage || firstPage.missing || !firstPage.extract || !firstPage.title) {
    return null;
  }

  return {
    title: firstPage.title,
    extract: firstPage.extract,
    url: firstPage.fullurl || `https://en.wikipedia.org/wiki/${encodeURIComponent(firstPage.title)}`,
    thumbnailUrl: firstPage.thumbnail?.source,
  };
}

async function searchWikipediaTitle(term: string): Promise<string | null> {
  const searchUrl =
    "https://en.wikipedia.org/w/api.php?action=query&list=search&format=json&origin=*&srsearch=" +
    encodeURIComponent(term);
  const response = await fetch(searchUrl, { headers: WIKIPEDIA_HEADERS });
  if (!response.ok) {
    return null;
  }
  const data = (await response.json()) as SearchResponse;
  const title = data.query?.search?.[0]?.title;
  return title || null;
}

function normalizeTerms(terms: string[] | string): string[] {
  if (typeof terms === "string") {
    return terms.trim() ? [terms.trim()] : [];
  }

  const normalized = terms.map((term) => term.trim()).filter((term) => term.length > 0);
  return Array.from(new Set(normalized));
}

export async function fetchWikipediaSummary(terms: string[] | string): Promise<WikipediaSummary | null> {
  const termList = normalizeTerms(terms);
  if (termList.length === 0) {
    return null;
  }

  for (const term of termList) {
    const directRest = await fetchSummaryByTitle(term);
    if (directRest) {
      return directRest;
    }
    const directAction = await fetchActionSummaryByTitle(term);
    if (directAction) {
      return directAction;
    }
  }

  for (const term of termList) {
    const discoveredTitle = await searchWikipediaTitle(term);
    if (!discoveredTitle) {
      continue;
    }

    const discoveredRest = await fetchSummaryByTitle(discoveredTitle);
    if (discoveredRest) {
      return discoveredRest;
    }

    const discoveredAction = await fetchActionSummaryByTitle(discoveredTitle);
    if (discoveredAction) {
      return discoveredAction;
    }
  }

  return null;
}
