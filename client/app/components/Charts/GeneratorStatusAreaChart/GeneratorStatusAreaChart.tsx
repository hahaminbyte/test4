import {
  Area,
  AreaChart,
  CartesianGrid,
  Label,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const generatorStatusYAxis = ([_dataMin, dataMax]: [number, number]): [number, number] => {
  const yMax = dataMax < 100 ? 120 : dataMax < 1000 ? 1200 : Math.ceil((dataMax * 1.5) / 100) * 100;
  return [0, yMax];
};

type DayPoint = { day: number; haz: number };

export function GeneratorStatusAreaChart({ data = [] }: { data?: DayPoint[] }) {
  const monthNumber = new Date().getMonth();
  const days = data.length || new Date(new Date().getFullYear(), monthNumber + 1, 0).getDate();

  if (!data.length || data.every((point) => point.haz === 0)) {
    return (
      <p className="text-muted text-center mb-0 py-5">
        No generator activity this month.
      </p>
    );
  }

  return (
    <ResponsiveContainer minWidth={100} minHeight={300} height={'10%'}>
      <AreaChart data={data} margin={{ top: 10, right: 50, left: 25, bottom: 25 }}>
        <defs>
          <linearGradient id="colorHaz" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8} />
            <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
          </linearGradient>
        </defs>
        <ReferenceLine
          y={1000}
          label={{ value: 'LQG', position: 'right' }}
          stroke="red"
          strokeDasharray="3 3"
        />
        <ReferenceLine
          y={100}
          label={{ value: 'SQG', position: 'right' }}
          stroke="blue"
          strokeDasharray="3 3"
        />
        <XAxis
          dataKey="day"
          type="number"
          domain={[1, days]}
          tickFormatter={(value, _index) => `${monthNumber + 1}/${value}`}
        >
          <Label value="Date" position="bottom" />
        </XAxis>
        <YAxis domain={generatorStatusYAxis}>
          <Label value="Manifests created" position="left" angle={-90} />
        </YAxis>
        <CartesianGrid strokeDasharray="3 3" />
        <Tooltip />
        <Area
          type="monotone"
          dataKey="haz"
          stroke="#8884d8"
          fillOpacity={1}
          fill="url(#colorHaz)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}


// PR: Update Chart Components for New Data Structure
// Contextual improvement from pull request history
