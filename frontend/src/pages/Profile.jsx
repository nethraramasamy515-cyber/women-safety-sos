import { useAuth } from '../context/AuthContext';
import { User, Mail, Shield, Calendar, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Profile = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => { logout(); navigate('/'); };

  return (
    <div className="min-h-screen bg-animated-gradient relative">
      <div className="orb orb-1" /><div className="orb orb-2" />
      <div className="mesh-bg absolute inset-0" />
      <div className="relative z-10 max-w-lg mx-auto px-5 sm:px-8 pt-28 pb-16">
        <div className="glass-card rounded-3xl p-8 sm:p-10 text-center animate-scale-in">
          <div className="w-24 h-24 rounded-full bg-gradient-to-br from-emerald-500 to-green-700 flex items-center justify-center mx-auto mb-6 shadow-lg shadow-emerald-700/30">
            <span className="text-4xl font-black text-white">{user?.name?.[0]?.toUpperCase() || 'U'}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white mb-2">{user?.name || 'User'}</h1>
          <p className="text-gray-400 flex items-center justify-center gap-2 mb-8 text-sm sm:text-base">
            <Mail size={16} className="text-emerald-400 flex-shrink-0" /> <span className="truncate">{user?.email || 'user@example.com'}</span>
          </p>

          <div className="space-y-3 mb-8 text-left">
            <div className="glass rounded-xl p-4 flex items-center gap-4">
              <Shield className="text-emerald-400 flex-shrink-0" size={20} />
              <div>
                <p className="text-gray-500 text-xs">Role</p>
                <p className="text-white font-medium capitalize">{user?.role || 'User'}</p>
              </div>
            </div>
            <div className="glass rounded-xl p-4 flex items-center gap-4">
              <Calendar className="text-emerald-400 flex-shrink-0" size={20} />
              <div>
                <p className="text-gray-500 text-xs">Joined</p>
                <p className="text-white font-medium">{user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A'}</p>
              </div>
            </div>
          </div>

          <button onClick={handleLogout}
            className="w-full glass border border-red-500/30 text-red-400 py-4 rounded-xl font-bold text-lg hover:bg-red-500/10 transition-all flex items-center justify-center gap-2">
            <LogOut size={20} /> Sign Out
          </button>
        </div>
      </div>
    </div>
  );
};

export default Profile;
