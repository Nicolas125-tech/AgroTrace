import { useEffect } from 'react';
import NetInfo from '@react-native-community/netinfo';
import { useSyncStore } from '../store/useSyncStore';

export function useNetworkSync() {
  const flushQueue = useSyncStore((state) => state.flushQueue);

  useEffect(() => {
    // Escuta ativamente mudanças de torre (3G/4G/Wifi)
    const unsubscribe = NetInfo.addEventListener((state) => {
      // isInternetReachable valida ping real, não apenas conexão à antena
      if (state.isConnected && state.isInternetReachable) {
        console.log('[NetworkSync] Conexão restabelecida. Limpando a fila de mutações offline...');
        flushQueue();
      }
    });

    return () => {
      unsubscribe();
    };
  }, [flushQueue]);
}
