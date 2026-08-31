import React from 'react';
import { StyleSheet, View, SafeAreaView, StatusBar, Text } from 'react-native';
import { useNetworkSync } from './src/hooks/useNetworkSync';
import { ScannerScreen } from './src/screens/ScannerScreen';
import { useSyncStore } from './src/store/useSyncStore';

export default function App() {
  // Inicializa o Listener de Fila Offline globalmente
  useNetworkSync();

  const pendingHandshakes = useSyncStore((state) => state.pendingHandshakes);
  const isSyncing = useSyncStore((state) => state.isSyncing);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      
      {/* Top bar de status (exibe a fila de sync) */}
      <View style={styles.header}>
        <Text style={styles.headerText}>AgroTrace Driver</Text>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>
            {isSyncing ? 'Sincronizando...' : `${pendingHandshakes.length} pendentes`}
          </Text>
        </View>
      </View>

      <ScannerScreen />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#18181b', // dark background (combina com a câmera)
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: '#18181b',
    borderBottomWidth: 1,
    borderBottomColor: '#27272a',
  },
  headerText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  badge: {
    backgroundColor: '#2563eb',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  badgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  }
});
