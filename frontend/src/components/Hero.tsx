import { ArrowRight, Play, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

export const Hero = () => {
    return (
        <section className="relative overflow-hidden pt-20 pb-16 md:pt-32 md:pb-24">
            {/* Background Gradients */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full max-w-7xl opacity-30 pointer-events-none">
                <div className="absolute top-20 left-20 w-72 h-72 bg-primary/30 rounded-full blur-[100px]" />
                <div className="absolute top-40 right-20 w-80 h-80 bg-accent/30 rounded-full blur-[100px]" />
            </div>

            <div className="container mx-auto px-4 relative z-10 text-center">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                >
                    <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-sm text-gray-300 mb-6 backdrop-blur-sm">
                        <Sparkles className="w-4 h-4 text-accent" />
                        <span>Powered by Google Veo 3</span>
                    </span>

                    <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white via-white/90 to-white/50">
                        Create Magical Videos <br /> with AI
                    </h1>

                    <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
                        Generate stunning 3D animated character videos from simple text prompts.
                        Automated trend discovery meets state-of-the-art video generation.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                        <button
                            onClick={() => document.getElementById('generator')?.scrollIntoView({ behavior: 'smooth' })}
                            className="px-8 py-4 bg-white text-black font-semibold rounded-xl hover:bg-gray-200 transition-all flex items-center gap-2"
                        >
                            Start Generating <ArrowRight className="w-5 h-5" />
                        </button>
                        <button className="px-8 py-4 bg-white/5 text-white font-semibold rounded-xl hover:bg-white/10 transition-all border border-white/10 flex items-center gap-2 backdrop-blur-sm">
                            Watch Demo <Play className="w-5 h-5" />
                        </button>
                    </div>
                </motion.div>
            </div>
        </section>
    );
};
