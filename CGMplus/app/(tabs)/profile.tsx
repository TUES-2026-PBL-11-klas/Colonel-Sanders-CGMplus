import { tabScreenStyles } from '@/constants/tab-screens';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { useRouter } from 'expo-router';


export default function ExploreScreen() {
  const router = useRouter();
  return (
    <>
      <ThemedView style={tabScreenStyles.container}>
        <ThemedText type="title">Profile</ThemedText>
      </ThemedView>
    </>
  );
}
