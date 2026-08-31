'use client';
import { useParams } from 'next/navigation';
import { useShipment, useTelemetry, useRoute } from '@/hooks/useShipmentData';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TelemetryChart } from '@/components/TelemetryChart';
import { RouteMap } from '@/components/RouteMap';
import { AlertTriangle, Package, Activity, Map as MapIcon } from 'lucide-react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

function ShipmentDashboard() {
  const params = useParams();
  const id = params.id as string;
  
  const { data: shipment, isLoading: loadingShipment } = useShipment(id);
  const { data: telemetry } = useTelemetry(id);
  const { data: route } = useRoute(id);

  if (loadingShipment) return <div className="p-8 text-center text-lg">Carregando Remessa...</div>;
  if (!shipment) return <div className="p-8 text-center text-red-500 text-lg">Remessa não encontrada</div>;

  const statusColors = {
    pending_sync: 'warning',
    accepted: 'success',
    rejected: 'destructive',
    quarantined: 'warning',
    breached: 'destructive',
    in_transit: 'default'
  } as const;

  const badgeVariant = statusColors[shipment.status as keyof typeof statusColors] || 'default';
  const isBreached = shipment.status === 'breached';

  return (
    <div className="container mx-auto p-6 space-y-6 max-w-7xl">
      <header className="flex justify-between items-center mb-8 border-b pb-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Package className="h-8 w-8 text-blue-600" />
            Remessa #{shipment.id}
          </h1>
          <p className="text-gray-500 mt-1">Cargo Profile: {shipment.profile.name}</p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <Badge variant={badgeVariant} className="text-sm px-4 py-1 uppercase">
            {shipment.status.replace('_', ' ')}
          </Badge>
          {isBreached && (
            <Badge variant="destructive" className="flex items-center gap-1 animate-pulse">
              <AlertTriangle className="w-4 h-4" /> Ruptura de Cadeia Fria Confirmada
            </Badge>
          )}
        </div>
      </header>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-gray-500" />
              Telemetria (Downsampled)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {telemetry ? (
              <TelemetryChart 
                data={telemetry} 
                maxTemp={shipment.profile.max_temp} 
                minTemp={shipment.profile.min_temp} 
              />
            ) : (
              <div className="flex h-[400px] items-center justify-center text-gray-400">Carregando série temporal...</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapIcon className="h-5 w-5 text-gray-500" />
              Histórico de Rota Espacial
            </CardTitle>
          </CardHeader>
          <CardContent>
            {route ? (
              <RouteMap route={route} />
            ) : (
              <div className="flex h-[400px] items-center justify-center text-gray-400">Carregando mapa...</div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default function Page() {
  return (
    <QueryClientProvider client={queryClient}>
      <ShipmentDashboard />
    </QueryClientProvider>
  );
}
