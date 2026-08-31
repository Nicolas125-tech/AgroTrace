import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';

export function useShipment(id: string) {
  return useQuery({
    queryKey: ['shipment', id],
    queryFn: async () => {
      const { data } = await api.get(`/shipments/${id}`);
      return data;
    },
    refetchInterval: 15000,
  });
}

export function useTelemetry(id: string) {
  return useQuery({
    queryKey: ['telemetry', id],
    queryFn: async () => {
      const { data } = await api.get(`/shipments/${id}/telemetry?bucket_interval=5 minutes`);
      return data;
    },
    refetchInterval: 15000,
  });
}

export function useRoute(id: string) {
  return useQuery({
    queryKey: ['route', id],
    queryFn: async () => {
      const { data } = await api.get(`/shipments/${id}/route?bucket_interval=15 minutes`);
      return data;
    },
    refetchInterval: 60000,
  });
}
