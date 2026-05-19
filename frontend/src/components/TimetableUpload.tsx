import React, { useState } from 'react';
import { BASE_URL } from '../api/client';

export interface ClassEntry {
    course_code: string;
    course_name: string;
    day: string;
    start_time: string;
    end_time: string;
    venue: string | null;
    section: string | null;
}

interface UploadResult {
    message: string;
    entries_saved: number;
    classes_detected: ClassEntry[];
    skipped: number;
}

interface TimetableUploadProps {
    onUploadComplete: (classes: ClassEntry[]) => void;
}

const TimetableUpload: React.FC<TimetableUploadProps> = ({ onUploadComplete }) => {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState<UploadResult | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('timetable', file);

        const token = sessionStorage.getItem('token');

        try {
            const response = await fetch(`${BASE_URL}/timetable/upload`, {
                method: 'POST',
                headers: {
                    ...(token ? { Authorization: `Bearer ${token}` } : {}),
                },
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                setError(data.error || data.message || 'Upload failed');
                return;
            }

            setResult(data);
        } catch {
            setError('Network error. Please try again.');
        } finally {
            setUploading(false);
        }
    };

    const handleRetry = () => {
        setError(null);
        setResult(null);
        setFile(null);
    };

    if (result) {
        const classes = result.classes_detected || [];
        return (
            <div className="space-y-4">
                <p className="text-sm text-gray-700 font-medium">
                    We found {classes.length} class{classes.length !== 1 ? 'es' : ''} in your timetable:
                </p>
                {classes.length > 0 ? (
                    <div className="overflow-x-auto border border-gray-200 rounded-lg">
                        <table className="min-w-full text-sm">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-3 py-2 text-left font-semibold text-gray-600">Course Code</th>
                                    <th className="px-3 py-2 text-left font-semibold text-gray-600">Course Name</th>
                                    <th className="px-3 py-2 text-left font-semibold text-gray-600">Day</th>
                                    <th className="px-3 py-2 text-left font-semibold text-gray-600">Time</th>
                                    <th className="px-3 py-2 text-left font-semibold text-gray-600">Venue</th>
                                </tr>
                            </thead>
                            <tbody>
                                {classes.map((cls, idx) => (
                                    <tr key={idx} className="border-t border-gray-100">
                                        <td className="px-3 py-2 font-mono">{cls.course_code}</td>
                                        <td className="px-3 py-2">{cls.course_name}</td>
                                        <td className="px-3 py-2">{cls.day}</td>
                                        <td className="px-3 py-2">{cls.start_time} – {cls.end_time}</td>
                                        <td className="px-3 py-2">{cls.venue || '—'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <p className="text-sm text-amber-700 bg-amber-50 border border-amber-100 rounded-lg p-3">
                        No classes matched your enrolled courses. Check that your course codes match the timetable file.
                    </p>
                )}
                <button
                    type="button"
                    onClick={() => onUploadComplete(classes)}
                    className="w-full bg-blue-800 hover:bg-blue-900 text-white font-semibold py-2.5 px-4 rounded-lg text-sm transition-colors"
                >
                    Confirm and Generate Schedule
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <input
                type="file"
                accept=".xlsx"
                onChange={e => setFile(e.target.files?.[0] || null)}
                className="block w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-50 file:text-blue-800 file:font-semibold hover:file:bg-blue-100"
            />

            {error && (
                <div className="space-y-3">
                    <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg p-3">
                        {error}
                    </p>
                    <button
                        type="button"
                        onClick={handleRetry}
                        className="text-sm font-semibold text-blue-800 hover:text-blue-900"
                    >
                        Try again
                    </button>
                </div>
            )}

            <button
                type="button"
                onClick={handleUpload}
                disabled={!file || uploading}
                className="w-full bg-blue-800 hover:bg-blue-900 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-2.5 px-4 rounded-lg text-sm transition-colors"
            >
                {uploading ? 'Uploading…' : 'Upload Timetable'}
            </button>
        </div>
    );
};

export default TimetableUpload;

