import { tabScreenStyles } from '@/constants/tab-screens';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';

export default function TicketsScreen() {
  return (
      <ThemedView style={tabScreenStyles.container}>
        <ThemedText type="title">Tickets</ThemedText>
      </ThemedView>
  );
}
