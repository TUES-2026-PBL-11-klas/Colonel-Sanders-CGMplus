import { Button } from 'react-native';
import { tabScreenStyles } from '@/constants/tab-screens';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { useRouter } from 'expo-router';


let isAdmin = 1; //kato napravim userite i authentikaciqta shte go smenq

export default function ExploreScreen() {
  const router = useRouter();
  return (
    <>
      <ThemedView style={tabScreenStyles.container}>
        <ThemedText type="title">Profile</ThemedText>
      </ThemedView>
      <ThemedText> {isAdmin ? 'You are an admin!' : 'Hello, user!'} </ThemedText>
      {isAdmin && <Button title="Go to Admin Panel" onPress={() => router.push('/admin')} />}
    </>
  );
}
