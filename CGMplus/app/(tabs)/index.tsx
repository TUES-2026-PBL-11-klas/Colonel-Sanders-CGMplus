import { ThemedView } from '@/components/themed-view';
import { tabScreenStyles } from '@/constants/tab-screens';
import { ThemedText } from '@/components/themed-text';

export default function HomeScreen() {
	return (
		<ThemedView style={tabScreenStyles.container}>
      <ThemedText type="title">Home</ThemedText>
    </ThemedView>
	);
}
