import { Pressable } from 'react-native';
import * as Haptics from 'expo-haptics';

export function HapticTab(props: any) {
  return (
    <Pressable
      {...props}
      onPress={(e) => {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        props.onPress?.(e);
      }}
    />
  );
}
