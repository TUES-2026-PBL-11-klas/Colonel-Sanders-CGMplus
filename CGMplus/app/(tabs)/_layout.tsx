import { Tabs } from 'expo-router';
import React from 'react';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { HapticTab } from '@/components/haptic-tab';
import { HomeIcon, MapIcon, WalletIcon, ProfileIcon, TicketIcon } from '@/components/ui/tab-icons';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

export default function TabLayout() {
  const colorScheme = useColorScheme();
  const insets = useSafeAreaInsets();

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: Colors[colorScheme ?? 'light'].tint,
        headerShown: false,
        tabBarButton: HapticTab,
        tabBarStyle: {
          height: 100 + insets.bottom,
          backgroundColor: Colors[colorScheme ?? 'light'].background,
          borderTopLeftRadius: 20,
          borderTopRightRadius: 20,
          borderTopWidth: 0,
          overflow: 'hidden',
          paddingTop: 30,
          paddingBottom: insets.bottom,
        },
      }}>
      <Tabs.Screen
        name="index"
        options={{
          title: '',
          tabBarIcon: ({ color }) => <HomeIcon size={28} color={color} />,
        }}
      />
      <Tabs.Screen
        name="map"
        options={{
          title: '',
          tabBarIcon: ({ color }) => <MapIcon size={28} color={color} />,
        }}
      />
      <Tabs.Screen
        name="wallet"
        options={{
          title: '',
          tabBarIcon: ({ color }) => <WalletIcon size={28} color={color} />,
        }}
      />
      <Tabs.Screen
        name="tickets"
        options={{
          title: '',
          tabBarIcon: ({ color }) => <TicketIcon size={28} color={color} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: '',
          tabBarIcon: ({ color }) => <ProfileIcon size={28} color={color} />,
        }}
      />
    </Tabs>
  );
}
