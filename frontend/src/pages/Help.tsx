import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';
import { HelpCircle, ChevronDown } from 'lucide-react';

const faqs = [
    {
        question: "What is the difference between Deep Work, Pomodoro, and Active Recall?",
        answer: "Deep Work assigns one long uninterrupted 90-minute block for complex courses. Pomodoro breaks your session into 25-minute focus periods with 5-minute breaks, repeated 2 to 4 times. Active Recall uses 45-minute sessions designed around retrieval practice — testing yourself rather than re-reading."
    },
    {
        question: "Why does my schedule look different from last week?",
        answer: "The system adapts your schedule every week based on how your sessions went. If you struggled with a course, it will allocate more time and adjust the technique. You can see the full reasoning on your Profile page under \"Why Your Schedule Changed.\""
    },
    {
        question: "Can I change my study preferences after onboarding?",
        answer: "Yes. Go to Settings and update your peak study time, focus length, environment, or learning style at any time. Changes take effect from your next adaptation."
    },
    {
        question: "What happens if I miss a session?",
        answer: "Nothing is penalised automatically. The adaptation engine works from completed session data — if a course has no sessions logged, it maintains the existing allocation unchanged."
    },
    {
        question: "Why do I need to upload my timetable?",
        answer: "The schedule generator avoids placing study blocks during your class hours. Without your timetable, it cannot know when you are unavailable and may schedule study time that conflicts with lectures."
    },
    {
        question: "How is my streak calculated?",
        answer: "Your streak increments only when you fully complete at least one session on a given day. Sessions ended early do not count toward your streak."
    },
    {
        question: "What does the XP and badge system do?",
        answer: "XP is awarded for completed sessions based on duration and focus quality. Badges (Novice → Apprentice → Scholar → Expert → Master → Legend) are unlocked at XP thresholds and reflect your overall consistency."
    },
    {
        question: "Can I use the app on my phone?",
        answer: "Yes. Open the app URL in your phone's browser while connected to the same network as the server."
    }
];

const AccordionItem: React.FC<{ question: string, answer: string }> = ({ question, answer }) => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div className="border border-gray-200 rounded-xl mb-4 overflow-hidden bg-white shadow-sm">
            <button 
                onClick={() => setIsOpen(!isOpen)}
                className="w-full flex items-center justify-between p-5 text-left bg-gray-50 hover:bg-gray-100 transition-colors focus:outline-none"
            >
                <span className="font-semibold text-gray-900">{question}</span>
                <ChevronDown className={`text-gray-500 transition-transform duration-200 flex-shrink-0 ml-4 ${isOpen ? 'rotate-180' : ''}`} size={20} />
            </button>
            <div 
                className="transition-all duration-300 ease-in-out"
                style={{ maxHeight: isOpen ? '500px' : '0px', opacity: isOpen ? 1 : 0 }}
            >
                <div className="p-5 text-gray-600 text-sm leading-relaxed border-t border-gray-100 bg-white">
                    {answer}
                </div>
            </div>
        </div>
    );
};

const Help: React.FC = () => {
    return (
        <div className="flex h-screen bg-white font-sans text-gray-900">
            <Sidebar />

            <div className="flex-1 md:py-8 py-16 pr-4 md:pr-8 pl-4 md:pl-[75px] overflow-y-auto w-full">
                <div className="max-w-3xl mx-auto">
                    <header className="mb-10 flex items-center space-x-3">
                        <HelpCircle className="text-gray-900" size={28} />
                        <h1 className="text-2xl font-bold text-gray-900">Help Center</h1>
                    </header>

                    {/* Part 1: Quick Start Guide */}
                    <section className="mb-12">
                        <h2 className="text-xl font-bold text-gray-900 mb-6">Quick Start Guide</h2>
                        <div className="space-y-6">
                            <div className="flex">
                                <div className="flex-shrink-0 mr-4">
                                    <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold flex items-center justify-center">1</div>
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900 mb-1">Complete Onboarding</h3>
                                    <p className="text-gray-600 text-sm">Fill in your details, select your courses, choose a study template, and set your preferences. This takes about 3 minutes.</p>
                                </div>
                            </div>
                            <div className="flex">
                                <div className="flex-shrink-0 mr-4">
                                    <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold flex items-center justify-center">2</div>
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900 mb-1">Upload Your Timetable</h3>
                                    <p className="text-gray-600 text-sm">Go to the Schedule page and upload your official Nile University timetable (.xlsx). This ensures your study blocks never clash with your classes.</p>
                                </div>
                            </div>
                            <div className="flex">
                                <div className="flex-shrink-0 mr-4">
                                    <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold flex items-center justify-center">3</div>
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900 mb-1">Generate Your Schedule</h3>
                                    <p className="text-gray-600 text-sm">Your personalised weekly schedule is generated automatically based on your courses, preferences, and class times.</p>
                                </div>
                            </div>
                            <div className="flex">
                                <div className="flex-shrink-0 mr-4">
                                    <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold flex items-center justify-center">4</div>
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900 mb-1">Start a Session</h3>
                                    <p className="text-gray-600 text-sm">Click any schedule block to start a study session. The timer will guide you through your technique — Pomodoro, Deep Work, or Active Recall.</p>
                                </div>
                            </div>
                            <div className="flex">
                                <div className="flex-shrink-0 mr-4">
                                    <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold flex items-center justify-center">5</div>
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900 mb-1">Log Your Session</h3>
                                    <p className="text-gray-600 text-sm">After each session, rate how it went. This data teaches the system about your performance over time.</p>
                                </div>
                            </div>
                            <div className="flex">
                                <div className="flex-shrink-0 mr-4">
                                    <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold flex items-center justify-center">6</div>
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900 mb-1">Adapt Weekly</h3>
                                    <p className="text-gray-600 text-sm">At the end of the week, the system analyses your sessions and adjusts next week's plan automatically.</p>
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* Part 2: FAQ */}
                    <section className="mb-12">
                        <h2 className="text-xl font-bold text-gray-900 mb-6">Frequently Asked Questions</h2>
                        <div>
                            {faqs.map((faq, index) => (
                                <AccordionItem key={index} question={faq.question} answer={faq.answer} />
                            ))}
                        </div>
                    </section>
                </div>
            </div>
        </div>
    );
};

export default Help;
