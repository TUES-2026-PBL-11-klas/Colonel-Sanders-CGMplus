import { Animated, Dimensions, StyleSheet } from 'react-native';

const SCREEN_WIDTH = Dimensions.get('window').width;
const SHEET_TOP_PADDING = 20;
const SHEET_BOTTOM_PADDING = 40;

export const SHEET_HEIGHT = 460;

export const walletStyles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 60,
  },
  headerRow: {
    width: '100%',
    alignItems: 'flex-start',
    marginBottom: 32,
  },
  mainCardTrigger: {
    width: '100%',
    aspectRatio: 1.586,
    borderRadius: 28,
    overflow: 'hidden',
    position: 'relative',
    elevation: 8,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
  },
  triggerGraphic: {
    width: '120%',
    height: '100%',
    resizeMode: 'cover',
    transform: [{ rotate: '180deg' }],
    left: -40,
  },
  cardContentOverlay: {
    ...StyleSheet.absoluteFillObject,
    padding: 24,
    justifyContent: 'space-between',
    backgroundColor: 'rgba(0,0,0,0.15)',
  },
  chip: {
    width: 44,
    height: 32,
    borderRadius: 8,
    borderWidth: 1,
    marginTop: 'auto',
    marginBottom: 16,
  },
  barelyVisibleNumbers: {
    fontSize: 20,
    fontWeight: '600',
    letterSpacing: 4,
    color: '#FFF',
    opacity: 0.65,
    textShadowColor: 'rgba(0,0,0,0.7)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 3,
    alignSelf: 'flex-start',
  },
  instructionHint: {
    marginTop: 32,
    fontSize: 14,
    textAlign: 'center',
    fontWeight: '500',
    letterSpacing: 0.5,
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    zIndex: 20,
    backgroundColor: 'rgba(0,0,0,0.4)',
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
    borderBottomLeftRadius: 16,
    borderBottomRightRadius: 16,
    paddingTop: SHEET_TOP_PADDING,
    paddingBottom: SHEET_BOTTOM_PADDING,
    zIndex: 30,
    elevation: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.15,
    shadowRadius: 16,
  },
  handleBarWrap: {
    alignItems: 'center',
    marginBottom: 40,
    paddingTop: 12,
  },
  handleBar: {
    width: 32,
    height: 3,
    borderRadius: 1,
    opacity: 0.2,
  },
  nfcActiveContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingBottom: 20,
  },
  nfcScanningCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
    elevation: 2,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
  },
  sheetText: {
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 8,
    letterSpacing: -0.2,
  },
  sheetCaption: {
    fontSize: 14,
    opacity: 0.7,
  },
  qrContainer: {
    width: 240,
    aspectRatio: 1,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 8,
    elevation: 4,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
  },
  bottomSheet: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: SHEET_HEIGHT,
    borderTopLeftRadius: 32,
    borderTopRightRadius: 32,
    paddingTop: SHEET_TOP_PADDING,
    paddingBottom: SHEET_BOTTOM_PADDING,
    zIndex: 30,
    elevation: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -6 },
    shadowOpacity: 0.15,
    shadowRadius: 16,
  },
});

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
    backgroundColor: cardBg,
    transform: [{ translateY }],
  },
];

export const getBottomSheetStyle = (
  borderColor: string,
  cardBg: string,
  translateY: Animated.Value
) => [
  walletStyles.bottomSheet,
  {
    backgroundColor: cardBg,
    transform: [{ translateY }],
  },
];
