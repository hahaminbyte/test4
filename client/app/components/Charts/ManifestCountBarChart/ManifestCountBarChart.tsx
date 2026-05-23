import React, { ReactElement } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

type MonthCount = {
  date: string;
  hazardous: number;
  nonHazardous: number;
};

const monthTickFormatter = (tick: string) => {
  const date = new Date(`${tick}-01`);
  return date.getMonth() + 1;
};

const renderQuarterTick = (tickProps: any): ReactElement<SVGElement> => {
  const { x, y, payload } = tickProps;
  const { value, offset } = payload;
  const date = new Date(`${value}-01`);
  const month = date.getMonth();
  const quarterNo = Math.floor(month / 3) + 1;

  if (month % 3 === 1) {
    return <text x={x} y={y - 4} textAnchor="middle">{`Q${quarterNo}`}</text>;
  }

  const isLast = month === 11;

  if (month % 3 === 0 || isLast) {
    const pathX = Math.floor(isLast ? x + offset : x - offset) + 0.5;
    return <path d={`M${pathX},${y - 4}v${-35}`} stroke="red" />;
  }
  return <></>;
};

export function ManifestCountBarChart({ data = [] }: { data?: MonthCount[] }) {
  if (!data.length) {
    return <p className="text-muted text-center mb-0 py-5">No monthly manifest data yet.</p>;
  }

  return (
    <ResponsiveContainer minWidth={100} minHeight={300} height={'10%'}>
      <BarChart
        width={500}
        height={300}
        data={data}
        margin={{
          top: 5,
          right: 30,
          left: 20,
          bottom: 5,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" tickFormatter={monthTickFormatter} />
        <XAxis
          dataKey="date"
          axisLine={false}
          tickLine={false}
          interval={0}
          tick={renderQuarterTick}
          height={1}
          scale="band"
          xAxisId="quarter"
        />
        <YAxis allowDecimals={false} />
        <Tooltip />
        <Legend />
        <Bar dataKey="nonHazardous" fill="#8884d8" />
        <Bar dataKey="hazardous" fill="#82ca9d" />
      </BarChart>
    </ResponsiveContainer>
  );
}
