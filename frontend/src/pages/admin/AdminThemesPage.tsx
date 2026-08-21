import { useEffect, useState } from 'react';
import { adminGetThemes, adminCreateTheme, adminUpdateTheme, adminDeleteTheme } from '../../lib/api';
import type { Theme } from '../../types';
import { formatPrice } from '../../lib/utils';
import { Plus } from 'lucide-react';

export default function AdminThemesPage() {
  const [themes, setThemes] = useState<Theme[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [editingTheme, setEditingTheme] = useState<Theme | null>(null);

  // Form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [promptTemplate, setPromptTemplate] = useState('');
  const [priceGbp, setPriceGbp] = useState('0');
  const [maxRegenerations, setMaxRegenerations] = useState(3);
  const [active, setActive] = useState(true);

  const fetchThemes = () => {
    adminGetThemes().then(res => setThemes(res.data)).catch(console.error);
  };

  useEffect(() => {
    fetchThemes();
  }, []);

  const openModal = (theme?: Theme) => {
    if (theme) {
      setEditingTheme(theme);
      setName(theme.name);
      setDescription(theme.description);
      setPromptTemplate(theme.prompt_template || '');
      setPriceGbp((theme.price_cents / 100).toString());
      setMaxRegenerations(theme.max_regenerations ?? 3);
      setActive(theme.active ?? true);
    } else {
      setEditingTheme(null);
      setName('');
      setDescription('');
      setPromptTemplate('');
      setPriceGbp('0');
      setMaxRegenerations(3);
      setActive(true);
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingTheme(null);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    const data: Partial<Theme> = {
      name,
      description,
      prompt_template: promptTemplate,
      price_cents: Math.round(parseFloat(priceGbp) * 100),
      max_regenerations: maxRegenerations,
      active
    };

    try {
      if (editingTheme) {
        await adminUpdateTheme(editingTheme.id, data);
      } else {
        await adminCreateTheme(data);
      }
      closeModal();
      fetchThemes();
    } catch (err) {
      console.error(err);
      alert('Error saving theme');
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this theme?')) {
      try {
        await adminDeleteTheme(id);
        fetchThemes();
      } catch (err) {
        console.error(err);
        alert('Error deleting theme');
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Themes</h1>
        <button onClick={() => openModal()} className="flex items-center gap-2 bg-brand-gold text-gray-900 px-4 py-2 rounded-lg font-medium hover:bg-brand-amber">
          <Plus className="w-4 h-4" /> Add Theme
        </button>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {themes.map(theme => (
          <div key={theme.id} className="bg-gray-800 rounded-lg p-6 border border-gray-700 flex flex-col">
            <div className="flex justify-between items-start mb-4">
              <h3 className="font-bold text-lg text-white">{theme.name}</h3>
              <span className={`text-xs px-2 py-1 rounded-full ${theme.active ? 'bg-green-900/50 text-green-400' : 'bg-gray-700 text-gray-400'}`}>
                {theme.active ? 'Active' : 'Inactive'}
              </span>
            </div>
            <p className="text-sm text-gray-400 flex-1 mb-4">{theme.description}</p>
            <div className="flex justify-between items-center text-sm">
              <span className="text-white font-medium">{formatPrice(theme.price_cents)}</span>
              <div className="flex gap-3">
                <button onClick={() => openModal(theme)} className="text-brand-gold hover:underline">Edit</button>
                <button onClick={() => handleDelete(theme.id)} className="text-red-500 hover:underline">Delete</button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-gray-900 p-6 rounded-lg w-full max-w-lg border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4">{editingTheme ? 'Edit Theme' : 'Add Theme'}</h2>
            <form onSubmit={handleSave} className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Name</label>
                <input required type="text" value={name} onChange={e => setName(e.target.value)} className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white" />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Description</label>
                <textarea required value={description} onChange={e => setDescription(e.target.value)} className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white h-20" />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Prompt Template</label>
                <textarea required value={promptTemplate} onChange={e => setPromptTemplate(e.target.value)} className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white h-24" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Price (£)</label>
                  <input required type="number" step="0.01" value={priceGbp} onChange={e => setPriceGbp(e.target.value)} className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white" />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Max Regenerations</label>
                  <input required type="number" value={maxRegenerations} onChange={e => setMaxRegenerations(parseInt(e.target.value))} className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white" />
                </div>
              </div>
              <div className="flex items-center gap-2 mt-4">
                <input type="checkbox" id="active" checked={active} onChange={e => setActive(e.target.checked)} className="w-4 h-4 rounded bg-gray-800 border-gray-700 text-brand-gold focus:ring-brand-gold" />
                <label htmlFor="active" className="text-sm text-gray-400">Active</label>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button type="button" onClick={closeModal} className="px-4 py-2 text-gray-400 hover:text-white">Cancel</button>
                <button type="submit" className="bg-brand-gold text-gray-900 px-4 py-2 rounded font-medium hover:bg-brand-amber">Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
