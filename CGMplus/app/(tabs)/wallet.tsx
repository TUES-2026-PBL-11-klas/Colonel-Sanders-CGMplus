import { tabScreenStyles } from '@/constants/tab-screens';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';

export default function ExploreScreen() {
  return (
    <ThemedView style={tabScreenStyles.container}>
      <ThemedText type="title">Wallet</ThemedText>
    </ThemedView>
  );
}
