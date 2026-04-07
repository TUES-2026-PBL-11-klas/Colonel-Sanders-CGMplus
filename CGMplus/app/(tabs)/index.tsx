import React from 'react';
import { View, Text, StyleSheet, ScrollView, Image, TouchableOpacity, useColorScheme, BackHandler, Alert, Linking } from 'react-native';
import { useRouter, useFocusEffect } from 'expo-router';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import { useAuth } from '../../context/auth-context';
import { Colors } from '@/constants/theme';
import Animated, { FadeInDown, FadeInUp } from 'react-native-reanimated';
import { Animated as RNAnimated, PanResponder, type PanResponderGestureState, Pressable } from 'react-native';
import QRCodeStyled from 'react-native-qrcode-styled';
import { HCESession, NFCTagType4NDEFContentType, NFCTagType4 } from 'react-native-hce';
import {
  getOverlayStyle,
  getTopSheetStyle,
  SHEET_HEIGHT,
  walletStyles,
} from '../../components/wallet-styles';

import { membershipCardMock, MOCK_TICKETS, MOCK_LOYALTY } from '@/constants/mock-data';

const QR_HEIGHT = 540;

export default function HomeScreen() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];
  const borderColor = theme.outline || '#d9dde3';
  const isDark = colorScheme === 'dark';

  // Sheet background: lighter undertone so it floats above the page bg
  const sheetBg = isDark ? '#26252B' : '#F2F5F9';

  // --- QR Bottom Sheet ---
  const [isQrOpen, setIsQrOpen] = React.useState(false);
  const qrTranslateY = React.useRef(new RNAnimated.Value(QR_HEIGHT)).current;
  const qrOverlayOpacity = React.useRef(new RNAnimated.Value(0)).current;

  // --- NFC Top Sheet ---
  const [isNfcOpen, setIsNfcOpen] = React.useState(false);
  const nfcTranslateY = React.useRef(new RNAnimated.Value(-SHEET_HEIGHT)).current;
  const nfcOverlayOpacity = React.useRef(new RNAnimated.Value(0)).current;

  const nfcPayload = 'CGMplus-SecurePass';
  const qrValue = `${nfcPayload} | ${membershipCardMock.cardNumber}`;

  // ── HCE ──────────────────────────────────────────────────────────────────────
  const startHceBroadcast = async () => {
    try {
      const session = await HCESession.getInstance();
      const tag = new NFCTagType4({ type: NFCTagType4NDEFContentType.Text, content: nfcPayload, writable: false });
      await session.setApplication(tag);
      await session.setEnabled(true);
    } catch (e) { /* ignored */ }
  };

  const stopHceBroadcast = async () => {
    try {
      const session = await HCESession.getInstance();
      await session.setEnabled(false);
    } catch (e) { /* ignored */ }
  };

  // ── QR Sheet ─────────────────────────────────────────────────────────────────
  const openQr = () => {
    setIsQrOpen(true);
    RNAnimated.parallel([
      RNAnimated.spring(qrTranslateY, { toValue: 0, useNativeDriver: true, damping: 18, stiffness: 180, mass: 0.8 }),
      RNAnimated.timing(qrOverlayOpacity, { toValue: 1, duration: 180, useNativeDriver: true }),
    ]).start();
  };

  const closeQr = () => {
    RNAnimated.parallel([
      RNAnimated.timing(qrTranslateY, { toValue: QR_HEIGHT, duration: 180, useNativeDriver: true }),
      RNAnimated.timing(qrOverlayOpacity, { toValue: 0, duration: 160, useNativeDriver: true }),
    ]).start(() => setIsQrOpen(false));
  };

  // ── NFC Sheet ────────────────────────────────────────────────────────────────
  const openNfc = () => {
    setIsNfcOpen(true);
    startHceBroadcast();
    RNAnimated.parallel([
      RNAnimated.spring(nfcTranslateY, { toValue: 0, useNativeDriver: true, damping: 18, stiffness: 180, mass: 0.8 }),
      RNAnimated.timing(nfcOverlayOpacity, { toValue: 1, duration: 180, useNativeDriver: true }),
    ]).start();
  };

  const closeNfc = () => {
    stopHceBroadcast();
    RNAnimated.parallel([
      RNAnimated.timing(nfcTranslateY, { toValue: -SHEET_HEIGHT, duration: 180, useNativeDriver: true }),
      RNAnimated.timing(nfcOverlayOpacity, { toValue: 0, duration: 160, useNativeDriver: true }),
    ]).start(() => setIsNfcOpen(false));
  };

  // ── Pan Responders ───────────────────────────────────────────────────────────
  const nfcPan = React.useRef(PanResponder.create({
    onMoveShouldSetPanResponder: (_, g) => Math.abs(g.dy) > 8,
    onPanResponderMove: (_, g) => nfcTranslateY.setValue(Math.min(0, g.dy)),
    onPanResponderRelease: (_, g) => {
      if (g.dy < -40 || g.vy < -0.8) closeNfc();
      else RNAnimated.spring(nfcTranslateY, { toValue: 0, useNativeDriver: true, damping: 18, stiffness: 180, mass: 0.8 }).start();
    },
    onPanResponderTerminate: (_, g) => {
      if (g.dy < -40 || g.vy < -0.8) closeNfc();
      else RNAnimated.spring(nfcTranslateY, { toValue: 0, useNativeDriver: true, damping: 18, stiffness: 180, mass: 0.8 }).start();
    },
  })).current;

  const qrPan = React.useRef(PanResponder.create({
    onMoveShouldSetPanResponder: (_, g) => Math.abs(g.dy) > 8,
    onPanResponderMove: (_, g) => qrTranslateY.setValue(Math.max(0, g.dy)),
    onPanResponderRelease: (_, g) => {
      if (g.dy > 40 || g.vy > 0.8) closeQr();
      else RNAnimated.spring(qrTranslateY, { toValue: 0, useNativeDriver: true, damping: 18, stiffness: 180, mass: 0.8 }).start();
    },
    onPanResponderTerminate: (_, g) => {
      if (g.dy > 40 || g.vy > 0.8) closeQr();
      else RNAnimated.spring(qrTranslateY, { toValue: 0, useNativeDriver: true, damping: 18, stiffness: 180, mass: 0.8 }).start();
    },
  })).current;

  useFocusEffect(
    React.useCallback(() => {
      const onBackPress = () => {
        if (isQrOpen) { closeQr(); return true; }
        Alert.alert('Exit App', 'Are you sure you want to exit CGMplus?', [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Exit', style: 'destructive', onPress: () => BackHandler.exitApp() },
        ]);
        return true;
      };
      const subscription = BackHandler.addEventListener('hardwareBackPress', onBackPress);
      return () => {
        subscription.remove();
        if (isQrOpen) closeQr();
      };
    }, [isQrOpen])
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

        {/* Quick Actions */}
        <Animated.View entering={FadeInDown.delay(400).duration(600)} style={{ marginTop: 24 }}>
          <Text style={[styles.sectionTitle, { color: theme.onSurfaceVariant }]}>Quick Actions</Text>
          <View style={{ gap: 12 }}>

            {/* Show QR Pass */}
            <TouchableOpacity
              onPress={openQr}
              style={[styles.miniCard, { backgroundColor: theme.surface }]}
            >
              <View style={[styles.miniIconBg, { backgroundColor: theme.primaryContainer }]}>
                <Ionicons name="qr-code-outline" size={22} color={theme.onPrimaryContainer} />
              </View>
              <View style={styles.miniCardContent}>
                <Text style={[styles.miniCardText, { color: theme.onSurface }]}>Show QR Pass</Text>
                <Text style={[styles.miniCardSub, { color: theme.onSurfaceVariant }]}>Scan at transit gates</Text>
              </View>
              <Ionicons name="chevron-forward" size={18} color={theme.outline} />
            </TouchableOpacity>

            {/* Scan NFC Pass – opens top sheet */}
            <TouchableOpacity
              onPress={openNfc}
              style={[styles.miniCard, { backgroundColor: theme.surface }]}
            >
              <View style={[styles.miniIconBg, { backgroundColor: theme.primaryContainer }]}>
                <MaterialIcons name="contactless" size={22} color={theme.onPrimaryContainer} />
              </View>
              <View style={styles.miniCardContent}>
                <Text style={[styles.miniCardText, { color: theme.onSurface }]}>Scan NFC Pass</Text>
                <Text style={[styles.miniCardSub, { color: theme.onSurfaceVariant }]}>Tap your phone to a reader</Text>
              </View>
              <MaterialIcons name="contactless" size={18} color={theme.outline} />
            </TouchableOpacity>

            {/* My Tix */}
            <TouchableOpacity
              onPress={() => router.push('/(tabs)/wallet' as any)}
              style={[styles.miniCard, { backgroundColor: theme.surface }]}
            >
              <View style={[styles.miniIconBg, { backgroundColor: '#FFF3CD' }]}>
                <Ionicons name="star-outline" size={22} color="#A05C00" />
              </View>
              <View style={styles.miniCardContent}>
                <Text style={[styles.miniCardText, { color: theme.onSurface }]}>My Tix</Text>
                <Text style={[styles.miniCardSub, { color: '#A05C00', fontWeight: '700' }]}>
                  {MOCK_LOYALTY.points.toLocaleString()} Tix
                </Text>
              </View>
              <Ionicons name="chevron-forward" size={18} color={theme.outline} />
            </TouchableOpacity>

            {/* My Tickets */}
            <TouchableOpacity
              onPress={() => router.push('/(tabs)/tickets' as any)}
              style={[styles.miniCard, { backgroundColor: theme.surface }]}
            >
              <View style={[styles.miniIconBg, { backgroundColor: '#EDE7F6' }]}>
                <Ionicons name="ticket-outline" size={22} color="#512DA8" />
              </View>
              <View style={styles.miniCardContent}>
                <Text style={[styles.miniCardText, { color: theme.onSurface }]}>My Tickets</Text>
                <Text style={[styles.miniCardSub, { color: theme.onSurfaceVariant }]}>
                  {MOCK_TICKETS.filter(t => t.status === 'Active').length} active passes
                </Text>
              </View>
              <Ionicons name="chevron-forward" size={18} color={theme.outline} />
            </TouchableOpacity>

            {/* Trip Planner */}
            <TouchableOpacity
              onPress={() => router.push('/(tabs)/map' as any)}
              style={[styles.miniCard, { backgroundColor: theme.surface }]}
            >
              <View style={[styles.miniIconBg, { backgroundColor: '#FCE4EC' }]}>
                <Ionicons name="map-outline" size={22} color="#880E4F" />
              </View>
              <View style={styles.miniCardContent}>
                <Text style={[styles.miniCardText, { color: theme.onSurface }]}>Trip Planner</Text>
                <Text style={[styles.miniCardSub, { color: theme.onSurfaceVariant }]}>Plan your commute</Text>
              </View>
              <Ionicons name="chevron-forward" size={18} color={theme.outline} />
            </TouchableOpacity>

          </View>
        </Animated.View>

      </ScrollView>

      {/* NFC Sheet Overlay */}
      {isNfcOpen && (
        <RNAnimated.View style={getOverlayStyle(nfcOverlayOpacity)}>
          <Pressable style={{ flex: 1 }} onPress={closeNfc} />
        </RNAnimated.View>
      )}

      {/* NFC TOP SHEET */}
      <RNAnimated.View
        pointerEvents={isNfcOpen ? 'auto' : 'none'}
        style={[walletStyles.topSheet, { backgroundColor: sheetBg, transform: [{ translateY: nfcTranslateY }] }]}
        {...nfcPan.panHandlers}
      >
        <View style={walletStyles.nfcActiveContainer}>
          <View style={[walletStyles.nfcScanningCircle, { backgroundColor: theme.primaryContainer }]}>
            <MaterialIcons name="contactless" size={48} color={theme.onPrimaryContainer} />
          </View>
          <Text style={[walletStyles.sheetText, { color: isDark ? '#E6E1E5' : '#1C1B1F' }]}>Ready to Scan</Text>
          <Text style={[walletStyles.sheetCaption, { color: isDark ? '#938F99' : '#79747E' }]}>
            Hold near the transit reader
          </Text>
        </View>
      </RNAnimated.View>

      {/* QR Bottom Sheet Overlay */}
      {isQrOpen && (
        <RNAnimated.View style={getOverlayStyle(qrOverlayOpacity)}>
          <Pressable style={{ flex: 1 }} onPress={closeQr} />
        </RNAnimated.View>
      )}

      {/* QR Bottom Sheet */}
      <RNAnimated.View
        pointerEvents={isQrOpen ? 'auto' : 'none'}
        style={[styles.qrSheet, { backgroundColor: sheetBg, transform: [{ translateY: qrTranslateY }] }]}
        {...qrPan.panHandlers}
      >
        <Text style={[styles.qrSheetTitle, { color: isDark ? '#E6E1E5' : '#1C1B1F' }]}>Digital Pass</Text>
        <View style={styles.qrBody}>
          <View style={styles.qrWrapper}>
            <QRCodeStyled
              data={qrValue}
              size={220}
              pieceBorderRadius={0}
              color={'#000000'}
            />
          </View>
          <Text style={[styles.qrCardNum, { color: isDark ? '#CAC4D0' : '#49454F' }]}>
            {membershipCardMock.cardNumber}
          </Text>
          <Text style={[styles.qrCaption, { color: isDark ? '#938F99' : '#79747E' }]}>
            Show this code to the attendant
          </Text>
        </View>
      </RNAnimated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  scrollContent: {
    padding: 24,
    paddingTop: 60,
    paddingBottom: 120,
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
  nfcIcon: { opacity: 0.9 },
  cardBody: { padding: 24 },
  validationContainer: {
    flexDirection: 'row',
    padding: 16,
    borderRadius: 20,
    alignItems: 'flex-start',
  },
  validationTextGroup: { marginLeft: 12, flex: 1 },
  validationTitle: { fontSize: 16, fontWeight: '600' },
  validationDesc: { fontSize: 14, marginTop: 4, lineHeight: 20 },
  actionGroup: { marginTop: 24, gap: 12 },
  button: {
    height: 52,
    borderRadius: 999,
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonOutlined: { backgroundColor: 'transparent', borderWidth: 1 },
  buttonText: { color: '#FFFFFF', fontSize: 16, fontWeight: '600' },
  buttonTextOutlined: { fontSize: 16, fontWeight: '600' },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
    marginLeft: 4,
  },
  miniCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.03,
    shadowRadius: 8,
    elevation: 2,
  },
  miniIconBg: {
    width: 44,
    height: 44,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
  },
  miniCardContent: { flex: 1 },
  miniCardText: { fontSize: 15, fontWeight: '600' },
  miniCardSub: { fontSize: 12, marginTop: 2 },
  // QR Bottom Sheet
  qrSheet: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: QR_HEIGHT,
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    zIndex: 30,
    elevation: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -6 },
    shadowOpacity: 0.2,
    shadowRadius: 20,
    paddingTop: 20,
    paddingBottom: 83, // navbar height keeps content above tab bar
    paddingHorizontal: 24,
  },
  qrSheetTitle: {
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 20,
  },
  qrBody: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  qrWrapper: {
    backgroundColor: '#FFFFFF',
    padding: 20,
    borderRadius: 12,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    marginBottom: 24,
  },
  qrCardNum: {
    fontSize: 16,
    fontWeight: '600',
    letterSpacing: 4,
    marginBottom: 8,
  },
  qrCaption: {
    fontSize: 13,
    textAlign: 'center',
  },
});
