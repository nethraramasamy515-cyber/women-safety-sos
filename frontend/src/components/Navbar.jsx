import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Shield, LogOut, Menu, X, Home, Users, Clock, MapPin, Phone, LayoutDashboard, User } from 'lucide-react';
import { useState } from 'react';

const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);

  const handleLogout = () => { logout(); navigate('/'); setIsOpen(false); };

  const navLink = (to, label, icon) => (
    <Link to={to} onClick={() => setIsOpen(false)}
      className={`flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium transition-all duration-300 ${
        location.pathname === to
          ? 'bg-gradient-to-r from-emerald-600 to-green-600 text-white shadow-lg shadow-emerald-700/25'
          : 'text-gray-300 hover:text-white hover:bg-white/10'
      }`}>
      {icon} {label}
    </Link>
  );

  const guestLinks = (
    <>
      {navLink('/', 'Home', <Home size={16} />)}
      {navLink('/helplines', 'Helplines', <Phone size={16} />)}
    </>
  );

  const userLinks = (
    <>
      {navLink('/dashboard', 'Dashboard', <LayoutDashboard size={16} />)}
      {navLink('/contacts', 'Contacts', <Users size={16} />)}
      {navLink('/history', 'History', <Clock size={16} />)}
      {navLink('/police', 'Nearby', <MapPin size={16} />)}
      {navLink('/helplines', 'Helplines', <Phone size={16} />)}
      {navLink('/profile', 'Profile', <User size={16} />)}
      {user?.role === 'admin' && navLink('/admin', 'Admin', <Shield size={16} />)}
    </>
  );

  return (
    <nav className="glass sticky top-0 z-50 border-b border-emerald-500/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="relative">
              <Shield className="h-8 w-8 text-emerald-400 group-hover:text-emerald-300 transition-all duration-300 group-hover:scale-110" />
              <div className="absolute inset-0 bg-emerald-500/30 blur-lg rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </div>
            <span className="text-xl font-extrabold text-gradient">SafeHer</span>
          </Link>

          <div className="hidden lg:flex items-center gap-1">
            {user ? userLinks : guestLinks}
          </div>

          <div className="hidden md:flex items-center gap-3">
            {user ? (
              <>
                <span className="text-sm text-gray-400">
                  Hi, <span className="text-white font-semibold">{user.name}</span>
                </span>
                <button onClick={handleLogout}
                  className="flex items-center gap-1 px-4 py-2 text-sm text-red-400 hover:text-white hover:bg-red-500/20 rounded-xl transition-all duration-300 border border-transparent hover:border-red-500/30">
                  <LogOut size={16} /> Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white hover:bg-white/10 rounded-xl transition-all duration-300">Login</Link>
                <Link to="/register" className="px-5 py-2 text-sm font-bold bg-gradient-to-r from-emerald-600 to-green-600 text-white rounded-xl hover:shadow-lg hover:shadow-emerald-700/25 transition-all duration-300 hover:scale-105">Register</Link>
              </>
            )}
          </div>

          <button onClick={() => setIsOpen(!isOpen)} className="md:hidden p-2 text-gray-400 hover:text-white transition-colors">
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {isOpen && (
        <div className="md:hidden glass border-t border-emerald-500/10 slide-in">
          <div className="px-4 py-4 space-y-1">
            {user ? userLinks : guestLinks}
            <hr className="my-2 border-emerald-500/10" />
            {user ? (
              <button onClick={handleLogout} className="flex items-center gap-2 w-full px-3 py-2 text-red-400 hover:text-white hover:bg-red-500/20 rounded-xl text-sm font-medium transition-all">
                <LogOut size={16} /> Logout
              </button>
            ) : (
              <>
                <Link to="/login" onClick={() => setIsOpen(false)} className="block px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-xl text-sm font-medium transition-all">Login</Link>
                <Link to="/register" onClick={() => setIsOpen(false)} className="block px-3 py-2 bg-gradient-to-r from-emerald-600 to-green-600 text-white rounded-xl text-sm font-bold text-center transition-all">Register</Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
