import React from 'react';
import { ThemedText } from '@/components/themed-text';

//const dataProvider = simpleRestProvider('http://localhost:3000/api');

export default function AdminApp() {
  return (
    <ThemedText type="title" style={{ margin: 20 }}>
      Admin Panel
    </ThemedText>
  );
}
