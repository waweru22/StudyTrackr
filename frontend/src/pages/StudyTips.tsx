import React, { useEffect, useState } from 'react';
import Sidebar from '../components/Sidebar';
import { api } from '../api/client';
import { Lightbulb, Code, BookOpen } from 'lucide-react';

interface Tip {
    id: number;
    title: string;
    description: string;
    use_case: string;
    se_tip: string;
}

const StudyTips: React.FC = () => {
    const [tips, setTips] = useState<Tip[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get<Tip[]>('/resources/tips')
            .then(data => setTips(data))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, []);

    return (
        <div className="flex h-screen bg-white font-sans text-gray-900">
            <Sidebar />

            <div className="flex-1 ml-64 py-8 pr-8 pl-[75px] overflow-y-auto">
                <header className="mb-10">
                    <h1 className="text-2xl font-bold text-gray-900">Study Tips Library</h1>
                    <p className="text-gray-500 mt-2">Optimization techniques with a Software Engineering twist.</p>
                </header>

                {loading ? (
                    <div>Loading knowledge base...</div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {tips.map((tip) => (
                            <div key={tip.id} className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow flex flex-col h-full">
                                <div className="mb-4">
                                    <div className="h-10 w-10 rounded-full bg-yellow-100 flex items-center justify-center mb-3">
                                        <Lightbulb className="text-yellow-600" size={20} />
                                    </div>
                                    <h3 className="text-lg font-bold text-gray-900">{tip.title}</h3>
                                </div>

                                <p className="text-sm text-gray-600 mb-4 flex-grow">{tip.description}</p>

                                <div className="space-y-3 mt-auto">
                                    <div className="bg-blue-50 p-3 rounded-lg">
                                        <p className="text-xs font-bold text-blue-700 uppercase mb-1 flex items-center">
                                            <BookOpen size={12} className="mr-1" /> Best Use Case
                                        </p>
                                        <p className="text-xs text-blue-900">{tip.use_case}</p>
                                    </div>

                                    <div className="bg-gray-900 p-3 rounded-lg">
                                        <p className="text-xs font-bold text-green-400 uppercase mb-1 flex items-center">
                                            <Code size={12} className="mr-1" /> SE Analogy
                                        </p>
                                        <p className="text-xs text-gray-300 font-mono">"{tip.se_tip}"</p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default StudyTips;
