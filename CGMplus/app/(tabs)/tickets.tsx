import { tabScreenStyles } from '@/constants/tab-screens';

import ParallaxScrollView from '@/components/parallax-scroll-view';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Link } from 'expo-router';

export default function TicketsScreen() {
  return (
      <ThemedView style={tabScreenStyles.container}>
        <ThemedText type="title">Tickets</ThemedText>
      </ThemedView>
  );
}
