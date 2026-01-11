import { Hero } from './components/Hero';
import { Generator } from './components/Generator';
import { Status } from './components/Status';
import { Gallery } from './components/Gallery';

function App() {
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
        <Generator />
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
