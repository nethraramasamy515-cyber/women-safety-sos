import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { sosAPI, contactsAPI } from '../services/api';
import { AlertTriangle, MapPin, X, CheckCircle, Loader2, Shield } from 'lucide-react';
import toast from 'react-hot-toast';

const SOSTrigger = () => {
  const [countdown, setCountdown] = useState(null);
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [location, setLocation] = useState(null);
  const [contacts, setContacts] = useState([]);
  const [contactsNotified, setContactsNotified] = useState(0);
  const timerRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    navigator.geolocation.getCurrentPosition(
      (pos) => setLocation({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
      () => toast.error('Location access is required for SOS alerts')
    );
    contactsAPI.getAll().then((res) => setContacts(res.data.contacts)).catch(() => {});
  }, []);

  const triggerSOS = () => {
    if (contacts.length === 0) { toast.error('Add at least one emergency contact first!'); navigate('/contacts'); return; }
    setCountdown(5);
    timerRef.current = setInterval(() => {
      setCountdown((prev) => { if (prev <= 1) { clearInterval(timerRef.current); sendSOS(); return null; } return prev - 1; });
    }, 1000);
  };

  const cancelSOS = () => { clearInterval(timerRef.current); setCountdown(null); toast.success('SOS cancelled'); };

  const sendSOS = async () => {
    setSending(true);
    try {
      if (!location) { toast.error('Getting location... Please try again'); setSending(false); return; }
      const { data } = await sosAPI.trigger({ latitude: location.lat, longitude: location.lon, message: 'SOS! I need immediate help!' });
      setContactsNotified(data.contactsNotified); setSent(true); toast.success('SOS alert sent!');
    } catch (err) { toast.error(err.response?.data?.message || 'Failed to send SOS'); }
    finally { setSending(false); }
  };

  if (sent) {
    return (
      <div className="min-h-screen bg-animated-gradient flex items-center justify-center px-5 sm:px-8 relative">
        <div className="orb orb-1" /><div className="orb orb-2" />
        <div className="relative z-10 max-w-md w-full text-center animate-bounce-in">
          <div className="glass-card rounded-3xl p-8 sm:p-12">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center mx-auto mb-8 shadow-lg shadow-green-600/30 animate-heartbeat">
              <CheckCircle className="h-12 w-12 text-white" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white mb-4">SOS Alert Sent!</h1>
            <p className="text-gray-400 mb-8 text-base sm:text-lg leading-relaxed">
              Your <span className="text-emerald-400 font-bold">{contactsNotified}</span> emergency contact(s) have been notified.
            </p>
            {location && (
              <div className="glass rounded-xl p-5 mb-8">
                <div className="flex items-center justify-center gap-2 text-sm text-gray-300">
                  <MapPin size={16} className="text-emerald-400 flex-shrink-0" />
                  <span>{location.lat.toFixed(4)}, {location.lon.toFixed(4)}</span>
                </div>
                <a href={`https://www.google.com/maps?q=${location.lat},${location.lon}`} target="_blank" rel="noopener noreferrer"
                  className="text-emerald-400 text-sm font-medium hover:text-emerald-300 transition-colors mt-2 inline-block">Open in Google Maps</a>
              </div>
            )}
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
              <button onClick={() => { setSent(false); navigate('/dashboard'); }}
                className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 text-white py-4 rounded-xl font-bold text-lg hover:shadow-lg transition-all">I'm Safe Now</button>
              <button onClick={() => { setSent(false); navigate('/dashboard'); }}
                className="flex-1 glass border-emerald-500/30 text-emerald-400 py-4 rounded-xl font-bold text-lg hover:bg-emerald-500/10 transition-all">False Alarm</button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-animated-gradient flex items-center justify-center px-5 sm:px-8 relative">
      <div className="orb orb-1" /><div className="orb orb-2" /><div className="orb orb-4" />
      <div className="relative z-10 max-w-md w-full text-center">
        {countdown !== null ? (
          <div className="animate-scale-in">
            <div className="glass-card rounded-3xl p-8 sm:p-12">
              <div className="relative inline-block mb-8">
                <div className="absolute inset-0 bg-red-500/20 blur-3xl rounded-full animate-ping" />
                <span className="relative font-black text-red-500" style={{ fontSize: 'clamp(5rem, 15vw, 8rem)', lineHeight: 1, animation: 'countPulse 1s ease-in-out infinite' }}>{countdown}</span>
              </div>
              <h2 className="text-2xl font-black text-white mb-3">Sending SOS...</h2>
              <p className="text-gray-400 mb-10 text-lg">All emergency contacts will be notified</p>
              <button onClick={cancelSOS}
                className="inline-flex items-center gap-2 glass border border-white/20 text-white px-10 py-5 rounded-2xl font-bold hover:bg-red-500/20 hover:border-red-500/30 transition-all text-lg">
                <X size={24} /> Cancel SOS
              </button>
            </div>
          </div>
        ) : sending ? (
          <div className="glass-card rounded-3xl p-8 sm:p-12 animate-scale-in">
            <Loader2 className="h-16 w-16 sm:h-20 sm:w-20 text-emerald-400 mx-auto mb-6 animate-spin" />
            <h2 className="text-2xl font-black text-white mb-3">Sending SOS Alert...</h2>
            <p className="text-gray-400 text-lg">Notifying your emergency contacts</p>
          </div>
        ) : (
          <div className="animate-slide-up">
            <div className="glass-card rounded-3xl p-8 sm:p-12">
              <div className="relative inline-block mb-8">
                <Shield className="h-14 w-14 sm:h-16 sm:w-16 text-emerald-400" />
                <div className="absolute inset-0 bg-emerald-500/30 blur-2xl rounded-full" />
              </div>
              <h1 className="text-3xl sm:text-4xl font-black text-white mb-4">Emergency SOS</h1>
              <p className="text-gray-400 mb-3 text-base sm:text-lg">Press the button to send an SOS alert</p>
              <p className="text-sm text-gray-500 mb-10 sm:mb-12">
                Your <span className="text-emerald-400 font-bold">{contacts.length}</span> emergency contacts will be notified instantly
              </p>

              {!location && (
                <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 mb-8 text-sm text-emerald-400 animate-pulse">
                  <MapPin size={16} className="inline mr-1" />
                  Getting your location... Please allow location access.
                </div>
              )}

              <button onClick={triggerSOS} disabled={!location}
                className="relative inline-flex items-center justify-center group disabled:opacity-50 disabled:cursor-not-allowed mb-8">
                <div className="absolute w-40 h-40 sm:w-48 sm:h-48 rounded-full border-2 border-red-500/30 sos-ring" />
                <div className="absolute w-40 h-40 sm:w-48 sm:h-48 rounded-full border-2 border-red-500/20 sos-ring" />
                <div className="absolute w-40 h-40 sm:w-48 sm:h-48 rounded-full border-2 border-red-500/10 sos-ring" />
                <div className="relative w-40 h-40 sm:w-48 sm:h-48 rounded-full bg-gradient-to-br from-red-600 via-red-700 to-red-900 flex items-center justify-center text-white text-3xl font-black sos-glow group-hover:scale-105 transition-transform duration-300 cursor-pointer">
                  <div className="text-center">
                    <AlertTriangle className="h-12 w-12 sm:h-14 sm:w-14 mx-auto mb-2" />
                    SOS
                  </div>
                </div>
              </button>

              <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
                <MapPin size={14} className="text-emerald-400 flex-shrink-0" />
                {location ? `Location: ${location.lat.toFixed(4)}, ${location.lon.toFixed(4)}` : 'Acquiring location...'}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SOSTrigger;
