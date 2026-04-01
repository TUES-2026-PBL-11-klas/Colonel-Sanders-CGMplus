import React from 'react';
import { View, Text, StyleSheet, ScrollView, Image, TouchableOpacity, useColorScheme, Platform, BackHandler, Alert } from 'react-native';
import { useRouter, useFocusEffect } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../context/auth-context';
import { Colors } from '@/constants/theme';
import Animated, { FadeInDown, FadeInUp } from 'react-native-reanimated';

export default function HomeScreen() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];

  useFocusEffect(
    React.useCallback(() => {
      const onBackPress = () => {
        Alert.alert('Exit App', 'Are you sure you want to exit CGMplus?', [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Exit', style: 'destructive', onPress: () => BackHandler.exitApp() },
        ]);
        return true;
      };
      const subscription = BackHandler.addEventListener('hardwareBackPress', onBackPress);
      return () => subscription.remove();
    }, [])
  );

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        
        <Animated.View 
          entering={FadeInUp.delay(100).duration(600)}
          style={styles.header}
        >
          <View style={[styles.logoContainer, { backgroundColor: theme.primaryContainer }]}>
            <Ionicons name="home" size={36} color={theme.onPrimaryContainer} />
          </View>
          <Text style={[styles.title, { color: theme.text }]}>Dashboard</Text>
          <Text style={[styles.subtitle, { color: theme.onSurfaceVariant }]}>Welcome to CGMplus</Text>
        </Animated.View>

        <Animated.View 
          entering={FadeInDown.delay(250).duration(600)}
          style={[styles.ticketCard, { backgroundColor: theme.surface }]}
        >
          <View style={styles.cardGraphicContainer}>
            <Image
              source={require('@/assets/graphics/card-graphic.jpg')}
              style={styles.cardGraphic}
            />
            <View style={styles.cardGraphicOverlay}>
              <Text style={styles.graphicText}>Overview</Text>
              <Ionicons name="stats-chart" size={24} color="#FFF" style={styles.nfcIcon} />
            </View>
          </View>

          <View style={styles.cardBody}>
            {!isAuthenticated ? (
              <View style={[styles.validationContainer, { backgroundColor: theme.surfaceVariant }]}>
                <Ionicons name="information-circle" size={24} color={theme.primary} />
                <View style={styles.validationTextGroup}>
                  <Text style={[styles.validationTitle, { color: theme.onSurface }]}>Guest Mode</Text>
                  <Text style={[styles.validationDesc, { color: theme.onSurfaceVariant }]}>
                    You are currently viewing the app as a guest. Sign in to access all features.
                  </Text>
                </View>
              </View>
            ) : (
              <View style={[styles.validationContainer, { backgroundColor: theme.primaryContainer }]}>
                <Ionicons name="checkmark-circle" size={24} color={theme.primary} />
                <View style={styles.validationTextGroup}>
                  <Text style={[styles.validationTitle, { color: theme.onPrimaryContainer }]}>Active Session</Text>
                  <Text style={[styles.validationDesc, { color: theme.onPrimaryContainer, opacity: 0.8 }]}>
                    Your digital pass and features are ready to use.
                  </Text>
                </View>
              </View>
            )}

            {!isAuthenticated && (
              <View style={styles.actionGroup}>
                <TouchableOpacity 
                  style={[styles.button, { backgroundColor: theme.primary }]} 
                  onPress={() => router.push('/(auth)/login' as any)}
                >
                  <Text style={styles.buttonText}>Log In</Text>
                </TouchableOpacity>
                <TouchableOpacity 
                  style={[styles.button, styles.buttonOutlined, { borderColor: theme.outline }]} 
                  onPress={() => router.push('/(auth)/register' as any)}
                >
                  <Text style={[styles.buttonTextOutlined, { color: theme.primary }]}>Register</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        </Animated.View>

        {/* Example of additional M3 layout / content blocks */}
        <Animated.View entering={FadeInDown.delay(400).duration(600)} style={{marginTop: 24}}>
          <Text style={[styles.sectionTitle, { color: theme.onSurfaceVariant }]}>Quick Actions</Text>
          <View style={[styles.miniCard, { backgroundColor: theme.surface, shadowColor: '#000' }]}>
            <Ionicons name="qr-code-outline" size={24} color={theme.primary} />
            <Text style={[styles.miniCardText, { color: theme.onSurface }]}>Scan QR Pass</Text>
          </View>
        </Animated.View>

      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    padding: 24,
    paddingTop: 60,
    paddingBottom: 120, // Leave room for tab bar
  },
  header: {
    alignItems: 'flex-start',
    marginBottom: 32,
  },
  logoContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
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
  ticketCard: {
    borderRadius: 28,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 4,
  },
  cardGraphicContainer: {
    height: 120,
    width: '100%',
    position: 'relative',
  },
  cardGraphic: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  cardGraphicOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.4)',
    justifyContent: 'flex-end',
    padding: 20,
    flexDirection: 'row',
    alignItems: 'flex-end',
  },
  graphicText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: '600',
    flex: 1,
  },
  nfcIcon: {
    opacity: 0.9,
  },
  cardBody: {
    padding: 24,
  },
  validationContainer: {
    flexDirection: 'row',
    padding: 16,
    borderRadius: 20,
    alignItems: 'flex-start',
  },
  validationTextGroup: {
    marginLeft: 12,
    flex: 1,
  },
  validationTitle: {
    fontSize: 16,
    fontWeight: '600',
  },
  validationDesc: {
    fontSize: 14,
    marginTop: 4,
    lineHeight: 20,
  },
  actionGroup: {
    marginTop: 24,
    gap: 12,
  },
  button: {
    height: 52,
    borderRadius: 999,
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonOutlined: {
    backgroundColor: 'transparent',
    borderWidth: 1,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  buttonTextOutlined: {
    fontSize: 16,
    fontWeight: '600',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
    marginLeft: 8,
  },
  miniCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    borderRadius: 24,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.03,
    shadowRadius: 8,
    elevation: 2,
  },
  miniCardText: {
    fontSize: 16,
    fontWeight: '500',
    marginLeft: 16,
  }
});
