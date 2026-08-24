import { useState, useRef } from 'react';

export default function App() {
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [matchCandidates, setMatchCandidates] = useState<any[]>([]);
  const textAreaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = async () => {
    if (!inputText.trim()) return;
    setLoading(true);
    setResult(null);
    setMatchCandidates([]);

    try {
      // 1. AI Extraction (Parse Order)
      const resParse = await fetch('http://127.0.0.1:8000/api/orders/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_text: inputText }),
      });
      const dataParse = await resParse.json();
      setResult(dataParse);

      // 2. Carrier Matching
      if (dataParse.order && dataParse.order.id) {
        const resMatch = await fetch(`http://127.0.0.1:8000/api/shipments/${dataParse.order.id}/match`, {
          method: 'POST',
        });
        const dataMatch = await resMatch.json();
        setMatchCandidates(dataMatch.candidates || []);
      }
    } catch (error) {
      console.error(error);
      setResult({ error: "Failed to connect to backend. Is the server running?" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-background text-on-surface min-h-screen flex flex-col font-sans">
      {/* ── Top Navigation ── */}
      <nav className="bg-surface text-primary top-0 w-full border-b border-outline-variant">
        <div className="flex items-center w-full px-6 py-4 max-w-7xl mx-auto">
          <div className="text-xl font-bold text-primary tracking-tight">
            MuatBalik AI
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
                className={`material-symbols-outlined text-3xl ${loading ? 'animate-spin' : ''}`}
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
            <div className="absolute inset-0 bg-secondary rounded-xl opacity-0 group-focus-within:opacity-20 blur-xl transition-opacity duration-300 pointer-events-none" />
            <div
              className="rounded-xl shadow-[0_10px_15px_-3px_rgba(99,102,241,0.08)] focus-within:shadow-[0_0_12px_rgba(139,92,246,0.5)] transition-shadow duration-300 relative z-10"
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
                  ref={textAreaRef}
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                  className="w-full bg-transparent border-none focus:ring-0 resize-none py-4 px-4 text-base text-on-surface placeholder-on-surface-variant h-24 outline-none"
                  placeholder='e.g., "bos tlg cariin kapal rute bitung k mks buat angkut 1.5 ton cakalang fresh, butuh chiller 2-4 C, tlg muat lusa sore ya."'
                  disabled={loading}
                />
                <div className="flex flex-col justify-end h-full p-2">
                  <button
                    onClick={handleSend}
                    disabled={loading || !inputText.trim()}
                    className="text-white rounded-full w-12 h-12 flex items-center justify-center hover:opacity-90 transition-opacity shadow-md disabled:opacity-50"
                    style={{ background: 'linear-gradient(to right, #6366F1, #06B6D4)' }}
                    aria-label="Send"
                  >
                    <span className="material-symbols-outlined">
                      {loading ? 'hourglass_empty' : 'send'}
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Suggested prompts / chips */}
          <div className="flex flex-wrap gap-2 justify-center">
            {[
              'bos tlg cariin kapal rute bitung k mks buat angkut 1.5 ton cakalang fresh, butuh chiller 2-4 C, tlg muat lusa sore ya.',
              '300 kg tuna Ambon ke Surabaya, suhu 0-4 C, pickup besok pagi',
            ].map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setInputText(prompt);
                  if (textAreaRef.current) textAreaRef.current.focus();
                }}
                className="px-4 py-2 rounded-full border border-outline-variant bg-surface text-sm text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors duration-150 text-left max-w-[300px] truncate"
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Results Output */}
          {result && (
            <div className="w-full mt-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="bg-surface-container rounded-xl p-6 border border-outline-variant shadow-sm space-y-6">
                
                {/* Extraction Result */}
                <div>
                  <h3 className="text-lg font-bold text-primary mb-3 flex items-center gap-2">
                    <span className="material-symbols-outlined">data_object</span>
                    AI Extraction
                  </h3>
                  <div className="bg-black/5 rounded-lg p-4 font-mono text-sm overflow-x-auto text-on-surface">
                    <pre>{JSON.stringify(result, null, 2)}</pre>
                  </div>
                </div>

                {/* Match Candidates Result */}
                {matchCandidates.length > 0 && (
                  <div>
                    <h3 className="text-lg font-bold text-primary mb-3 flex items-center gap-2">
                      <span className="material-symbols-outlined">route</span>
                      Carrier Matches
                    </h3>
                    <div className="flex flex-col gap-3">
                      {matchCandidates.map((c, idx) => (
                        <div key={idx} className={`p-4 rounded-lg border ${c.status === 'recommended' ? 'border-primary bg-primary/5' : c.status === 'rejected' ? 'border-error/50 bg-error/5 opacity-70' : 'border-outline-variant bg-surface'}`}>
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <div className="font-bold">{c.carrier.name}</div>
                              <div className="text-xs text-on-surface-variant">
                                {c.carrier.origin} → {c.carrier.destination} • {c.carrier.capacity_kg} kg • {c.carrier.temperature_min_c ?? 'N/A'} to {c.carrier.temperature_max_c ?? 'N/A'}°C
                              </div>
                            </div>
                            <div className={`px-2 py-1 rounded text-xs font-bold ${c.status === 'recommended' ? 'bg-primary text-white' : c.status === 'rejected' ? 'bg-error text-white' : 'bg-secondary/20 text-secondary'}`}>
                              Score: {c.score}
                            </div>
                          </div>
                          <ul className="text-sm list-disc pl-4 text-on-surface-variant">
                            {c.reasons.map((r: string, i: number) => (
                              <li key={i}>{r}</li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>

      {/* ── Footer ── */}
      <footer className="bg-surface-container-low text-on-surface-variant border-t border-outline-variant mt-auto">
        <div className="w-full py-8 px-6 flex flex-col md:flex-row justify-between items-center gap-4 max-w-7xl mx-auto">
          <div className="text-lg font-semibold text-primary mb-4 md:mb-0">
            MuatBalik AI
          </div>
          <div className="text-center text-sm">
            © 2026 MuatBalik AI. Precision Logistics Intelligence.
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
