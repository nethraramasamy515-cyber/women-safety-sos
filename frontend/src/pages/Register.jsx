import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { UserPlus, Mail, Lock, User, Phone, AlertTriangle, Eye, EyeOff } from 'lucide-react';
import toast from 'react-hot-toast';

const Register = () => {
  const [formData, setFormData] = useState({ name: '', email: '', password: '', phone: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { register, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => { if (user) navigate('/dashboard'); }, [user, navigate]);

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register(formData.name, formData.email, formData.password, formData.phone);
      toast.success('Account created!');
      navigate('/dashboard');
    } catch (err) { toast.error(err.response?.data?.message || 'Registration failed'); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-animated-gradient flex items-center justify-center px-5 sm:px-8 relative">
      <div className="orb orb-1" /><div className="orb orb-2" />
      <div className="mesh-bg absolute inset-0" />
      <div className="relative z-10 max-w-md w-full animate-slide-up">
        <div className="glass-card rounded-3xl p-8 sm:p-10">
          <div className="text-center mb-10">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-emerald-500 to-green-700 flex items-center justify-center mx-auto mb-6 shadow-lg shadow-emerald-700/30">
              <UserPlus className="h-10 w-10 text-white" />
            </div>
            <h1 className="text-3xl font-black text-white mb-2">Create Account</h1>
            <p className="text-gray-400">Join us and stay safe with instant alerts</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5">
            <div className="relative group">
              <User size={20} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-emerald-400 transition-colors" />
              <input name="name" type="text" placeholder="Full name" required value={formData.name} onChange={handleChange}
                className="w-full pl-12 pr-4 py-4 glass rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all" />
            </div>
            <div className="relative group">
              <Mail size={20} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-emerald-400 transition-colors" />
              <input name="email" type="email" placeholder="Email address" required value={formData.email} onChange={handleChange}
                className="w-full pl-12 pr-4 py-4 glass rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all" />
            </div>
            <div className="relative group">
              <Phone size={20} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-emerald-400 transition-colors" />
              <input name="phone" type="tel" placeholder="Phone number" required value={formData.phone} onChange={handleChange}
                className="w-full pl-12 pr-4 py-4 glass rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all" />
            </div>
            <div className="relative group">
              <Lock size={20} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-emerald-400 transition-colors" />
              <input name="password" type={showPassword ? 'text' : 'password'} placeholder="Password (min 6 chars)" required minLength={6} value={formData.password} onChange={handleChange}
                className="w-full pl-12 pr-12 py-4 glass rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all" />
              <button type="button" onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-emerald-400 transition-colors">
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            <button type="submit" disabled={loading}
              className="w-full btn-gradient text-white py-4 rounded-xl font-bold text-lg disabled:opacity-50 shadow-lg shadow-emerald-900/30">
              <span className="relative z-10">{loading ? 'Creating account...' : 'Create Account'}</span>
            </button>
          </form>

          <p className="text-center text-gray-400 mt-8">
            Already have an account?{' '}
            <Link to="/login" className="text-emerald-400 font-bold hover:text-emerald-300 transition-colors">Sign in</Link>
          </p>

          <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-3">
            <AlertTriangle size={18} className="text-red-400 flex-shrink-0" />
            <p className="text-sm text-red-300">Emergency? Call <span className="font-bold">1091</span> (Women Helpline) or <span className="font-bold">100</span> (Police)</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
