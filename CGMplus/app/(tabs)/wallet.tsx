import { useEffect, useRef, useState, useCallback } from 'react';
import {
  Animated,
  PanResponder,
  Pressable,
  View,
  BackHandler,
  Image,
  Text,
  ScrollView,
  useColorScheme,
  type PanResponderGestureState,
} from 'react-native';
import MaterialIcons from '@expo/vector-icons/MaterialIcons';
import { Ionicons } from '@expo/vector-icons';
import { HCESession, NFCTagType4NDEFContentType, NFCTagType4 } from 'react-native-hce';
import { useLocalSearchParams, useFocusEffect } from 'expo-router';
import QRCodeStyled from 'react-native-qrcode-styled';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Colors } from '@/constants/theme';

import { getOverlayStyle, SHEET_HEIGHT, walletStyles} from '@/components/wallet-styles';

import { MOCK_CARD, MOCK_LOYALTY } from '@/constants/mock-data';

const nfcPayload = 'CGMplus-SecurePass';
const qrValue = `${nfcPayload} | ${MOCK_CARD.number}`;

const QR_SHEET_HEIGHT = 540;

// ─── Component ─────────────────────────────────────────────────────────────────
export default function WalletScreen() {
  const { action } = useLocalSearchParams<{ action?: string }>();

  const [isNfcOpen, setIsNfcOpen] = useState(false);
  const [isQrOpen, setIsQrOpen] = useState(false);

  const nfcTranslateY = useRef(new Animated.Value(-SHEET_HEIGHT)).current;
  const qrTranslateY = useRef(new Animated.Value(QR_SHEET_HEIGHT)).current;
  const nfcOverlayOpacity = useRef(new Animated.Value(0)).current;
  const qrOverlayOpacity = useRef(new Animated.Value(0)).current;

  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];
  const isDark = colorScheme === 'dark';

  // Sheet backgrounds: lighter undertone so they float above page bg
  const sheetBg = isDark ? '#26252B' : '#F2F5F9';

  // Progress for Tix
  const tixProgress = Math.min(MOCK_LOYALTY.points / MOCK_LOYALTY.nextTierAt, 1);

  // ─── HCE ───────────────────────────────────────────────────────────────────
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

  // ─── NFC Sheet ─────────────────────────────────────────────────────────────
  const openNfc = () => {
    setIsNfcOpen(true);
    startHceBroadcast();
    Animated.parallel([
      Animated.spring(nfcTranslateY, { toValue: 0, useNativeDriver: true, damping: 18, stiffness: 180, mass: 0.8 }),
      Animated.timing(nfcOverlayOpacity, { toValue: 1, duration: 180, useNativeDriver: true }),
    ]).start();
  };

  const closeNfc = () => {
    stopHceBroadcast();
    Animated.parallel([
      Animated.timing(nfcTranslateY, { toValue: -SHEET_HEIGHT, duration: 180, useNativeDriver: true }),
      Animated.timing(nfcOverlayOpacity, { toValue: 0, duration: 160, useNativeDriver: true }),
    ]).start(() => setIsNfcOpen(false));
  };

  // ─── QR Sheet ──────────────────────────────────────────────────────────────
  const openQr = () => {
    setIsQrOpen(true);
    Animated.parallel([
      Animated.spring(qrTranslateY, { toValue: 0, useNativeDriver: true, damping: 18, stiffness: 180, mass: 0.8 }),
      Animated.timing(qrOverlayOpacity, { toValue: 1, duration: 180, useNativeDriver: true }),
    ]).start();
  };

  const closeQr = () => {
    Animated.parallel([
      Animated.timing(qrTranslateY, { toValue: QR_SHEET_HEIGHT, duration: 180, useNativeDriver: true }),
      Animated.timing(qrOverlayOpacity, { toValue: 0, duration: 160, useNativeDriver: true }),
    ]).start(() => setIsQrOpen(false));
  };

  // ─── Lifecycle ─────────────────────────────────────────────────────────────
  useFocusEffect(
    useCallback(() => {
      return () => {
        if (isNfcOpen) closeNfc();
        if (isQrOpen) closeQr();
      };
    }, [isNfcOpen, isQrOpen])
  );

  useEffect(() => {
    if (action === 'nfc') openNfc();
    else if (action === 'qr') openQr();
  }, [action]);

  useEffect(() => {
    const onBackPress = () => {
      if (isNfcOpen) { closeNfc(); return true; }
      if (isQrOpen) { closeQr(); return true; }
      return false;
    };
    const sub = BackHandler.addEventListener('hardwareBackPress', onBackPress);
    return () => sub.remove();
  }, [isNfcOpen, isQrOpen]);

  // ─── Pan Responders ────────────────────────────────────────────────────────
  const handleRelease = (closeFn: () => void, anim: Animated.Value, isBottom: boolean) =>
    (_e: any, gesture: PanResponderGestureState) => {
      if (isBottom) {
        if (gesture.dy > 40 || gesture.vy > 0.8) closeFn();
        else Animated.spring(anim, { toValue: 0, useNativeDriver: true, damping: 18, stiffness: 180, mass: 0.8 }).start();
      } else {
        if (gesture.dy < -40 || gesture.vy < -0.8) closeFn();
        else Animated.spring(anim, { toValue: 0, useNativeDriver: true, damping: 18, stiffness: 180, mass: 0.8 }).start();
      }
    };

  const nfcPan = useRef(PanResponder.create({
    onMoveShouldSetPanResponder: (_, g) => Math.abs(g.dy) > 8,
    onPanResponderMove: (_, g) => nfcTranslateY.setValue(Math.min(0, g.dy)),
    onPanResponderRelease: handleRelease(closeNfc, nfcTranslateY, false),
    onPanResponderTerminate: handleRelease(closeNfc, nfcTranslateY, false),
  })).current;

  const qrPan = useRef(PanResponder.create({
    onMoveShouldSetPanResponder: (_, g) => Math.abs(g.dy) > 8,
    onPanResponderMove: (_, g) => qrTranslateY.setValue(Math.max(0, g.dy)),
    onPanResponderRelease: handleRelease(closeQr, qrTranslateY, true),
    onPanResponderTerminate: handleRelease(closeQr, qrTranslateY, true),
  })).current;

  // ─── Render ────────────────────────────────────────────────────────────────
  return (
    <ThemedView style={[styles.container, { backgroundColor: theme.background }]}>
      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>

        {/* Header */}
        <View style={styles.headerRow}>
          <ThemedText type="title">Wallet</ThemedText>
        </View>

        {/* ── CARD ──────────────────────────────────────────────────────── */}
        <Pressable
          onPress={openNfc}
          style={({ pressed }) => [styles.card, { opacity: pressed ? 0.93 : 1 }]}
        >
          {/* Gradient-style background using layered views */}
          <Image
            source={require('@/assets/graphics/card-graphic.jpg')}
            style={styles.cardBgImage}
          />
          <View style={styles.cardOverlay} />

          {/* Card Top Row */}
          <View style={styles.cardTopRow}>
            <Text style={styles.cardBrand}>{MOCK_CARD.type}</Text>
            <MaterialIcons name="contactless" size={28} color="rgba(255,255,255,0.85)" />
          </View>

          {/* Card Number – crisp & bright */}
          <Text style={styles.cardNumber}>{MOCK_CARD.number}</Text>

          {/* Card Bottom Row */}
          <View style={styles.cardBottomRow}>
            <View>
              <Text style={styles.cardLabel}>CARD HOLDER</Text>
              <Text style={styles.cardValue}>{MOCK_CARD.holder}</Text>
            </View>
            <View style={{ alignItems: 'flex-end' }}>
              <Text style={styles.cardLabel}>EXPIRES</Text>
              <Text style={styles.cardValue}>{MOCK_CARD.expiry}</Text>
            </View>
          </View>
        </Pressable>

        <Text style={[styles.instructionHint, { color: theme.onSurfaceVariant }]}>
          <MaterialIcons name="contactless" size={16} color={theme.onSurfaceVariant} />
          {' '}Tap card to use NFC
        </Text>

        {/* ── ACTION ROW ─────────────────────────────────────────────────── */}
        <View style={styles.actionRow}>
          <Pressable
            onPress={openQr}
            style={({ pressed }) => [styles.actionBtn, { backgroundColor: theme.primaryContainer, opacity: pressed ? 0.7 : 1 }]}
          >
            <MaterialIcons name="qr-code" size={22} color={theme.onPrimaryContainer} />
            <Text style={[styles.actionBtnText, { color: theme.onPrimaryContainer }]}>QR Pass</Text>
          </Pressable>

          <Pressable
            onPress={openNfc}
            style={({ pressed }) => [styles.actionBtn, { backgroundColor: theme.surfaceVariant, opacity: pressed ? 0.7 : 1 }]}
          >
            <MaterialIcons name="contactless" size={22} color={theme.onSurfaceVariant} />
            <Text style={[styles.actionBtnText, { color: theme.onSurfaceVariant }]}>NFC</Text>
          </Pressable>
        </View>


        {/* ── TIX LOYALTY SECTION ───────────────────────────────────────── */}
        <Text style={[styles.heading, { color: theme.onSurfaceVariant }]}>Tix Loyalty Points</Text>
        <View style={[styles.tixCard, { backgroundColor: theme.surface }]}>
          {/* Top */}
          <View style={styles.tixTopRow}>
            <View style={[styles.tixIconBg, { backgroundColor: '#FFF3CD' }]}>
              <Ionicons name="star" size={22} color="#A05C00" />
            </View>
            <View style={{ flex: 1, marginLeft: 14 }}>
              <Text style={[styles.tixPoints, { color: theme.onSurface }]}>
                {MOCK_LOYALTY.points.toLocaleString()} <Text style={[styles.tixPtsLabel, { color: theme.onSurfaceVariant }]}>Tix</Text>
              </Text>
              <Text style={[styles.tixTier, { color: '#A05C00' }]}>{MOCK_LOYALTY.tier} Member</Text>
            </View>
            <View style={[styles.tixBadge, { backgroundColor: '#FFF3CD' }]}>
              <Text style={styles.tixBadgeText}>{MOCK_LOYALTY.tier}</Text>
            </View>
          </View>

          {/* Progress to next tier */}
          <View style={styles.tixProgressSection}>
            <View style={styles.tixProgressLabelRow}>
              <Text style={[styles.tixProgressLabel, { color: theme.onSurfaceVariant }]}>
                {MOCK_LOYALTY.points} / {MOCK_LOYALTY.nextTierAt} to {MOCK_LOYALTY.nextTier}
              </Text>
              <Text style={[styles.tixProgressPct, { color: '#A05C00' }]}>
                {Math.round(tixProgress * 100)}%
              </Text>
            </View>
            <View style={[styles.tixProgressBg, { backgroundColor: theme.surfaceVariant }]}>
              <View style={[styles.tixProgressFill, { width: `${tixProgress * 100}%` as any }]} />
            </View>
          </View>

          {/* History */}
          <View style={[styles.tixDivider, { backgroundColor: theme.surfaceVariant }]} />
          <Text style={[styles.tixHistoryTitle, { color: theme.onSurfaceVariant }]}>Recent Activity</Text>
          {MOCK_LOYALTY.history.map((item) => (
            <View key={item.id} style={styles.tixHistoryRow}>
              <View style={{ flex: 1 }}>
                <Text style={[styles.tixHistoryDesc, { color: theme.onSurface }]}>{item.desc}</Text>
                <Text style={[styles.tixHistoryDate, { color: theme.onSurfaceVariant }]}>{item.date}</Text>
              </View>
              <Text style={[
                styles.tixHistoryPts,
                { color: item.pts > 0 ? '#16A349' : '#B3261E' },
              ]}>
                {item.pts > 0 ? '+' : ''}{item.pts}
              </Text>
            </View>
          ))}
        </View>

      </ScrollView>

      {/* NFC Sheet Overlay */}
      {isNfcOpen && (
        <Animated.View style={getOverlayStyle(nfcOverlayOpacity)}>
          <Pressable style={{ flex: 1 }} onPress={closeNfc} />
        </Animated.View>
      )}

      {/* QR Sheet Overlay */}
      {isQrOpen && (
        <Animated.View style={getOverlayStyle(qrOverlayOpacity)}>
          <Pressable style={{ flex: 1 }} onPress={closeQr} />
        </Animated.View>
      )}

      {/* NFC TOP SHEET */}
      <Animated.View
        pointerEvents={isNfcOpen ? 'auto' : 'none'}
        style={[walletStyles.topSheet, { backgroundColor: sheetBg, transform: [{ translateY: nfcTranslateY }] }]}
        {...nfcPan.panHandlers}
      >
        <View style={walletStyles.nfcActiveContainer}>
          <View style={[walletStyles.nfcScanningCircle, { backgroundColor: theme.primaryContainer }]}>
            <MaterialIcons name="contactless" size={48} color={theme.onPrimaryContainer} />
          </View>
          <Text style={[walletStyles.sheetText, { color: isDark ? '#E6E1E5' : '#1C1B1F' }]}>Ready to Scan</Text>
          <Text style={[walletStyles.sheetCaption, { color: isDark ? '#938F99' : '#79747E' }]}>Hold near the transit reader</Text>
        </View>
      </Animated.View>

      {/* QR BOTTOM SHEET */}
      <Animated.View
        pointerEvents={isQrOpen ? 'auto' : 'none'}
        style={[styles.qrSheet, { backgroundColor: sheetBg, transform: [{ translateY: qrTranslateY }] }]}
        {...qrPan.panHandlers}
      >
        <Text style={[styles.sheetTitle, { color: isDark ? '#E6E1E5' : '#1C1B1F', paddingHorizontal: 24, paddingTop: 20, marginBottom: 4 }]}>Digital Pass</Text>
        <View style={styles.qrBody}>
          <View style={styles.qrWrapper}>
            <QRCodeStyled
              data={qrValue}
              size={220}
              pieceBorderRadius={0}
              color={'#000000'}
            />
          </View>
          <Text style={[styles.qrCardNum, { color: isDark ? '#CAC4D0' : '#49454F' }]}>{MOCK_CARD.number}</Text>
          <Text style={[styles.qrCaption, { color: isDark ? '#938F99' : '#79747E' }]}>Show this code to the attendant</Text>
        </View>
      </Animated.View>
    </ThemedView>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────
const styles = {
  container: { flex: 1 },
  scrollContent: {
    paddingHorizontal: 24,
    paddingTop: 60,
    paddingBottom: 120,
  },
  headerRow: {
    width: '100%' as const,
    alignItems: 'flex-start' as const,
    marginBottom: 28,
  },

  // ── CARD ──────────────────────────────────────────────────────────────────
  card: {
    width: '100%' as const,
    aspectRatio: 1.586,
    borderRadius: 24,
    overflow: 'hidden' as const,
    elevation: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.2,
    shadowRadius: 16,
  },
  cardBgImage: {
    ...({} as any),
    position: 'absolute' as const,
    width: '130%' as const,
    height: '100%' as const,
    left: -40,
    resizeMode: 'cover' as const,
    transform: [{ rotate: '180deg' }],
  },
  cardOverlay: {
    ...({} as any),
    position: 'absolute' as const,
    top: 0, left: 0, right: 0, bottom: 0,
    backgroundColor: 'rgba(6, 20, 60, 0.68)',
  },
  cardTopRow: {
    flexDirection: 'row' as const,
    justifyContent: 'space-between' as const,
    alignItems: 'center' as const,
    paddingHorizontal: 24,
    paddingTop: 22,
  },
  cardBrand: {
    color: 'rgba(255,255,255,0.9)',
    fontSize: 14,
    fontWeight: '700' as const,
    letterSpacing: 0.8,
    textTransform: 'uppercase' as const,
  },
  cardNumber: {
    color: '#FFFFFF',
    fontSize: 17,
    fontWeight: '600' as const,
    letterSpacing: 3,
    paddingHorizontal: 24,
    marginTop: 'auto' as const,
    marginBottom: 16,
    textShadowColor: 'rgba(0,0,0,0.6)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 4,
    flex: 1,
    textAlignVertical: 'center' as const,
  },
  cardBottomRow: {
    flexDirection: 'row' as const,
    justifyContent: 'space-between' as const,
    paddingHorizontal: 24,
    paddingBottom: 20,
  },
  cardLabel: {
    color: 'rgba(255,255,255,0.55)',
    fontSize: 9,
    fontWeight: '600' as const,
    letterSpacing: 1.2,
    marginBottom: 3,
  },
  cardValue: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600' as const,
  },

  instructionHint: {
    marginTop: 16,
    marginBottom: 20,
    fontSize: 13,
    textAlign: 'center' as const,
    fontWeight: '500' as const,
    letterSpacing: 0.3,
  },

  // ── ACTION ROW ────────────────────────────────────────────────────────────
  actionRow: {
    flexDirection: 'row' as const,
    gap: 10,
    marginBottom: 20,
  },
  actionBtn: {
    flex: 1,
    flexDirection: 'column' as const,
    alignItems: 'center' as const,
    justifyContent: 'center' as const,
    paddingVertical: 14,
    borderRadius: 16,
    gap: 6,
  },
  actionBtnText: {
    fontSize: 12,
    fontWeight: '600' as const,
    letterSpacing: 0.2,
  },

  // ── BALANCE ───────────────────────────────────────────────────────────────
  sectionCard: {
    borderRadius: 20,
    padding: 20,
    marginBottom: 24,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 6,
  },
  sectionCardRow: {
    flexDirection: 'row' as const,
    justifyContent: 'space-between' as const,
    alignItems: 'center' as const,
    marginBottom: 8,
  },
  sectionLabel: { fontSize: 13, fontWeight: '500' as const },
  balanceAmount: { fontSize: 32, fontWeight: '700' as const, letterSpacing: -0.5, marginBottom: 4 },
  balanceSub: { fontSize: 12 },

  // ── TIX ──────────────────────────────────────────────────────────────────
  heading: {
    fontSize: 16,
    fontWeight: '600' as const,
    marginBottom: 12,
    marginLeft: 4,
  },
  tixCard: {
    borderRadius: 20,
    padding: 20,
    marginBottom: 24,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 6,
  },
  tixTopRow: {
    flexDirection: 'row' as const,
    alignItems: 'center' as const,
    marginBottom: 20,
  },
  tixIconBg: {
    width: 48,
    height: 48,
    borderRadius: 14,
    justifyContent: 'center' as const,
    alignItems: 'center' as const,
  },
  tixPoints: { fontSize: 24, fontWeight: '700' as const, letterSpacing: -0.3 },
  tixPtsLabel: { fontSize: 15, fontWeight: '500' as const },
  tixTier: { fontSize: 13, fontWeight: '600' as const, marginTop: 2 },
  tixBadge: {
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 999,
  },
  tixBadgeText: { fontSize: 12, fontWeight: '700' as const, color: '#A05C00' },
  tixProgressSection: { marginBottom: 16 },
  tixProgressLabelRow: {
    flexDirection: 'row' as const,
    justifyContent: 'space-between' as const,
    marginBottom: 8,
  },
  tixProgressLabel: { fontSize: 12 },
  tixProgressPct: { fontSize: 12, fontWeight: '700' as const },
  tixProgressBg: {
    height: 8,
    borderRadius: 4,
    overflow: 'hidden' as const,
  },
  tixProgressFill: {
    height: '100%' as const,
    borderRadius: 4,
    backgroundColor: '#F59E0B',
  },
  tixDivider: { height: 1, marginVertical: 16 },
  tixHistoryTitle: { fontSize: 12, fontWeight: '600' as const, letterSpacing: 0.6, textTransform: 'uppercase' as const, marginBottom: 12 },
  tixHistoryRow: {
    flexDirection: 'row' as const,
    alignItems: 'center' as const,
    marginBottom: 14,
  },
  tixHistoryDesc: { fontSize: 14, fontWeight: '500' as const },
  tixHistoryDate: { fontSize: 12, marginTop: 2 },
  tixHistoryPts: { fontSize: 15, fontWeight: '700' as const },

  // ── SHEETS ────────────────────────────────────────────────────────────────
  sheetTitle: {
    fontSize: 20,
    fontWeight: '700' as const,
  },
  qrSheet: {
    position: 'absolute' as const,
    bottom: 0,
    left: 0,
    right: 0,
    height: QR_SHEET_HEIGHT,
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    zIndex: 30,
    elevation: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -6 },
    shadowOpacity: 0.2,
    shadowRadius: 20,
    paddingBottom: 83, // navbar height keeps content above tab bar
  },
  qrBody: {
    flex: 1,
    alignItems: 'center' as const,
    justifyContent: 'center' as const,
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
    fontWeight: '600' as const,
    letterSpacing: 4,
    marginBottom: 8,
  },
  qrCaption: {
    fontSize: 13,
    textAlign: 'center' as const,
  },
};
