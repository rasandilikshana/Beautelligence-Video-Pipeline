import { useEffect, useState } from 'react';
import axios from 'axios';
import { Play } from 'lucide-react';

interface Video {
    id: string;
    status: string;
    video_file_path: string;
    prompt: string;
    created_at: string;
}

export const Gallery = () => {
    const [videos, setVideos] = useState<Video[]>([]);
    const [expandedAccords, setExpandedAccords] = useState<Record<string, boolean>>({});

    const toggleExpand = (id: string) => {
        setExpandedAccords(prev => ({ ...prev, [id]: !prev[id] }));
    };

    const fetchVideos = async () => {
        try {
            const { data } = await axios.get('http://localhost:8000/api/videos');
            setVideos(data);
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        fetchVideos();
        const interval = setInterval(fetchVideos, 10000);
        return () => clearInterval(interval);
    }, []);

    return (
        <section className="py-16 container mx-auto px-4">
            <div className="mb-12">
                <h2 className="text-3xl font-bold text-white mb-4">Your Personal Brand Gallery</h2>
                <p className="text-gray-400 max-w-2xl">
                    See how your <span className="text-secondary font-mono bg-secondary/10 px-2 py-0.5 rounded">Personal AI Workflow</span> maintains consistency.
                    Same template, same character style—just changing <strong>one keyword</strong> generates endless on-brand content.
                </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {videos.map((video) => (
                    <div key={video.id} className="bg-surface border border-white/5 rounded-2xl overflow-hidden group hover:border-white/20 transition-all">
                        <div className="aspect-[9/16] bg-black/50 relative">
                            {video.video_file_path ? (
                                <video
                                    src={`http://localhost:8000/data/videos/${video.video_file_path.split('/').pop()}`}
                                    className="w-full h-full object-cover"
                                    controls
                                    loop
                                    muted
                                    crossOrigin="anonymous"
                                />
                            ) : (
                                <div className="flex items-center justify-center h-full text-gray-600">
                                    Processing...
                                </div>
                            )}

                            {/* Overlay */}
                            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                <Play className="w-12 h-12 text-white fill-white" />
                            </div>
                        </div>

                        <div className="p-4">
                            <div className="mb-3">
                                <p className={`text-sm text-gray-300 ${expandedAccords[video.id] ? '' : 'line-clamp-2'}`} title="Click to view full template">
                                    {video.prompt}
                                </p>
                                <button
                                    onClick={() => toggleExpand(video.id)}
                                    className="text-xs text-primary hover:text-primary/80 mt-1 font-medium transition-colors"
                                >
                                    {expandedAccords[video.id] ? 'Show Less' : 'View Full Prompt Template'}
                                </button>
                            </div>
                            <div className="flex justify-between items-center text-xs text-gray-500">
                                <span>{new Date(video.created_at).toLocaleDateString()}</span>
                                <span className={`px-2 py-1 rounded-full ${video.status === 'complete' ? 'bg-green-500/10 text-green-400' : 'bg-yellow-500/10 text-yellow-400'
                                    }`}>
                                    {video.status}
                                </span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </section>
    );
};
