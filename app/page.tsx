export default function Home() {
  return (
    <main className="min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-black overflow-hidden">
      {/* Background animated elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-orange-600/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="relative z-10 flex flex-col items-center justify-center gap-8 px-4 max-w-3xl">
        {/* Kilterboard Image */}
        <div className="relative w-full max-w-md animate-fade-in">
          <div className="aspect-square rounded-2xl overflow-hidden shadow-2xl border-2 border-orange-500/30">
            <img
              src="https://images.unsplash.com/photo-1577720643272-265e434b5b7e?w=600&h=600&fit=crop"
              alt="Kilterboard climbing wall"
              className="w-full h-full object-cover"
            />
          </div>
          {/* Glow effect */}
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-t from-orange-600/30 to-transparent pointer-events-none"></div>
          <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-orange-500 to-orange-600 opacity-25 blur-lg -z-10"></div>
        </div>

        {/* KILTER UP Heading - VIVID ORANGE */}
        <div className="text-center space-y-4 animate-fade-in">
          <h1 className="text-6xl md:text-8xl font-black text-orange-500 drop-shadow-2xl tracking-tighter" style={{textShadow: '0 0 30px rgba(255, 107, 53, 0.5)'}}>
            KILTER UP
          </h1>
          <p className="text-lg md:text-xl text-slate-300 max-w-md font-medium">
            AI-Powered Circuit Generation & Training Planning for Kilterboard
          </p>
        </div>

        {/* CTA Button - PREMIUM */}
        <button className="mt-8 px-8 py-4 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-bold rounded-lg shadow-2xl hover:shadow-orange-500/50 transition-all duration-300 transform hover:scale-110 border border-orange-400/50">
          Coming Soon 🧗‍♂️
        </button>

        {/* Feature cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-12 pt-8 border-t border-orange-500/20 w-full">
          <div className="text-center p-4 rounded-lg bg-gradient-to-br from-orange-500/10 to-transparent border border-orange-500/20 hover:border-orange-500/50 transition-all">
            <div className="text-3xl mb-2">🎬</div>
            <p className="text-sm font-semibold text-slate-300">Video Analysis</p>
          </div>
          <div className="text-center p-4 rounded-lg bg-gradient-to-br from-orange-500/10 to-transparent border border-orange-500/20 hover:border-orange-500/50 transition-all">
            <div className="text-3xl mb-2">🤖</div>
            <p className="text-sm font-semibold text-slate-300">AI Circuits</p>
          </div>
          <div className="text-center p-4 rounded-lg bg-gradient-to-br from-orange-500/10 to-transparent border border-orange-500/20 hover:border-orange-500/50 transition-all">
            <div className="text-3xl mb-2">📊</div>
            <p className="text-sm font-semibold text-slate-300">Training Plans</p>
          </div>
        </div>
      </div>
    </main>
  );
}
