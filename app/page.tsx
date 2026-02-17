export default function Home() {
  return (
    <main className="min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-black">
      <div className="flex flex-col items-center justify-center gap-8 px-4 max-w-2xl">
        {/* Kilterboard Image */}
        <div className="relative w-full max-w-md">
          <div className="aspect-square rounded-lg overflow-hidden shadow-2xl">
            <img
              src="https://images.unsplash.com/photo-1577720643272-265e434b5b7e?w=600&h=600&fit=crop"
              alt="Kilterboard climbing wall"
              className="w-full h-full object-cover"
              priority
            />
          </div>
          {/* Glow effect */}
          <div className="absolute inset-0 rounded-lg bg-gradient-to-t from-orange-500/20 to-transparent pointer-events-none"></div>
        </div>

        {/* KILTER UP Heading */}
        <div className="text-center space-y-4">
          <h1 className="text-6xl md:text-8xl font-black text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-orange-600 tracking-tighter">
            KILTER UP
          </h1>
          <p className="text-lg md:text-xl text-slate-300 max-w-md">
            AI-Powered Circuit Generation & Training Planning for Kilterboard
          </p>
        </div>

        {/* CTA Button */}
        <button className="mt-8 px-8 py-4 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-bold rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105">
          Coming Soon 🧗‍♂️
        </button>

        {/* Feature hints */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-12 pt-8 border-t border-slate-700">
          <div className="text-center">
            <div className="text-2xl mb-2">🎬</div>
            <p className="text-sm text-slate-400">Video Analysis</p>
          </div>
          <div className="text-center">
            <div className="text-2xl mb-2">🤖</div>
            <p className="text-sm text-slate-400">AI Circuits</p>
          </div>
          <div className="text-center">
            <div className="text-2xl mb-2">📊</div>
            <p className="text-sm text-slate-400">Training Plans</p>
          </div>
        </div>
      </div>
    </main>
  );
}
