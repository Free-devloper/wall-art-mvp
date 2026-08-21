import { useEffect, useState } from 'react';
import { adminGetCosts } from '../../lib/api';
import type { CostReport } from '../../types';
import LoadingSpinner from '../../components/LoadingSpinner';

const formatMoney = (val: number | undefined) => {
  if (val === undefined) return '$0.00';
  return `$${val.toFixed(2)}`;
};

export default function AdminCostsPage() {
  const [costs, setCosts] = useState<CostReport | null>(null);

  useEffect(() => {
    adminGetCosts().then(res => setCosts(res.data)).catch(console.error);
  }, []);

  if (!costs) return <div className="flex justify-center py-20"><LoadingSpinner size="lg" message="Loading cost data..." /></div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Cost Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-sm text-gray-400 mb-1">Total Spend Today</h3>
          <p className="text-3xl font-bold text-white">{formatMoney(costs.total_today)}</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-sm text-gray-400 mb-1">Total Spend This Month</h3>
          <p className="text-3xl font-bold text-white">{formatMoney(costs.total_this_month)}</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-sm text-gray-400 mb-1">Avg Cost per Generation</h3>
          <p className="text-3xl font-bold text-white">{formatMoney(costs.average_cost)}</p>
        </div>
      </div>

      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-lg font-bold text-white mb-4">Daily Spend Overview</h3>
        <div className="h-48 flex items-end gap-2 border-b border-gray-700 pb-2">
          {costs.daily_spend?.map((day: any, i: number) => {
            const maxVal = Math.max(...(costs.daily_spend?.map((d: any) => d.total) || [1]));
            const pct = Math.max(5, (day.total / (maxVal || 1)) * 100);
            return (
              <div key={i} className="flex-1 bg-brand-gold/80 hover:bg-brand-gold rounded-t relative group" style={{ height: `${pct}%` }}>
                <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-xs py-1 px-2 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap z-10">
                  {day.date}: {formatMoney(day.total)}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-lg font-bold text-white mb-4">Spend Per Theme</h3>
        <table className="min-w-full divide-y divide-gray-700 text-left">
          <thead>
            <tr>
              <th className="py-2 text-gray-400 font-medium">Theme ID</th>
              <th className="py-2 text-gray-400 font-medium">Total Spend</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {Object.entries(costs.per_theme || {}).map(([themeId, total]: any) => (
              <tr key={themeId}>
                <td className="py-2 text-white">{themeId}</td>
                <td className="py-2 text-white">{formatMoney(total)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
