import { Animated, Dimensions, StyleSheet } from 'react-native';

const SCREEN_WIDTH = Dimensions.get('window').width;
const SCREEN_SIDE_PADDING = 16;
const SHEET_SIDE_PADDING = 18;
const SHEET_TOP_PADDING = 20;
const SHEET_BOTTOM_PADDING = 12;
const CARD_MAX_WIDTH = 440;
const NFC_LOGO_SIZE = 34;
const PANEL_GAP = 20;
const DEBIT_CARD_ASPECT_RATIO = 1.586 / 1;
const CARD_WIDTH = Math.min(
  CARD_MAX_WIDTH,
  SCREEN_WIDTH - SCREEN_SIDE_PADDING * 2 - SHEET_SIDE_PADDING * 2
);
const CARD_HEIGHT = CARD_WIDTH / DEBIT_CARD_ASPECT_RATIO;

export const SHEET_HEIGHT = Math.ceil(
  SHEET_TOP_PADDING + NFC_LOGO_SIZE + PANEL_GAP + CARD_HEIGHT + SHEET_BOTTOM_PADDING + SHEET_SIDE_PADDING + 8
);

export const walletStyles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 16,
    paddingTop: 16,
    backgroundColor: 'transparent',
  },
  headerRow: {
    width: '100%',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  nfcTrigger: {
    width: '100%',
    borderRadius: 18,
    borderWidth: 1,
    paddingVertical: 18,
    alignItems: 'center',
    justifyContent: 'center',
  },
  nfcLogoWrap: {
    width: '100%',
    height: NFC_LOGO_SIZE,
    position: 'relative',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: PANEL_GAP,
  },
  nfcGlowPulse: {
    position: 'absolute',
    width: 45,
    height: 45,
    borderRadius: 31,
    backgroundColor: '#3BA7FF',
  },
  nfcGlowCore: {
    position: 'absolute',
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(59, 167, 255, 0.24)',
  },
  nfcBar: {
    width: '100%',
    maxWidth: 440,
    alignSelf: 'center',
    aspectRatio: DEBIT_CARD_ASPECT_RATIO,
    borderWidth: 1,
    borderRadius: 24,
    paddingHorizontal: 18,
    paddingVertical: 18,
    justifyContent: 'space-between',
    overflow: 'hidden',
  },
  cardTopRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  membershipPill: {
    borderRadius: 999,
    borderWidth: 1,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  chip: {
    width: 38,
    height: 28,
    borderRadius: 7,
    borderWidth: 1,
  },
  cardNumber: {
    letterSpacing: 2,
    fontSize: 20,
  },
  cardBottomRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
  },
  labelText: {
    fontSize: 11,
    opacity: 0.72,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  valueText: {
    marginTop: 2,
    fontSize: 15,
  },
  cardBareInner: {
    alignItems: 'flex-end',
    justifyContent: 'flex-end',
    overflow: 'hidden',
  },
  cardGraphic: {
    position: 'absolute',
    left: -10,
    top: 0,
    bottom: 0,
    width: '75%',
    height: undefined,
    aspectRatio: 1,
    resizeMode: 'cover',
    transform: [{ rotate: '180deg' }],
    opacity: 0.9,
  },
  cardNumberBare: {
    letterSpacing: 2,
    fontSize: 12,
    color: '#1d5448',
    opacity: 1,
    textAlign: 'right',
    textShadowColor: 'rgba(255, 255, 255, 1)',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 4,
    transform: [{ translateY: 10 }],
  },
  nfcHint: {
    marginTop: 10,
    opacity: 0.72,
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    zIndex: 20,
    backgroundColor: 'rgba(0,0,0,0.28)',
  },
  overlayPressTarget: {
    flex: 1,
  },
  topSheet: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: SHEET_HEIGHT,
    borderBottomLeftRadius: 24,
    borderBottomRightRadius: 24,
    borderWidth: 1,
    borderTopWidth: 0,
    paddingHorizontal: 18,
    paddingTop: SHEET_TOP_PADDING,
    paddingBottom: SHEET_BOTTOM_PADDING,
    gap: 0,
    overflow: 'hidden',
    zIndex: 30,
  },
  sheetText: {
    opacity: 0.78,
  },
});

export const getNfcBarStyle = (
  pressed: boolean,
  borderColor: string,
  cardBg: string,
  accentColor: string
) => [
  walletStyles.nfcBar,
  {
    borderColor,
    backgroundColor: accentColor || cardBg,
    opacity: pressed ? 0.86 : 1,
  },
];

export const getOverlayStyle = (overlayOpacity: Animated.Value) => [
  walletStyles.overlay,
  { opacity: overlayOpacity },
];

export const getTopSheetStyle = (
  borderColor: string,
  cardBg: string,
  translateY: Animated.Value
) => [
  walletStyles.topSheet,
  {
    borderColor,
    backgroundColor: cardBg,
    transform: [{ translateY }],
  },
];
