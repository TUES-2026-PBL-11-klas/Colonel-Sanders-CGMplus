import { Platform } from 'react-native';
import { Redirect } from 'expo-router';

// Hard block — should never be reached on native, but just in case
function AdminPage() {
  if (Platform.OS !== 'web') {
    return <Redirect href="/" />;
  } else {
    const { default: AdminApp } = require('@/admin/adminApp');
    return <AdminApp />;
  }
}

export default AdminPage;
