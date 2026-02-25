import React, { useState, useEffect, useRef } from 'react';
import styled, { keyframes } from 'styled-components';
import Sidebar from '../components/Sidebar';
import { api } from '../api/client';
import type { SearchResult, SavedResource } from '../types';
import { ExternalLink, Search, BookOpen, FileText, Bookmark, BookmarkCheck, Trash2, AlertCircle, Loader } from 'lucide-react';

// --- Styled Components ---

const LayoutContainer = styled.div`
    display: flex;
    min-height: 100vh;
    background-color: #F8FAFC;
    font-family: 'Inter', system-ui, sans-serif;
`;

const MainContent = styled.main`
    flex: 1;
    margin-left: 16rem;
    padding: 2.5rem 3rem;
`;

const Header = styled.header`
    margin-bottom: 2rem;
`;

const Title = styled.h1`
    font-size: 1.875rem;
    font-weight: 700;
    color: #0F172A;
`;

const Subtitle = styled.p`
    color: #64748B;
    margin-top: 0.5rem;
    font-size: 1rem;
`;

// --- Search Section ---

const SearchForm = styled.form`
    display: flex;
    gap: 0.75rem;
    margin-bottom: 2rem;
    max-width: 700px;
`;

const SearchInputContainer = styled.div`
    position: relative;
    flex: 1;
`;

const SearchInput = styled.input`
    width: 100%;
    padding: 0.875rem 1rem 0.875rem 2.75rem;
    border-radius: 0.75rem;
    border: 1px solid #E2E8F0;
    font-size: 1rem;
    outline: none;
    transition: all 0.2s;

    &:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
`;

const SearchIconWrapper = styled.div`
    position: absolute;
    left: 0.875rem;
    top: 50%;
    transform: translateY(-50%);
    color: #94A3B8;
`;

const SearchButton = styled.button`
    padding: 0.875rem 1.5rem;
    border-radius: 0.75rem;
    border: none;
    background: linear-gradient(135deg, #3B82F6, #2563EB);
    color: white;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;

    &:hover {
        background: linear-gradient(135deg, #2563EB, #1D4ED8);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }

    &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }
`;

// --- Loading ---

const spin = keyframes`
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
`;

const LoadingContainer = styled.div`
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    color: #64748B;
    gap: 1rem;

    svg {
        animation: ${spin} 1s linear infinite;
        color: #3B82F6;
    }
`;

// --- Cards ---

const SectionTitle = styled.h2`
    font-size: 1.25rem;
    font-weight: 600;
    color: #1E293B;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
`;

const Grid = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.25rem;
    margin-bottom: 3rem;
`;

const Card = styled.div`
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 0.75rem;
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 160px;
    transition: all 0.2s;

    &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        border-color: #CBD5E1;
    }
`;

const CardTitle = styled.a`
    font-size: 1rem;
    font-weight: 600;
    color: #1E293B;
    text-decoration: none;
    line-height: 1.4;
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;

    &:hover {
        color: #3B82F6;
    }
`;

const CardUrl = styled.a`
    font-size: 0.75rem;
    color: #94A3B8;
    text-decoration: none;
    margin-top: 0.25rem;
    word-break: break-all;
    display: block;

    &:hover {
        color: #3B82F6;
    }
`;

const CardFooter = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: auto;
    padding-top: 1rem;
`;

const Badge = styled.span<{ variant?: string }>`
    font-size: 0.7rem;
    font-weight: 500;
    padding: 0.2rem 0.5rem;
    border-radius: 0.25rem;
    text-transform: uppercase;
    background-color: ${props => props.variant === 'video' ? '#FEF2F2' : '#EFF6FF'};
    color: ${props => props.variant === 'video' ? '#DC2626' : '#2563EB'};
`;

const ActionButton = styled.button<{ variant?: string }>`
    display: flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.35rem 0.65rem;
    border-radius: 0.375rem;
    border: 1px solid ${props => props.variant === 'danger' ? '#FEE2E2' : '#E2E8F0'};
    background: ${props => props.variant === 'danger' ? '#FEF2F2' : 'white'};
    color: ${props => props.variant === 'danger' ? '#DC2626' : '#3B82F6'};
    font-size: 0.75rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;

    &:hover {
        background: ${props => props.variant === 'danger' ? '#FEE2E2' : '#EFF6FF'};
    }

    &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
`;

const WarningBox = styled.div`
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 1.25rem;
    border-radius: 0.75rem;
    background: #FFFBEB;
    border: 1px solid #FEF3C7;
    color: #92400E;
    font-size: 0.9rem;
    margin-bottom: 2rem;
`;

const EmptyState = styled.div`
    text-align: center;
    padding: 2.5rem 2rem;
    color: #94A3B8;
    font-size: 0.9rem;
    background: #F8FAFC;
    border-radius: 0.75rem;
    border: 1px dashed #E2E8F0;
    margin-bottom: 3rem;
`;

const Divider = styled.hr`
    border: none;
    border-top: 1px solid #E2E8F0;
    margin: 2rem 0;
`;

const SavedDate = styled.span`
    font-size: 0.7rem;
    color: #94A3B8;
`;

const ToastMessage = styled.div<{ type: 'success' | 'error' }>`
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    padding: 0.75rem 1.25rem;
    border-radius: 0.5rem;
    font-size: 0.85rem;
    font-weight: 500;
    color: white;
    z-index: 1000;
    background: ${props => props.type === 'success' ? '#10B981' : '#EF4444'};
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    animation: slideIn 0.3s ease;

    @keyframes slideIn {
        from { transform: translateY(1rem); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
`;


// --- Component ---

const Materials: React.FC = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
    const [savedResources, setSavedResources] = useState<SavedResource[]>([]);
    const [searching, setSearching] = useState(false);
    const [loadingSaved, setLoadingSaved] = useState(true);
    const [warning, setWarning] = useState('');
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
    const [savingUrls, setSavingUrls] = useState<Set<string>>(new Set());
    // const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    // Load saved resources on mount
    useEffect(() => {
        const loadSaved = async () => {
            try {
                const saved = await api.get<SavedResource[]>('/materials/saved');
                setSavedResources(saved);
            } catch (e) {
                console.error('Failed to load saved resources', e);
            } finally {
                setLoadingSaved(false);
            }
        };
        loadSaved();
    }, []);

    // Toast auto-dismiss
    useEffect(() => {
        if (toast) {
            const timer = setTimeout(() => setToast(null), 3000);
            return () => clearTimeout(timer);
        }
    }, [toast]);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!searchQuery.trim() || searching) return;

        setSearching(true);
        setWarning('');
        setSearchResults([]);

        try {
            const response = await api.post<{ results: SearchResult[]; warning?: string }>(
                '/materials/search',
                { query: searchQuery.trim() }
            );

            setSearchResults(response.results || []);
            if (response.warning) {
                setWarning(response.warning);
            }
        } catch (err: any) {
            setWarning("Couldn't find resources for that topic. Try rephrasing your search.");
        } finally {
            setSearching(false);
        }
    };

    // const handleSearch = async (e: React.FormEvent) => {
    //     e.preventDefault();
    //     if (!searchQuery.trim() || searching) return;

    //     setSearching(true);
    //     setWarning('');
    //     setSearchResults([]);

    //     // Set a 30-second frontend timeout
    //     const timeoutPromise = new Promise<never>((_, reject) => {
    //         timeoutRef.current = setTimeout(() => {
    //             reject(new Error('timeout'));
    //         }, 30000);
    //     });

    //     try {
    //         const response = await Promise.race([
    //             api.post<{ results: SearchResult[]; warning?: string }>('/materials/search', { query: searchQuery.trim() }),
    //             timeoutPromise
    //         ]);

    //         if (timeoutRef.current) clearTimeout(timeoutRef.current);

    //         setSearchResults(response.results || []);
    //         if (response.warning) {
    //             setWarning(response.warning);
    //         }
    //     } catch (err: any) {
    //         if (timeoutRef.current) clearTimeout(timeoutRef.current);
    //         if (err.message === 'timeout') {
    //             setWarning('Search is taking too long. The AI service may be overloaded — please try again.');
    //         } else {
    //             setWarning("Couldn't find enough verified resources for that topic. Try rephrasing your search.");
    //         }
    //     } finally {
    //         setSearching(false);
    //     }
    // };

    const handleSave = async (result: SearchResult) => {
        // Check if already saved
        if (savedResources.some(s => s.url === result.url)) {
            setToast({ message: "You've already saved this resource.", type: 'error' });
            return;
        }

        setSavingUrls(prev => new Set(prev).add(result.url));
        try {
            const saved = await api.post<SavedResource>('/materials/saved', {
                title: result.title,
                url: result.url,
                type: result.type,
            });
            setSavedResources(prev => [saved, ...prev]);
            setToast({ message: 'Resource saved!', type: 'success' });
        } catch (err: any) {
            if (err.message?.includes('already saved')) {
                setToast({ message: "You've already saved this resource.", type: 'error' });
            } else {
                setToast({ message: 'Failed to save resource.', type: 'error' });
            }
        } finally {
            setSavingUrls(prev => {
                const next = new Set(prev);
                next.delete(result.url);
                return next;
            });
        }
    };

    const handleDelete = async (id: number) => {
        try {
            await api.delete(`/materials/saved/${id}`);
            setSavedResources(prev => prev.filter(r => r.id !== id));
            setToast({ message: 'Resource removed.', type: 'success' });
        } catch {
            setToast({ message: 'Failed to remove resource.', type: 'error' });
        }
    };

    const isAlreadySaved = (url: string) => savedResources.some(s => s.url === url);

    return (
        <LayoutContainer>
            <Sidebar />
            <MainContent>
                <Header>
                    <Title>Materials Search</Title>
                    <Subtitle>Search any topic to find verified learning resources, then save the ones you need.</Subtitle>
                </Header>

                {/* --- Search Bar --- */}
                <SearchForm onSubmit={handleSearch}>
                    <SearchInputContainer>
                        <SearchIconWrapper>
                            <Search size={18} />
                        </SearchIconWrapper>
                        <SearchInput
                            placeholder='Try "recursion base case", "SQL joins explained", "binary search tree"...'
                            value={searchQuery}
                            onChange={e => setSearchQuery(e.target.value)}
                            disabled={searching}
                        />
                    </SearchInputContainer>
                    <SearchButton type="submit" disabled={searching || !searchQuery.trim()}>
                        {searching ? 'Searching...' : 'Search'}
                    </SearchButton>
                </SearchForm>

                {/* --- Loading State --- */}
                {searching && (
                    <LoadingContainer>
                        <Loader size={32} />
                        <p>AI is searching for verified resources...</p>
                        <p style={{ fontSize: '0.8rem', color: '#94A3B8' }}>This may take up to 20 seconds</p>
                    </LoadingContainer>
                )}

                {/* --- Warning --- */}
                {warning && !searching && (
                    <WarningBox>
                        <AlertCircle size={18} style={{ flexShrink: 0 }} />
                        {warning}
                    </WarningBox>
                )}

                {/* --- Search Results --- */}
                {searchResults.length > 0 && !searching && (
                    <>
                        <SectionTitle>
                            <Search size={18} />
                            Search Results
                        </SectionTitle>
                        <Grid>
                            {searchResults.map((result, index) => (
                                <Card key={`${result.url}-${index}`}>
                                    <div>
                                        <CardTitle href={result.url} target="_blank" rel="noopener noreferrer">
                                            <ExternalLink size={14} style={{ flexShrink: 0, marginTop: '3px' }} />
                                            {result.title}
                                        </CardTitle>
                                        <CardUrl href={result.url} target="_blank" rel="noopener noreferrer">
                                            {result.url.length > 60 ? result.url.substring(0, 60) + '...' : result.url}
                                        </CardUrl>
                                    </div>
                                    <CardFooter>
                                        <Badge variant={result.type}>{result.type}</Badge>
                                        {isAlreadySaved(result.url) ? (
                                            <ActionButton disabled>
                                                <BookmarkCheck size={14} />
                                                Saved
                                            </ActionButton>
                                        ) : (
                                            <ActionButton
                                                onClick={() => handleSave(result)}
                                                disabled={savingUrls.has(result.url)}
                                            >
                                                <Bookmark size={14} />
                                                {savingUrls.has(result.url) ? 'Saving...' : 'Save'}
                                            </ActionButton>
                                        )}
                                    </CardFooter>
                                </Card>
                            ))}
                        </Grid>
                    </>
                )}

                <Divider />

                {/* --- Saved Resources --- */}
                <SectionTitle>
                    <BookmarkCheck size={18} />
                    Your Saved Resources
                </SectionTitle>

                {loadingSaved ? (
                    <LoadingContainer>
                        <Loader size={24} />
                        <p>Loading your library...</p>
                    </LoadingContainer>
                ) : savedResources.length === 0 ? (
                    <EmptyState>
                        <BookOpen size={32} style={{ marginBottom: '0.75rem', opacity: 0.4 }} />
                        <p>Resources you save will appear here.</p>
                        <p style={{ marginTop: '0.25rem', fontSize: '0.8rem' }}>
                            Search for a topic above and click "Save" on any result.
                        </p>
                    </EmptyState>
                ) : (
                    <Grid>
                        {savedResources.map(resource => (
                            <Card key={resource.id}>
                                <div>
                                    <CardTitle href={resource.url} target="_blank" rel="noopener noreferrer">
                                        <ExternalLink size={14} style={{ flexShrink: 0, marginTop: '3px' }} />
                                        {resource.title}
                                    </CardTitle>
                                    <CardUrl href={resource.url} target="_blank" rel="noopener noreferrer">
                                        {resource.url.length > 60 ? resource.url.substring(0, 60) + '...' : resource.url}
                                    </CardUrl>
                                </div>
                                <CardFooter>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                        <Badge variant={resource.type}>{resource.type}</Badge>
                                        <SavedDate>
                                            {new Date(resource.saved_at).toLocaleDateString()}
                                        </SavedDate>
                                    </div>
                                    <ActionButton variant="danger" onClick={() => handleDelete(resource.id)}>
                                        <Trash2 size={13} />
                                        Remove
                                    </ActionButton>
                                </CardFooter>
                            </Card>
                        ))}
                    </Grid>
                )}

                {/* --- Toast --- */}
                {toast && <ToastMessage type={toast.type}>{toast.message}</ToastMessage>}
            </MainContent>
        </LayoutContainer>
    );
};

export default Materials;
