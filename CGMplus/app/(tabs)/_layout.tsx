import { Tabs } from 'expo-router';
import React from 'react';
import { StyleSheet } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { HapticTab } from '@/components/haptic-tab';
import { HomeIcon, MapIcon, WalletIcon, ProfileIcon, TicketIcon } from '@/components/ui/tab-icons';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

export default function TabLayout() {
  const colorScheme = useColorScheme();
  const { top, bottom } = useSafeAreaInsets();

  return (
    <Tabs
      backBehavior="initialRoute"
      screenOptions={{
        tabBarActiveTintColor: Colors[colorScheme ?? 'light'].primary,
        tabBarInactiveTintColor: Colors[colorScheme ?? 'light'].onSurfaceVariant,
        headerShown: false,
        sceneStyle: {
          paddingTop: top,
        },

        tabBarButton: HapticTab,
        tabBarStyle: {
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: 100 + bottom,
          backgroundColor: Colors[colorScheme ?? 'light'].surface,
          borderTopLeftRadius: 28,
          borderTopRightRadius: 28,
          borderWidth: StyleSheet.hairlineWidth,
          borderColor: Colors[colorScheme ?? 'light'].outline + '55',
          paddingTop: 30,
          paddingBottom: bottom,
          shadowColor: '#000',
          shadowOffset: { width: 0, height: -2 },
          shadowOpacity: 0.05,
          shadowRadius: 10,
          elevation: 8,
          zIndex: 100,
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
