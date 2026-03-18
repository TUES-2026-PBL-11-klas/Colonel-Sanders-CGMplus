import { StyleSheet, Text, Button } from 'react-native';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { useRouter } from 'expo-router';


let isAdmin = 1; //kato napravim userite i authentikaciqta shte go smenq

export default function ExploreScreen() {
  const router = useRouter();
  return (
    <>
    <ThemedView style={styles.container}>
      <ThemedText type="title">Profile</ThemedText> 
    </ThemedView>
    <ThemedText> {isAdmin ? 'You are an admin!' : 'Hello, user!'} </ThemedText>
    {isAdmin && <Button title="Go to Admin Panel" onPress={() => router.push('/admin')} />}
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 0.1,
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    justifyContent: 'center',
  },
});
