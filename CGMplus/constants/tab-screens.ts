import { StyleSheet } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

export const tabScreenStyles = StyleSheet.create({
  container: {
    flex: 1,
    flexDirection: 'column',
    alignItems: 'center',
    padding: 16,
    justifyContent: 'center',
    backgroundColor: 'transparent',
  },
});

export const useTabScreenStyles = () => {
  const insets = useSafeAreaInsets();
  return {
    containerWithInsets: {
      ...tabScreenStyles.container,
      paddingTop: Math.max(insets.top, 16),
      paddingLeft: Math.max(insets.left, 16),
      paddingRight: Math.max(insets.right, 16),
      paddingBottom: 16,
    },
  };
};
