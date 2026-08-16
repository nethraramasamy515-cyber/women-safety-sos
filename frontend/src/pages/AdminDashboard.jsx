import { useState, useEffect } from 'react';
import { adminAPI } from '../services/api';
import { Users, AlertTriangle, Shield, Clock, TrendingUp } from 'lucide-react';
import toast from 'react-hot-toast';

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadDashboard(); }, []);

  const loadDashboard = async () => {
    try {
      const [statsRes, alertsRes, usersRes] = await Promise.all([
        adminAPI.getStats(), adminAPI.getAllAlerts(), adminAPI.getAllUsers()
      ]);
      setStats(statsRes.data.stats); setAlerts(alertsRes.data.alerts); setUsers(usersRes.data.users);
    } catch (err) { toast.error('Failed to load dashboard'); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-animated-gradient relative">
      <div className="orb orb-1" /><div className="orb orb-2" />
      <div className="mesh-bg absolute inset-0" />
      <div className="relative z-10 max-w-6xl mx-auto px-5 sm:px-8 pt-28 pb-16">
        <div className="mb-10 animate-slide-up">
          <h1 className="text-2xl sm:text-3xl font-black text-white mb-2">Admin Dashboard</h1>
          <p className="text-gray-400 text-sm sm:text-base">System overview and user management</p>
        </div>

        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 mb-10">
            {[
              { icon: Users, label: 'Total Users', value: stats.totalUsers, color: 'text-emerald-400' },
              { icon: AlertTriangle, label: 'Total Alerts', value: stats.totalAlerts, color: 'text-red-400' },
              { icon: Shield, label: 'Active Alerts', value: stats.activeAlerts, color: 'text-red-500' },
              { icon: TrendingUp, label: 'Resolved', value: stats.resolvedAlerts, color: 'text-green-400' },
            ].map((s, i) => (
              <div key={i} className="glass-card rounded-2xl p-4 sm:p-6 text-center animate-slide-up" style={{ animationDelay: `${i * 0.1}s` }}>
                <s.icon className={`h-5 w-5 sm:h-6 sm:w-6 ${s.color} mx-auto mb-2 sm:mb-3`} />
                <p className="text-2xl sm:text-3xl font-black text-white mb-1">{s.value}</p>
                <p className="text-gray-500 text-xs sm:text-sm">{s.label}</p>
              </div>
            ))}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 sm:gap-6">
          <div className="glass-card rounded-2xl p-5 sm:p-6 animate-slide-up">
            <div className="flex items-center gap-2 mb-5">
              <AlertTriangle className="text-red-400" size={20} />
              <h2 className="text-lg sm:text-xl font-black text-white">Recent Alerts</h2>
            </div>
            <div className="space-y-3 max-h-80 overflow-y-auto pr-2">
              {alerts.slice(0, 10).map((a) => (
                <div key={a.id} className="glass rounded-xl p-4 flex items-center gap-3 sm:gap-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${a.status === 'active' ? 'bg-red-500/20' : 'bg-green-500/20'}`}>
                    <AlertTriangle size={16} className={a.status === 'active' ? 'text-red-400' : 'text-green-400'} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-sm font-medium truncate">{a.user?.name || 'Unknown'}</p>
                    <p className="text-gray-500 text-xs flex items-center gap-1"><Clock size={12} className="flex-shrink-0" /> <span className="truncate">{new Date(a.createdAt).toLocaleString()}</span></p>
                  </div>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-bold flex-shrink-0 ${a.status === 'active' ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
                    {a.status}
                  </span>
                </div>
              ))}
              {alerts.length === 0 && <p className="text-gray-500 text-sm text-center py-4">No alerts yet</p>}
            </div>
          </div>

          <div className="glass-card rounded-2xl p-5 sm:p-6 animate-slide-up delay-200">
            <div className="flex items-center gap-2 mb-5">
              <Users className="text-emerald-400" size={20} />
              <h2 className="text-lg sm:text-xl font-black text-white">All Users</h2>
            </div>
            <div className="space-y-3 max-h-80 overflow-y-auto pr-2">
              {users.map((u) => (
                <div key={u.id} className="glass rounded-xl p-4 flex items-center gap-3 sm:gap-4">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-green-700 flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-bold text-white">{u.name?.[0]?.toUpperCase()}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-sm font-medium truncate">{u.name}</p>
                    <p className="text-gray-500 text-xs truncate">{u.email}</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className="text-emerald-400 text-sm font-bold">{u.alertCount || 0}</p>
                    <p className="text-gray-600 text-xs">alerts</p>
                  </div>
                </div>
              ))}
              {users.length === 0 && <p className="text-gray-500 text-sm text-center py-4">No users yet</p>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
