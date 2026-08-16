import { Phone, ExternalLink, Shield, AlertTriangle, Heart } from 'lucide-react';

const helplines = [
  { name: 'Women Helpline', number: '1091', desc: '24/7 Women in Distress', gradient: 'from-emerald-600 to-green-700' },
  { name: 'Police', number: '100', desc: 'Immediate Police Assistance', gradient: 'from-red-600 to-red-800' },
  { name: 'Emergency', number: '112', desc: 'National Emergency Number', gradient: 'from-orange-600 to-red-700' },
  { name: 'Child Helpline', number: '1098', desc: 'Child in Distress', gradient: 'from-emerald-700 to-green-800' },
  { name: 'Domestic Violence', number: '181', desc: 'Women Domestic Violence Helpline', gradient: 'from-green-600 to-emerald-800' },
  { name: 'National Commission Women', number: '7827-170-170', desc: 'NCW Women Helpline', gradient: 'from-emerald-600 to-green-900' },
];

const tips = [
  'Always keep your phone charged and emergency numbers saved.',
  'Share your live location with trusted contacts when traveling.',
  'Learn basic self-defense techniques.',
  'Trust your instincts — if something feels wrong, leave immediately.',
  'Keep emergency cash and documents accessible.',
  'Install safety apps and keep emergency contacts on speed dial.',
];

const Helplines = () => (
  <div className="min-h-screen bg-animated-gradient relative">
    <div className="orb orb-1" /><div className="orb orb-2" /><div className="orb orb-5" />
    <div className="mesh-bg absolute inset-0" />
    <div className="relative z-10 max-w-4xl mx-auto px-5 sm:px-8 pt-28 pb-16">
      <div className="mb-10 animate-slide-up">
        <h1 className="text-2xl sm:text-3xl font-black text-white mb-2">Emergency Helplines</h1>
        <p className="text-gray-400 text-sm sm:text-base">Important numbers to keep you safe</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-14">
        {helplines.map((h, i) => (
          <a key={i} href={`tel:${h.number}`}
            className="glass-card card-shine rounded-2xl p-5 sm:p-6 flex items-center gap-4 sm:gap-5 animate-slide-up group" style={{ animationDelay: `${i * 0.1}s` }}>
            <div className={`w-14 h-14 sm:w-16 sm:h-16 rounded-2xl bg-gradient-to-br ${h.gradient} flex items-center justify-center flex-shrink-0 shadow-lg group-hover:scale-110 transition-transform`}>
              <Phone className="h-7 w-7 sm:h-8 sm:w-8 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-base sm:text-lg font-bold text-white mb-1 group-hover:text-emerald-400 transition-colors">{h.name}</h3>
              <p className="text-gray-400 text-xs sm:text-sm mb-2">{h.desc}</p>
              <p className="text-emerald-400 font-black text-lg sm:text-xl">{h.number}</p>
            </div>
            <ExternalLink size={16} className="text-gray-600 group-hover:text-emerald-400 transition-colors flex-shrink-0" />
          </a>
        ))}
      </div>

      <div className="glass-card rounded-3xl p-8 sm:p-10 mb-10 animate-slide-up">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-green-700 flex items-center justify-center shadow-lg">
            <Shield className="h-6 w-6 text-white" />
          </div>
          <h2 className="text-xl sm:text-2xl font-black text-white">Safety Tips</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
          {tips.map((tip, i) => (
            <div key={i} className="glass rounded-xl p-4 flex items-start gap-3">
              <AlertTriangle size={16} className="text-emerald-400 mt-0.5 flex-shrink-0" />
              <p className="text-gray-300 text-sm leading-relaxed">{tip}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="glass-card rounded-2xl p-8 text-center animate-scale-in">
        <Heart className="h-10 w-10 text-emerald-400 mx-auto mb-4 animate-heartbeat" />
        <p className="text-white font-bold mb-2">You are not alone</p>
        <p className="text-gray-400 text-sm">If you or someone you know is in danger, don't hesitate to call for help.</p>
      </div>
    </div>
  </div>
);

export default Helplines;
