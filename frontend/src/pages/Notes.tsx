import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import Sidebar from '../components/Sidebar';
import { api, BASE_URL } from '../api/client';
import { useUser } from '../context/UserContext';
import { Plus, Upload, FileText, X, Save, ArrowLeft, File, Trash2, ExternalLink, ChevronLeft } from 'lucide-react';

// --- Types ---
interface Note {
    id: number;
    title: string;
    content: string;
    file_path?: string;
    file_type?: string;
    last_edited: string;
    created_at?: string;
    course_id?: number;
}

// --- Styled Components ---

const LayoutContainer = styled.div`
    display: flex;
    min-height: 100vh;
    background-color: #F8FAFC;
`;

const MainContent = styled.main`
    flex: 1;
    margin-left: 16rem;
    padding: 2.5rem 3rem;
    font-family: 'Inter', system-ui, sans-serif;
`;

const TopBar = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
`;

const PageHeader = styled.div`
    display: flex;
    flex-direction: column;
`;

const PageTitle = styled.h1`
    font-size: 1.875rem;
    font-weight: 700;
    color: #0F172A;
`;

const SubTitle = styled.p`
    color: #64748B;
    margin-top: 0.25rem;
`;

const ActionButtons = styled.div`
    display: flex;
    gap: 1rem;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' | 'danger' }>`
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.625rem 1.25rem;
    border-radius: 0.5rem;
    font-weight: 600;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s;
    
    ${props => props.variant === 'primary' ? `
        background-color: #4F46E5;
        color: white;
        border: none;
        &:hover { background-color: #4338CA; }
    ` : props.variant === 'danger' ? `
        background-color: #FEE2E2;
        color: #B91C1C;
        border: 1px solid #FECACA;
        &:hover { background-color: #FECACA; }
    ` : `
        background-color: white;
        color: #475569;
        border: 1px solid #E2E8F0;
        &:hover { background-color: #F1F5F9; border-color: #CBD5E1; }
    `}

    &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
`;

// --- List View Components ---

const NotesGrid = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
`;

const NoteCard = styled.div`
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 0.75rem;
    padding: 1.5rem;
    transition: all 0.2s;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 160px;
    
    &:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-color: #CBD5E1;
    }
`;

const NoteHeader = styled.div`
    display: flex;
    align-items: flex-start;
    gap: 1rem; 
    margin-bottom: 0.75rem;
`;

const NoteIcon = styled.div<{ type: 'text' | 'file' }>`
    width: 40px; height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: ${props => props.type === 'text' ? '#EFF6FF' : '#FFF7ED'};
    color: ${props => props.type === 'text' ? '#3B82F6' : '#EA580C'};
    flex-shrink: 0;
`;

const NoteInfo = styled.div`
    flex: 1;
    min-width: 0; 
`;

const NoteTitle = styled.h3`
    font-size: 1.125rem;
    font-weight: 600;
    color: #1E293B;
    line-height: 1.4;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
`;

const NoteDate = styled.span`
    font-size: 0.75rem;
    color: #94A3B8;
    display: block;
    margin-top: 2px;
`;

const NoteMeta = styled.div`
    display: flex;
    justify-content: flex-end;
    align-items: center;
    margin-top: auto;
    padding-top: 1rem;
    border-top: 1px solid #F1F5F9;
`;

// --- Editor Components ---

const EditorContainer = styled.div`
    background: white;
    border-radius: 1rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    border: 1px solid #E2E8F0;
    min-height: 600px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
`;

const EditorHeader = styled.div`
    padding: 1.5rem 2rem;
    border-bottom: 1px solid #E2E8F0;
    background: #F8FAFC;
    display: flex;
    gap: 1rem;
`;

const TitleInput = styled.input`
    flex: 1;
    font-size: 1.5rem;
    font-weight: 700;
    color: #1E293B;
    background: transparent;
    border: none;
    outline: none;
    &::placeholder { color: #CBD5E1; }
`;

const EditorBody = styled.textarea`
    flex: 1;
    padding: 2rem;
    font-size: 1rem;
    line-height: 1.75;
    color: #334155;
    border: none;
    resize: none;
    outline: none;
    font-family: 'Inter', system-ui, sans-serif;
`;

// --- Modal ---
const ModalOverlay = styled.div`
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.5);
    backdrop-filter: blur(4px);
    display: flex; align-items: center; justify-content: center;
    z-index: 50;
`;

const ModalContent = styled.div`
    background: white;
    border-radius: 1rem;
    width: 100%; max-width: 500px;
    padding: 2rem;
    box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
`;


const Notes: React.FC = () => {
    const { user } = useUser();
    const [view, setView] = useState<'list' | 'create' | 'edit'>('list');
    const [notes, setNotes] = useState<Note[]>([]);
    const [loading, setLoading] = useState(true);

    // Editor State
    const [currentNote, setCurrentNote] = useState<Partial<Note>>({});
    const [saving, setSaving] = useState(false);

    // Upload State
    const [showUpload, setShowUpload] = useState(false);
    const [uploadFile, setUploadFile] = useState<File | null>(null);
    const [uploadTitle, setUploadTitle] = useState('');
    const [uploading, setUploading] = useState(false);

    // Fetch Notes
    const fetchNotes = async () => {
        setLoading(true);
        try {
            const data = await api.get<Note[]>('/notes/');
            setNotes(data);
        } catch (err) {
            console.error("Failed to fetch notes", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchNotes();
    }, []);

    const handleCreate = () => {
        setCurrentNote({ title: '', content: '' });
        setView('create');
    };

    const handleEdit = (note: Note) => {
        if (note.file_path) {
            window.open(`${BASE_URL}/notes/file/${note.file_path}`, '_blank');
            return;
        }
        setCurrentNote(note);
        setView('edit');
    };

    const handleBack = () => {
        // If user writes content but no title, logic handles save validation on SAVE click.
        // Prompt: "if they choose to go back without writing anything, the note does not save."
        // Implies if they wrote something, we should perhaps confirm?
        // Or essentially, back = discard.
        // But prompt says "if a user tries to save...". SAVE button is explicit.
        // So clicking BACK means discard, which aligns with "does not save".

        // However, if strict "without writing anything" means if I WROTE something it SHOULD save, 
        // usually apps autosave or ask.
        // I will assume Back = Discard for simplicity unless explicitly asked to confirm.
        setView('list');
    };

    const handleSave = async () => {
        if (!currentNote.title?.trim()) {
            if (currentNote.content?.trim()) {
                alert("Please add a title to save your note."); // Specific requirement
            } else {
                alert("Please provide a title.");
            }
            return;
        }

        setSaving(true);
        try {
            if (view === 'create') {
                await api.post('/notes/', currentNote);
            } else if (view === 'edit' && currentNote.id) {
                await api.put(`/notes/${currentNote.id}`, currentNote);
            }
            setView('list');
            fetchNotes();
        } catch (err) {
            console.error("Failed to save note", err);
            alert("Failed to save note. Please try again.");
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async (e: React.MouseEvent, id: number) => {
        e.stopPropagation();
        if (!window.confirm("Are you sure you want to delete this note?")) return;

        try {
            await api.delete(`/notes/${id}`);
            setNotes(prev => prev.filter(n => n.id !== id));
        } catch (err) {
            console.error("Failed to delete", err);
        }
    };

    const handleUpload = async () => {
        if (!uploadFile) return;
        setUploading(true);

        const formData = new FormData();
        formData.append('file', uploadFile);
        formData.append('title', uploadTitle || uploadFile.name);

        try {
            await api.post('/notes/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setShowUpload(false);
            setUploadFile(null);
            setUploadTitle('');
            fetchNotes(); // Refresh list
        } catch (err) {
            console.error("Upload failed", err);
            alert("Upload failed. Only PDF/PPTX supported.");
        } finally {
            setUploading(false);
        }
    };

    const formatDate = (dateStr?: string) => {
        if (!dateStr) return 'Unknown date';
        return new Date(dateStr).toLocaleString(); // "Date and time" as requested
    };

    return (
        <LayoutContainer>
            <Sidebar />
            <MainContent>
                {/* Header */}
                <TopBar>
                    {view === 'list' ? (
                        <>
                            <PageHeader>
                                <PageTitle>My Notes</PageTitle>
                                <SubTitle>Capture ideas, summaries, and resources.</SubTitle>
                            </PageHeader>
                            <ActionButtons>
                                <Button onClick={() => setShowUpload(true)} variant="secondary">
                                    <Upload size={18} />
                                    <span>Upload Note</span>
                                </Button>
                                <Button onClick={handleCreate} variant="primary">
                                    <Plus size={18} />
                                    <span>Create Note</span>
                                </Button>
                            </ActionButtons>
                        </>
                    ) : (
                        <>
                            {/* Single Back Button (Top Left) */}
                            <Button onClick={handleBack} variant="secondary">
                                <ChevronLeft size={18} />
                                <span>Back</span>
                            </Button>

                            {/* Save Button (Top Right) */}
                            <Button onClick={handleSave} variant="primary" disabled={saving}>
                                <Save size={18} />
                                <span>{saving ? 'Saving...' : 'Save Note'}</span>
                            </Button>
                        </>
                    )}
                </TopBar>

                {/* Content */}
                {view === 'list' ? (
                    loading ? (
                        <div className="flex h-64 items-center justify-center text-gray-400 animate-pulse">Loading notes...</div>
                    ) : notes.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-20 border-2 border-dashed border-gray-200 rounded-xl bg-gray-50/50">
                            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-sm mb-4">
                                <FileText className="text-gray-300" size={32} />
                            </div>
                            <h3 className="text-xl font-bold text-gray-900 mb-2">No notes yet</h3>
                            <p className="text-gray-500 max-w-sm text-center mb-6">Start by creating a text note or uploading your study materials.</p>
                            <Button onClick={handleCreate} variant="primary">
                                <Plus size={18} />
                                <span>Create your first note</span>
                            </Button>
                        </div>
                    ) : (
                        <NotesGrid>
                            {notes.map(note => (
                                <NoteCard key={note.id} onClick={() => handleEdit(note)}>
                                    <div className="flex-1">
                                        <NoteHeader>
                                            {/* Icon on Left */}
                                            <NoteIcon type={note.file_path ? 'file' : 'text'}>
                                                {note.file_path ? <File size={20} /> : <FileText size={20} />}
                                            </NoteIcon>

                                            {/* Title and Date */}
                                            <NoteInfo>
                                                <NoteTitle>{note.title}</NoteTitle>
                                                <NoteDate>{formatDate(note.created_at || note.last_edited)}</NoteDate>
                                            </NoteInfo>
                                        </NoteHeader>
                                        <p className="text-sm text-gray-500 mt-2 line-clamp-3">
                                            {note.file_path ? `File: ${note.file_type?.toUpperCase()}` : note.content}
                                        </p>
                                    </div>
                                    <NoteMeta>
                                        {note.file_path && <ExternalLink size={14} className="text-blue-500 mr-auto" />}
                                        <button
                                            className="text-gray-300 hover:text-red-500 transition-colors p-1"
                                            onClick={(e) => handleDelete(e, note.id)}
                                        >
                                            <Trash2 size={16} />
                                        </button>
                                    </NoteMeta>
                                </NoteCard>
                            ))}
                        </NotesGrid>
                    )
                ) : (
                    <EditorContainer>
                        <EditorHeader>
                            <TitleInput
                                placeholder="Note Title..."
                                value={currentNote.title || ''}
                                onChange={e => setCurrentNote({ ...currentNote, title: e.target.value })}
                                autoFocus
                            />
                        </EditorHeader>
                        <EditorBody
                            placeholder="Start writing..."
                            value={currentNote.content || ''}
                            onChange={e => setCurrentNote({ ...currentNote, content: e.target.value })}
                        />
                    </EditorContainer>
                )}
            </MainContent>

            {/* Upload Modal */}
            {showUpload && (
                <ModalOverlay onClick={() => setShowUpload(false)}>
                    <ModalContent onClick={e => e.stopPropagation()}>
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-xl font-bold text-gray-900">Upload Note</h2>
                            <button onClick={() => setShowUpload(false)} className="text-gray-400 hover:text-gray-600">
                                <X size={24} />
                            </button>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Title (Optional)</label>
                                <input
                                    type="text"
                                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                    placeholder="My Lecture Slides"
                                    value={uploadTitle}
                                    onChange={e => setUploadTitle(e.target.value)}
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">File (PDF / PPTX)</label>
                                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:bg-gray-50 transition-colors cursor-pointer relative">
                                    <input
                                        type="file"
                                        accept=".pdf,.ppt,.pptx"
                                        className="absolute inset-0 opacity-0 cursor-pointer"
                                        onChange={e => setUploadFile(e.target.files?.[0] || null)}
                                    />
                                    {uploadFile ? (
                                        <div className="flex items-center justify-center gap-2 text-blue-600 font-medium">
                                            <File size={20} />
                                            {uploadFile.name}
                                        </div>
                                    ) : (
                                        <div className="text-gray-500">
                                            <Upload className="mx-auto mb-2 text-gray-400" size={24} />
                                            <span className="text-sm">Click to select file</span>
                                        </div>
                                    )}
                                </div>
                            </div>

                            <Button
                                variant="primary"
                                className="w-full justify-center mt-6"
                                onClick={handleUpload}
                                disabled={!uploadFile || uploading}
                            >
                                {uploading ? 'Uploading...' : 'Upload File'}
                            </Button>
                        </div>
                    </ModalContent>
                </ModalOverlay>
            )}
        </LayoutContainer>
    );
};

export default Notes;
