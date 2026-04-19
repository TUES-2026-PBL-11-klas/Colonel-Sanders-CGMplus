import React, { useState } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  Alert,
  Modal,
  TextInput,
  ActivityIndicator,
  useColorScheme,
  Image,
  Linking,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../context/auth-context';
import { API } from '../../utils/api';
import Animated, { FadeInDown, FadeInUp } from 'react-native-reanimated';
import { Colors } from '@/constants/theme';

export default function ProfileScreen() {
  const { user, logout, refreshUser } = useAuth();
  const [passwordModalVisible, setPasswordModalVisible] = useState(false);
  const [deleteModalVisible, setDeleteModalVisible] = useState(false);
  const [isActionLoading, setIsActionLoading] = useState(false);

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];

  const handleLogout = () => {
    Alert.alert('Излез', 'Сигурен ли си, че искаш да излезеш от профила си?', [
      { text: 'Отказ', style: 'cancel' },
      { text: 'Излез', style: 'destructive', onPress: logout },
    ]);
  };

  const handleChangePassword = async () => {
    if (!currentPassword || !newPassword || !confirmPassword) return;
    if (newPassword !== confirmPassword) {
      Alert.alert('Паролите не съвпадат', 'Новата парола и потвърждението трябва да са еднакви.');
      return;
    }
    setIsActionLoading(true);
    try {
      const response = await API.changePassword({ current_password: currentPassword, new_password: newPassword });
      if (response.status === 204) {
        Alert.alert('Успех', 'Паролата беше променена успешно. Моля влез в профила си отново!', [
          { text: 'ОК', onPress: logout }
        ]);
        setPasswordModalVisible(false);
      } else {
        const data = await response.json().catch(() => ({}));
        Alert.alert('Грешка', data.message || 'Възникна грешка в сменянето на паролата');
      }
    } catch (e) {
      Alert.alert('Грешка', 'Грешка с мрежата');
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    setIsActionLoading(true);
    try {
      const response = await API.deleteAccount();
      if (response.status === 204) {
        Alert.alert('Изтрит акаунт', 'Вашият акаунт беше успешно деактивиран.', [
          { text: 'ОК', onPress: logout }
        ]);
      } else {
        Alert.alert('Грешка', 'Неуспешно изтриване на акаунта');
      }
    } catch (e) {
      Alert.alert('Грешка', 'Грешка с мрежата');
    } finally {
      setIsActionLoading(false);
      setDeleteModalVisible(false);
    }
  };

  const ProfileItem = ({ icon, label, onPress, color = theme.onSurface }: any) => (
    <TouchableOpacity style={styles.profileItem} onPress={onPress}>
      <View style={styles.itemLeft}>
        <View style={[styles.iconContainer, { backgroundColor: theme.surfaceVariant }]}>
          <Ionicons name={icon} size={20} color={color} />
        </View>
        <Text style={[styles.itemLabel, { color }]}>{label}</Text>
      </View>
      <Ionicons name="chevron-forward" size={20} color={theme.outline} />
    </TouchableOpacity>
  );

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <ScrollView contentContainerStyle={styles.scrollContent}>

        <Animated.View entering={FadeInUp.delay(100).duration(600)} style={styles.header}>
          <Text style={[styles.title, { color: theme.text }]}>Профил</Text>
          <Text style={[styles.subtitle, { color: theme.onSurfaceVariant }]}>Управляване на ЦГМ+ акаунт</Text>
        </Animated.View>

        <Animated.View
          entering={FadeInDown.delay(300).duration(600)}
          style={[styles.ticketCard, { backgroundColor: theme.surface, shadowColor: '#000' }]}
        >
          <View style={styles.cardGraphicContainer}>
            <Image
              source={require('@/assets/graphics/card-graphic.jpg')}
              style={styles.cardGraphic}
            />
            <View style={styles.cardGraphicOverlay}>
              <View style={styles.avatarRow}>
                <View style={[styles.avatarContainer, { backgroundColor: theme.primaryContainer }]}>
                   <Ionicons name="person" size={32} color={theme.onPrimaryContainer} />
                </View>
                <View>
                  <Text style={styles.graphicText}>{user?.name || user?.email || 'Guest User'}</Text>
                </View>
              </View>
            </View>
          </View>

          <View style={styles.cardBody}>
            <Text style={[styles.sectionTitle, { color: theme.primary }]}>Настройки на акаунт</Text>
            <View style={[styles.cardBlock, { backgroundColor: theme.surface }]}>
              <ProfileItem
                icon="lock-closed"
                label="Смени парола"
                onPress={() => setPasswordModalVisible(true)}
              />
            </View>

            <Text style={[styles.sectionTitle, { color: theme.primary, marginTop: 24 }]}>Поддръжка</Text>
            <View style={[styles.cardBlock, { backgroundColor: theme.surface }]}>
              <ProfileItem icon="help-circle" label="Помощен център" onPress={() => Linking.openURL('http://192.168.1.164/support')} />
              <View style={[styles.separator, { backgroundColor: theme.surfaceVariant }]} />
              <ProfileItem icon="document-text" label="Условия за ползване" onPress={() => Linking.openURL('http://192.168.1.164/terms')} />
              <View style={[styles.separator, { backgroundColor: theme.surfaceVariant }]} />
              <ProfileItem icon="shield-checkmark" label="Поверителност" onPress={() => Linking.openURL('http://192.168.1.164/privacy')} />
            </View>

            {user && (
              <>
                <Text style={[styles.sectionTitle, { color: theme.error, marginTop: 24 }]}>Опасна зона</Text>
                <View style={[styles.cardBlock, { backgroundColor: theme.surface }]}>
                  <ProfileItem
                    icon="log-out"
                    label="Излез от профила"
                    color={theme.error}
                    onPress={handleLogout}
                  />
                  <View style={[styles.separator, { backgroundColor: theme.surfaceVariant }]} />
                  <ProfileItem
                    icon="trash"
                    label="Изтрий акаунт"
                    color={theme.error}
                    onPress={() => setDeleteModalVisible(true)}
                  />
                </View>
              </>
            )}
          </View>
        </Animated.View>
      </ScrollView>

      {/* Change Password Modal */}
      <Modal visible={passwordModalVisible} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: theme.surface }]}>
            <Text style={[styles.modalTitle, { color: theme.onSurface }]}>Промени парола</Text>
            <TextInput
              style={[styles.modalInput, { color: theme.text, borderColor: theme.outline, backgroundColor: theme.surfaceVariant }]}
              placeholder="Текуща парола"
              placeholderTextColor={theme.onSurfaceVariant}
              secureTextEntry
              value={currentPassword}
              onChangeText={setCurrentPassword}
            />
            <TextInput
              style={[styles.modalInput, { color: theme.text, borderColor: theme.outline, backgroundColor: theme.surfaceVariant }]}
              placeholder="Нова парола"
              placeholderTextColor={theme.onSurfaceVariant}
              secureTextEntry
              value={newPassword}
              onChangeText={setNewPassword}
            />
            <TextInput
              style={[styles.modalInput, { color: theme.text, borderColor: theme.outline, backgroundColor: theme.surfaceVariant }]}
              placeholder="Потвърди новата парола"
              placeholderTextColor={theme.onSurfaceVariant}
              secureTextEntry
              value={confirmPassword}
              onChangeText={setConfirmPassword}
            />
            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton, { borderColor: theme.outline }]}
                onPress={() => setPasswordModalVisible(false)}
              >
                <Text style={[styles.cancelButtonText, { color: theme.onSurfaceVariant }]}>Отказ</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.modalButton, styles.submitButton, { backgroundColor: theme.primary }]}
                onPress={handleChangePassword}
                disabled={isActionLoading}
              >
               {isActionLoading ? <ActivityIndicator color={theme.onPrimary} /> : <Text style={[styles.submitButtonText, { color: theme.onPrimary }]}>Промяна</Text>}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Delete Account Modal (M3 Style alert) */}
      <Modal visible={deleteModalVisible} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: theme.surface }]}>
            <Ionicons name="warning" size={40} color={theme.error} style={{ alignSelf: 'center', marginBottom: 16 }} />
            <Text style={[styles.modalTitle, { color: theme.onSurface }]}>Изтрий акаунт?</Text>
            <Text style={[styles.modalDescription, { color: theme.onSurfaceVariant }]}>
              Това действие е постоянно и ще деактивира акаунта ви. Всички пропуски и данни ще бъдат загубени.
            </Text>
            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton, { borderColor: theme.outline }]}
                onPress={() => setDeleteModalVisible(false)}
              >
                <Text style={[styles.cancelButtonText, { color: theme.onSurfaceVariant }]}>Отказ</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.modalButton, styles.submitButton, { backgroundColor: theme.error }]}
                onPress={handleDeleteAccount}
                disabled={isActionLoading}
              >
               {isActionLoading ? <ActivityIndicator color="#FFF" /> : <Text style={[styles.submitButtonText, { color: '#FFF' }]}>Изтрий</Text>}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
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
    marginTop: 4,
    fontWeight: '400',
  },
  ticketCard: {
    borderRadius: 28,
    overflow: 'hidden',
    elevation: 4,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
  },
  cardGraphicContainer: {
    height: 120,
    width: '100%',
    position: 'relative',
  },
  cardGraphic: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  cardGraphicOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
    padding: 24,
  },
  avatarRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatarContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  graphicText: {
    color: '#FFF',
    fontSize: 20,
    fontWeight: '600',
  },
  badgeText: {
    fontSize: 13,
    fontWeight: '500',
    marginTop: 4,
  },
  cardBody: {
    padding: 24,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 12,
    marginLeft: 4,
  },
  cardBlock: {
    borderRadius: 24,
  },
  profileItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
  },
  itemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  itemLabel: {
    fontSize: 16,
    marginLeft: 16,
    fontWeight: '500',
  },
  separator: {
    height: 1,
    marginLeft: 56, // Align with text
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.4)', // M3 Scrim
    justifyContent: 'center',
    padding: 24,
  },
  modalContent: {
    borderRadius: 28, // M3 Extra Large
    padding: 24,
  },
  modalTitle: {
    fontSize: 22,
    fontWeight: '600',
    marginBottom: 16,
    textAlign: 'center',
  },
  modalDescription: {
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 20,
  },
  modalInput: {
    borderRadius: 16,
    height: 56,
    paddingHorizontal: 16,
    marginBottom: 12,
    borderWidth: 1,
  },
  modalButtons: {
    flexDirection: 'row',
    marginTop: 12,
    gap: 8,
  },
  modalButton: {
    flex: 1,
    height: 52,
    borderRadius: 999, // Pill
    justifyContent: 'center',
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
  },
  cancelButtonText: {
    fontWeight: '600',
    fontSize: 16,
  },
  submitButton: {
    borderWidth: 0,
  },
  submitButtonText: {
    fontWeight: '600',
    fontSize: 16,
  },
});
