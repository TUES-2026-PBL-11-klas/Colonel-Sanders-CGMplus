import { useEffect, useRef, useState } from 'react';
import {
  Animated,
  Image,
  PanResponder,
  Platform,
  Pressable,
  View,
  type GestureResponderEvent,
  type PanResponderGestureState,
} from 'react-native';
import MaterialIcons from '@expo/vector-icons/MaterialIcons';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { useThemeColor } from '@/hooks/use-theme-color';
import { membershipCardMock } from '@/constants/membership-card-mock';

// Only import HCE on native platforms
let HCESession: any;
let NFCTagType4: any;
let NFCTagType4NDEFContentType: any;

if (Platform.OS !== 'web') {
  const hceModule = require('react-native-hce');
  HCESession = hceModule.HCESession;
  NFCTagType4 = hceModule.NFCTagType4;
  NFCTagType4NDEFContentType = hceModule.NFCTagType4NDEFContentType;
}
import {
  getNfcBarStyle,
  getOverlayStyle,
  getTopSheetStyle,
  SHEET_HEIGHT,
  walletStyles,
} from '../../components/wallet-styles';

export default function ExploreScreen() {
  const [isOpen, setIsOpen] = useState(false);
  const translateY = useRef(new Animated.Value(-SHEET_HEIGHT)).current;
  const overlayOpacity = useRef(new Animated.Value(0)).current;
  const glowPulse = useRef(new Animated.Value(0)).current;

  const startHceBroadcast = async () => {
    try {
      const tag = new NFCTagType4({
        type: NFCTagType4NDEFContentType.Text,
        content: `CGMplus|${membershipCardMock.cardNumber}|${membershipCardMock.holderName}`,
        writable: false
      });
      const session = await HCESession.getInstance();
      await session.setApplication(tag);
      await session.setEnabled(true);
    } catch (e) {
      console.warn('Failed to start HCE broadcasting', e);
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

  const borderColor = useThemeColor({ light: '#d9dde3', dark: '#343a40' }, 'icon');
  const cardBg = useThemeColor({ light: '#f7fafc', dark: '#1f2428' }, 'background');

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

  useEffect(() => {
    if (!isOpen) {
      glowPulse.stopAnimation();
      glowPulse.setValue(0);
      return;
    }

    const glowLoop = Animated.loop(
      Animated.sequence([
        Animated.timing(glowPulse, {
          toValue: 1,
          duration: 900,
          useNativeDriver: true,
        }),
        Animated.timing(glowPulse, {
          toValue: 0,
          duration: 900,
          useNativeDriver: true,
        }),
      ])
    );

    glowLoop.start();
    return () => glowLoop.stop();
  }, [isOpen, glowPulse]);

  const glowScale = glowPulse.interpolate({
    inputRange: [0, 1],
    outputRange: [1, 1.52],
  });

  const glowOpacity = glowPulse.interpolate({
    inputRange: [0, 1],
    outputRange: [0.34, 0.08],
  });

  return (
    <ThemedView style={walletStyles.container}>
      <View style={walletStyles.headerRow}>
        <ThemedText type="title">Wallet</ThemedText>
      </View>

      <Pressable
        onPress={openSheet}
        style={({ pressed }) => [
          walletStyles.nfcTrigger,
          { borderColor, backgroundColor: cardBg, opacity: pressed ? 0.85 : 1 },
        ]}>
        <MaterialIcons name="nfc" size={44} color={borderColor} />
      </Pressable>

      {isOpen ? (
        <Animated.View style={getOverlayStyle(overlayOpacity)}>
          <Pressable style={walletStyles.overlayPressTarget} onPress={closeSheet} />
        </Animated.View>
      ) : null}

      <Animated.View
        pointerEvents={isOpen ? 'auto' : 'none'}
        style={[
          getTopSheetStyle(borderColor, cardBg, translateY),
          !isOpen && { opacity: 0 }
        ]}
        {...panResponder.panHandlers}>
        <View style={walletStyles.nfcLogoWrap}>
          <Animated.View
            style={[
              walletStyles.nfcGlowPulse,
              { opacity: glowOpacity, transform: [{ scale: glowScale }] },
            ]}
          />
          <View style={walletStyles.nfcGlowCore} />
          <MaterialIcons name="nfc" size={34} color="#2A8CFF" />
        </View>

        <View style={[getNfcBarStyle(false, borderColor, cardBg, '#ffffff'), walletStyles.cardBareInner]}>
          <Image
            source={require('@/assets/graphics/card-graphic.jpg')}
            style={walletStyles.cardGraphic}
          />
          <ThemedText type="subtitle" style={walletStyles.cardNumberBare}>
            {membershipCardMock.cardNumber}
          </ThemedText>
        </View>
      </Animated.View>
    </ThemedView>
  );
}
