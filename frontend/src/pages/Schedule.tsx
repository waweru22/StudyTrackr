import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import Sidebar from '../components/Sidebar';
import { api } from '../api/client';
import { useUser } from '../context/UserContext';
import type { ScheduleData, SessionBlock } from '../types';

// --- Icons ---
const CheckIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="currentColor" style={{ width: 18, height: 18 }}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
    </svg>
);

const ChevronDown = ({ style }: { style?: React.CSSProperties }) => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" style={{ width: 20, height: 20, ...style }}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
    </svg>
);

const BoltIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" style={{ width: 14, height: 14 }}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
    </svg>
);

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
    margin-bottom: 2.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #E2E8F0;
`;

const Breadcrumb = styled.div`
    display: flex;
    gap: 2.5rem;
`;

const BreadcrumbItem = styled.div`
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    
    span.label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        font-weight: 600;
    }
    
    span.value {
        font-size: 1rem;
        font-weight: 600;
        color: #334155;
    }
`;

const UserProfile = styled.div`
    display: flex;
    align-items: center;
    gap: 1rem;
    
    span.name {
        font-weight: 600;
        color: #1E293B;
    }
`;

const Avatar = styled.img`
    width: 44px; height: 44px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid white;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
`;

const SectionTitle = styled.h2`
    font-size: 1.25rem;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 1.25rem;
`;

const CardContainer = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 1.5rem;
    margin-bottom: 4rem;
`;

// Weekly Section Styled Components
const WeekSection = styled.div`
    margin-top: 2rem;
`;

const InsightText = styled.p`
    color: #64748B;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
    line-height: 1.5;
`;

const WeekGrid = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
    padding-bottom: 2rem;
`;

const DayCard = styled.div`
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 1rem;
    min-height: 200px;
    display: flex;
    flex-direction: column;
`;

const DayHeader = styled.h4`
    font-size: 0.9rem;
    font-weight: 700;
    color: #334155;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #F1F5F9;
    text-transform: uppercase;
    text-align: center;
`;

// Timeline
const Timeline = styled.div`
    position: relative;
    padding-left: 12px;
    border-left: 2px solid #E2E8F0;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-left: 4px;
`;

const TimelineItem = styled.div`
    position: relative;
`;

const Dot = styled.div`
    position: absolute;
    left: -19px; // Account for border (2px) + padding (12px) + half dot (5px)
    top: 4px;
    width: 10px; height: 10px;
    border-radius: 50%;
    background-color: #CBD5E1;
    border: 2px solid white;
    box-shadow: 0 0 0 1px #E2E8F0;
`;

const TimeLabel = styled.span`
    display: block;
    font-size: 0.7rem;
    color: #94A3B8;
    font-weight: 600;
    margin-bottom: 2px;
`;

const CourseLabel = styled.span`
    display: block;
    font-size: 0.8rem;
    color: #475569;
    font-weight: 500;
    line-height: 1.2;
`;


// --- Interactive Session Card ---

const SessionCard = ({ session, onStart, onComplete }: { session: SessionBlock, onStart: (id: number) => void, onComplete: (id: number) => void }) => {
    const [expanded, setExpanded] = useState(false);
    const isCompleted = session.status === 'completed';
    const isActive = session.status === 'active';

    return (
        <div className={`bg-white rounded-xl p-5 border border-gray-100 shadow-sm transition-all duration-300 ${isCompleted ? 'opacity-60 grayscale-[0.5]' : 'hover:shadow-md'} ${isActive ? 'ring-2 ring-indigo-500 border-transparent' : ''}`}>
            <div className="flex justify-between items-start mb-3">
                <div className="flex items-center space-x-3">
                    <span className="text-sm font-bold text-gray-500 font-mono">
                        {session.start_time.slice(0, 5)}
                    </span>
                    {isActive && (
                        <span className="px-2 py-0.5 rounded text-xs font-bold bg-green-100 text-green-700 uppercase tracking-wide animate-pulse">
                            Active
                        </span>
                    )}
                    <span className={`px-2 py-0.5 rounded text-xs font-semibold tracking-wide uppercase ${session.color_theme === 'blue' ? 'bg-blue-100 text-blue-700' :
                        session.color_theme === 'purple' ? 'bg-purple-100 text-purple-700' :
                            'bg-gray-100 text-gray-700'
                        }`}>
                        {session.technique_name || session.block_type}
                    </span>
                </div>
                <button
                    onClick={() => setExpanded(!expanded)}
                    className="text-gray-400 hover:text-gray-600 focus:outline-none transition-transform"
                    style={{ transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)' }}
                >
                    <ChevronDown />
                </button>
            </div>

            <h3 className="text-lg font-bold text-gray-900 mb-1 leading-tight">
                {session.course_title}
            </h3>
            <p className="text-sm text-gray-500 font-medium mb-4">{session.course_code}</p>

            {session.technique_name && (
                <div className="mb-4 flex items-center space-x-2">
                    <span className="flex items-center space-x-1 text-xs font-semibold text-indigo-600 bg-indigo-50 px-2 py-1 rounded border border-indigo-100">
                        <BoltIcon />
                        <span>{session.technique_name}</span>
                    </span>
                </div>
            )}

            {expanded && (
                <div className="mb-5 p-3 bg-gray-50 rounded-lg text-sm space-y-2 border border-gray-100 animate-fadeIn">
                    {session.refinement_reason && (
                        <p className="text-gray-600">
                            <span className="font-semibold text-gray-700">Why:</span> {session.refinement_reason}
                        </p>
                    )}
                    {session.technique_details && (
                        <p className="text-gray-600">
                            <span className="font-semibold text-gray-700">How:</span> {session.technique_details}
                        </p>
                    )}
                    {session.academic_citation && (
                        <div className="pt-2 border-t border-gray-200/50">
                            <p className="text-xs text-gray-400 italic text-right">
                                {session.academic_citation}
                            </p>
                        </div>
                    )}
                </div>
            )}

            <div className="flex items-center justify-between mt-2">
                {isCompleted ? (
                    <div className="w-full flex items-center justify-center text-green-600 font-bold space-x-2 py-2.5 bg-green-50 rounded-lg">
                        <div className="bg-green-100 p-1 rounded-full">
                            <CheckIcon />
                        </div>
                        <span className="text-sm">Completed</span>
                    </div>
                ) : isActive ? (
                    <button
                        onClick={() => onComplete(session.id)}
                        className="w-full bg-green-600 hover:bg-green-700 text-white text-sm font-semibold py-2.5 rounded-lg transition-colors flex items-center justify-center space-x-2 shadow-sm"
                    >
                        <span>Finish Session</span>
                    </button>
                ) : (
                    <button
                        onClick={() => onStart(session.id)}
                        className="w-full bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold py-2.5 rounded-lg transition-colors flex items-center justify-center space-x-2"
                    >
                        <span>Start Session</span>
                    </button>
                )}
            </div>
        </div>
    );
};


// --- Main Schedule Component ---

const Schedule: React.FC = () => {
    const { user, semester } = useUser(); // Using UserContext data
    const [schedule, setSchedule] = useState<ScheduleData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSchedule = async () => {
            try {
                const data = await api.get<ScheduleData>('/schedule');
                setSchedule(data);
            } catch (err) {
                console.error("Failed to fetch schedule", err);
            } finally {
                setLoading(false);
            }
        };
        fetchSchedule();
    }, []);

    const handleComplete = async (block_id: number) => {
        // Optimistic UI update
        if (!schedule) return;

        const updatedToday = schedule.today_blocks.map(b =>
            b.id === block_id ? { ...b, status: 'completed' as const } : b
        );
        setSchedule({ ...schedule, today_blocks: updatedToday });

        try {
            await api.post(`/schedule/${block_id}/complete`, {});
        } catch (error) {
            console.error("Failed to complete session", error);
        }
    };

    const handleStart = async (block_id: number) => {
        if (!schedule) return;

        // Optimistic UI
        const updatedToday = schedule.today_blocks.map(b =>
            b.id === block_id ? { ...b, status: 'active' as const } : b
        );
        setSchedule({ ...schedule, today_blocks: updatedToday });

        try {
            await api.post(`/schedule/${block_id}/start`, {});
        } catch (error) {
            console.error("Failed to start session", error);
        }
    };

    if (loading) return (
        <LayoutContainer>
            <Sidebar />
            <MainContent>
                <div className="flex items-center justify-center h-64 text-gray-400 animate-pulse">
                    Loading your schedule...
                </div>
            </MainContent>
        </LayoutContainer>
    );

    if (!schedule) return (
        <LayoutContainer>
            <Sidebar />
            <MainContent>
                <div className="p-8 text-center text-red-500">
                    Unable to load schedule. Please try refreshing.
                </div>
            </MainContent>
        </LayoutContainer>
    );

    const { today_blocks, weekly_summary } = schedule;
    const username = user?.username || 'Student';
    const level = user?.level || '100';
    const avatarSrc = `https://ui-avatars.com/api/?name=${username}&background=random&color=fff&background=4F46E5`;

    // Define day order for the week grid
    const dayOrder = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

    return (
        <LayoutContainer>
            <Sidebar />
            <MainContent>
                <TopBar>
                    <Breadcrumb>
                        <BreadcrumbItem>
                            <span className="label">Semester</span>
                            <span className="value">{semester || '1'}</span>
                        </BreadcrumbItem>
                        <BreadcrumbItem>
                            <span className="label">Level</span>
                            <span className="value">{level}</span>
                        </BreadcrumbItem>
                    </Breadcrumb>

                    <UserProfile>
                        <span className="name">{username}</span>
                        <Avatar src={avatarSrc} alt="Profile" />
                    </UserProfile>
                </TopBar>

                <SectionTitle>Today's Schedule</SectionTitle>
                <CardContainer>
                    {today_blocks.length === 0 ? (
                        <div className="col-span-full p-8 border-2 border-dashed border-gray-200 rounded-xl text-center text-gray-500">
                            No sessions scheduled for today. Enjoy your free time!
                        </div>
                    ) : (
                        today_blocks.map(block => (
                            <SessionCard
                                key={block.id}
                                session={block}
                                onStart={handleStart}
                                onComplete={handleComplete}
                            />
                        ))
                    )}
                </CardContainer>

                <WeekSection>
                    <SectionTitle>For the Week</SectionTitle>
                    <InsightText>
                        Your schedule is optimized for varying difficulty. Use the specified techniques for maximum retention.
                    </InsightText>

                    <WeekGrid>
                        {dayOrder.map(day => (
                            <DayCard key={day}>
                                <DayHeader>{day.slice(0, 3)}</DayHeader>
                                <Timeline>
                                    {weekly_summary[day]?.length > 0 ? (
                                        weekly_summary[day].map((b, idx) => (
                                            <TimelineItem key={`${day}-${idx}`}>
                                                <Dot />
                                                <TimeLabel>{b.start_time.slice(0, 5)}</TimeLabel>
                                                <CourseLabel>{b.course_code}</CourseLabel>
                                                {b.technique_name && (
                                                    <span className="text-[10px] text-indigo-500 font-medium">
                                                        {b.technique_name.split(' ')[0]}
                                                    </span>
                                                )}
                                            </TimelineItem>
                                        ))
                                    ) : (
                                        <span className="text-xs text-gray-300 italic">Rest day</span>
                                    )}
                                </Timeline>
                            </DayCard>
                        ))}
                    </WeekGrid>
                </WeekSection>
            </MainContent>
        </LayoutContainer>
    );
};

export default Schedule;
