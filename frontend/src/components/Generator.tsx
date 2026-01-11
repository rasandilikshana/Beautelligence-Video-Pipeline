import { useState } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Wand2, Loader2 } from 'lucide-react';
import axios from 'axios';

export const Generator = () => {
    const [prompt, setPrompt] = useState('');
    const [isGenerating, setIsGenerating] = useState(false);
    const [status, setStatus] = useState<string | null>(null);

    const handleGenerate = async () => {
        if (!prompt.trim()) return;

        setIsGenerating(true);
        setStatus('queueing');

        try {
            await axios.post('http://localhost:8000/api/generate', {
                prompt,
                force: true
            });
            setStatus('success');
            setPrompt('');
            // Ideally trigger refresh of status/gallery here
        } catch (error) {
            console.error(error);
            setStatus('error');
        } finally {
            setIsGenerating(false);
            setTimeout(() => setStatus(null), 3000);
        }
    };

    return (
        <section id="generator" className="py-20 container mx-auto px-4">
            <div className="max-w-3xl mx-auto">
                <motion.div
                    className="bg-surface border border-white/10 rounded-3xl p-8 shadow-2xl relative overflow-hidden"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                >
                    {/* Glow effect */}
                    <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-[80px] -z-10" />

                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-3 bg-primary/20 rounded-xl">
                            <Wand2 className="w-6 h-6 text-primary" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-white">Generation Studio</h2>
                            <div className="flex items-center gap-2">
                                <p className="text-gray-400 text-sm">Turn your imagination into reality</p>
                                <span className="px-2 py-0.5 rounded-full bg-secondary/10 border border-secondary/20 text-xs text-secondary font-mono">
                                    Brand Safe Mode: Active
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Prompt
                            </label>
                            <textarea
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                placeholder={`Scene: A YouTuber sits in a studio with a ring light and camera.

Sinhala: "ඔයාගේ video content එක next level එකට ගන්න කැමතිද?"

Translation: "Want to take your video content to the next level?"

Music: Youthful lo-fi beat

Character: Alive Strawberry YouTube Content Creator character with big expressive cartoon eyes...

Action: The Strawberry is enthusiastically gesturing with tiny, leafy hands...

Setting: A miniature, brightly lit YouTube studio...

Visual Style:
- Soft studio lighting with subtle rim light
- Glossy plastic-like texture with soft shadows
- Vibrant and cheerful color palette
- High-quality 3D render, Pixar-style animation quality

Camera: Slow pan up
Duration: 8 seconds
Audio: Upbeat and youthful lo-fi music...`}
                                className="w-full bg-black/50 border border-white/10 rounded-xl p-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary/50 min-h-[300px] resize-none transition-all font-mono text-sm"
                            />
                        </div>

                        <div className="flex justify-end pt-4">
                            <button
                                onClick={handleGenerate}
                                disabled={isGenerating || !prompt.trim()}
                                className={`
                  px-6 py-3 rounded-xl font-semibold flex items-center gap-2 transition-all
                  ${isGenerating || !prompt.trim()
                                        ? 'bg-gray-800 text-gray-500 cursor-not-allowed'
                                        : 'bg-primary hover:bg-blue-600 text-white shadow-lg shadow-primary/25'}
                `}
                            >
                                {isGenerating ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        Generating...
                                    </>
                                ) : (
                                    <>
                                        <Sparkles className="w-5 h-5" />
                                        Generate Video
                                    </>
                                )}
                            </button>
                        </div>

                        {status === 'success' && (
                            <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-xl text-green-400 text-sm text-center">
                                ✨ Task started successfully! Check the status below.
                            </div>
                        )}
                        {status === 'error' && (
                            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm text-center">
                                ⚠️ Failed to start generation. Please check the API.
                            </div>
                        )}
                    </div>
                </motion.div>

                {/* Sample Prompt Tile */}
                <motion.div
                    className="mt-8 bg-surface/50 border border-white/5 rounded-3xl p-6 relative overflow-hidden group hover:border-primary/20 transition-colors cursor-pointer"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 }}
                    onClick={() => {
                        setPrompt(`Scene: A YouTuber sits in a studio with a ring light and camera.

Sinhala: "ඔයාගේ video content එක next level එකට ගන්න කැමතිද?"

Translation: "Want to take your video content to the next level?"

Music: Youthful lo-fi beat

Character: Alive Strawberry YouTube Content Creator character with big expressive cartoon eyes and a Excited, enthusiastic, helpful, and friendly. expression.

The character is The Strawberry is enthusiastically gesturing with tiny, leafy hands while explaining something to the camera, occasionally pointing with a cheerful wiggle. It glances at its audience and nods encouragingly. in a A miniature, brightly lit YouTube studio with a tiny camera, ring light, computer, microphone, and trendy decorations like plants and a motivational poster..

Visual Style:
- Soft studio lighting with subtle rim light
- Glossy plastic-like texture with soft shadows
- Vibrant vibrant and cheerful color palette
- High-quality 3D render, Pixar-style animation quality

Camera: slow pan up
Duration: 8 seconds
Audio: Upbeat and youthful lo-fi music with a slight Sinhalese influence. Sound effects include a gentle 'ding' when the text appears and a subtle click of a camera shutter.`);
                        window.scrollTo({ top: document.getElementById('generator')?.offsetTop, behavior: 'smooth' });
                    }}
                >
                    <div className="absolute top-0 right-0 p-4 opacity-50 group-hover:opacity-100 transition-opacity">
                        <span className="text-xs font-mono text-primary bg-primary/10 px-2 py-1 rounded">CLICK TO TRY</span>
                    </div>

                    <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-secondary" />
                        Sample Template
                    </h3>

                    <div className="bg-black/30 rounded-xl p-4 font-mono text-xs text-gray-400 whitespace-pre-wrap leading-relaxed border border-white/5 h-96 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                        <span className="text-secondary font-bold block mb-1">Scene:</span> A YouTuber sits in a studio with a ring light and camera.<br /><br />
                        <span className="text-secondary font-bold block mb-1">Sinhala:</span> "ඔයාගේ video content එක next level එකට ගන්න කැමතිද?"<br /><br />
                        <span className="text-secondary font-bold block mb-1">Translation:</span> "Want to take your video content to the next level?"<br /><br />
                        <span className="text-secondary font-bold block mb-1">Music:</span> Youthful lo-fi beat<br /><br />
                        <span className="text-secondary font-bold block mb-1">Character:</span> Alive Strawberry YouTube Content Creator character with big expressive cartoon eyes...<br /><br />
                        <span className="text-secondary font-bold block mb-1">Action:</span> The Strawberry is enthusiastically gesturing with tiny, leafy hands while explaining something to the camera...<br /><br />
                        <span className="text-secondary font-bold block mb-1">Setting:</span> A miniature, brightly lit YouTube studio with a tiny camera...<br /><br />
                        <span className="text-secondary font-bold block mb-1">Visual Style:</span>
                        - Soft studio lighting<br />
                        - Glossy plastic-like texture<br />
                        - Vibrant color palette<br />
                        - High-quality 3D render<br /><br />
                        <span className="text-secondary font-bold block mb-1">Camera:</span> slow pan up<br /><br />
                        <span className="text-secondary font-bold block mb-1">Audio:</span> Upbeat and youthful lo-fi music...
                    </div>
                </motion.div>
            </div>
        </section>
    );
};
