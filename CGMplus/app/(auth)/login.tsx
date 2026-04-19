import React, { useState } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Image,
  useColorScheme,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useAuth } from '../../context/auth-context';
import Animated, { FadeInDown, FadeInUp } from 'react-native-reanimated';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading, error, clearError } = useAuth();
  const router = useRouter();
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';

  const COLORS = {
    background: isDark ? '#1C1B1F' : '#F4F7F9',
    surface: isDark ? '#2B2A2F' : '#FFFFFF',
    text: isDark ? '#E6E1E5' : '#1C1B1F',
    textSecondary: isDark ? '#CAC4D0' : '#49454F',
    primary: '#0B57D0', // Google Material Blue
    primaryContainer: isDark ? '#004A77' : '#D3E3FD',
    onPrimaryContainer: isDark ? '#C2E7FF' : '#041E49',
    outline: isDark ? '#938F99' : '#79747E',
    error: '#B3261E',
    mint: '#4FD1C5', // Original Brand
    navy: '#1A2B44', // Original Brand
  };

  const handleLogin = async () => {
    if (!email || !password) return;
    const success = await login(email, password);
    if (success) {
      router.replace('/(tabs)');
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: COLORS.background }]}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.content}
      >
        <Animated.View 
          entering={FadeInUp.delay(100).duration(600)}
          style={styles.header}
        >
          {/* Header area resembling a clean Google app logo or transit app icon */}
          <View style={[styles.logoContainer, { backgroundColor: COLORS.primaryContainer }]}>
            <Ionicons name="bus" size={36} color={COLORS.onPrimaryContainer} />
          </View>
          <Text style={[styles.title, { color: COLORS.text }]}>CGMplus</Text>
          <Text style={[styles.subtitle, { color: COLORS.textSecondary }]}>Your Digital Transit Pass</Text>
        </Animated.View>

        <Animated.View 
          entering={FadeInDown.delay(250).duration(600)}
          style={[styles.ticketCard, { backgroundColor: COLORS.surface }]}
        >
          {/* Transit Pass Graphic Header inside the card */}
          <View style={styles.cardGraphicContainer}>
            <Image
              source={require('@/assets/graphics/card-graphic.jpg')}
              style={styles.cardGraphic}
            />
            <View style={styles.cardGraphicOverlay}>
              <Text style={styles.graphicText}>Sign in to access</Text>
              <Ionicons name="scan" size={24} color="#FFF" style={styles.nfcIcon} />
            </View>
          </View>

          <View style={styles.cardBody}>
            {error ? (
              <View style={styles.errorContainer}>
                <Ionicons name="alert-circle" size={20} color={COLORS.error} />
                <Text style={styles.errorText}>{error}</Text>
              </View>
            ) : null}

            <View style={[styles.inputWrapper, { borderColor: COLORS.outline }]}>
              <TextInput
                style={[styles.input, { color: COLORS.text }]}
                placeholder="Email Address"
                placeholderTextColor={COLORS.textSecondary}
                value={email}
                onChangeText={(text) => {
                  setEmail(text);
                  clearError();
                }}
                autoCapitalize="none"
                keyboardType="email-address"
              />
            </View>

            <View style={[styles.inputWrapper, { borderColor: COLORS.outline, marginTop: 16 }]}>
              <TextInput
                style={[styles.input, { color: COLORS.text }]}
                placeholder="Password"
                placeholderTextColor={COLORS.textSecondary}
                value={password}
                onChangeText={(text) => {
                  setPassword(text);
                  clearError();
                }}
                secureTextEntry
                maxLength={72}
              />
            </View>

            <TouchableOpacity 
              style={[
                styles.button, 
                { backgroundColor: COLORS.primary },
                isLoading && styles.buttonDisabled
              ]} 
              onPress={handleLogin}
              disabled={isLoading}
            >
              {isLoading ? (
                <ActivityIndicator color="#FFFFFF" />
              ) : (
                <Text style={styles.buttonText}>Sign In</Text>
              )}
            </TouchableOpacity>

            <View style={styles.footer}>
              <Text style={[styles.footerText, { color: COLORS.textSecondary }]}>Need a pass? </Text>
              <TouchableOpacity onPress={() => router.push('/(auth)/register' as any)}>
                <Text style={[styles.linkText, { color: COLORS.primary }]}>Create Account</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Animated.View>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    padding: 24,
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logoContainer: {
    width: 72,
    height: 72,
    borderRadius: 36,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: '600',
    letterSpacing: -0.5,
  },
  subtitle: {
    fontSize: 14,
    marginTop: 4,
    fontWeight: '400',
  },
  ticketCard: {
    borderRadius: 28, // Material 3 extra large rounding
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 10,
    elevation: 4,
  },
  cardGraphicContainer: {
    height: 100,
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
    backgroundColor: 'rgba(0,0,0,0.3)',
    justifyContent: 'flex-end',
    padding: 20,
    flexDirection: 'row',
    alignItems: 'flex-end',
  },
  graphicText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '500',
    flex: 1,
  },
  nfcIcon: {
    opacity: 0.8,
  },
  cardBody: {
    padding: 24,
  },
  inputWrapper: {
    borderWidth: 1,
    borderRadius: 16,
    height: 56,
    paddingHorizontal: 16,
    justifyContent: 'center',
  },
  input: {
    fontSize: 16,
    height: '100%',
  },
  button: {
    height: 56,
    borderRadius: 999, // Pill shape
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 24,
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 24,
  },
  footerText: {
    fontSize: 14,
  },
  linkText: {
    fontSize: 14,
    fontWeight: '600',
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F9DEDC',
    padding: 12,
    borderRadius: 12,
    marginBottom: 16,
  },
  errorText: {
    color: '#B3261E',
    fontSize: 14,
    marginLeft: 8,
    flex: 1,
  },
});
