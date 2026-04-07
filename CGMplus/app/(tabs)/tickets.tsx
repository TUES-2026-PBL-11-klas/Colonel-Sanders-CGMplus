import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, useColorScheme } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/theme';
import Animated, { FadeInDown, FadeInUp } from 'react-native-reanimated';
import { MOCK_TICKETS, type Ticket } from '@/constants/mock-data';

export default function TicketsScreen() {
  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];


  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <ScrollView contentContainerStyle={styles.scrollContent}>

        <Animated.View entering={FadeInUp.delay(100).duration(600)} style={styles.header}>
          <Text style={[styles.title, { color: theme.text }]}>My Tickets</Text>
          <Text style={[styles.subtitle, { color: theme.onSurfaceVariant }]}>Active passes and trips</Text>
        </Animated.View>

        {MOCK_TICKETS.map((ticket: Ticket, index: number) => (
          <Animated.View
            entering={FadeInDown.delay(200 + index * 100).duration(600)}
            key={ticket.id}
          >
            <TouchableOpacity
              style={[styles.ticketCard, { backgroundColor: theme.surface, shadowColor: '#000' }]}
              activeOpacity={0.8}
            >
              <View style={[styles.ticketHeader, { borderBottomColor: theme.surfaceVariant }]}>
                <View style={styles.ticketHeaderLeft}>
                  <View style={[styles.iconContainer, { backgroundColor: theme.primaryContainer }]}>
                    <Ionicons
                      name={ticket.type === 'Bus' ? 'bus' : 'train'}
                      size={24}
                      color={theme.onPrimaryContainer}
                    />
                  </View>
                  <Text style={[styles.ticketTitle, { color: theme.onSurface }]}>{ticket.title}</Text>
                </View>
              </View>

              <View style={styles.ticketBody}>
                <View style={styles.infoRow}>
                  <Text style={[styles.infoLabel, { color: theme.onSurfaceVariant }]}>Status</Text>
                  <Text style={[
                      styles.infoValue,
                      { color: ticket.status === 'Active' ? theme.mint : theme.primary }
                    ]}>
                    {ticket.status}
                  </Text>
                </View>
                <View style={styles.infoRow}>
                  <Text style={[styles.infoLabel, { color: theme.onSurfaceVariant }]}>Valid Until</Text>
                  <Text style={[styles.infoValue, { color: theme.onSurface }]}>{ticket.expiry}</Text>
                </View>
              </View>

              <View style={[styles.ticketTear, { backgroundColor: theme.background, left: -10 }]} />
              <View style={[styles.ticketTear, { backgroundColor: theme.background, right: -10 }]} />
            </TouchableOpacity>
          </Animated.View>
        ))}

        <Animated.View entering={FadeInDown.delay(300).duration(600)} style={styles.actionContainer}>
           <TouchableOpacity style={[styles.buyButton, { backgroundColor: theme.primaryContainer }]}>
             <Ionicons name="add" size={24} color={theme.onPrimaryContainer} />
             <Text style={[styles.buyButtonText, { color: theme.onPrimaryContainer }]}>Buy New Ticket</Text>
           </TouchableOpacity>
        </Animated.View>

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
    paddingBottom: 120, // Leave room for tab bar
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
    marginTop: 4,
    fontWeight: '400',
  },
  ticketCard: {
    borderRadius: 24,
    marginBottom: 20,
    overflow: 'hidden',
    position: 'relative',
    elevation: 3,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
  },
  ticketHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1.5,
    borderStyle: 'dashed', // Transit ticket aesthetic
  },
  ticketHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  ticketTitle: {
    fontSize: 18,
    fontWeight: '600',
  },
  ticketBody: {
    padding: 20,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  infoLabel: {
    fontSize: 14,
    fontWeight: '500',
  },
  infoValue: {
    fontSize: 16,
    fontWeight: '600',
  },
  ticketTear: {
    position: 'absolute',
    top: 80, // Align exactly with the dashed border
    width: 20,
    height: 20,
    borderRadius: 10,
  },
  actionContainer: {
    marginTop: 16,
  },
  buyButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 56,
    borderRadius: 999, // Pill shape
  },
  buyButtonText: {
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  }
});
