import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../services/api';

interface HandshakeTask {
  id: string; // ID único interno para a mutação local
  token: string;
  payload: {
    driver_cpf: string;
    driver_name: string;
    vehicle_plate: string;
    offline_timestamp: string; // A prova legal de data
  };
}

interface SyncState {
  pendingHandshakes: HandshakeTask[];
  isSyncing: boolean;
  addHandshake: (token: string, driverData: Omit<HandshakeTask['payload'], 'offline_timestamp'>) => void;
  flushQueue: () => Promise<void>;
}

export const useSyncStore = create<SyncState>()(
  persist(
    (set, get) => ({
      pendingHandshakes: [],
      isSyncing: false,

      addHandshake: (token, driverData) => {
        const newTask: HandshakeTask = {
          id: Date.now().toString() + Math.random().toString(36).substring(7),
          token,
          payload: {
            ...driverData,
            // CAPTURA CRÍTICA: Momento exato em que a ação física ocorre, indiferente à rede
            offline_timestamp: new Date().toISOString() 
          }
        };
        set((state) => ({
          pendingHandshakes: [...state.pendingHandshakes, newTask]
        }));
      },

      flushQueue: async () => {
        const { pendingHandshakes, isSyncing } = get();
        // Não flusheia se já estiver rodando ou não houver dados
        if (isSyncing || pendingHandshakes.length === 0) return;

        set({ isSyncing: true });

        const remainingTasks = [...pendingHandshakes];

        for (const task of pendingHandshakes) {
          try {
            const response = await api.post(`/public/handshake?token=${task.token}`, task.payload);
            if (response.status === 200 || response.status === 201) {
              // Sucesso no servidor: remove da fila local (idempotência garantida)
              const index = remainingTasks.findIndex((t) => t.id === task.id);
              if (index > -1) {
                remainingTasks.splice(index, 1);
              }
            }
          } catch (error) {
            console.warn(`[SyncStore] Falha ao enviar a task ${task.id}, mantendo na fila.`);
            // Sai do loop se a internet realmente ainda estiver instável, aguardando o próximo flush
            break;
          }
        }

        set({ pendingHandshakes: remainingTasks, isSyncing: false });
      }
    }),
    {
      name: 'agrotrace-sync-storage', // Chave no AsyncStorage nativo
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
