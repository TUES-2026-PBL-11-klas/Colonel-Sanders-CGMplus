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

import { getOverlayStyle, SHEET_HEIGHT, walletStyles } from '@/components/wallet-styles';

import { useWalletData } from '@/hooks/useWalletData';
import { API } from '@/utils/api';
import { Alert } from 'react-native';

const QR_SHEET_HEIGHT = 540;

// ─── Helpers ──────────────────────────────────────────────────────────────────
const formatCardNumber = (id?: string) => {
  if (!id) return '—';
  // Use first 16 characters for a clean 4x4 card number format, uppercase
  const clean = id.replace(/[^0-9a-fA-F]/g, '').toUpperCase();
  const truncated = clean.slice(0, 16);
  return truncated.match(/.{1,4}/g)?.join(' ') || truncated;
};

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

  const { profile, card, offers, redemptions, refresh, loading } = useWalletData();

  // Keep nfcPayload in a ref so HCE always uses the latest value
  const nfcPayloadRef = useRef<string>('CGMplus-SecurePass');
  const nfcPayload = card?.nfc_id || 'CGMplus-SecurePass';
  nfcPayloadRef.current = nfcPayload;
  const qrValue = `CGMplus | ${card?.nfc_id || ''}`;

  // Sheet backgrounds: lighter undertone so they float above page bg
  const sheetBg = isDark ? '#26252B' : '#F2F5F9';

  // Progress for Tix
  const loyaltyPoints = profile?.balance ?? 0;
  const loyaltyTier = profile?.rank || '—';
  const NEXT_TIER_AT = 500; // Backend doesn't expose this yet; update when it does
  const tixProgress = Math.min(loyaltyPoints / NEXT_TIER_AT, 1);

  const handleRedeem = async (offerId: number, price: number) => {
    if (loyaltyPoints < price) {
      Alert.alert('Недостатъчно Tix', 'Нямаш достатъчно Tix за да валидирате на тази оферта.');
      return;
    }
    try {
      const res = await API.redeemOffer(offerId);
      if (res.status === 402) {
        Alert.alert('Нужно е заплащане', 'Нямаш достатъчно Tix за да валидирате на тази оферта.');
      } else if (res.ok) {
        Alert.alert('Успех', 'Офертата е валидирана успешно!');
        refresh();
      } else {
        Alert.alert('Грешка', 'Не успяхме да валидираме офертата.');
      }
    } catch (e) {
      Alert.alert('Грешка', 'Възникна неочаквана грешка.');
    }
  };

  // ─── HCE ───────────────────────────────────────────────────────────────────
  const startHceBroadcast = async () => {
    try {
      const payload = nfcPayloadRef.current;
      const session = await HCESession.getInstance();
      const tag = new NFCTagType4({
        type: NFCTagType4NDEFContentType.Text,
        content: payload,
        writable: false,
      });
      await session.setApplication(tag);
      await session.setEnabled(true);
      console.log('[HCE] Broadcasting payload:', payload);
    } catch (e) {
      console.error('[HCE] Failed to start broadcast:', e);
    }
  };

  const stopHceBroadcast = async () => {
    try {
      const session = await HCESession.getInstance();
      await session.setEnabled(false);
      console.log('[HCE] Stopped broadcast');
    } catch (e) {
      console.error('[HCE] Failed to stop broadcast:', e);
    }
  };

  // Re-apply HCE tag when card data arrives while sheet is already open
  useEffect(() => {
    if (isNfcOpen && card?.nfc_id) {
      startHceBroadcast();
    }
  }, [card?.nfc_id, isNfcOpen]);

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
          <ThemedText type="title">Портфейл</ThemedText>
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
            <Text style={styles.cardBrand}>ЦГМ+ лоялност</Text>
            <MaterialIcons name="contactless" size={28} color="rgba(255,255,255,0.85)" />
          </View>

          {/* Card Number – crisp & bright */}
          <Text style={styles.cardNumber}>{formatCardNumber(card?.nfc_id)}</Text>

          {/* Card Bottom Row */}
          <View style={styles.cardBottomRow}>
            <View>
              <Text style={styles.cardLabel}>СОБСТВЕНИК НА КАРТА</Text>
              <Text style={styles.cardValue}>{loading ? '—' : (card ? 'ЦГМ+ потребител' : 'Няма карта')}</Text>
            </View>
            <View style={{ alignItems: 'flex-end' }}>
              <Text style={styles.cardLabel}>ИЗТИЧА</Text>
              <Text style={styles.cardValue}>{card?.expiry_date ? new Date(card.expiry_date).toLocaleDateString() : '—'}</Text>
            </View>
          </View>
        </Pressable>

        <Text style={[styles.instructionHint, { color: theme.onSurfaceVariant }]}>
          <MaterialIcons name="contactless" size={16} color={theme.onSurfaceVariant} />
          {' '}Натисни картата за да използваш NFC
        </Text>

        {/* ── ACTION ROW ─────────────────────────────────────────────────── */}
        <View style={styles.actionRow}>
          <Pressable
            onPress={openQr}
            style={({ pressed }) => [styles.actionBtn, { backgroundColor: theme.primaryContainer, opacity: pressed ? 0.7 : 1 }]}
          >
            <MaterialIcons name="qr-code" size={22} color={theme.onPrimaryContainer} />
            <Text style={[styles.actionBtnText, { color: theme.onPrimaryContainer }]}>QR код</Text>
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
        <Text style={[styles.heading, { color: theme.onSurfaceVariant }]}>Tix Лоялни Точки</Text>
        <View style={[styles.tixCard, { backgroundColor: theme.surface }]}>
          {/* Top */}
          <View style={styles.tixTopRow}>
            <View style={[styles.tixIconBg, { backgroundColor: '#FFF3CD' }]}>
              <Ionicons name="star" size={22} color="#A05C00" />
            </View>
            <View style={{ flex: 1, marginLeft: 14 }}>
              <Text style={[styles.tixPoints, { color: theme.onSurface }]}>
                {loyaltyPoints.toLocaleString()} <Text style={[styles.tixPtsLabel, { color: theme.onSurfaceVariant }]}>Tix</Text>
              </Text>
              <Text style={[styles.tixTier, { color: '#A05C00' }]}>{loyaltyTier} член</Text>
            </View>
            <View style={[styles.tixBadge, { backgroundColor: '#FFF3CD' }]}>
              <Text style={styles.tixBadgeText}>{loyaltyTier}</Text>
            </View>
          </View>

          {/* Progress to next tier */}
          <View style={styles.tixProgressSection}>
            <View style={styles.tixProgressLabelRow}>
              <Text style={[styles.tixProgressLabel, { color: theme.onSurfaceVariant }]}>
                {loyaltyPoints} / {NEXT_TIER_AT} към следващия ниво
              </Text>
              <Text style={[styles.tixProgressPct, { color: '#A05C00' }]}>
                {Math.round(tixProgress * 100)}%
              </Text>
            </View>
            <View style={[styles.tixProgressBg, { backgroundColor: theme.surfaceVariant }]}>
              <View style={[styles.tixProgressFill, { width: `${tixProgress * 100}%` as any }]} />
            </View>
          </View>

          {/* Active Offers */}
          {offers.length > 0 && (
            <>
              <View style={[styles.tixDivider, { backgroundColor: theme.surfaceVariant }]} />
              <Text style={[styles.tixHistoryTitle, { color: theme.onSurfaceVariant }]}>Активни оферти</Text>
              {offers.map((offer) => (
                <View key={offer.id} style={styles.tixHistoryRow}>
                  <View style={{ flex: 1 }}>
                    <Text style={[styles.tixHistoryDesc, { color: theme.onSurface }]}>{offer.name}</Text>
                    {offer.description && <Text style={[styles.tixHistoryDate, { color: theme.onSurfaceVariant }]}>{offer.description}</Text>}
                  </View>
                  <Pressable
                    onPress={() => handleRedeem(offer.id, offer.price)}
                    style={{ backgroundColor: theme.primaryContainer, paddingHorizontal: 12, paddingVertical: 6, borderRadius: 12 }}
                  >
                    <Text style={{ color: theme.onPrimaryContainer, fontWeight: '600', fontSize: 13 }}>-{offer.price} Tix</Text>
                  </Pressable>
                </View>
              ))}
            </>
          )}

          {/* History */}
          <View style={[styles.tixDivider, { backgroundColor: theme.surfaceVariant }]} />
          <Text style={[styles.tixHistoryTitle, { color: theme.onSurfaceVariant }]}>Последна активност</Text>
          {redemptions.length > 0 ? (
            redemptions.map((item) => (
              <View key={item.id} style={styles.tixHistoryRow}>
                <View style={{ flex: 1 }}>
                  <Text style={[styles.tixHistoryDesc, { color: theme.onSurface }]}>Оферта #{item.offer_id}</Text>
                  <Text style={[styles.tixHistoryDate, { color: theme.onSurfaceVariant }]}>ID: {item.id.slice(0, 8)}</Text>
                </View>
                <Text style={[
                  styles.tixHistoryPts,
                  { color: '#B3261E' },
                ]}>
                  -{item.points_cost}
                </Text>
              </View>
            ))
          ) : (
            <Text style={[styles.tixHistoryDate, { color: theme.onSurfaceVariant, marginTop: 4 }]}>Все още няма валидирания.</Text>
          )}
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
          <Text style={[walletStyles.sheetText, { color: isDark ? '#E6E1E5' : '#1C1B1F' }]}>Готов за сканиране</Text>
          <Text style={[walletStyles.sheetCaption, { color: isDark ? '#938F99' : '#79747E' }]}>Задръж близо до четец</Text>
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
          <Text style={[styles.qrCardNum, { color: isDark ? '#CAC4D0' : '#49454F' }]}>{formatCardNumber(card?.nfc_id)}</Text>
          <Text style={[styles.qrCaption, { color: isDark ? '#938F99' : '#79747E' }]}>Покажи този код на кондуктора</Text>
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
