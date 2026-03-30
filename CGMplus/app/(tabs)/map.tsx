import React from 'react';
import { View, Text, StyleSheet, useColorScheme } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/theme';
import Animated, { FadeInDown, FadeInUp } from 'react-native-reanimated';

export default function MapScreen() {
  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <Animated.View entering={FadeInUp.delay(100).duration(600)} style={styles.header}>
        <Text style={[styles.title, { color: theme.text }]}>Network Map</Text>
        <Text style={[styles.subtitle, { color: theme.onSurfaceVariant }]}>Live transit routes</Text>
      </Animated.View>

      <Animated.View 
        entering={FadeInDown.delay(200).duration(600)}
        style={[styles.mapCard, { backgroundColor: theme.surface, shadowColor: '#000' }]}
      >
        <Ionicons name="map-outline" size={64} color={theme.outline} style={{ marginBottom: 16 }} />
        <Text style={[styles.placeholderText, { color: theme.onSurfaceVariant }]}>Interactive Map Coming Soon</Text>
        <Text style={[styles.placeholderSub, { color: theme.outline }]}>Integration with Google Maps is pending.</Text>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 24,
    paddingTop: 60,
  },
  header: {
    marginBottom: 32,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    letterSpacing: -0.5,
  },
  subtitle: {
    fontSize: 14,
    marginTop: 4,
    fontWeight: '400',
  },
  mapCard: {
    flex: 1,
    marginBottom: 100, // Leave room for tab bar
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
    elevation: 3,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
  },
  placeholderText: {
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center',
    marginBottom: 8,
  },
  placeholderSub: {
    fontSize: 14,
    textAlign: 'center',
  }
});
