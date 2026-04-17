import React from 'react';
import Svg, { G, Path } from 'react-native-svg';

type TabIconProps = {
  color: string;
  size?: number;
};

export function ProfileIcon({ color, size = 28 }: TabIconProps) {
  return (
    <Svg
      width={size}
      height={size}
      viewBox="0 0 32.724987 37.04422"
    >
      <G transform="translate(-125.67924,-130.46879)">
        <Path
          d="m 142.04148,131.41885 a 9.0233431,9.0233431 0 0 0 -9.02322,9.02322 9.0233431,9.0233431 0 0 0 9.02322,9.02374 9.0233431,9.0233431 0 0 0 9.02374,-9.02374 9.0233431,9.0233431 0 0 0 -9.02374,-9.02322 z m 0,20.18275 c -6.04139,1.1e-4 -11.45133,3.07087 -14.6234,7.8295 -2.34132,3.51235 0.70089,7.13186 4.95629,7.13186 h 19.33474 c 4.25539,0 7.29761,-3.6195 4.95629,-7.13186 -3.17217,-4.75877 -8.58234,-7.82957 -14.62392,-7.8295 z"
          fill="none"
          stroke={color}
          strokeWidth={1.9001}
          strokeOpacity={1}
        />
      </G>
    </Svg>
  );
}
