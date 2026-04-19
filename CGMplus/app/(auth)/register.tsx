import React, { useState, useEffect } from 'react';
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
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useAuth } from '../../context/auth-context';
import Animated, { FadeInDown, FadeInUp } from 'react-native-reanimated';

export default function RegisterScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const { register, isLoading, error, clearError } = useAuth();
  const router = useRouter();
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';

  const COLORS = {
    background: isDark ? '#1C1B1F' : '#F4F7F9',
    surface: isDark ? '#2B2A2F' : '#FFFFFF',
    text: isDark ? '#E6E1E5' : '#1C1B1F',
    textSecondary: isDark ? '#CAC4D0' : '#49454F',
    primary: '#0B57D0',
    primaryContainer: isDark ? '#004A77' : '#D3E3FD',
    onPrimaryContainer: isDark ? '#C2E7FF' : '#041E49',
    outline: isDark ? '#938F99' : '#79747E',
    error: '#B3261E',
    success: isDark ? '#81C995' : '#137333',
    surfaceVariant: isDark ? '#49454F' : '#E7E0EC',
  };

  const [validation, setValidation] = useState({
    length: false,
    uppercase: false,
    digit: false,
    special: false,
  });

  useEffect(() => {
    setValidation({
      length: password.length >= 8 && password.length <= 72,
      uppercase: /[A-Z]/.test(password),
      digit: /[0-9]/.test(password),
      special: /[!@#$%^&*]/.test(password),
    });
  }, [password]);

  const isPasswordValid = Object.values(validation).every(Boolean);
  const passwordsMatch = password === confirmPassword && confirmPassword !== '';

  const handleRegister = async () => {
    if (!email || !isPasswordValid || !passwordsMatch) return;
    const success = await register(email, password);
    if (success) {
      router.replace('/(tabs)');
    }
  };

  const ValidationItem = ({ label, isValid }: { label: string, isValid: boolean }) => (
    <View style={styles.validationRow}>
      <Ionicons
        name={isValid ? "checkmark-circle" : "ellipse-outline"}
        size={16}
        color={isValid ? COLORS.success : COLORS.textSecondary}
      />
      <Text style={[styles.validationText, isValid ? { color: COLORS.success } : { color: COLORS.textSecondary }]}>
        {label}
      </Text>
    </View>
  );

  return (
    <View style={[styles.container, { backgroundColor: COLORS.background }]}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}
      >
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <Animated.View
            entering={FadeInUp.delay(100).duration(600)}
            style={styles.header}
          >
            <View style={[styles.logoContainer, { backgroundColor: COLORS.primaryContainer }]}>
              <Ionicons name="card" size={36} color={COLORS.onPrimaryContainer} />
            </View>
            <Text style={[styles.title, { color: COLORS.text }]}>Нов пропуск</Text>
            <Text style={[styles.subtitle, { color: COLORS.textSecondary }]}>Регистрирай се за ЦГМ+</Text>
          </Animated.View>

          <Animated.View
            entering={FadeInDown.delay(250).duration(600)}
            style={[styles.ticketCard, { backgroundColor: COLORS.surface }]}
          >
            <View style={styles.cardGraphicContainer}>
              <Image
                source={require('@/assets/graphics/card-graphic.jpg')}
                style={styles.cardGraphic}
              />
              <View style={styles.cardGraphicOverlay}>
                <Text style={styles.graphicText}>Активирай акаунт</Text>
                <Ionicons name="scan" size={24} color="#FFF" style={styles.nfcIcon} />
              </View>
            </View>

            <View style={styles.cardBody}>
              {error ? (
                <View style={[styles.errorContainer, { backgroundColor: '#F9DEDC' }]}>
                  <Ionicons name="alert-circle" size={20} color={COLORS.error} />
                  <Text style={[styles.errorText, { color: COLORS.error }]}>{error}</Text>
                </View>
              ) : null}

              <View style={[styles.inputWrapper, { borderColor: COLORS.outline }]}>
                <TextInput
                  style={[styles.input, { color: COLORS.text }]}
                  placeholder="Имейл адрес"
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
                  placeholder="Парола"
                  placeholderTextColor={COLORS.textSecondary}
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry
                  maxLength={72}
                />
              </View>

              <View style={[styles.validationContainer, { backgroundColor: COLORS.surfaceVariant }]}>
                <ValidationItem label="8-72 символа" isValid={validation.length} />
                <ValidationItem label="Една главна буква" isValid={validation.uppercase} />
                <ValidationItem label="Една цифра" isValid={validation.digit} />
                <ValidationItem label="Един специален символ (!@#$%^&*)" isValid={validation.special} />
              </View>

              <View style={[styles.inputWrapper, { borderColor: COLORS.outline, marginTop: 8 }]}>
                <TextInput
                  style={[styles.input, { color: COLORS.text }]}
                  placeholder="Потвърди паролата"
                  placeholderTextColor={COLORS.textSecondary}
                  value={confirmPassword}
                  onChangeText={setConfirmPassword}
                  secureTextEntry
                  maxLength={72}
                />
              </View>

              {confirmPassword !== '' && !passwordsMatch && (
                <Text style={[styles.validationError, { color: COLORS.error }]}>Паролите не съвпадат</Text>
              )}

              <TouchableOpacity
                style={[
                  styles.button,
                  { backgroundColor: COLORS.primary },
                  (isLoading || !isPasswordValid || !passwordsMatch) && { backgroundColor: COLORS.outline }
                ]}
                onPress={handleRegister}
                disabled={isLoading || !isPasswordValid || !passwordsMatch}
              >
                {isLoading ? (
                  <ActivityIndicator color="#FFFFFF" />
                ) : (
                  <Text style={styles.buttonText}>Регистрирай се</Text>
                )}
              </TouchableOpacity>

              <View style={styles.footer}>
                <Text style={[styles.footerText, { color: COLORS.textSecondary }]}>Вече имаш акаунт? </Text>
                <TouchableOpacity onPress={() => router.back()}>
                  <Text style={[styles.linkText, { color: COLORS.primary }]}>Влез</Text>
                </TouchableOpacity>
              </View>
            </View>
          </Animated.View>
        </ScrollView>
      </KeyboardAvoidingView>
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
    paddingBottom: 40,
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
    borderRadius: 28,
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
  validationContainer: {
    padding: 16,
    marginTop: 16,
    borderRadius: 16,
  },
  validationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 4,
  },
  validationText: {
    fontSize: 12,
    marginLeft: 8,
  },
  validationError: {
    fontSize: 12,
    marginTop: 8,
    marginLeft: 4,
  },
  button: {
    height: 56,
    borderRadius: 999, // Pill shape
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 24,
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
    padding: 12,
    borderRadius: 12,
    marginBottom: 16,
  },
  errorText: {
    fontSize: 14,
    marginLeft: 8,
    flex: 1,
  },
});
