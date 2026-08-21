import { useEffect, useState } from 'react';
import { getAuthHeader } from '../../lib/auth';
import { formatPrice } from '../../lib/utils';
import LoadingSpinner from '../../components/LoadingSpinner';
import axios from 'axios';

interface UserRow {
  user_id: string;
  name: string;
  email: string;
  order_count: number;
  total_spent_cents: number;
  first_order: string | null;
  last_order: string | null;
}

export default function AdminUsersPage() {
  const [users, setUsers] = useState<UserRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/api/admin/users', { headers: getAuthHeader() })
      .then(res => setUsers(res.data.users))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex justify-center py-20"><LoadingSpinner size="lg" message="Loading users..." /></div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Users</h1>
        <span className="text-gray-400 text-sm">{users.length} total users</span>
      </div>

      <div className="bg-gray-800 rounded-lg overflow-hidden shadow">
        <table className="w-full text-sm">
          <thead className="bg-gray-900 text-gray-400 uppercase text-xs">
            <tr>
              <th className="px-6 py-3 text-left">Name</th>
              <th className="px-6 py-3 text-left">Email</th>
              <th className="px-6 py-3 text-center">Orders</th>
              <th className="px-6 py-3 text-right">Total Spent</th>
              <th className="px-6 py-3 text-right">Last Order</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {users.map(user => (
              <tr key={user.user_id} className="hover:bg-gray-700/50 transition-colors">
                <td className="px-6 py-4 text-white font-medium">{user.name}</td>
                <td className="px-6 py-4 text-gray-300">{user.email}</td>
                <td className="px-6 py-4 text-center">
                  <span className="bg-brand-gold/20 text-brand-gold px-2 py-1 rounded-full text-xs font-bold">
                    {user.order_count}
                  </span>
                </td>
                <td className="px-6 py-4 text-right text-white">{formatPrice(user.total_spent_cents)}</td>
                <td className="px-6 py-4 text-right text-gray-400">
                  {user.last_order ? new Date(user.last_order).toLocaleDateString() : '-'}
                </td>
              </tr>
            ))}
            {users.length === 0 && (
              <tr><td colSpan={5} className="px-6 py-12 text-center text-gray-500">No users found</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
