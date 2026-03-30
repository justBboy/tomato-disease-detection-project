import Constants from "expo-constants";
import { Platform } from "react-native";

function extractHostFromExpo(): string | null {
  const candidates: (string | undefined)[] = [
    (Constants as any)?.expoConfig?.hostUri,
    (Constants as any)?.expoGoConfig?.debuggerHost,
    (Constants as any)?.manifest2?.extra?.expoClient?.hostUri,
    (Constants as any)?.manifest?.debuggerHost,
  ];

  for (const candidate of candidates) {
    if (!candidate || typeof candidate !== "string") {
      continue;
    }
    const host = candidate.split(":")[0]?.trim();
    if (host) {
      return host;
    }
  }
  return null;
}

function resolveDefaultApiBaseUrl(): string {
  const envValue = process.env.EXPO_PUBLIC_API_BASE_URL;
  console.log("env value ====> ", envValue);
  if (envValue && envValue.trim().length > 0) {
    return envValue.trim();
  }

  const hostFromExpo = extractHostFromExpo();
  if (hostFromExpo) {
    return `http://${hostFromExpo}:8000/api/v1`;
  }

  if (Platform.OS === "android") {
    return "http://10.0.2.2:8000/api/v1";
  }
  return "http://localhost:8000/api/v1";
}

export const DEFAULT_API_BASE_URL = resolveDefaultApiBaseUrl();

export const API_URL_HINT =
  "Same Wi-Fi: use your PC LAN IP (for example http://192.168.x.x:8000/api/v1).";
