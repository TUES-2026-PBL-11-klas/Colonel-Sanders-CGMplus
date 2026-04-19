import { Platform } from 'react-native';

const PRIMARY_COLOR = '#0B57D0'; // Google Material Blue
const PRIMARY_DARK = '#A8C7FA'; 
const MINT = '#4FD1C5';
const NAVY = '#1A2B44';

export const Colors = {
  light: {
    // Legacy mapping (to not break everything immediately)
    text: '#1C1B1F',
    background: '#F4F7F9', // M3 Surface background for pages
    tint: PRIMARY_COLOR,
    icon: '#49454F',
    tabIconDefault: '#49454F',
    tabIconSelected: PRIMARY_COLOR,

    // M3 Tokens
    surface: '#FFFFFF', // Elevated Cards base
    surfaceVariant: '#E7E0EC',
    onSurface: '#1C1B1F',
    onSurfaceVariant: '#49454F',
    primary: PRIMARY_COLOR,
    onPrimary: '#FFFFFF',
    primaryContainer: '#D3E3FD',
    onPrimaryContainer: '#041E49',
    outline: '#79747E',
    error: '#B3261E',
    mint: MINT,
    navy: NAVY,
  },
  dark: {
    // Legacy mapping
    text: '#E6E1E5',
    background: '#1C1B1F', // Dark M3 Background
    tint: PRIMARY_DARK,
    icon: '#CAC4D0',
    tabIconDefault: '#CAC4D0',
    tabIconSelected: PRIMARY_DARK,

    // M3 Tokens
    surface: '#2B2A2F',
    surfaceVariant: '#49454F',
    onSurface: '#E6E1E5',
    onSurfaceVariant: '#CAC4D0',
    primary: PRIMARY_DARK,
    onPrimary: '#002F6C', // Dark on primary
    primaryContainer: '#004A77',
    onPrimaryContainer: '#C2E7FF',
    outline: '#938F99',
    error: '#F2B8B5',
    mint: MINT,
    navy: NAVY,
  },
};

export const Fonts = Platform.select({
  ios: {
    sans: 'system-ui',
    serif: 'ui-serif',
    rounded: 'ui-rounded',
    mono: 'ui-monospace',
  },
  default: {
    sans: 'normal',
    serif: 'serif',
    rounded: 'normal',
    mono: 'monospace',
  },
  web: {
    sans: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    serif: "Georgia, 'Times New Roman', serif",
    rounded: "'SF Pro Rounded', 'Hiragino Maru Gothic ProN', Meiryo, 'MS PGothic', sans-serif",
    mono: "SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
  },
});
