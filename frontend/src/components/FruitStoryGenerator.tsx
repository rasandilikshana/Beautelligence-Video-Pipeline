import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Loader2, CheckCircle, XCircle, ChevronRight, Heart, Zap, RefreshCw } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL, api } from '../config/api';

// Types
interface FruitCharacter {
    key: string;
    name: string;
    archetype: string;
    personality: string;
    core_message: string;
    color_palette: string;
    health_benefits: string[];
}

interface StoryEpisode {
    episode_number: number;
    title: string;
    scene_description: string;
    dialogue: string;
    emotion: string;
    action: string;
    health_message: string;
    status: string;
    video_url?: string;
    video_path?: string;
}

interface StoryResponse {
    story_id: string;
    fruit_type: string;
    fruit_name: string;
    character_description: string;
    color_palette: string;
    episodes: StoryEpisode[];
    overall_status: string;
    videos_completed: number;
    videos_total: number;
}

// Fruit emoji mapping
const FRUIT_EMOJIS: Record<string, string> = {
    apple: '🍎',
    banana: '🍌',
    strawberry: '🍓',
    mango: '🥭',
    orange: '🍊',
    grape: '🍇',
    watermelon: '🍉',
    kiwi: '🥝',
};

// Episode status icons
const StatusIcon = ({ status }: { status: string }) => {
    switch (status) {
        case 'complete':
            return <CheckCircle className="w-5 h-5 text-green-400" />;
        case 'generating':
            return <Loader2 className="w-5 h-5 text-primary animate-spin" />;
        case 'failed':
            return <XCircle className="w-5 h-5 text-red-400" />;
        default:
            return <div className="w-5 h-5 rounded-full border-2 border-gray-600" />;
    }
};

export const FruitStoryGenerator = () => {
    // State
    const [characters, setCharacters] = useState<FruitCharacter[]>([]);
    const [selectedChar, setSelectedChar] = useState<FruitCharacter | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isGenerating, setIsGenerating] = useState(false);
    const [currentStory, setCurrentStory] = useState<StoryResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [pollInterval, setPollInterval] = useState<ReturnType<typeof setInterval> | null>(null);

    // Fetch characters on mount
    useEffect(() => {
        fetchCharacters();
        return () => {
            if (pollInterval) clearInterval(pollInterval);
        };
    }, []);

    const fetchCharacters = async () => {
        try {
            const response = await axios.get(api.storyCharacters());
            setCharacters(response.data);
            if (response.data.length > 0) {
                setSelectedChar(response.data[0]);
            }
        } catch (err) {
            setError('Failed to load characters. Is the API running?');
        } finally {
            setIsLoading(false);
        }
    };

    const generateStory = async () => {
        if (!selectedChar) return;

        setIsGenerating(true);
        setError(null);
        setCurrentStory(null);

        try {
            const response = await axios.post(api.storyGenerate(), {
                fruit_type: selectedChar.key,
                mock: false,
            });

            setCurrentStory(response.data);

            // Start polling for status
            const interval = setInterval(async () => {
                try {
                    const statusResponse = await axios.get(
                        api.storyStatus(response.data.story_id)
                    );

                    const updatedEpisodes = statusResponse.data.episodes;
                    setCurrentStory(prev => prev ? {
                        ...prev,
                        episodes: updatedEpisodes,
                        overall_status: statusResponse.data.overall_status,
                        videos_completed: updatedEpisodes.filter((e: StoryEpisode) => e.status === 'complete').length,
                    } : null);

                    // Stop polling when complete or failed
                    if (statusResponse.data.overall_status === 'complete' ||
                        statusResponse.data.overall_status === 'partial_failure') {
                        clearInterval(interval);
                        setPollInterval(null);
                        setIsGenerating(false);
                    }
                } catch (err) {
                    console.error('Polling error:', err);
                }
            }, 5000); // Poll every 5 seconds

            setPollInterval(interval);

        } catch (err) {
            setError('Failed to start story generation. Please try again.');
            setIsGenerating(false);
        }
    };

    const resetGenerator = () => {
        if (pollInterval) clearInterval(pollInterval);
        setCurrentStory(null);
        setIsGenerating(false);
        setError(null);
    };

    if (isLoading) {
        return (
            <section className="py-20 container mx-auto px-4">
                <div className="max-w-4xl mx-auto flex items-center justify-center h-64">
                    <Loader2 className="w-8 h-8 text-primary animate-spin" />
                </div>
            </section>
        );
    }

    return (
        <section id="story-generator" className="py-20 container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <motion.div
                    className="text-center mb-12"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                >
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-pink-500/10 to-purple-500/10 border border-pink-500/20 mb-4">
                        <Heart className="w-4 h-4 text-pink-500" />
                        <span className="text-sm text-pink-400">Emotionally Intelligent Content</span>
                    </div>
                    <h2 className="text-4xl font-bold text-white mb-4">
                        Fruit Character Story Generator
                    </h2>
                    <p className="text-gray-400 max-w-2xl mx-auto">
                        Create educational content that connects with your audience through lovable fruit characters.
                        Each story is designed with psychology-based emotional hooks and health messaging.
                    </p>
                </motion.div>

                {/* Main Content */}
                <AnimatePresence mode="wait">
                    {!currentStory ? (
                        /* Character Selection UI */
                        <motion.div
                            key="selection"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                        >
                            {/* Character Grid */}
                            <motion.div
                                className="bg-surface border border-white/10 rounded-3xl p-8 mb-6"
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                            >
                                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                    <Zap className="w-5 h-5 text-secondary" />
                                    Select Your Character
                                </h3>

                                <div className="grid grid-cols-4 sm:grid-cols-8 gap-3 mb-6">
                                    {characters.map((char) => (
                                        <button
                                            key={char.key}
                                            onClick={() => setSelectedChar(char)}
                                            className={`
                                                aspect-square rounded-2xl text-4xl flex items-center justify-center
                                                transition-all duration-200 hover:scale-110
                                                ${selectedChar?.key === char.key
                                                    ? 'bg-primary/20 border-2 border-primary ring-4 ring-primary/20'
                                                    : 'bg-black/30 border border-white/10 hover:border-white/30'
                                                }
                                            `}
                                            title={char.name}
                                        >
                                            {FRUIT_EMOJIS[char.key] || '🍎'}
                                        </button>
                                    ))}
                                </div>

                                {/* Selected Character Preview */}
                                {selectedChar && (
                                    <motion.div
                                        key={selectedChar.key}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="bg-gradient-to-br from-primary/5 to-secondary/5 border border-white/5 rounded-2xl p-6"
                                    >
                                        <div className="flex items-start gap-6">
                                            <div className="text-6xl">
                                                {FRUIT_EMOJIS[selectedChar.key]}
                                            </div>
                                            <div className="flex-1">
                                                <div className="flex items-center gap-3 mb-2">
                                                    <h4 className="text-2xl font-bold text-white">
                                                        {selectedChar.name}
                                                    </h4>
                                                    <span className="px-2 py-1 rounded-full bg-secondary/10 text-secondary text-xs font-medium">
                                                        {selectedChar.archetype}
                                                    </span>
                                                </div>
                                                <p className="text-gray-400 text-sm mb-3">
                                                    {selectedChar.personality}
                                                </p>
                                                <div className="p-3 bg-black/30 rounded-xl border border-white/5">
                                                    <p className="text-primary text-sm font-medium italic">
                                                        "{selectedChar.core_message}"
                                                    </p>
                                                </div>
                                                <div className="mt-3 flex flex-wrap gap-2">
                                                    {selectedChar.health_benefits.map((benefit, i) => (
                                                        <span
                                                            key={i}
                                                            className="px-2 py-1 rounded-full bg-green-500/10 text-green-400 text-xs"
                                                        >
                                                            ✓ {benefit}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    </motion.div>
                                )}
                            </motion.div>

                            {/* Generate Button */}
                            <motion.div
                                className="bg-gradient-to-r from-primary/10 to-secondary/10 border border-primary/20 rounded-3xl p-8 text-center"
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: 0.1 }}
                            >
                                <div className="mb-6">
                                    <h3 className="text-xl font-bold text-white mb-2">
                                        Ready to Create Magic? ✨
                                    </h3>
                                    <p className="text-gray-400 text-sm">
                                        This will generate 3 connected story episodes with consistent character design
                                    </p>
                                    <div className="flex justify-center gap-6 mt-4 text-sm text-gray-500">
                                        <span>📽️ 3 Videos</span>
                                        <span>⏱️ 8 seconds each</span>
                                        <span>🎯 One consistent story</span>
                                    </div>
                                </div>

                                <button
                                    onClick={generateStory}
                                    disabled={isGenerating || !selectedChar}
                                    className={`
                                        px-10 py-4 rounded-2xl font-bold text-lg flex items-center gap-3 mx-auto
                                        transition-all duration-300 shadow-2xl
                                        ${isGenerating || !selectedChar
                                            ? 'bg-gray-800 text-gray-500 cursor-not-allowed'
                                            : 'bg-gradient-to-r from-primary to-blue-600 hover:from-blue-600 hover:to-primary text-white shadow-primary/25 hover:shadow-primary/50 hover:scale-105'
                                        }
                                    `}
                                >
                                    <Sparkles className="w-6 h-6" />
                                    Generate 3-Episode Story
                                    <ChevronRight className="w-5 h-5" />
                                </button>

                                {error && (
                                    <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
                                        {error}
                                    </div>
                                )}
                            </motion.div>
                        </motion.div>
                    ) : (
                        /* Story Generation Progress / Results */
                        <motion.div
                            key="progress"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                        >
                            {/* Story Header */}
                            <div className="bg-surface border border-white/10 rounded-3xl p-6 mb-6">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-4">
                                        <div className="text-5xl">
                                            {FRUIT_EMOJIS[currentStory.fruit_type]}
                                        </div>
                                        <div>
                                            <h3 className="text-2xl font-bold text-white">
                                                {currentStory.fruit_name}'s Story
                                            </h3>
                                            <p className="text-gray-400 text-sm">
                                                {currentStory.character_description}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-3xl font-bold text-primary">
                                            {currentStory.videos_completed}/{currentStory.videos_total}
                                        </div>
                                        <div className="text-xs text-gray-500">Videos Complete</div>
                                    </div>
                                </div>

                                {/* Progress Bar */}
                                <div className="mt-4 h-2 bg-black/50 rounded-full overflow-hidden">
                                    <motion.div
                                        className="h-full bg-gradient-to-r from-primary to-secondary"
                                        initial={{ width: 0 }}
                                        animate={{ width: `${(currentStory.videos_completed / currentStory.videos_total) * 100}%` }}
                                        transition={{ duration: 0.5 }}
                                    />
                                </div>
                            </div>

                            {/* Episodes Grid */}
                            <div className="space-y-4">
                                {currentStory.episodes.map((episode, index) => (
                                    <motion.div
                                        key={episode.episode_number}
                                        className={`
                                            bg-surface border rounded-2xl p-6 transition-all
                                            ${episode.status === 'complete'
                                                ? 'border-green-500/30'
                                                : episode.status === 'generating'
                                                    ? 'border-primary/50 shadow-lg shadow-primary/10'
                                                    : 'border-white/10'
                                            }
                                        `}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: index * 0.1 }}
                                    >
                                        <div className="flex items-start gap-4">
                                            <div className="flex-shrink-0">
                                                <StatusIcon status={episode.status} />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center gap-2 mb-1">
                                                    <span className="text-xs text-gray-500 font-mono">
                                                        EP {episode.episode_number}
                                                    </span>
                                                    <span className="text-sm font-bold text-white">
                                                        {episode.title}
                                                    </span>
                                                </div>
                                                <p className="text-gray-400 text-sm line-clamp-2 mb-2">
                                                    {episode.scene_description}
                                                </p>
                                                <p className="text-primary/80 text-sm italic">
                                                    "{episode.dialogue}"
                                                </p>

                                                {/* Video Player (when complete) */}
                                                {episode.status === 'complete' && episode.video_url && (
                                                    <motion.div
                                                        initial={{ opacity: 0, height: 0 }}
                                                        animate={{ opacity: 1, height: 'auto' }}
                                                        className="mt-4"
                                                    >
                                                        <video
                                                            controls
                                                            className="w-full max-w-md rounded-xl border border-white/10"
                                                            src={`${API_BASE_URL}${episode.video_url}`}
                                                        >
                                                            Your browser does not support video playback.
                                                        </video>
                                                    </motion.div>
                                                )}
                                            </div>
                                            <div className="flex-shrink-0">
                                                {episode.status === 'generating' && (
                                                    <span className="px-2 py-1 rounded-full bg-primary/10 text-primary text-xs animate-pulse">
                                                        Generating...
                                                    </span>
                                                )}
                                                {episode.status === 'complete' && (
                                                    <span className="px-2 py-1 rounded-full bg-green-500/10 text-green-400 text-xs">
                                                        Ready
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>

                            {/* Actions */}
                            <div className="mt-8 flex justify-center gap-4">
                                {currentStory.overall_status === 'complete' && (
                                    <button
                                        onClick={resetGenerator}
                                        className="px-6 py-3 rounded-xl bg-primary hover:bg-blue-600 text-white font-semibold flex items-center gap-2 transition-all"
                                    >
                                        <RefreshCw className="w-5 h-5" />
                                        Create Another Story
                                    </button>
                                )}
                                {isGenerating && (
                                    <div className="flex items-center gap-2 text-gray-400">
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        <span>Generating videos... This may take a few minutes</span>
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </section>
    );
};
