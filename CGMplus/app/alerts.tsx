import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, useColorScheme } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useGtfsData } from '@/hooks/use-gtfs-data';
import { Colors } from '@/constants/theme';
import Animated, { FadeInDown, FadeInUp } from 'react-native-reanimated';

interface GtfsAlert {
  id: string;
  start_time: number;
  routes: string[];
  description: string;
}

interface TextSegment {
  text: string;
  bold?: boolean;
  isNewLine?: boolean;
}

// Decode HTML entities
const decodeHtmlEntities = (text: string): string => {
  const entityMap: Record<string, string> = {
    '&amp;': '&',
    '&lt;': '<',
    '&gt;': '>',
    '&quot;': '"',
    '&#39;': "'",
    '&nbsp;': ' ',
    '&iexcl;': '¡',
    '&iquest;': '¿',
    '&copy;': '©',
    '&reg;': '®',
    '&trade;': '™',
    '&deg;': '°',
    '&ndash;': '–',
    '&mdash;': '—',
    '&lsquo;': "'",
    '&rsquo;': "'",
    '&ldquo;': '"',
    '&rdquo;': '"',
    '&bull;': '•',
    '&hellip;': '…',
  };

  let decoded = text.replace(/&[a-zA-Z0-9]+;/g, (match) => entityMap[match] || match);
  decoded = decoded.replace(/&#(\d+);/g, (_match, code) => String.fromCharCode(parseInt(code, 10)));
  decoded = decoded.replace(/&#x([0-9a-fA-F]+);/g, (_match, code) => String.fromCharCode(parseInt(code, 16)));

  return decoded;
};

// Parse HTML and extract text segments with styling information
const parseHtmlDescription = (html: string): TextSegment[] => {
  const segments: TextSegment[] = [];
  let currentText = '';
  let isBold = false;
  let i = 0;

const flushText = () => {
  if (currentText) {
    let decoded = decodeHtmlEntities(currentText);
    decoded = decoded.replace(/\s+/g, ' ');
    if (decoded.trim()) {
      segments.push({ text: decoded, bold: isBold });
    }
    currentText = '';
  }
};

  while (i < html.length) {
    if (html[i] === '<') {
      const endTag = html.indexOf('>', i);
      if (endTag !== -1) {
        const tag = html.substring(i + 1, endTag).toLowerCase();

        if (tag === 'p' || tag === 'br' || tag === 'br/') {
          flushText();
          if (segments.length > 0 && !segments[segments.length - 1].isNewLine) {
            segments.push({ text: '', isNewLine: true });
          }
          i = endTag + 1;
          continue;
        }

        // Handle opening tags
        if (tag === 'strong' || tag === 'b') {
          flushText();
          isBold = true;
          i = endTag + 1;
          continue;
        }

        // Handle closing tags
        if (tag === '/strong' || tag === '/b') {
          flushText();
          isBold = false;
          i = endTag + 1;
          continue;
        }

        // Handle span and other tags we want to preserve content from
        if (tag.startsWith('span') || tag.startsWith('/span') || tag.startsWith('/p')) {
          i = endTag + 1;
          continue;
        }

        i = endTag + 1;
        continue;
      }
    }

    currentText += html[i];
    i++;
  }

  flushText();

  return segments;
};

const formatDescription = (text: string): TextSegment[][] => {
  const segments = parseHtmlDescription(text);
  const lines: TextSegment[][] = [[]];

  segments.forEach((segment) => {
    if (segment.isNewLine) {
      if (lines[lines.length - 1].length > 0) {
        lines.push([]);
      }
    } else {
      lines[lines.length - 1].push(segment);
    }
  });

  return lines.filter((line) => line.length > 0);
};

export default function AlertsScreen() {
  const [alerts, setAlerts] = useState<GtfsAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];
  const gtfsData = useGtfsData();

  useEffect(() => {
    gtfsData.init();

    const unsubscribe = gtfsData.subscribe((type, data) => {
      if (type === 'alerts') {
        setAlerts(data);
        setLoading(false);
      }
    });

    return unsubscribe;
  }, []);

  if (loading) {
    return (
      <View style={[styles.container, { backgroundColor: theme.background }]}>
        <ActivityIndicator size="large" color={theme.primary} />
      </View>
    );
  }

  if (alerts.length === 0) {
    return (
      <View style={[styles.container, { backgroundColor: theme.background }]}>
        <Animated.View entering={FadeInUp.delay(100).duration(600)}>
          <Text style={[styles.title, { color: theme.text }]}>Маршрутни промени</Text>
          <Text style={[styles.subtitle, { color: theme.onSurfaceVariant }]}>Нямат активни в момента.</Text>
        </Animated.View>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Animated.View entering={FadeInUp.delay(100).duration(600)} style={styles.header}>
          <Text style={[styles.subtitle, { color: theme.onSurfaceVariant }]}>
            {alerts.length} активни промени
          </Text>
        </Animated.View>

        {alerts.map((alert, index) => {
          const formattedSentences = formatDescription(alert.description);
          return (
            <Animated.View
              entering={FadeInDown.delay(200 + index * 100).duration(600)}
              key={alert.id}
            >
              <View
                style={[
                  styles.alertCard,
                  {
                    backgroundColor: theme.surface,
                    shadowColor: '#000',
                  },
                ]}
              >
                <View style={[styles.alertHeader, { borderBottomColor: theme.surfaceVariant }]}>
                  <View style={[styles.iconContainer, { backgroundColor: theme.primaryContainer }]}>
                    <Ionicons
                      name="alert-circle"
                      size={24}
                      color={theme.onPrimaryContainer}
                    />
                  </View>
                  <View style={styles.headerContent}>
                    <Text style={[styles.routeTitle, { color: theme.onSurface }]}>
                      Линия: {alert.routes.join(', ')}
                    </Text>
                  </View>
                </View>

                <View style={styles.alertBody}>
                  {formattedSentences.map((line, lineIndex) => (
                    <Text
                      key={lineIndex}
                      style={[styles.description, { color: theme.onSurface }]}
                    >
                      {line.map((segment, segmentIndex) => (
                        <Text
                          key={segmentIndex}
                          style={segment.bold ? { fontWeight: '700' } : undefined}
                        >
                          {segment.text}
                        </Text>
                      ))}
                    </Text>
                  ))}
                </View>
              </View>
            </Animated.View>
          );
        })}

        <View style={styles.footer} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    padding: 24,
    paddingTop: 60,
    paddingBottom: 120,
  },
  header: {
    marginBottom: 32,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    letterSpacing: -0.5,
  },
  subtitle: {
    fontSize: 14,
    fontWeight: '400',
  },
  alertCard: {
    borderRadius: 24,
    marginBottom: 20,
    overflow: 'hidden',
    position: 'relative',
    elevation: 3,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08,
    shadowRadius: 12,
  },
  alertHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    padding: 20,
    borderBottomWidth: 1.5,
    borderStyle: 'solid',
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
    flexShrink: 0,
  },
  headerContent: {
    flex: 1,
  },
  routeTitle: {
    marginTop: 15,
    fontSize: 16,
    fontWeight: '600',
  },
  alertBody: {
    padding: 20,
  },
  description: {
    fontSize: 14,
    lineHeight: 22,
    marginBottom: 12,
  },
  footer: {
    height: 40,
  },
});
