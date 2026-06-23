import React, { useId } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface SignalChartProps {
  data: number[];
  color?: string;
  title?: string;
}

const SignalChart: React.FC<SignalChartProps> = ({ data, color = "#075985", title }) => {
  const chartData = data.map((val, i) => ({ index: i, value: val }));
  const uniqueId = useId().replace(/:/g, '');
  const gradientId = `colorValue-${uniqueId}`;

  return (
    <div className="glass-card p-6">
      {title && <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-6">{title}</h3>}
      <div className="h-[350px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.15}/>
                <stop offset="95%" stopColor={color} stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
            <XAxis dataKey="index" hide />
            <YAxis domain={['auto', 'auto']} stroke="#94a3b8" fontSize={10} axisLine={false} tickLine={false} />
            <Tooltip 
              contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)', backgroundColor: '#fff' }}
              labelStyle={{ display: 'none' }}
            />
            <Area 
              type="monotone" 
              dataKey="value" 
              stroke={color} 
              strokeWidth={3}
              fillOpacity={1} 
              fill={`url(#${gradientId})`} 
              animationDuration={500}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default SignalChart;
