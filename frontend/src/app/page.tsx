'use client';

import { useEffect, useState } from 'react';
import { api } from '../services/api';
import Link from 'next/link';
import Map, { Marker } from 'react-map-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import maplibregl from 'maplibre-gl';

interface ShipmentListItem {
  id: number;
  status: string;
  tenant_id: number;
  profile_id: number;
  grace_period_hours: number;
}

export default function Home() {
  const [shipments, setShipments] = useState<ShipmentListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: Adicionar checagem de token real depois que tivermos tela de login
    api.get('/shipments')
      .then(res => setShipments(res.data))
      .catch(err => console.error("Erro ao carregar remessas:", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <header className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Visão Geral da Frota</h1>
        </header>
        
        {/* Mapa das frotas */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-800">Frotas em Trânsito</h2>
          </div>
          <div className="h-96 w-full">
            <Map
              mapLib={maplibregl}
              initialViewState={{
                longitude: -46.6333,
                latitude: -23.5505,
                zoom: 4
              }}
              mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
            >
              {/* No futuro os marcadores reais virão de /api/shipments/{id}/route da lista ativa */}
              <Marker longitude={-46.6333} latitude={-23.5505} color="red" />
            </Map>
          </div>
        </section>

        {/* Lista de Remessas */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-800">Minhas Remessas</h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID da Remessa</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={3} className="px-6 py-4 text-center text-gray-500">
                      Carregando remessas...
                    </td>
                  </tr>
                ) : shipments.length === 0 ? (
                  <tr>
                    <td colSpan={3} className="px-6 py-4 text-center text-gray-500">
                      Nenhuma remessa encontrada. (Você fez login?)
                    </td>
                  </tr>
                ) : shipments.map(s => (
                  <tr key={s.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      #{s.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                        ${s.status === 'in_transit' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}`}>
                        {s.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600 hover:text-blue-900">
                      <Link href={`/shipments/${s.id}`}>
                        Acompanhar
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
}
