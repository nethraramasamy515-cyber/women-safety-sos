import { useState, useEffect } from 'react';
import { policeAPI } from '../services/api';
import { MapPin, Phone, Clock, Navigation, Search, Shield } from 'lucide-react';
import toast from 'react-hot-toast';

const PoliceStations = () => {
  const [stations, setStations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    navigator.geolocation.getCurrentPosition(
      (pos) => loadNearest(pos.coords.latitude, pos.coords.longitude),
      () => loadAll()
    );
  }, []);

  const loadNearest = async (lat, lon) => {
    try { const { data } = await policeAPI.nearest(lat, lon); setStations(data.stations); }
    catch { loadAll(); }
    finally { setLoading(false); }
  };

  const loadAll = async () => {
    try { const { data } = await policeAPI.getAll(); setStations(data.stations); }
    catch (err) { toast.error('Failed to load stations'); }
    finally { setLoading(false); }
  };

  const filtered = stations.filter(s => s.name.toLowerCase().includes(searchTerm.toLowerCase()) || s.address?.toLowerCase().includes(searchTerm.toLowerCase()));

  return (
    <div className="min-h-screen bg-animated-gradient relative">
      <div className="orb orb-1" /><div className="orb orb-2" />
      <div className="mesh-bg absolute inset-0" />
      <div className="relative z-10 max-w-4xl mx-auto px-5 sm:px-8 pt-28 pb-16">
        <div className="mb-10 animate-slide-up">
          <h1 className="text-2xl sm:text-3xl font-black text-white mb-2">Police Stations</h1>
          <p className="text-gray-400 text-sm sm:text-base">Nearest stations to your location</p>
        </div>

        <div className="relative mb-8 animate-slide-up delay-100">
          <Search size={20} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" />
          <input type="text" placeholder="Search stations..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-12 pr-4 py-4 glass rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all" />
        </div>

        <div className="space-y-4">
          {filtered.map((station, i) => (
            <div key={station.id} className="glass-card card-shine rounded-2xl p-5 sm:p-6 animate-slide-up" style={{ animationDelay: `${i * 0.1}s` }}>
              <div className="flex items-start gap-4 sm:gap-5">
                <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-xl bg-gradient-to-br from-emerald-500 to-green-700 flex items-center justify-center flex-shrink-0 shadow-lg">
                  <Shield className="h-6 w-6 sm:h-7 sm:w-7 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-base sm:text-lg font-bold text-white mb-1">{station.name}</h3>
                  {station.address && (
                    <div className="flex items-start gap-2 text-xs sm:text-sm text-gray-400 mb-2">
                      <MapPin size={14} className="text-emerald-400 flex-shrink-0 mt-0.5" /> <span className="break-words">{station.address}</span>
                    </div>
                  )}
                  {station.phone && (
                    <div className="flex items-center gap-2 text-xs sm:text-sm text-gray-400 mb-2">
                      <Phone size={14} className="text-emerald-400 flex-shrink-0" />
                      <a href={`tel:${station.phone}`} className="hover:text-emerald-300 transition-colors">{station.phone}</a>
                    </div>
                  )}
                  {station.hours && (
                    <div className="flex items-center gap-2 text-xs sm:text-sm text-gray-400">
                      <Clock size={14} className="text-emerald-400 flex-shrink-0" /> {station.hours}
                    </div>
                  )}
                </div>
                {station.latitude && station.longitude && (
                  <a href={`https://www.google.com/maps/dir/?api=1&destination=${station.latitude},${station.longitude}`}
                    target="_blank" rel="noopener noreferrer"
                    className="p-2.5 sm:p-3 glass rounded-xl text-emerald-400 hover:bg-emerald-500/10 transition-all flex-shrink-0" title="Get directions">
                    <Navigation size={18} />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>

        {filtered.length === 0 && !loading && (
          <div className="glass-card rounded-2xl p-10 sm:p-12 text-center">
            <Shield className="h-12 w-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">No stations found</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PoliceStations;
