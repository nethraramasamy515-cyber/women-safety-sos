import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { sosAPI, historyAPI } from '../services/api';
import { AlertTriangle, MapPin, Clock, Shield, Users, History, ChevronRight, Zap } from 'lucide-react';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [recentAlerts, setRecentAlerts] = useState([]);
  const [stats, setStats] = useState({ total: 0, active: 0, resolved: 0 });

  useEffect(() => { loadRecentAlerts(); }, []);

  const loadRecentAlerts = async () => {
    try {
      const { data } = await historyAPI.getAll();
      const alerts = data.alerts || [];
      setRecentAlerts(alerts.slice(0, 3));
      setStats({
        total: alerts.length,
        active: alerts.filter(a => a.status === 'active').length,
        resolved: alerts.filter(a => a.status === 'resolved').length,
      });
    } catch (err) { /* silent */ }
  };

  const quickActions = [
    { icon: AlertTriangle, label: 'SOS Alert', desc: 'Send emergency alert', path: '/sos', gradient: 'from-red-600 to-red-800', urgent: true },
    { icon: Users, label: 'Contacts', desc: 'Manage contacts', path: '/contacts', gradient: 'from-emerald-600 to-green-800' },
    { icon: MapPin, label: 'Stations', desc: 'Find police stations', path: '/police', gradient: 'from-emerald-700 to-green-900' },
    { icon: History, label: 'History', desc: 'View alert history', path: '/history', gradient: 'from-green-700 to-emerald-900' },
  ];

  return (
    <div className="min-h-screen bg-animated-gradient relative">
      <div className="orb orb-1" /><div className="orb orb-2" /><div className="orb orb-5" />
      <div className="mesh-bg absolute inset-0" />

      <div className="relative z-10 max-w-6xl mx-auto px-5 sm:px-8 pt-28 pb-16">
        {/* WELCOME */}
        <div className="mb-14 animate-slide-up">
          <div className="flex items-center gap-4 mb-3">
            <div className="w-14 h-14 rounded-full bg-gradient-to-br from-emerald-500 to-green-700 flex items-center justify-center shadow-lg flex-shrink-0">
              <Shield className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-black text-white">Welcome back, {user?.name?.split(' ')[0] || 'User'} 👋</h1>
              <p className="text-gray-400 text-sm sm:text-base">Your safety dashboard is ready</p>
            </div>
          </div>
        </div>

        {/* SOS BUTTON */}
        <div className="mb-14 animate-slide-up delay-100">
          <Link to="/sos" className="block glass-card rounded-3xl p-8 sm:p-10 text-center group relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-red-900/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative z-10">
              <div className="relative inline-block mb-5">
                <div className="absolute inset-0 bg-red-500/20 blur-3xl rounded-full animate-ping" />
                <div className="w-28 h-28 sm:w-32 sm:h-32 rounded-full bg-gradient-to-br from-red-600 via-red-700 to-red-900 flex items-center justify-center shadow-2xl shadow-red-900/50 sos-pulse">
                  <AlertTriangle className="h-14 w-14 text-white" />
                </div>
              </div>
              <h2 className="text-2xl sm:text-3xl font-black text-white mb-2 group-hover:text-red-400 transition-colors">SOS Emergency</h2>
              <p className="text-gray-400 text-base sm:text-lg">Press to send emergency alert to all contacts</p>
            </div>
          </Link>
        </div>

        {/* STATS */}
        <div className="grid grid-cols-3 gap-3 sm:gap-5 mb-14">
          {[
            { label: 'Total Alerts', value: stats.total, icon: Zap, color: 'text-emerald-400' },
            { label: 'Active', value: stats.active, icon: AlertTriangle, color: 'text-red-400' },
            { label: 'Resolved', value: stats.resolved, icon: Shield, color: 'text-green-400' },
          ].map((s, i) => (
            <div key={i} className="glass-card rounded-2xl p-4 sm:p-6 text-center animate-slide-up" style={{ animationDelay: `${(i + 2) * 0.1}s` }}>
              <s.icon className={`h-5 w-5 sm:h-6 sm:w-6 ${s.color} mx-auto mb-2 sm:mb-3`} />
              <p className="text-2xl sm:text-3xl font-black text-white mb-1">{s.value}</p>
              <p className="text-gray-500 text-xs sm:text-sm">{s.label}</p>
            </div>
          ))}
        </div>

        {/* QUICK ACTIONS */}
        <div className="mb-14">
          <h2 className="text-xl sm:text-2xl font-black text-white mb-6">Quick Actions</h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-5">
            {quickActions.map((action, i) => (
              <Link key={i} to={action.path}
                className={`glass-card card-shine rounded-2xl p-5 sm:p-6 text-center group animate-slide-up ${action.urgent ? 'ring-1 ring-red-500/30' : ''}`} style={{ animationDelay: `${(i + 1) * 0.1}s` }}>
                <div className={`w-14 h-14 sm:w-16 sm:h-16 rounded-2xl bg-gradient-to-br ${action.gradient} flex items-center justify-center mx-auto mb-3 sm:mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                  <action.icon className="h-7 w-7 sm:h-8 sm:w-8 text-white" />
                </div>
                <h3 className="text-base sm:text-lg font-bold text-white mb-1 group-hover:text-emerald-400 transition-colors">{action.label}</h3>
                <p className="text-gray-500 text-xs sm:text-sm hidden sm:block">{action.desc}</p>
                <ChevronRight size={18} className="text-gray-600 mx-auto mt-2 group-hover:text-emerald-400 group-hover:translate-x-1 transition-all" />
              </Link>
            ))}
          </div>
        </div>

        {/* RECENT ALERTS */}
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl sm:text-2xl font-black text-white">Recent Alerts</h2>
            <Link to="/history" className="text-emerald-400 font-medium text-sm flex items-center gap-1 hover:text-emerald-300 transition-colors">
              View All <ChevronRight size={16} />
            </Link>
          </div>
          {recentAlerts.length === 0 ? (
            <div className="glass-card rounded-2xl p-10 text-center">
              <Shield className="h-12 w-12 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">No alerts yet — you're safe!</p>
              <p className="text-gray-600 text-sm mt-2">Your alert history will appear here</p>
            </div>
          ) : (
            <div className="space-y-3 sm:space-y-4">
              {recentAlerts.map((alert) => (
                <div key={alert.id} className="glass-card rounded-xl p-4 sm:p-5 flex items-center gap-4 sm:gap-5">
                  <div className={`w-11 h-11 sm:w-12 sm:h-12 rounded-full flex items-center justify-center flex-shrink-0 ${alert.status === 'active' ? 'bg-red-500/20' : 'bg-green-500/20'}`}>
                    <AlertTriangle size={18} className={alert.status === 'active' ? 'text-red-400' : 'text-green-400'} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-white font-medium">SOS Alert</p>
                    <div className="flex items-center gap-2 text-xs sm:text-sm text-gray-400">
                      <Clock size={14} className="flex-shrink-0" />
                      <span className="truncate">{new Date(alert.createdAt).toLocaleString()}</span>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold flex-shrink-0 ${alert.status === 'active' ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
                    {alert.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
