import React, { useEffect, useState } from 'react';
import AdminSidebar from '../../components/AdminSidebar';
import { adminCourses } from '../../api/adminService';
import { Plus, Pencil, Trash2, X, Search, BookOpen } from 'lucide-react';
import type { AdminCourse } from '../../types';

interface CourseForm {
    code: string;
    name: string;
    level: number;
    semester: number;
    credits: number;
    weight: number;
}

const emptyForm: CourseForm = { code: '', name: '', level: 100, semester: 1, credits: 3, weight: 1 };

const AdminCourses: React.FC = () => {
    const [courses, setCourses] = useState<AdminCourse[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [showModal, setShowModal] = useState(false);
    const [editId, setEditId] = useState<number | null>(null);
    const [form, setForm] = useState<CourseForm>(emptyForm);
    const [formError, setFormError] = useState('');
    const [saving, setSaving] = useState(false);

    const fetchCourses = async () => {
        setLoading(true);
        try {
            const data = await adminCourses.list();
            setCourses(data);
        } catch (e) { console.error(e); }
        finally { setLoading(false); }
    };

    useEffect(() => { fetchCourses(); }, []);

    const filtered = courses.filter(c =>
        c.code.toLowerCase().includes(search.toLowerCase()) ||
        c.name.toLowerCase().includes(search.toLowerCase())
    );

    const openCreate = () => {
        setForm(emptyForm);
        setEditId(null);
        setFormError('');
        setShowModal(true);
    };

    const openEdit = (c: AdminCourse) => {
        setForm({ code: c.code, name: c.name, level: c.level, semester: c.semester, credits: c.credits, weight: c.weight });
        setEditId(c.id);
        setFormError('');
        setShowModal(true);
    };

    const handleSave = async () => {
        setFormError('');
        if (!form.code || !form.name) { setFormError('Code and name are required'); return; }
        if (form.credits < 1 || form.credits > 4) { setFormError('Credits must be 1–4'); return; }
        if (form.weight < 1 || form.weight > 5) { setFormError('Weight must be 1–5'); return; }

        setSaving(true);
        try {
            if (editId) {
                await adminCourses.update(editId, form);
            } else {
                await adminCourses.create(form);
            }
            setShowModal(false);
            fetchCourses();
        } catch (err: any) {
            setFormError(err.message || 'Save failed');
        } finally { setSaving(false); }
    };

    const handleDelete = async (id: number) => {
        if (!confirm('Deactivate this course? Students will no longer see it in course lists.')) return;
        try {
            await adminCourses.remove(id);
            fetchCourses();
        } catch (e) { console.error(e); }
    };

    return (
        <div className="flex h-screen bg-slate-950 text-white">
            <AdminSidebar />
            <div className="flex-1 ml-64 py-8 pr-8 pl-10 overflow-y-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-2xl font-bold">Course Management</h1>
                        <p className="text-sm text-slate-400 mt-1">Create, edit, and manage university courses</p>
                    </div>
                    <button onClick={openCreate} className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2.5 px-5 rounded-xl text-sm shadow-lg shadow-blue-500/25 transition-all active:scale-[0.98]">
                        <Plus size={18} />
                        <span>Add Course</span>
                    </button>
                </div>

                {/* Search */}
                <div className="relative mb-6 max-w-md">
                    <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                        type="text"
                        placeholder="Search by code or name..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full pl-10 pr-4 py-3 rounded-xl bg-slate-800/60 border border-slate-700/50 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-sm"
                    />
                </div>

                {/* Table */}
                <div className="bg-slate-800/60 backdrop-blur rounded-2xl border border-slate-700/30 overflow-hidden">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-slate-700/30">
                                {['Code', 'Name', 'Level', 'Sem', 'Credits', 'Weight', 'Status', 'Actions'].map(h => (
                                    <th key={h} className="text-left px-5 py-4 text-[11px] font-bold text-slate-400 uppercase tracking-wider">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr><td colSpan={8} className="text-center py-12 text-slate-500">Loading...</td></tr>
                            ) : filtered.length === 0 ? (
                                <tr><td colSpan={8} className="text-center py-12 text-slate-500">No courses found</td></tr>
                            ) : filtered.map(c => (
                                <tr key={c.id} className="border-b border-slate-700/20 hover:bg-slate-700/20 transition-colors">
                                    <td className="px-5 py-3.5 text-sm font-bold text-blue-300">{c.code}</td>
                                    <td className="px-5 py-3.5 text-sm text-slate-200">{c.name}</td>
                                    <td className="px-5 py-3.5 text-sm text-slate-300">{c.level}</td>
                                    <td className="px-5 py-3.5 text-sm text-slate-300">{c.semester}</td>
                                    <td className="px-5 py-3.5 text-sm text-slate-300">{c.credits}</td>
                                    <td className="px-5 py-3.5 text-sm text-slate-300">{c.weight}</td>
                                    <td className="px-5 py-3.5">
                                        <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-bold ${c.is_active ? 'bg-green-500/15 text-green-400' : 'bg-red-500/15 text-red-400'}`}>
                                            {c.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td className="px-5 py-3.5">
                                        <div className="flex items-center space-x-2">
                                            <button onClick={() => openEdit(c)} className="p-2 rounded-lg hover:bg-slate-600/50 text-slate-400 hover:text-blue-400 transition-colors">
                                                <Pencil size={15} />
                                            </button>
                                            {c.is_active && (
                                                <button onClick={() => handleDelete(c.id)} className="p-2 rounded-lg hover:bg-red-500/10 text-slate-400 hover:text-red-400 transition-colors">
                                                    <Trash2 size={15} />
                                                </button>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Modal */}
                {showModal && (
                    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50" onClick={() => setShowModal(false)}>
                        <div className="bg-slate-800 rounded-2xl border border-slate-700/50 p-8 w-full max-w-lg shadow-2xl" onClick={e => e.stopPropagation()}>
                            <div className="flex justify-between items-center mb-6">
                                <div className="flex items-center space-x-3">
                                    <div className="w-10 h-10 bg-blue-500/15 rounded-xl flex items-center justify-center">
                                        <BookOpen size={20} className="text-blue-400" />
                                    </div>
                                    <h2 className="text-lg font-bold">{editId ? 'Edit Course' : 'New Course'}</h2>
                                </div>
                                <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white"><X size={20} /></button>
                            </div>

                            <div className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-xs font-semibold text-slate-400 mb-1">Code</label>
                                        <input value={form.code} onChange={e => setForm({ ...form, code: e.target.value })} className="w-full px-3 py-2.5 rounded-xl bg-slate-700/50 border border-slate-600/50 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50" placeholder="e.g. SEN 301" />
                                    </div>
                                    <div>
                                        <label className="block text-xs font-semibold text-slate-400 mb-1">Level</label>
                                        <select value={form.level} onChange={e => setForm({ ...form, level: Number(e.target.value) })} className="w-full px-3 py-2.5 rounded-xl bg-slate-700/50 border border-slate-600/50 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50">
                                            {[100, 200, 300, 400].map(l => <option key={l} value={l}>{l}</option>)}
                                        </select>
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-xs font-semibold text-slate-400 mb-1">Name</label>
                                    <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} className="w-full px-3 py-2.5 rounded-xl bg-slate-700/50 border border-slate-600/50 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50" placeholder="e.g. Software Engineering I" />
                                </div>
                                <div className="grid grid-cols-3 gap-4">
                                    <div>
                                        <label className="block text-xs font-semibold text-slate-400 mb-1">Semester</label>
                                        <select value={form.semester} onChange={e => setForm({ ...form, semester: Number(e.target.value) })} className="w-full px-3 py-2.5 rounded-xl bg-slate-700/50 border border-slate-600/50 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50">
                                            <option value={1}>1st</option>
                                            <option value={2}>2nd</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-xs font-semibold text-slate-400 mb-1">Credits (1–4)</label>
                                        <input type="number" min={1} max={4} value={form.credits} onChange={e => setForm({ ...form, credits: Number(e.target.value) })} className="w-full px-3 py-2.5 rounded-xl bg-slate-700/50 border border-slate-600/50 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50" />
                                    </div>
                                    <div>
                                        <label className="block text-xs font-semibold text-slate-400 mb-1">Weight (1–5)</label>
                                        <input type="number" min={1} max={5} value={form.weight} onChange={e => setForm({ ...form, weight: Number(e.target.value) })} className="w-full px-3 py-2.5 rounded-xl bg-slate-700/50 border border-slate-600/50 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50" />
                                    </div>
                                </div>

                                {formError && <p className="text-red-400 text-sm bg-red-500/10 p-3 rounded-xl">{formError}</p>}

                                <div className="flex justify-end space-x-3 pt-2">
                                    <button onClick={() => setShowModal(false)} className="px-5 py-2.5 rounded-xl bg-slate-700 text-slate-300 hover:bg-slate-600 text-sm font-semibold transition-colors">Cancel</button>
                                    <button onClick={handleSave} disabled={saving} className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-bold shadow-lg transition-all disabled:opacity-50">
                                        {saving ? 'Saving...' : (editId ? 'Update' : 'Create')}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdminCourses;
