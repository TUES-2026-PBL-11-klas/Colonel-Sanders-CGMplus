import React from 'react';
import { Admin, Resource, ListGuesser } from 'react-admin';
import simpleRestProvider from 'ra-data-simple-rest';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';

//const dataProvider = simpleRestProvider('http://localhost:3000/api');

export default function AdminApp() {
  return (
    <ThemedText type="title" style={{ margin: 20 }}>
      Admin Panel
    </ThemedText>
  );
}
