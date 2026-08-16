import { useState, useEffect } from 'react';
import { contactsAPI } from '../services/api';
import { UserPlus, Phone, Trash2, Edit, X, Users, Heart } from 'lucide-react';
import toast from 'react-hot-toast';

const Contacts = () => {
  const [contacts, setContacts] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name: '', phone: '', relationship: '' });
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadContacts(); }, []);

  const loadContacts = async () => {
    try { const { data } = await contactsAPI.getAll(); setContacts(data.contacts); }
    catch (err) { toast.error('Failed to load contacts'); }
    finally { setLoading(false); }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editing) { await contactsAPI.update(editing.id, form); toast.success('Contact updated!'); }
      else { await contactsAPI.create(form); toast.success('Contact added!'); }
      setShowModal(false); setEditing(null); setForm({ name: '', phone: '', relationship: '' }); loadContacts();
    } catch (err) { toast.error(err.response?.data?.message || 'Operation failed'); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Remove this contact?')) return;
    try { await contactsAPI.delete(id); toast.success('Contact removed'); loadContacts(); }
    catch (err) { toast.error('Failed to remove contact'); }
  };

  const openEdit = (c) => { setEditing(c); setForm({ name: c.name, phone: c.phone, relationship: c.relationship || '' }); setShowModal(true); };

  return (
    <div className="min-h-screen bg-animated-gradient relative">
      <div className="orb orb-1" /><div className="orb orb-2" />
      <div className="mesh-bg absolute inset-0" />
      <div className="relative z-10 max-w-4xl mx-auto px-5 sm:px-8 pt-28 pb-16">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-10 animate-slide-up">
          <div>
            <h1 className="text-2xl sm:text-3xl font-black text-white mb-2">Emergency Contacts</h1>
            <p className="text-gray-400 text-sm sm:text-base">People who'll be notified when you press SOS</p>
          </div>
          <button onClick={() => { setEditing(null); setForm({ name: '', phone: '', relationship: '' }); setShowModal(true); }}
            className="btn-gradient text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-emerald-900/30 w-full sm:w-auto justify-center">
            <span className="relative z-10 flex items-center gap-2"><UserPlus size={18} /> Add Contact</span>
          </button>
        </div>

        {contacts.length === 0 && !loading ? (
          <div className="glass-card rounded-2xl p-10 sm:p-12 text-center animate-scale-in">
            <Heart className="h-14 w-14 sm:h-16 sm:w-16 text-gray-600 mx-auto mb-6" />
            <h2 className="text-xl font-bold text-white mb-3">No contacts yet</h2>
            <p className="text-gray-400 mb-6">Add your first emergency contact to stay protected</p>
            <button onClick={() => setShowModal(true)}
              className="btn-gradient text-white px-8 py-3 rounded-xl font-bold inline-flex items-center gap-2">
              <span className="relative z-10 flex items-center gap-2"><UserPlus size={18} /> Add Your First Contact</span>
            </button>
          </div>
        ) : (
          <div className="grid gap-4">
            {contacts.map((c, i) => (
              <div key={c.id} className="glass-card card-shine rounded-2xl p-5 sm:p-6 flex items-center gap-4 sm:gap-5 animate-slide-up" style={{ animationDelay: `${i * 0.1}s` }}>
                <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-full bg-gradient-to-br from-emerald-500 to-green-700 flex items-center justify-center flex-shrink-0 shadow-lg">
                  <span className="text-lg sm:text-xl font-black text-white">{c.name[0].toUpperCase()}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-base sm:text-lg font-bold text-white truncate">{c.name}</h3>
                  <div className="flex items-center gap-2 text-xs sm:text-sm text-gray-400">
                    <Phone size={14} className="flex-shrink-0" /> <span className="truncate">{c.phone}</span>
                  </div>
                  {c.relationship && <p className="text-xs text-gray-500 mt-1 capitalize">{c.relationship}</p>}
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  <button onClick={() => openEdit(c)} className="p-2.5 sm:p-3 glass rounded-xl text-gray-400 hover:text-emerald-400 hover:border-emerald-500/30 transition-all">
                    <Edit size={16} />
                  </button>
                  <button onClick={() => handleDelete(c.id)} className="p-2.5 sm:p-3 glass rounded-xl text-gray-400 hover:text-red-400 hover:border-red-500/30 transition-all">
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {showModal && (
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center px-5 animate-fade-in">
            <div className="glass-card rounded-2xl p-6 sm:p-8 max-w-md w-full animate-scale-in">
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-xl font-black text-white">{editing ? 'Edit Contact' : 'Add Contact'}</h2>
                <button onClick={() => { setShowModal(false); setEditing(null); }} className="text-gray-400 hover:text-white transition-colors"><X size={24} /></button>
              </div>
              <form onSubmit={handleSubmit} className="space-y-4">
                <input type="text" placeholder="Full name" required value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}
                  className="w-full px-4 py-3 glass rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50" />
                <input type="tel" placeholder="Phone number" required value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })}
                  className="w-full px-4 py-3 glass rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50" />
                <select value={form.relationship} onChange={e => setForm({ ...form, relationship: e.target.value })}
                  className="w-full px-4 py-3 glass rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/50 bg-transparent">
                  <option value="" className="bg-gray-900">Select relationship</option>
                  {['Mother', 'Father', 'Sister', 'Brother', 'Friend', 'Spouse', 'Other'].map(r => (
                    <option key={r} value={r} className="bg-gray-900">{r}</option>
                  ))}
                </select>
                <button type="submit" className="w-full btn-gradient text-white py-3 rounded-xl font-bold shadow-lg shadow-emerald-900/30">
                  <span className="relative z-10">{editing ? 'Update Contact' : 'Add Contact'}</span>
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Contacts;
