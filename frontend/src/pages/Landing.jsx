import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Shield, AlertTriangle, MapPin, Phone, Users, ChevronRight, Heart } from 'lucide-react';

const features = [
  { icon: AlertTriangle, title: 'Instant SOS', desc: 'One-tap emergency alert with live GPS location to all your contacts', gradient: 'from-red-600 to-red-800' },
  { icon: Users, title: 'Emergency Contacts', desc: 'Add and manage your trusted circle who get notified instantly', gradient: 'from-emerald-600 to-green-800' },
  { icon: MapPin, title: 'Live Tracking', desc: 'Real-time location sharing during emergencies with Google Maps', gradient: 'from-green-600 to-emerald-800' },
  { icon: Phone, title: 'Police Stations', desc: 'Find nearby police stations and women helpline numbers instantly', gradient: 'from-emerald-700 to-green-900' },
];

const Landing = () => {
  const [visible, setVisible] = useState(false);
  const heroRef = useRef(null);

  useEffect(() => {
    setVisible(true);
    const observer = new IntersectionObserver(([e]) => e.isIntersecting && setVisible(true), { threshold: 0.1 });
    if (heroRef.current) observer.observe(heroRef.current);
    return () => observer.disconnect();
  }, []);

  return (
    <div className="min-h-screen bg-animated-gradient relative overflow-hidden">
      <div className="orb orb-1" /><div className="orb orb-2" /><div className="orb orb-3" /><div className="orb orb-5" />
      <div className="mesh-bg absolute inset-0" />

      <div className="relative z-10 pt-32 pb-24 px-5 sm:px-8 lg:px-12">
        {/* HERO */}
        <div ref={heroRef} className="max-w-5xl mx-auto text-center mb-32">
          <div className={`transition-all duration-1000 ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
            <div className="relative inline-block mb-10">
              <div className="w-28 h-28 rounded-full bg-gradient-to-br from-emerald-500 to-green-700 flex items-center justify-center mx-auto shadow-lg shadow-emerald-700/30 animate-heartbeat">
                <Shield className="h-14 w-14 text-white" />
              </div>
              <div className="absolute inset-0 bg-emerald-500/20 blur-3xl rounded-full animate-ping" />
            </div>

            <h1 className="text-5xl sm:text-6xl md:text-8xl font-black text-white mb-8 leading-tight">
              Women's <span className="text-gradient">Safety</span><br />
              SOS <span className="text-gradient">Alert</span>
            </h1>
            <p className="text-lg sm:text-xl md:text-2xl text-gray-400 mb-12 max-w-2xl mx-auto leading-relaxed">
              One tap to send an emergency alert with your live location to all your trusted contacts
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-5">
              <Link to="/register"
                className="btn-gradient text-white px-10 py-5 rounded-2xl font-bold text-lg inline-flex items-center gap-3 shadow-xl shadow-emerald-900/30 w-full sm:w-auto justify-center">
                <span className="relative z-10 flex items-center gap-3">Get Started Free <ChevronRight size={22} /></span>
              </Link>
              <Link to="/helplines"
                className="glass border-emerald-500/30 text-emerald-400 px-10 py-5 rounded-2xl font-bold text-lg hover:bg-emerald-500/10 transition-all w-full sm:w-auto text-center">
                Emergency Helplines
              </Link>
            </div>
          </div>
        </div>

        {/* FEATURES */}
        <div className="max-w-6xl mx-auto mb-32">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-white mb-4">
              Everything you need for <span className="text-gradient">safety</span>
            </h2>
            <p className="text-gray-400 text-lg">Powerful features designed to keep you safe</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8">
            {features.map((f, i) => (
              <div key={i} className={`glass-card card-shine rounded-3xl p-8 lg:p-10 opacity-0 animate-slide-up`} style={{ animationDelay: `${i * 0.15}s` }}>
                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${f.gradient} flex items-center justify-center mb-6 shadow-lg`}>
                  <f.icon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">{f.title}</h3>
                <p className="text-gray-400 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* HOW IT WORKS */}
        <div className="max-w-4xl mx-auto mb-32">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-white mb-4">
              How it <span className="text-gradient">works</span>
            </h2>
            <p className="text-gray-400 text-lg">Simple, fast, and effective in 3 steps</p>
          </div>
          <div className="space-y-6 lg:space-y-8">
            {[
              { step: '1', title: 'Add Contacts', desc: 'Add your trusted emergency contacts — family, friends, or anyone you trust.' },
              { step: '2', title: 'Press SOS', desc: 'When in danger, press and hold the big SOS button for 5 seconds.' },
              { step: '3', title: 'Help is On The Way', desc: 'All your contacts are instantly notified with your live GPS location.' },
            ].map((item, i) => (
              <div key={i} className={`glass-card rounded-2xl p-8 flex flex-col sm:flex-row items-center gap-6 sm:gap-8 opacity-0 animate-slide-up`} style={{ animationDelay: `${i * 0.2}s` }}>
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-emerald-500 to-green-700 flex items-center justify-center flex-shrink-0 shadow-lg shadow-emerald-800/30">
                  <span className="text-3xl font-black text-white">{item.step}</span>
                </div>
                <div className="text-center sm:text-left">
                  <h3 className="text-xl font-bold text-white mb-2">{item.title}</h3>
                  <p className="text-gray-400 leading-relaxed">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="max-w-4xl mx-auto text-center">
          <div className="glass-card rounded-3xl p-10 sm:p-16 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-700/10 to-transparent" />
            <div className="relative z-10">
              <Heart className="h-14 w-14 text-emerald-400 mx-auto mb-6 animate-heartbeat" />
              <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-white mb-6">Your safety matters</h2>
              <p className="text-gray-400 text-lg mb-10 max-w-lg mx-auto leading-relaxed">
                Don't wait for help. Take control of your safety today. It's free, secure, and could save your life.
              </p>
              <Link to="/register"
                className="btn-gradient text-white px-12 py-5 rounded-2xl font-bold text-lg inline-flex items-center gap-3 shadow-xl shadow-emerald-900/30">
                <span className="relative z-10 flex items-center gap-3">Create Free Account <ChevronRight size={22} /></span>
              </Link>
            </div>
          </div>
        </div>

        {/* FOOTER */}
        <div className="max-w-4xl mx-auto mt-24 text-center">
          <div className="glass rounded-2xl p-8">
            <div className="flex items-center justify-center gap-2 text-emerald-400 font-bold mb-2">
              <Shield size={20} />
              <span>Women's Safety SOS</span>
            </div>
            <p className="text-gray-500 text-sm mb-4">Designed to empower women with instant emergency response</p>
            <div className="flex flex-wrap items-center justify-center gap-4 sm:gap-6 text-sm text-gray-600">
              <a href="#" className="hover:text-emerald-400 transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-emerald-400 transition-colors">Terms of Service</a>
              <a href="tel:1091" className="hover:text-emerald-400 transition-colors">Women Helpline: 1091</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Landing;
