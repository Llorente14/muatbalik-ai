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
            {/* Clean Sparkle Icon */}
            <div className="flex justify-center mb-2">
              <div className="flex items-center justify-center w-16 h-16 text-[#6366F1]">
                <span
                  className={`material-symbols-outlined text-5xl ${loading ? 'animate-pulse' : ''}`}
                  style={{ fontVariationSettings: "'FILL' 1" }}
                >
                  auto_awesome
                </span>
              </div>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-primary tracking-tight">
              Hello, Captain.
            </h1>
            <p className="text-xl md:text-2xl font-semibold text-on-surface-variant">
              How can I help you route today?
            </p>
          </div>

          {/* Input box without gradient border */}
          <div className="w-full relative group">
            <div className="absolute inset-0 bg-secondary rounded-xl opacity-0 group-focus-within:opacity-10 blur-xl transition-opacity duration-300 pointer-events-none" />
            <div className="rounded-xl border border-outline-variant bg-surface focus-within:border-primary focus-within:shadow-[0_0_12px_rgba(99,102,241,0.2)] transition-all duration-300 relative z-10">
              <div className="flex items-center p-2">
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
                  className="w-full bg-transparent border-none focus:ring-0 resize-none py-3 px-3 text-base text-on-surface placeholder-on-surface-variant h-24 outline-none"
                  placeholder='e.g., "bos tlg cariin kapal rute bitung k mks buat angkut 1.5 ton cakalang fresh, butuh chiller 2-4 C, tlg muat lusa sore ya."'
                  disabled={loading}
                />
                <div className="flex flex-col justify-end h-full p-2">
                  <button
                    onClick={handleSend}
                    disabled={loading || !inputText.trim()}
                    className="bg-primary text-white rounded-full w-12 h-12 flex items-center justify-center hover:bg-primary/90 transition-colors shadow-sm disabled:opacity-50"
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
          {result && !result.error && result.order && (
            <div className="w-full mt-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="bg-surface-container rounded-xl p-6 border border-outline-variant shadow-sm space-y-8">
                
                {/* Extraction Result - Human Readable */}
                <div>
                  <h3 className="text-lg font-bold text-primary mb-4 flex items-center gap-2">
                    <span className="material-symbols-outlined">check_circle</span>
                    Order Berhasil Diekstrak
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-surface p-4 rounded-xl border border-outline-variant shadow-sm">
                      <div className="text-xs font-semibold text-on-surface-variant flex items-center gap-1.5 mb-2 uppercase tracking-wider">
                        <span className="material-symbols-outlined text-[18px]">route</span> Rute
                      </div>
                      <div className="font-bold text-on-surface text-lg leading-tight">
                        {result.order.origin || '?'} <br/>
                        <span className="text-sm text-on-surface-variant font-normal">ke</span> {result.order.destination || '?'}
                      </div>
                    </div>
                    <div className="bg-surface p-4 rounded-xl border border-outline-variant shadow-sm">
                      <div className="text-xs font-semibold text-on-surface-variant flex items-center gap-1.5 mb-2 uppercase tracking-wider">
                        <span className="material-symbols-outlined text-[18px]">inventory_2</span> Muatan
                      </div>
                      <div className="font-bold text-on-surface text-lg leading-tight">
                        {result.order.weight_kg ? `${result.order.weight_kg} kg` : '?'} <br/>
                        <span className="text-sm text-on-surface-variant font-normal capitalize">{result.order.commodity}</span>
                      </div>
                    </div>
                    <div className="bg-surface p-4 rounded-xl border border-outline-variant shadow-sm">
                      <div className="text-xs font-semibold text-on-surface-variant flex items-center gap-1.5 mb-2 uppercase tracking-wider">
                        <span className="material-symbols-outlined text-[18px]">ac_unit</span> Suhu (Cold-Chain)
                      </div>
                      <div className="font-bold text-on-surface text-lg leading-tight">
                        {result.order.temperature_min_c !== null ? `${result.order.temperature_min_c}°C` : 'Ambient'} <br/>
                        <span className="text-sm text-on-surface-variant font-normal">
                          {result.order.temperature_max_c !== null ? `sampai ${result.order.temperature_max_c}°C` : 'Suhu Ruang'}
                        </span>
                      </div>
                    </div>
                    <div className="bg-surface p-4 rounded-xl border border-outline-variant shadow-sm">
                      <div className="text-xs font-semibold text-on-surface-variant flex items-center gap-1.5 mb-2 uppercase tracking-wider">
                        <span className="material-symbols-outlined text-[18px]">schedule</span> Waktu Pickup
                      </div>
                      <div className="font-bold text-on-surface text-lg leading-tight capitalize">
                        {result.order.pickup_deadline || 'Segera'} <br/>
                        <span className="text-sm text-on-surface-variant font-normal">Status: Pending</span>
                      </div>
                    </div>
                  </div>
                </div>

                <hr className="border-outline-variant" />

                {/* Match Candidates Result */}
                {matchCandidates.length > 0 && (
                  <div>
                    <h3 className="text-lg font-bold text-primary mb-4 flex items-center gap-2">
                      <span className="material-symbols-outlined">directions_boat</span>
                      Rekomendasi Kapal Tersedia
                    </h3>
                    
                    {/* INFO BAR FOR SCORE RANGE */}
                    <div className="flex items-start gap-3 bg-secondary/10 border border-secondary/20 p-4 rounded-xl text-sm mb-6 shadow-sm">
                      <span className="material-symbols-outlined text-secondary text-2xl mt-0.5">info</span>
                      <div className="text-on-surface w-full">
                        <strong className="text-base block mb-2">Panduan Skor Kecocokan (AI Scoring):</strong>
                        <ul className="flex flex-col md:flex-row gap-3 md:gap-6 w-full">
                          <li className="flex items-center gap-2 bg-surface px-3 py-1.5 rounded-lg border border-outline-variant flex-1">
                            <span className="w-3 h-3 rounded-full bg-primary flex-shrink-0 shadow-[0_0_8px_rgba(99,102,241,0.6)]"></span> 
                            <span><b>≥ 90</b>: Direkomendasikan (Suhu & Rute pas)</span>
                          </li>
                          <li className="flex items-center gap-2 bg-surface px-3 py-1.5 rounded-lg border border-outline-variant flex-1">
                            <span className="w-3 h-3 rounded-full bg-yellow-500 flex-shrink-0 shadow-[0_0_8px_rgba(234,179,8,0.6)]"></span> 
                            <span><b>60-89</b>: Alternatif (Bisa masuk / Transit)</span>
                          </li>
                          <li className="flex items-center gap-2 bg-surface px-3 py-1.5 rounded-lg border border-outline-variant flex-1">
                            <span className="w-3 h-3 rounded-full bg-error flex-shrink-0 shadow-[0_0_8px_rgba(239,68,68,0.6)]"></span> 
                            <span><b>0</b>: Ditolak (Constraint suhu/rute gagal)</span>
                          </li>
                        </ul>
                      </div>
                    </div>

                    <div className="flex flex-col gap-4">
                      {matchCandidates.map((c, idx) => (
                        <div key={idx} className={`p-5 rounded-xl border transition-colors ${c.status === 'recommended' ? 'border-primary bg-primary/5 shadow-sm' : c.status === 'rejected' ? 'border-error/30 bg-error/5 opacity-75' : 'border-outline-variant bg-surface shadow-sm'}`}>
                          <div className="flex flex-col md:flex-row justify-between md:items-center gap-3 mb-4">
                            <div>
                              <div className="font-bold text-lg text-primary">{c.carrier.name}</div>
                              <div className="text-sm text-on-surface-variant font-mono mt-1 bg-white/50 inline-block px-2 py-1 rounded">
                                {c.carrier.origin} → {c.carrier.destination} | Sisa: {c.carrier.capacity_kg} kg | Suhu: {c.carrier.temperature_min_c ?? 'N/A'}°C s/d {c.carrier.temperature_max_c ?? 'N/A'}°C
                              </div>
                            </div>
                            <div className={`px-4 py-2 rounded-full text-sm font-bold w-fit flex items-center gap-1.5 shadow-sm ${c.status === 'recommended' ? 'bg-primary text-white' : c.status === 'rejected' ? 'bg-error text-white' : 'bg-yellow-500 text-white'}`}>
                              <span className="material-symbols-outlined text-[18px]">
                                {c.status === 'recommended' ? 'star' : c.status === 'rejected' ? 'block' : 'done'}
                              </span>
                              Skor AI: {c.score}
                            </div>
                          </div>
                          
                          <div className="bg-surface-container-low p-3 rounded-lg border border-outline-variant/50">
                            <div className="text-xs font-bold text-on-surface-variant mb-2 uppercase tracking-wide">Alasan AI (Matching Reasoning):</div>
                            <ul className="text-sm list-none space-y-1.5">
                              {c.reasons.map((r: string, i: number) => (
                                <li key={i} className="flex items-start gap-2 text-on-surface">
                                  <span className={`material-symbols-outlined text-[18px] mt-0.5 ${c.status === 'rejected' ? 'text-error' : 'text-primary'}`}>
                                    {c.status === 'rejected' ? 'close' : 'check'}
                                  </span>
                                  {r}
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
          {result && result.error && (
            <div className="w-full mt-8 animate-in fade-in bg-error/10 border border-error p-4 rounded-xl text-error text-center font-semibold">
              <span className="material-symbols-outlined align-middle mr-2">error</span>
              {result.error}
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
