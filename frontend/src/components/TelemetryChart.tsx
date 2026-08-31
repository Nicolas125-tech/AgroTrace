'use client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';

interface TelemetryChartProps {
  data: any[];
  maxTemp: number;
  minTemp: number;
}

export function TelemetryChart({ data, maxTemp, minTemp }: TelemetryChartProps) {
  return (
    <div className="h-[400px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
          <XAxis dataKey="timestamp" tickFormatter={(t) => new Date(t).toLocaleTimeString()} />
          <YAxis />
          <Tooltip labelFormatter={(t) => new Date(t).toLocaleString()} />
          <Legend />
          <ReferenceLine y={maxTemp} label="Max Temp" stroke="red" strokeDasharray="3 3" />
          <ReferenceLine y={minTemp} label="Min Temp" stroke="blue" strokeDasharray="3 3" />
          <Line type="monotone" dataKey="temperature" stroke="#8884d8" name="Temp (°C)" dot={false} strokeWidth={2} />
          <Line type="monotone" dataKey="humidity" stroke="#82ca9d" name="Humidity (%)" dot={false} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
