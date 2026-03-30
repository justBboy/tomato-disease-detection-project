import { Ionicons } from "@expo/vector-icons";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Tabs } from "expo-router";
import { useState } from "react";

export default function RootLayout() {
  const [queryClient] = useState(() => new QueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      <Tabs
        screenOptions={{
          headerShown: false,
          tabBarActiveTintColor: "#15633b",
          tabBarInactiveTintColor: "#678474",
          tabBarStyle: {
            height: 66,
            paddingBottom: 8,
            paddingTop: 8,
            borderTopColor: "#d3e6da",
            backgroundColor: "#f8fffb",
          },
          tabBarLabelStyle: {
            fontSize: 12,
            fontWeight: "700",
          },
        }}
      >
        <Tabs.Screen
          name="index"
          options={{
            title: "Scan",
            tabBarIcon: ({ color, size }) => <Ionicons name="scan" size={size} color={color} />,
          }}
        />
        <Tabs.Screen
          name="history"
          options={{
            title: "History",
            tabBarIcon: ({ color, size }) => <Ionicons name="time" size={size} color={color} />,
          }}
        />
        <Tabs.Screen
          name="guide"
          options={{
            title: "Care Guide",
            tabBarIcon: ({ color, size }) => <Ionicons name="leaf" size={size} color={color} />,
          }}
        />
      </Tabs>
    </QueryClientProvider>
  );
}
