import { useEffect, useRef, useState } from 'react';
import {
  Animated,
  PanResponder,
  Pressable,
  View,
  BackHandler,
  Image,
  Text,
  useColorScheme,
  type GestureResponderEvent,
  type PanResponderGestureState,
} from 'react-native';
import MaterialIcons from '@expo/vector-icons/MaterialIcons';
import { HCESession, NFCTagType4NDEFContentType, NFCTagType4 } from 'react-native-hce';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Colors } from '@/constants/theme';
import {
  getOverlayStyle,
  getTopSheetStyle,
  SHEET_HEIGHT,
  walletStyles,
} from '../../components/wallet-styles';

export default function ExploreScreen() {
  const [isOpen, setIsOpen] = useState(false);
  const translateY = useRef(new Animated.Value(-SHEET_HEIGHT)).current;
  const overlayOpacity = useRef(new Animated.Value(0)).current;

  // NFC Logic
  const startHceBroadcast = async () => {
    try {
      const session = await HCESession.getInstance();
      const tag = new NFCTagType4({ type: NFCTagType4NDEFContentType.Text, content: 'CGMplus-SecurePass', writable: false });
      await session.setApplication(tag);
      await session.setEnabled(true);
    } catch (e) {
      // Ignored
    }
  };

  const stopHceBroadcast = async () => {
    try {
      const session = await HCESession.getInstance();
      await session.setEnabled(false);
    } catch (e) {
      // Ignored
    }
  };

  useEffect(() => {
    return () => {
      stopHceBroadcast();
    };
  }, []);

  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];

  const borderColor = theme.outline || '#d9dde3';
  const cardBg = theme.surface || '#f7fafc';

  const openSheet = () => {
    setIsOpen(true);
    startHceBroadcast();
    Animated.parallel([
      Animated.spring(translateY, {
        toValue: 0,
        useNativeDriver: true,
        damping: 18,
        stiffness: 180,
        mass: 0.8,
      }),
      Animated.timing(overlayOpacity, {
        toValue: 1,
        duration: 180,
        useNativeDriver: true,
      }),
    ]).start();
  };

  const closeSheet = () => {
    stopHceBroadcast();
    Animated.parallel([
      Animated.timing(translateY, {
        toValue: -SHEET_HEIGHT,
        duration: 180,
        useNativeDriver: true,
      }),
      Animated.timing(overlayOpacity, {
        toValue: 0,
        duration: 160,
        useNativeDriver: true,
      }),
    ]).start(() => setIsOpen(false));
  };

  useEffect(() => {
    const onBackPress = () => {
      if (isOpen) {
        closeSheet();
        return true;
      }
      return false;
    };
    const backSubscription = BackHandler.addEventListener('hardwareBackPress', onBackPress);
    return () => backSubscription.remove();
  }, [isOpen]);

  const releaseSheet = (_event: GestureResponderEvent, gesture: PanResponderGestureState) => {
    if (gesture.dy < -40 || gesture.vy < -0.8) {
      closeSheet();
      return;
    }

    Animated.spring(translateY, {
      toValue: 0,
      useNativeDriver: true,
      damping: 18,
      stiffness: 180,
      mass: 0.8,
    }).start();
  };

  const panResponder = useRef(
    PanResponder.create({
      onMoveShouldSetPanResponder: (_event, gesture) => Math.abs(gesture.dy) > 8,
      onPanResponderMove: (_event, gesture) => {
        const nextY = Math.min(0, gesture.dy);
        translateY.setValue(nextY);
      },
      onPanResponderRelease: releaseSheet,
      onPanResponderTerminate: releaseSheet,
    })
  ).current;

  return (
    <ThemedView style={[walletStyles.container, { backgroundColor: theme.background }]}>
      <View style={walletStyles.headerRow}>
        <ThemedText type="title">Digital Pass</ThemedText>
      </View>

      {/* Main card acts as the trigger instead of an NFC button */}
      <Pressable
        onPress={openSheet}
        style={({ pressed }) => [
          walletStyles.mainCardTrigger,
          { 
            backgroundColor: theme.primaryContainer, 
            opacity: pressed ? 0.9 : 1,
            shadowColor: '#000'
          },
        ]}>
        <Image
          source={require('@/assets/graphics/card-graphic.jpg')}
          style={walletStyles.triggerGraphic}
        />
        <View style={walletStyles.cardContentOverlay}>
          <View style={[walletStyles.chip, { borderColor: 'rgba(255,255,255,0.4)', backgroundColor: 'rgba(255,255,255,0.2)' }]} />
          <Text style={walletStyles.barelyVisibleNumbers}>
            1234  5678  9012  3456
          </Text>
        </View>
      </Pressable>

      <Text style={[walletStyles.instructionHint, { color: theme.onSurfaceVariant }]}>
         <MaterialIcons name="contactless" size={16} color={theme.onSurfaceVariant} style={{marginRight: 4}} /> Tap card to use pass
      </Text>

      {isOpen ? (
        <Animated.View style={getOverlayStyle(overlayOpacity)}>
          <Pressable style={walletStyles.overlayPressTarget} onPress={closeSheet} />
        </Animated.View>
      ) : null}

      <Animated.View
        pointerEvents={isOpen ? 'auto' : 'none'}
        style={getTopSheetStyle(borderColor, theme.surface, translateY)}
        {...panResponder.panHandlers}>
        <View style={walletStyles.handleBarWrap}>
          <View style={[walletStyles.handleBar, { backgroundColor: theme.outline }]} />
        </View>

        <View style={walletStyles.nfcActiveContainer}>
           <View style={[walletStyles.nfcScanningCircle, { backgroundColor: theme.primaryContainer }]}>
               <MaterialIcons name="contactless" size={54} color={theme.onPrimaryContainer} />
           </View>
           <Text style={[walletStyles.sheetText, { color: theme.onSurface }]}>Ready to Scan</Text>
           <Text style={[walletStyles.sheetCaption, { color: theme.onSurfaceVariant }]}>Hold near the transit reader</Text>
        </View>
      </Animated.View>
    </ThemedView>
  );
}
