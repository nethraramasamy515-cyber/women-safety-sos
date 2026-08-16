import { useState, useEffect } from 'react';
import { historyAPI, sosAPI } from '../services/api';
import { AlertTriangle, Clock, MapPin, ChevronDown, ChevronUp, Shield, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const History = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);

  useEffect(() => { loadHistory(); }, []);

  const loadHistory = async () => {
    try { const { data } = await historyAPI.getAll(); setAlerts(data.alerts); }
    catch (err) { toast.error('Failed to load history'); }
    finally { setLoading(false); }
  };

  const resolveAlert = async (id) => {
    try { await sosAPI.resolve(id, 'resolved'); toast.success('Alert resolved'); loadHistory(); }
    catch (err) { toast.error('Failed to resolve alert'); }
  };

  return (
    <div className="min-h-screen bg-animated-gradient relative">
      <div className="orb orb-1" /><div className="orb orb-2" />
      <div className="mesh-bg absolute inset-0" />
      <div className="relative z-10 max-w-4xl mx-auto px-5 sm:px-8 pt-28 pb-16">
        <div className="mb-10 animate-slide-up">
          <h1 className="text-2xl sm:text-3xl font-black text-white mb-2">Alert History</h1>
          <p className="text-gray-400 text-sm sm:text-base">All your emergency alerts in one place</p>
        </div>

        {alerts.length === 0 && !loading ? (
          <div className="glass-card rounded-2xl p-10 sm:p-12 text-center animate-scale-in">
            <Shield className="h-14 w-14 sm:h-16 sm:w-16 text-gray-600 mx-auto mb-6" />
            <h2 className="text-xl font-bold text-white mb-3">No alerts yet</h2>
            <p className="text-gray-400">Your emergency alert history will appear here</p>
          </div>
        ) : (
          <div className="space-y-3 sm:space-y-4">
            {alerts.map((alert, i) => (
              <div key={alert.id} className="glass-card card-shine rounded-2xl overflow-hidden animate-slide-up" style={{ animationDelay: `${i * 0.1}s` }}>
                <div className="p-5 sm:p-6 flex items-center gap-4 sm:gap-5 cursor-pointer" onClick={() => setExpanded(expanded === alert.id ? null : alert.id)}>
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 ${alert.status === 'active' ? 'bg-red-500/20' : 'bg-green-500/20'}`}>
                    {alert.status === 'active' ? <AlertTriangle className="text-red-400" size={22} /> : <CheckCircle className="text-green-400" size={22} />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="text-base sm:text-lg font-bold text-white">SOS Alert</h3>
                      <span className={`px-3 py-0.5 rounded-full text-xs font-bold ${alert.status === 'active' ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
                        {alert.status}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-xs sm:text-sm text-gray-400 mt-1">
                      <Clock size={14} className="flex-shrink-0" />
                      <span className="truncate">{new Date(alert.createdAt).toLocaleString()}</span>
                    </div>
                  </div>
                  {expanded === alert.id ? <ChevronUp className="text-gray-500 flex-shrink-0" /> : <ChevronDown className="text-gray-500 flex-shrink-0" />}
                </div>

                {expanded === alert.id && (
                  <div className="px-5 sm:px-6 pb-6 border-t border-white/5 pt-4 space-y-3 slide-in">
                    {alert.message && <p className="text-gray-300 text-sm"><span className="text-gray-500">Message:</span> {alert.message}</p>}
                    {alert.latitude && (
                      <div className="flex items-center gap-2 text-sm text-gray-400">
                        <MapPin size={14} className="text-emerald-400 flex-shrink-0" />
                        <span>{alert.latitude.toFixed(4)}, {alert.longitude.toFixed(4)}</span>
                        <a href={alert.locationUrl} target="_blank" rel="noopener noreferrer" className="text-emerald-400 hover:text-emerald-300 ml-2 font-medium">Open Map</a>
                      </div>
                    )}
                    {alert.recipients && alert.recipients.length > 0 && (
                      <div>
                        <p className="text-xs text-gray-500 mb-2">Contacts Notified:</p>
                        <div className="flex flex-wrap gap-2">
                          {alert.recipients.map((r) => (
                            <span key={r.id} className="glass px-3 py-1 rounded-full text-xs text-gray-300">{r.contact?.name || 'Unknown'}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {alert.status === 'active' && (
                      <button onClick={() => resolveAlert(alert.id)}
                        className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-5 py-2 rounded-xl font-bold text-sm hover:shadow-lg mt-2">
                        Mark as Resolved
                      </button>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default History;
