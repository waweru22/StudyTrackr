import React from 'react';
import Sidebar from '../components/Sidebar';
import { Lightbulb, BookOpen, Layers, ShieldCheck, } from 'lucide-react';

interface StudyTip {
    id: number;
    title: string;
    rating: number;
    summary: string;
    howToUse: string[];
    whyItWorks: string[];
    bestFor: string[];
    commonMistakes: string[];
    combinations: string[];
    example?: string;
}

const studyTips: StudyTip[] = [
    {
        id: 1,
        title: 'Pomodoro Technique',
        rating: 3,
        summary: 'A time management method that breaks work into focused intervals (typically 25 minutes) separated by short breaks, creating structured productivity cycles that maintain concentration while preventing mental fatigue and burnout.',
        howToUse: [
            'Pick one clear task (not "study DBMS" → "revise normalization").',
            'Set a timer for 25 minutes and work with zero distractions.',
            'Take a 5-minute break after each session.',
            'After 4 cycles, take a longer break of 15–30 minutes.',
        ],
        whyItWorks: [
            'Uses time pressure to force focus.',
            'Prevents mental fatigue by breaking work into manageable chunks.',
            'Builds a consistent rhythm without letting tasks feel endless.',
        ],
        bestFor: ['Procrastination', 'Long study sessions', 'Staying disciplined'],
        commonMistakes: ['Studying passively without an active goal.', 'Using breaks for social media or distractions.', 'Choosing tasks that are too vague.'],
        combinations: ['Active Recall', 'Spaced Repetition', 'Feynman Technique'],
        example: 'Use 25/5 for beginners, 50/10 for deeper work, and track Pomodoros per subject.',
    },
    {
        id: 2,
        title: 'Active Recall',
        rating: 3,
        summary: 'An evidence-based learning technique that actively stimulates memory retrieval by testing yourself on information rather than passively reviewing notes, strengthening neural pathways and improving long-term retention.',
        howToUse: [
            'Close your notes and ask yourself specific questions.',
            'Say or write answers from memory.',
            'Check and correct yourself immediately.',
        ],
        whyItWorks: ['Strengthens retrieval pathways like training a muscle.', 'Exams test recall, not recognition.', 'Makes learning active instead of passive.'],
        bestFor: ['Exams', 'Memorization-heavy courses', 'Definitions and concepts'],
        commonMistakes: ['Looking at notes too quickly.', 'Mistaking familiarity for understanding.', 'Only rereading without retrieval practice.'],
        combinations: ['Pomodoro Technique', 'Spaced Repetition', 'Blurting Method'],
        example: 'Use flashcards, practice questions, or teach the concept out loud.',
    },
    {
        id: 3,
        title: 'Spaced Repetition',
        rating: 2,
        summary: 'A learning technique that leverages the psychological spacing effect by reviewing material at gradually increasing intervals, optimizing memory consolidation and combating the natural forgetting curve for superior long-term knowledge retention.',
        howToUse: [
            'Review content on Day 1, Day 2, Day 4, Day 7, Day 14.',
            'Use spaced repetition tools like Anki or Quizlet.',
            'Add new cards gradually and keep review sessions focused.',
        ],
        whyItWorks: ['Targets the forgetting curve.', 'Reviews happen right before you forget.', 'Transforms short-term learning into durable retention.'],
        bestFor: ['Long-term retention', 'Learning languages', 'Large content volumes'],
        commonMistakes: ['Cramming instead of spacing.', 'Reviewing too often and wasting time.', 'Skipping the planned intervals.'],
        combinations: ['Active Recall', 'Pomodoro Technique', 'Chunking'],
        example: 'Anki is best; Quizlet is simpler for quick review.',
    },
    {
        id: 4,
        title: 'Feynman Technique',
        rating: 2,
        summary: 'A powerful learning method named after physicist Richard Feynman that involves explaining complex concepts in simple terms to identify knowledge gaps, promoting deep understanding rather than surface-level memorization.',
        howToUse: [
            'Study a topic fully.',
            'Explain it in simple terms as if teaching a 10-year-old.',
            'Identify gaps, relearn, and simplify again.',
        ],
        whyItWorks: ['Forces clarity instead of memorization.', 'Exposes fake understanding instantly.', 'Turns concepts into usable mental models.'],
        bestFor: ['Complex subjects', 'Math, programming, theory'],
        commonMistakes: ['Using jargon instead of simplification.', 'Memorizing definitions without understanding.', 'Skipping the gap-finding step.'],
        combinations: ['Active Recall', 'Chunking', 'Interleaving'],
        example: 'Record yourself explaining the topic or write a simple tutorial.',
    },
    {
        id: 5,
        title: 'Blurting Method',
        rating: 2,
        summary: 'A rapid assessment technique where you write down everything you can remember about a topic immediately after studying, then compare with your notes to identify knowledge gaps and reinforce learning through immediate feedback.',
        howToUse: [
            'Study a topic briefly.',
            'Close everything and write what you remember.',
            'Compare with notes and highlight missing points.',
        ],
        whyItWorks: ['Combines active recall with self-testing.', 'Shows exactly what you still need to learn.', 'Reveals weak areas quickly.'],
        bestFor: ['Quick revision', 'Identifying weak areas'],
        commonMistakes: ['Writing while checking notes.', 'Not correcting errors afterward.', 'Skipping the comparison step.'],
        combinations: ['Active Recall', 'Pomodoro Technique', 'Spaced Repetition'],
        example: 'Topic: OSI model → write layers, then fill gaps from notes.',
    },
    {
        id: 6,
        title: 'Chunking',
        rating: 2,
        summary: 'A cognitive strategy that organizes information into meaningful groups or patterns, reducing cognitive load and making complex information more manageable and memorable by leveraging the brain\'s preference for structured patterns over isolated facts.',
        howToUse: [
            'Break big information into categories, patterns, or themes.',
            'Create meaningful groups instead of memorizing isolated facts.',
            'Review each chunk as a unit.',
        ],
        whyItWorks: ['Brain prefers patterns over randomness.', 'Reduces cognitive load by organizing knowledge.', 'Makes large subjects easier to recall.'],
        bestFor: ['Overwhelming topics', 'Structured subjects', 'Large data sets'],
        commonMistakes: ['Making chunks too large.', 'Creating groups that don\'t connect.', 'Memorizing chunks without understanding their relationships.'],
        combinations: ['Feynman Technique', 'Interleaving', 'Spaced Repetition'],
        example: 'Networking facts → group by layers, protocols, and devices.',
    },
    {
        id: 7,
        title: 'Interleaving',
        rating: 3,
        summary: 'An advanced learning strategy that mixes different topics or problem types within a single study session, improving pattern recognition, problem-solving skills, and the ability to discriminate between similar concepts.',
        howToUse: [
            'Switch topics every 20–40 minutes.',
            'Mix different problem types within a session.',
            'Use interleaving after you already understand the basics.',
        ],
        whyItWorks: ['Improves adaptability and problem-solving.', 'Helps the brain recognize patterns across topics.', 'Prevents mental stagnation from one-topic repetition.'],
        bestFor: ['Math', 'Coding', 'Problem-solving subjects'],
        commonMistakes: ['Switching too fast and losing depth.', 'Using interleaving before basic mastery.', 'Treating topics as unrelated rather than connected.'],
        combinations: ['Chunking', 'Feynman Technique', 'Active Recall'],
        example: 'Study SQL, networking, and algorithms in the same block instead of only one subject.',
    },
    {
        id: 8,
        title: 'SQ3R Method',
        rating: 1,
        summary: 'A structured reading comprehension technique (Survey, Question, Read, Recite, Review) that transforms passive reading into an active learning process, though less effective than modern evidence-based methods for most learners.',
        howToUse: [
            'Survey: skim headings and structure.',
            'Question: ask what each section will teach.',
            'Read actively with a focus on answers.',
            'Recite: summarize from memory.',
            'Review key points afterward.',
        ],
        whyItWorks: ['Makes reading active instead of passive.', 'Prepares your brain for retention before deep study.', 'Helps you remember textbook material more efficiently.'],
        bestFor: ['Textbooks', 'Theory-heavy courses'],
        commonMistakes: ['Highlighting everything.', 'Reading without questioning.', 'Skipping the review step.'],
        combinations: ['Active Recall', 'Chunking'],
        example: 'Use SQ3R on one textbook chapter, then apply active recall afterward.',
    },
];

const StudyTips: React.FC = () => {
    const getRatingColor = (rating: number) => {
        switch (rating) {
            case 1:
                return 'bg-red-100 text-red-700 border border-red-300';
            case 2:
                return 'bg-yellow-100 text-yellow-700 border border-yellow-300';
            case 3:
                return 'bg-green-100 text-green-700 border border-green-300';
            default:
                return 'bg-slate-100 text-slate-600';
        }
    };
    return (
        <div className="flex h-screen bg-slate-50 font-sans text-slate-900">
            <Sidebar />

            <main className="flex-1 ml-64 py-8 pr-8 pl-[75px] overflow-y-auto">
                <header className="mb-10">
                    <div className="inline-flex items-center gap-3 rounded-full bg-white px-4 py-2 shadow-sm border border-slate-200">
                        <Lightbulb className="text-amber-500" size={20} />
                        <span className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Study System</span>
                    </div>
                    <h1 className="mt-6 text-2xl font-bold text-slate-900">Study Tips & Learning Workflow</h1>
                    <p className="mt-3 max-w-3xl text-sm text-slate-600 leading-7">
                        Deeply practical study techniques for software engineering students. Each method is explained with real steps, why it works, common pitfalls, and ideal use cases.
                    </p>
                    <div className="mt-4 p-4 bg-slate-100 rounded-lg">
                        <h3 className="text-sm font-semibold text-slate-800 mb-2">Rating System:</h3>
                        <div className="flex gap-4 text-xs text-slate-600">
                            <span><span className="font-bold text-red-600">1</span> = Lower rated technique</span>
                            <span><span className="font-bold text-yellow-600">2</span> = Medium rated technique</span>
                            <span><span className="font-bold text-green-600">3</span> = Higher rated technique</span>
                        </div>
                    </div>
                </header>

                <section className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
                    <div className="space-y-6">
                        {studyTips.map((tip) => (
                            <article key={tip.id} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                                <div className="flex items-start gap-4">
                                    <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-700 font-bold text-lg">
                                        {tip.id}
                                    </div>
                                    <div>
                                        <div className="flex items-center gap-3 text-slate-500 mb-2">
                                            <span className="text-sm font-semibold uppercase tracking-[0.18em]">Technique</span>
                                            <span className={`rounded-full px-3 py-1 text-xs font-medium ${getRatingColor(tip.rating)}`}>
                                                Rating: {tip.rating} {tip.rating === 1 ? '(Lower)' : tip.rating === 2 ? '(Medium)' : '(Higher)'}
                                            </span>
                                        </div>
                                        <h2 className="text-xl font-semibold text-slate-900">{tip.title}</h2>
                                    </div>
                                </div>

                                <p className="mt-5 text-sm leading-7 text-slate-600">{tip.summary}</p>

                                <div className="mt-6 grid gap-4 md:grid-cols-2">
                                    <div className="rounded-2xl bg-slate-50 p-4">
                                        <p className="text-xs uppercase tracking-[0.18em] text-slate-500 mb-3">How to use it</p>
                                        <ul className="space-y-2 text-sm text-slate-600 list-disc list-inside">
                                            {tip.howToUse.map((item) => (
                                                <li key={item}>{item}</li>
                                            ))}
                                        </ul>
                                    </div>

                                    <div className="rounded-2xl bg-slate-50 p-4">
                                        <p className="text-xs uppercase tracking-[0.18em] text-slate-500 mb-3">Why it works</p>
                                        <ul className="space-y-2 text-sm text-slate-600 list-disc list-inside">
                                            {tip.whyItWorks.map((item) => (
                                                <li key={item}>{item}</li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>

                                <div className="mt-6 grid gap-4 md:grid-cols-2">
                                    <div className="rounded-2xl bg-slate-50 p-4">
                                        <p className="text-xs uppercase tracking-[0.18em] text-slate-500 mb-3">Best for</p>
                                        <ul className="space-y-2 text-sm text-slate-600 list-disc list-inside">
                                            {tip.bestFor.map((item) => (
                                                <li key={item}>{item}</li>
                                            ))}
                                        </ul>
                                    </div>
                                    <div className="rounded-2xl bg-slate-50 p-4">
                                        <p className="text-xs uppercase tracking-[0.18em] text-slate-500 mb-3">Common mistakes</p>
                                        <ul className="space-y-2 text-sm text-slate-600 list-disc list-inside">
                                            {tip.commonMistakes.map((item) => (
                                                <li key={item}>{item}</li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>

                                <div className="mt-6 rounded-2xl bg-blue-50 p-4">
                                    <p className="text-xs uppercase tracking-[0.18em] text-slate-500 mb-3">Works well with</p>
                                    <div className="flex flex-wrap gap-2">
                                        {tip.combinations.map((combo) => (
                                            <span key={combo} className="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700">
                                                {combo}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                {tip.example ? (
                                    <div className="mt-6 rounded-2xl bg-slate-900 p-4 text-sm text-slate-100">
                                        <p className="font-semibold mb-2">Example</p>
                                        <p>{tip.example}</p>
                                    </div>
                                ) : null}
                            </article>
                        ))}
                    </div>

                    <aside className="space-y-6">
                        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                            <div className="flex items-center gap-3 text-slate-900 mb-4">
                                <div className="w-5 h-5 rounded-full bg-green-500 flex items-center justify-center">
                                    <span className="text-white text-xs font-bold">B</span>
                                </div>
                                <div>
                                    <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Beginner combos</p>
                                    <h3 className="text-lg font-semibold">Start with these foundations</h3>
                                </div>
                            </div>
                            <ul className="space-y-2 text-sm text-slate-600">
                                <li className="flex items-start gap-2">
                                    <span className="text-green-500 mt-1">•</span>
                                    <span><strong>Pomodoro + Active Recall:</strong> Build focus and memory habits</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="text-green-500 mt-1">•</span>
                                    <span><strong>Chunking + Blurting:</strong> Organize and test your knowledge</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="text-green-500 mt-1">•</span>
                                    <span><strong>SQ3R + Active Recall:</strong> Transform reading into learning</span>
                                </li>
                            </ul>
                        </div>

                        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                            <div className="flex items-center gap-3 text-slate-900 mb-4">
                                <div className="w-5 h-5 rounded-full bg-yellow-500 flex items-center justify-center">
                                    <span className="text-white text-xs font-bold">I</span>
                                </div>
                                <div>
                                    <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Intermediate combos</p>
                                    <h3 className="text-lg font-semibold">Build deeper understanding</h3>
                                </div>
                            </div>
                            <ul className="space-y-2 text-sm text-slate-600">
                                <li className="flex items-start gap-2">
                                    <span className="text-yellow-500 mt-1">•</span>
                                    <span><strong>Active Recall + Spaced Repetition:</strong> Strengthen long-term retention</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="text-yellow-500 mt-1">•</span>
                                    <span><strong>Feynman + Chunking:</strong> Master complex concepts</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="text-yellow-500 mt-1">•</span>
                                    <span><strong>Pomodoro + Blurting:</strong> Efficient revision cycles</span>
                                </li>
                            </ul>
                        </div>

                        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                            <div className="flex items-center gap-3 text-slate-900 mb-4">
                                <div className="w-5 h-5 rounded-full bg-red-500 flex items-center justify-center">
                                    <span className="text-white text-xs font-bold">E</span>
                                </div>
                                <div>
                                    <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Expert combos</p>
                                    <h3 className="text-lg font-semibold">Advanced learning mastery</h3>
                                </div>
                            </div>
                            <ul className="space-y-2 text-sm text-slate-600">
                                <li className="flex items-start gap-2">
                                    <span className="text-red-500 mt-1">•</span>
                                    <span><strong>Interleaving + Active Recall:</strong> Pattern recognition mastery</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="text-red-500 mt-1">•</span>
                                    <span><strong>Feynman + Interleaving:</strong> Complex problem-solving</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="text-red-500 mt-1">•</span>
                                    <span><strong>All techniques combined:</strong> Complete learning system</span>
                                </li>
                            </ul>
                        </div>

                        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                            <div className="flex items-center gap-3 text-slate-900 mb-4">
                                <Layers size={20} className="text-sky-500" />
                                <div>
                                    <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Daily workflow</p>
                                    <h3 className="text-lg font-semibold">Example study session</h3>
                                </div>
                            </div>
                            <ol className="space-y-3 text-sm leading-7 text-slate-600 list-decimal list-inside">
                                <li>Pomodoro 1 – Learn the topic with SQ3R and quick notes.</li>
                                <li>Pomodoro 2 – Use Active Recall or flashcards.</li>
                                <li>Pomodoro 3 – Blurting to identify gaps.</li>
                                <li>Break.</li>
                                <li>Pomodoro 4 – Feynman explain or teach it back.</li>
                                <li>Next day – Spaced Repetition review.</li>
                            </ol>
                        </div>

                        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                            <div className="flex items-center gap-3 text-slate-900 mb-4">
                                <ShieldCheck size={20} className="text-emerald-500" />
                                <div>
                                    <p className="text-xs uppercase tracking-[0.18em] text-slate-500">What matters</p>
                                    <h3 className="text-lg font-semibold">The real key</h3>
                                </div>
                            </div>
                            <ul className="space-y-3 text-sm leading-7 text-slate-600 list-disc list-inside">
                                <li>Struggle + recall + repetition = mastery.</li>
                                <li>Reading is not studying.</li>
                                <li>Highlighting is not learning.</li>
                                <li>Time spent is not progress; effort quality is.</li>
                            </ul>
                        </div>
                    </aside>
                </section>

                <section className="mt-10 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                    <div className="flex items-center gap-3 text-slate-900 mb-4">
                        <BookOpen size={20} className="text-indigo-500" />
                        <h2 className="text-xl font-semibold">Quick comparison</h2>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full min-w-[680px] border-collapse text-sm">
                            <thead>
                                <tr className="border-b border-slate-200 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                                    <th className="py-3 px-4">Technique</th>
                                    <th className="py-3 px-4">Focus</th>
                                    <th className="py-3 px-4">Best Use Case</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr className="border-b border-slate-100 hover:bg-slate-50">
                                    <td className="py-3 px-4">Pomodoro</td>
                                    <td className="py-3 px-4">Time management</td>
                                    <td className="py-3 px-4">Staying focused</td>
                                </tr>
                                <tr className="border-b border-slate-100 hover:bg-slate-50">
                                    <td className="py-3 px-4">Active Recall</td>
                                    <td className="py-3 px-4">Memory</td>
                                    <td className="py-3 px-4">Exams</td>
                                </tr>
                                <tr className="border-b border-slate-100 hover:bg-slate-50">
                                    <td className="py-3 px-4">Spaced Repetition</td>
                                    <td className="py-3 px-4">Long-term memory</td>
                                    <td className="py-3 px-4">Continuous learning</td>
                                </tr>
                                <tr className="border-b border-slate-100 hover:bg-slate-50">
                                    <td className="py-3 px-4">Feynman</td>
                                    <td className="py-3 px-4">Understanding</td>
                                    <td className="py-3 px-4">Complex topics</td>
                                </tr>
                                <tr className="border-b border-slate-100 hover:bg-slate-50">
                                    <td className="py-3 px-4">Blurting</td>
                                    <td className="py-3 px-4">Self-testing</td>
                                    <td className="py-3 px-4">Revision</td>
                                </tr>
                                <tr className="border-b border-slate-100 hover:bg-slate-50">
                                    <td className="py-3 px-4">Chunking</td>
                                    <td className="py-3 px-4">Organization</td>
                                    <td className="py-3 px-4">Large info</td>
                                </tr>
                                <tr className="border-b border-slate-100 hover:bg-slate-50">
                                    <td className="py-3 px-4">Interleaving</td>
                                    <td className="py-3 px-4">Problem solving</td>
                                    <td className="py-3 px-4">Math / coding</td>
                                </tr>
                                <tr className="hover:bg-slate-50">
                                    <td className="py-3 px-4">SQ3R</td>
                                    <td className="py-3 px-4">Reading</td>
                                    <td className="py-3 px-4">Textbooks</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </section>
            </main>
        </div>
    );
};

export default StudyTips;