import { useState } from 'react';
import { Hero } from './components/Hero';
import { Generator } from './components/Generator';
import { FruitStoryGenerator } from './components/FruitStoryGenerator';
import { Status } from './components/Status';
import { Gallery } from './components/Gallery';
import { Wand2, Heart } from 'lucide-react';

type GeneratorMode = 'prompt' | 'story';

function App() {
  const [mode, setMode] = useState<GeneratorMode>('story');

  return (
    <div className="min-h-screen bg-background text-white selection:bg-primary/30">
      <nav className="fixed top-0 w-full z-50 border-b border-white/5 bg-black/50 backdrop-blur-xl">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold text-xl tracking-tight">
            <img src="/branding/logo.jpg" alt="Beautelligence" className="h-10 w-auto rounded-full border border-pink-500/50" />
            <span className="hidden sm:inline bg-clip-text text-transparent bg-gradient-to-r from-pink-500 to-purple-500">
              Beautelligence
            </span>
          </div>
          <div className="flex items-center gap-6 text-sm text-gray-400">
            <a href="#generator" className="hover:text-white transition-colors">Create</a>
            <a href="#gallery" className="hover:text-white transition-colors">Gallery</a>
            <a href="https://github.com" target="_blank" className="hover:text-white transition-colors">GitHub</a>
          </div>
        </div>
      </nav>

      <main>
        <Hero />
        <Status />

        {/* Mode Toggle Tabs */}
        <div className="container mx-auto px-4 -mb-8">
          <div className="max-w-3xl mx-auto flex justify-center">
            <div className="inline-flex bg-surface border border-white/10 rounded-2xl p-1.5">
              <button
                onClick={() => setMode('story')}
                className={`
                  px-6 py-3 rounded-xl font-medium text-sm flex items-center gap-2 transition-all
                  ${mode === 'story'
                    ? 'bg-gradient-to-r from-pink-500/20 to-purple-500/20 text-white border border-pink-500/30'
                    : 'text-gray-400 hover:text-white'
                  }
                `}
              >
                <Heart className="w-4 h-4" />
                🍎 Story Mode
                <span className="px-1.5 py-0.5 rounded text-xs bg-green-500/20 text-green-400 ml-1">NEW</span>
              </button>
              <button
                onClick={() => setMode('prompt')}
                className={`
                  px-6 py-3 rounded-xl font-medium text-sm flex items-center gap-2 transition-all
                  ${mode === 'prompt'
                    ? 'bg-primary/20 text-white border border-primary/30'
                    : 'text-gray-400 hover:text-white'
                  }
                `}
              >
                <Wand2 className="w-4 h-4" />
                📝 Prompt Mode
              </button>
            </div>
          </div>
        </div>

        {/* Conditional Generator Display */}
        <div id="generator">
          {mode === 'story' ? <FruitStoryGenerator /> : <Generator />}
        </div>

        <div id="gallery">
          <Gallery />
        </div>
      </main>

      <footer className="py-8 border-t border-white/5 mt-20 text-center text-gray-500 text-sm">
        <p>© 2024 Beautelligence AI. Powered by Google Veo 3.</p>
      </footer>
    </div>
  );
}

export default App;

