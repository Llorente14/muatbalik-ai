export default function App() {
  return (
    <div className="bg-background text-on-surface min-h-screen flex flex-col font-sans">

      {/* ── Top Navigation ── */}
      <nav className="bg-surface text-primary top-0 w-full border-b border-outline-variant">
        <div className="flex justify-between items-center w-full px-6 py-4 max-w-7xl mx-auto">
          <div className="text-xl font-bold text-primary tracking-tight">
            MuatBalik AI
          </div>
          <div className="flex gap-4">
            <button
              className="hover:opacity-80 transition-opacity text-on-surface-variant"
              aria-label="Account"
            >
              <span className="material-symbols-outlined">account_circle</span>
            </button>
            <button
              className="hover:opacity-80 transition-opacity text-on-surface-variant"
              aria-label="Settings"
            >
              <span className="material-symbols-outlined">settings</span>
            </button>
          </div>
        </div>
      </nav>

      {/* ── Main Content ── */}
      <main className="flex-grow flex flex-col items-center justify-start pt-16 px-4 md:px-8 max-w-5xl mx-auto w-full">
        {/* Greeting & Input */}
        <div className="w-full max-w-3xl flex flex-col items-center space-y-8 mb-12">

          {/* Hero heading */}
          <div className="text-center space-y-4">
            {/* AI icon */}
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-indigo-100 text-indigo-600 mb-4 shadow-[0_0_12px_rgba(139,92,246,0.5)]">
              <span
                className="material-symbols-outlined text-3xl"
                style={{ fontVariationSettings: "'FILL' 1" }}
              >
                auto_awesome
              </span>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-primary tracking-tight">
              Hello, Captain.
            </h1>
            <p className="text-xl md:text-2xl font-semibold text-on-surface-variant">
              How can I help you route today?
            </p>
          </div>

          {/* Input box with gradient border */}
          <div className="w-full relative group">
            {/* Blur glow behind */}
            <div className="absolute inset-0 bg-secondary rounded-xl opacity-0 group-focus-within:opacity-20 blur-xl transition-opacity duration-300 pointer-events-none" />

            {/* Gradient border wrapper */}
            <div
              className="rounded-xl shadow-[0_10px_15px_-3px_rgba(99,102,241,0.08)] focus-within:shadow-[0_0_12px_rgba(139,92,246,0.5)] transition-shadow duration-300"
              style={{
                background: 'linear-gradient(to right, #6366F1, #06B6D4)',
                padding: '1px',
                borderRadius: '0.75rem',
              }}
            >
              <div
                className="flex items-center bg-surface"
                style={{ borderRadius: 'calc(0.75rem - 1px)', padding: '0.5rem' }}
              >
                <textarea
                  className="w-full bg-transparent border-none focus:ring-0 resize-none py-4 px-4 text-base text-on-surface placeholder-on-surface-variant h-24 outline-none"
                  placeholder='e.g., "300 kg tuna Ambon ke Surabaya, suhu 0-4°C, pickup besok pagi"'
                />
                <div className="flex flex-col justify-end h-full p-2">
                  <button
                    className="text-white rounded-full w-12 h-12 flex items-center justify-center hover:opacity-90 transition-opacity shadow-md"
                    style={{ background: 'linear-gradient(to right, #6366F1, #06B6D4)' }}
                    aria-label="Send"
                  >
                    <span className="material-symbols-outlined">send</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Suggested prompts / chips */}
          <div className="flex flex-wrap gap-2 justify-center">
            {[
              '300 kg tuna Ambon → Surabaya, 0-4°C',
              'Cek kapasitas kapal besok pagi',
              'Cari muatan balik Surabaya → Ambon',
            ].map((prompt) => (
              <button
                key={prompt}
                className="px-4 py-2 rounded-full border border-outline-variant bg-surface text-sm text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors duration-150"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      </main>

      {/* ── Footer ── */}
      <footer className="bg-surface-container-low text-on-surface-variant border-t border-outline-variant mt-auto">
        <div className="w-full py-8 px-6 flex flex-col md:flex-row justify-between items-center gap-4 max-w-7xl mx-auto">
          <div className="text-lg font-semibold text-primary mb-4 md:mb-0">
            MuatBalik AI
          </div>
          <div className="text-center text-sm">
            © 2024 MuatBalik AI. Precision Logistics Intelligence.
          </div>
          <div className="flex gap-6 text-xs font-semibold uppercase tracking-wide font-mono">
            <a href="#" className="hover:text-primary transition-colors duration-200">
              Terms of Service
            </a>
            <a href="#" className="hover:text-primary transition-colors duration-200">
              Privacy Policy
            </a>
            <a href="#" className="hover:text-primary transition-colors duration-200">
              Contact Support
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}
