import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import Sidebar from '../components/Sidebar';
import { api } from '../api/client';
import type { EnrolledCourse, Material } from '../types';
import { Video, BookOpen, FileText, ExternalLink, Search, Filter, Book, Youtube } from 'lucide-react';

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
    margin-bottom: 2.5rem;
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

const SearchContainer = styled.div`
    position: relative;
    margin-bottom: 2rem;
    max-width: 600px;
`;

const SearchInput = styled.input`
    width: 100%;
    padding: 1rem 1rem 1rem 3rem;
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
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: #94A3B8;
`;

// --- Course Section ---

const CourseSection = styled.div`
    margin-bottom: 3rem;
`;

const CourseHeader = styled.div`
    display: flex;
    align-items: baseline;
    gap: 1rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid #E2E8F0;
    padding-bottom: 0.75rem;
`;

const CourseTitle = styled.h2`
    font-size: 1.5rem;
    font-weight: 600;
    color: #1E293B;
`;

const CourseCode = styled.span`
    font-size: 1rem;
    font-weight: 500;
    color: #64748B;
    background: #F1F5F9;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
`;

const Grid = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
`;

// --- Material Card ---

const Card = styled.a`
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 0.75rem;
    padding: 1.5rem;
    text-decoration: none;
    transition: all 0.2s;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 180px;

    &:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-color: #CBD5E1;
    }
`;

const CardHeader = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
`;

const IconBox = styled.div<{ type: string }>`
    width: 48px; height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    ${props => props.type === 'video' && `
        background-color: #FEF2F2; color: #DC2626;
    `}
    ${props => props.type === 'textbook' && `
        background-color: #EFF6FF; color: #2563EB;
    `}
    ${props => props.type === 'journal' && `
        background-color: #F0FDF4; color: #16A34A;
    `}
    ${props => props.type === 'article' && `
        background-color: #F8FAFC; color: #475569;
    `}
`;

const CardTitle = styled.h3`
    font-size: 1.125rem;
    font-weight: 600;
    color: #1E293B;
    margin-bottom: 0.5rem;
    line-height: 1.4;
`;

const TagContainer = styled.div`
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: auto;
    padding-top: 1rem;
`;

const Badge = styled.span<{ color?: string }>`
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    background-color: ${props => props.color || '#F1F5F9'};
    color: #475569;
`;

const DifficultyDot = styled.div<{ level: number }>`
    display: flex;
    gap: 2px;
    margin-top: 0.5rem;
    
    span {
        width: 6px; height: 6px;
        border-radius: 50%;
        background-color: #E2E8F0;
        
        &:nth-child(-n+${props => props.level}) {
            background-color: ${props => props.level > 3 ? '#EF4444' : props.level > 1 ? '#F59E0B' : '#10B981'};
        }
    }
`;


const Materials: React.FC = () => {
    const [courses, setCourses] = useState<EnrolledCourse[]>([]);
    const [materials, setMaterials] = useState<Record<number, Material[]>>({});
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                // 1. Fetch Enrolled Courses
                const myCourses = await api.get<EnrolledCourse[]>('/courses/my_courses');
                setCourses(myCourses);

                // 2. Fetch Materials for each course
                const materialMap: Record<number, Material[]> = {};

                // Sequential Fetching to prevent backend overload
                for (const course of myCourses) {
                    try {
                        const mats = await api.get<Material[]>(`/materials/${course.id}`);
                        materialMap[course.id] = mats;
                    } catch (e) {
                        console.error(`Failed to fetch materials for course ${course.code}`, e);
                        materialMap[course.id] = [];
                    }
                }

                setMaterials(materialMap);
            } catch (err) {
                console.error("Failed to load materials data", err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const getIcon = (type: string) => {
        switch (type) {
            case 'video': return <Youtube size={24} />;
            case 'textbook': return <Book size={24} />;
            case 'journal': return <BookOpen size={24} />;
            default: return <FileText size={24} />;
        }
    };

    const getTypeColor = (type: string) => {
        switch (type) {
            case 'video': return '#FEF2F2';
            case 'textbook': return '#EFF6FF';
            case 'journal': return '#F0FDF4';
            default: return '#F8FAFC';
        }
    };

    // Filter Logic
    const filteredCourses = courses.filter(course => {
        // If searching, check course name or if any material matches
        if (!searchTerm) return true;
        const lowerSearch = searchTerm.toLowerCase();

        const courseMatch = course.name.toLowerCase().includes(lowerSearch) ||
            course.code.toLowerCase().includes(lowerSearch);

        const hasMatchingMaterial = materials[course.id]?.some(m =>
            m.title.toLowerCase().includes(lowerSearch)
        );

        return courseMatch || hasMatchingMaterial;
    });

    return (
        <LayoutContainer>
            <Sidebar />
            <MainContent>
                <Header>
                    <Title>Curated Materials</Title>
                    <Subtitle>AI-curated resources tailored to your learning style and curriculum.</Subtitle>
                </Header>

                <SearchContainer>
                    <SearchIconWrapper>
                        <Search size={20} />
                    </SearchIconWrapper>
                    <SearchInput
                        placeholder="Search for courses, topics, or specific resources..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </SearchContainer>

                {loading ? (
                    <div className="flex flex-col justify-center items-center h-64 text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
                        <p className="text-gray-600 font-medium">AI is curating high-quality academic resources for you...</p>
                        <p className="text-gray-400 text-sm mt-2">This may take a moment while we verify links.</p>
                    </div>
                ) : (
                    filteredCourses.map(course => {
                        const courseMaterials = materials[course.id] || [];
                        const displayMaterials = searchTerm
                            ? courseMaterials.filter(m => m.title.toLowerCase().includes(searchTerm.toLowerCase()) || course.name.toLowerCase().includes(searchTerm.toLowerCase()) || course.code.toLowerCase().includes(searchTerm.toLowerCase()))
                            : courseMaterials;

                        if (displayMaterials.length === 0) return null;

                        return (
                            <CourseSection key={course.id}>
                                <CourseHeader>
                                    <CourseTitle>{course.name}</CourseTitle>
                                    <CourseCode>{course.code}</CourseCode>
                                </CourseHeader>

                                <Grid>
                                    {displayMaterials.map(material => (
                                        <Card key={material.id} href={material.url} target="_blank" rel="noopener noreferrer">
                                            <div>
                                                <CardHeader>
                                                    <IconBox type={material.type}>
                                                        {getIcon(material.type)}
                                                    </IconBox>
                                                    <ExternalLink size={16} className="text-gray-400" />
                                                </CardHeader>

                                                <CardTitle>{material.title}</CardTitle>

                                                <DifficultyDot level={material.difficulty || 1}>
                                                    {[1, 2, 3, 4, 5].map(i => <span key={i} />)}
                                                </DifficultyDot>
                                            </div>

                                            <TagContainer>
                                                <Badge>{material.type.toUpperCase()}</Badge>
                                                {material.tag && (
                                                    <Badge color="#F0F9FF" style={{ color: '#0369A1' }}>
                                                        {material.tag}
                                                    </Badge>
                                                )}
                                            </TagContainer>
                                        </Card>
                                    ))}
                                </Grid>
                            </CourseSection>
                        );
                    })
                )}

                {!loading && filteredCourses.length === 0 && (
                    <div className="text-center py-20 text-gray-400">
                        <p>No materials found matching your search.</p>
                    </div>
                )}
            </MainContent>
        </LayoutContainer>
    );
};

export default Materials;
