import { useEffect, useState } from 'react';
import axios from 'axios';
import { Activity, Database, CheckCircle } from 'lucide-react';

interface Quota {
    videos_generated: number;
    videos_limit: number;
    videos_remaining: number;
    can_generate: boolean;
}

export const Status = () => {
    const [quota, setQuota] = useState<Quota | null>(null);

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const { data } = await axios.get('http://localhost:8000/api/status');
                setQuota(data.quota);
            } catch (e) {
                console.error("Failed to fetch status");
            }
        };

        fetchStatus();
        const interval = setInterval(fetchStatus, 30000); // Pulse every 30s
        return () => clearInterval(interval);
    }, []);

    if (!quota) return null;

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-surface border border-white/5 rounded-2xl p-6 flex flex-col justify-between hover:border-primary/20 transition-all group">
                    <div className="flex items-center gap-3 text-gray-400 mb-4 group-hover:text-primary transition-colors">
                        <Activity className="w-5 h-5" />
                        <h3 className="font-medium">Daily Quota</h3>
                    </div>
                    <div className="text-3xl font-bold text-white mb-2">
                        {quota.videos_generated} / {quota.videos_limit}
                    </div>
                    <div className="width-full bg-gray-800 h-1.5 rounded-full overflow-hidden">
                        <div
                            className="bg-primary h-full transition-all duration-1000"
                            style={{ width: `${(quota.videos_generated / quota.videos_limit) * 100}%` }}
                        />
                    </div>
                </div>

                <div className="bg-surface border border-white/5 rounded-2xl p-6 flex flex-col justify-between hover:border-green-500/20 transition-all group">
                    <div className="flex items-center gap-3 text-gray-400 mb-4 group-hover:text-green-400 transition-colors">
                        <CheckCircle className="w-5 h-5" />
                        <h3 className="font-medium">System Status</h3>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                        <span className="text-xl font-medium text-white">Online</span>
                    </div>
                    <p className="text-sm text-gray-500 mt-2">API & Agents Active</p>
                </div>

                <div className="bg-surface border border-white/5 rounded-2xl p-6 flex flex-col justify-between hover:border-yellow-500/20 transition-all group">
                    <div className="flex items-center gap-3 text-gray-400 mb-4 group-hover:text-yellow-400 transition-colors">
                        <Database className="w-5 h-5" />
                        <h3 className="font-medium">Remaining</h3>
                    </div>
                    <div className="text-3xl font-bold text-white">
                        {quota.videos_remaining}
                    </div>
                    <p className="text-sm text-gray-500 mt-1">Generations available today</p>
                </div>
            </div>
        </div>
    );
};
