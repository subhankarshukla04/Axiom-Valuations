import { ArrowRight, ArrowUpRight, ChevronDown, Database, ExternalLink, Film, Github } from 'lucide-react'

const GH_URL = 'https://github.com/subhankarshukla04/Axiom-Valuations'
const LI_URL = 'https://www.linkedin.com/in/subhankarshukla/'
const PORTFOLIO_URL = 'https://subhankarshukla.vercel.app'

const PIPELINE = [
  { label: 'Yahoo Finance', sub: 'Fundamentals + price', kind: 'input' as const },
  { label: 'Archetype Router', sub: '9 frameworks', kind: 'process' as const },
  { label: 'Clean DCF', sub: 'CAPM + credit spreads', kind: 'process' as const },
  { label: 'Comp Multiples', sub: '54-tag table', kind: 'process' as const },
  { label: 'Factor Model', sub: 'Research mode', kind: 'process' as const },
  { label: 'Fair Value', sub: 'Bear / Base / Bull', kind: 'output' as const },
]

const KIND_COLOR = {
  input: '#6366F1',
  process: '#3B82F6',
  ai: '#8B5CF6',
  output: '#22C55E',
} as const

type Section = {
  n: string
  title: string
  blurb: string
  duration: string
  shot: string
  url: string
  clip?: string
}

const SECTIONS: Section[] = [
  {
    n: '01',
    title: 'Type a ticker. Get a fair value.',
    blurb:
      'Enter any US ticker. AXIOM pulls fundamentals from Yahoo Finance, routes the company through one of 9 archetype frameworks (banks get P/B, REITs get P/FFO, mature businesses get a clean DCF), and projects 10 years forward. First lookup takes a few seconds; cached after that.',
    duration: '0:00 – 0:30',
    shot: '/screens/01-dashboard.png',
    url: 'axiom.app/dashboard',
    clip: '/clips/clip-1.mp4',
  },
  {
    n: '02',
    title: 'A clean 10-year DCF. Every cell auditable.',
    blurb:
      'One formula. No blending. The CAPM-derived WACC pulls credit spreads from a Damodaran-style table; terminal growth is capped below WACC. The same math drives the headline and the sensitivity table — change an input, the output recalculates live.',
    duration: '0:30 – 1:00',
    shot: '/screens/03-dcf-top.png',
    url: 'axiom.app/dcf/aapl',
    clip: '/clips/clip-2.mp4',
  },
  {
    n: '03',
    title: 'Comparables sit beside it — never folded in.',
    blurb:
      'EV/EBITDA and P/E live next to the DCF as labelled context. Peer tickers link to their Yahoo Finance pages so the comp set is verifiable. Drag a multiple slider to stress the comp — the DCF headline stays put. The two views never blend into one number.',
    duration: '1:00 – 1:30',
    shot: '/screens/06-evebitda.png',
    url: 'axiom.app/comps/aapl',
    clip: '/clips/clip-3.mp4',
  },
]

const RULES = [
  {
    n: '01',
    head: 'The headline number means what it says.',
    body: 'The fair value at the top of the page is a DCF output. Multiples are shown next to it as context, never blended in. No silent re-weighting.',
  },
  {
    n: '02',
    head: 'Every assumption is written down.',
    body: 'A HARDCODED_VALUES.md file inventories every hand-set constant in the codebase, alongside a phased plan to migrate them to live peer-comp estimates. The known unknowns are documented.',
  },
  {
    n: '03',
    head: 'Different businesses get different math.',
    body: 'A 9-archetype router (FINANCIAL, GROWTH, MATURE, CYCLICAL, HIGH_CAPEX, HYPER_GROWTH, TURNAROUND, DISTRESSED, STABLE_GROWTH) selects the formula. A 54-tag sub-sector table calibrates the multiples used for context.',
  },
  {
    n: '04',
    head: 'The factor model is in research mode.',
    body: 'A V/M/Q (value/momentum/quality) Z-scoring layer exists, but it isn\'t the headline. Its skill is being measured via Information Coefficient + quintile hit rates over walk-forward horizons in monitor.py — not yet shipped as a user-facing signal.',
  },
  {
    n: '05',
    head: 'Built and shipped by one person.',
    body: 'Flask + PostgreSQL + Python on the back end, vanilla JS on the front. yfinance for data. Limitations come with the territory — see "what this isn\'t" below.',
  },
]

const STACK = [
  'Python', 'Flask', 'PostgreSQL', 'yfinance',
  'CAPM + credit-spread WACC', '9-archetype router',
  '54-tag multiplier table', 'V/M/Q factor model (research)', 'IC · walk-forward monitor',
]

function ChromeFrame({ url, children }: { url: string; children: React.ReactNode }) {
  return (
    <div className="media-frame">
      <div className="chrome-bar">
        <span className="chrome-dot" />
        <span className="chrome-dot" />
        <span className="chrome-dot" />
        <span className="chrome-url">{url}</span>
      </div>
      {children}
    </div>
  )
}

function ClipSlot({ duration }: { duration: string }) {
  return (
    <div
      className="media-frame flex items-center justify-center"
      style={{
        aspectRatio: '16 / 9',
        background:
          'linear-gradient(135deg, rgba(79,158,255,0.10) 0%, rgba(139,92,246,0.07) 100%)',
      }}
    >
      <div className="text-center px-6 relative z-10">
        <Film size={32} style={{ color: 'var(--accent)', opacity: 0.7 }} className="mx-auto mb-3" />
        <p className="label" style={{ color: 'var(--t-med)' }}>Clip slot · drop video here</p>
        <p className="font-mono text-xs mt-2" style={{ color: 'var(--accent)' }}>{duration}</p>
      </div>
    </div>
  )
}

export default function Page() {
  return (
    <>
      {/* ─────────── HEADER ─────────── */}
      <header
        className="fixed top-0 left-0 right-0 z-50"
        style={{ backdropFilter: 'blur(14px)', background: 'rgba(3,3,8,0.65)', borderBottom: '1px solid var(--border)' }}
      >
        <div className="max-w-6xl mx-auto px-6 lg:px-8 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-md flex items-center justify-center" style={{ background: 'var(--accent)', color: '#000' }}>
              <span className="font-display font-black text-sm">A</span>
            </div>
            <span className="font-display font-extrabold tracking-[0.18em] text-sm">AXIOM</span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-sm" style={{ color: 'var(--t-med)' }}>
            <a href="#walkthrough" className="hover:text-white transition-colors">Walkthrough</a>
            <a href="#architecture" className="hover:text-white transition-colors">Architecture</a>
            <a href="#methodology" className="hover:text-white transition-colors">Methodology</a>
            <a href="#limits" className="hover:text-white transition-colors">Limits</a>
            <a href={GH_URL} target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors flex items-center gap-1.5">
              <Github size={14} /> GitHub
            </a>
          </nav>
        </div>
      </header>

      <main className="pt-14">
        {/* ─────────── HERO ─────────── */}
        <section className="px-6 lg:px-8 pt-28 pb-16">
          <div className="max-w-5xl mx-auto">
            <div className="flex flex-wrap gap-2 mb-10 fade-up">
              <span
                className="font-mono text-[10px] font-bold uppercase tracking-[0.22em] px-2.5 py-1 rounded"
                style={{ color: 'var(--accent)', background: 'var(--accent-10)', border: '1px solid var(--accent-20)' }}
              >
                Featured Project
              </span>
              <span
                className="font-mono text-[10px] uppercase tracking-[0.22em] px-2.5 py-1 rounded"
                style={{ color: 'var(--t-med)', border: '1px solid var(--border-2)' }}
              >
                Feb 2026 → Present
              </span>
            </div>

            <h1
              className="font-display mb-10 fade-up max-w-[18ch]"
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: 'clamp(2.5rem, 5.5vw, 4.25rem)',
                lineHeight: 1.02,
                letterSpacing: '-0.025em',
                fontWeight: 700,
              }}
            >
              Honest equity valuation,{' '}
              <span style={{ color: 'var(--accent)' }}>in your browser.</span>
            </h1>

            <p className="max-w-xl text-base sm:text-lg leading-relaxed mb-10 fade-up" style={{ color: 'var(--t-med)' }}>
              A 10-year DCF. Multiples shown as labelled context. A factor model in research mode. Built around one rule:{' '}
              <span style={{ color: 'var(--t-hi)' }}>the headline number has to mean what it says.</span>
            </p>

            <div className="flex flex-wrap gap-3 mb-12 fade-up">
              <a href={GH_URL} target="_blank" rel="noopener noreferrer" className="btn-primary">
                <Github size={15} />
                View on GitHub
                <ArrowUpRight size={14} />
              </a>
              <a href="#walkthrough" className="btn-ghost">
                Watch walkthrough
                <ArrowRight size={14} />
              </a>
            </div>

            <div
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg fade-up"
              style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}
            >
              <Database size={13} style={{ color: 'var(--accent)' }} />
              <span className="text-xs" style={{ color: 'var(--t-med)' }}>Data:</span>
              <a
                href="https://finance.yahoo.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs font-mono font-semibold inline-flex items-center gap-1"
                style={{ color: 'var(--accent)' }}
              >
                Yahoo Finance <ExternalLink size={10} />
              </a>
              <span className="text-xs" style={{ color: 'var(--t-low)' }}>· fundamentals · 10-yr forward projection</span>
            </div>
          </div>
        </section>

        {/* ─────────── HERO MEDIA — single big focal piece ─────────── */}
        <section className="px-6 lg:px-8 pb-24">
          <div className="max-w-6xl mx-auto">
            <ChromeFrame url="axiom.app/dashboard">
              <video
                src="/clips/hero.mp4"
                poster="/screens/01-dashboard.png"
                autoPlay
                loop
                muted
                playsInline
                preload="metadata"
                style={{ display: 'block', width: '100%', height: 'auto' }}
              />
            </ChromeFrame>
            <div className="flex justify-center mt-12">
              <a href="#premise" aria-label="scroll down">
                <ChevronDown size={26} style={{ color: 'var(--t-low)' }} className="bounce-y" />
              </a>
            </div>
          </div>
        </section>

        {/* ─────────── PREMISE — single huge pull quote ─────────── */}
        <section id="premise" className="px-6 lg:px-8 py-32" style={{ borderTop: '1px solid var(--border)' }}>
          <div className="max-w-4xl mx-auto">
            <p className="label mb-8" style={{ color: 'var(--accent)' }}>Why I built this</p>
            <p
              className="font-display font-bold tracking-[-0.025em] leading-[1.1] mb-12"
              style={{ fontSize: 'clamp(1.75rem, 4.5vw, 3.25rem)', color: 'var(--t-hi)' }}
            >
              I wanted a DCF tool where I could{' '}
              <span style={{ color: 'var(--accent)' }}>read every assumption</span>,{' '}
              <em style={{ color: 'var(--t-low)', fontStyle: 'normal' }}>change one</em>, and watch the headline move.
            </p>
            <p className="text-base sm:text-lg leading-relaxed max-w-2xl" style={{ color: 'var(--t-med)' }}>
              Most retail valuation tools either hide the math behind a single fair-value number, or bury it in a
              spreadsheet that nobody actually opens. AXIOM is my attempt at the version I wanted to use — a clean
              DCF, multiples shown as context, and every magic number in the codebase written down in one place.
            </p>
          </div>
        </section>

        {/* ─────────── WALKTHROUGH — three big focused blocks ─────────── */}
        <section id="walkthrough" className="px-6 lg:px-8 py-24" style={{ borderTop: '1px solid var(--border)' }}>
          <div className="max-w-6xl mx-auto">
            <p className="label mb-4" style={{ color: 'var(--accent)' }}>Walkthrough</p>
            <h2
              className="font-display font-bold tracking-[-0.025em] mb-5"
              style={{ fontSize: 'clamp(2rem, 5vw, 3.5rem)' }}
            >
              Three moments. Ninety seconds.
            </h2>
            <p className="text-base sm:text-lg max-w-2xl mb-24" style={{ color: 'var(--t-med)' }}>
              Each moment captures one slice of the workflow. Watch them in sequence and you&rsquo;ve seen the whole product.
            </p>

            <div className="space-y-32">
              {SECTIONS.map((s) => (
                <div key={s.n} className="grid lg:grid-cols-12 gap-10">
                  <div className="lg:col-span-4 lg:sticky lg:top-24 self-start">
                    <p className="font-mono text-xs mb-4" style={{ color: 'var(--accent)' }}>
                      {s.n} &nbsp;/&nbsp; 03
                    </p>
                    <h3
                      className="font-display font-bold tracking-[-0.02em] leading-tight mb-5"
                      style={{ fontSize: 'clamp(1.5rem, 2.5vw, 2rem)' }}
                    >
                      {s.title}
                    </h3>
                    <p className="text-sm sm:text-base leading-relaxed" style={{ color: 'var(--t-med)' }}>
                      {s.blurb}
                    </p>
                  </div>

                  <div className="lg:col-span-8 space-y-5">
                    {s.clip ? (
                      <ChromeFrame url={s.url}>
                        <video
                          src={s.clip}
                          poster={s.shot}
                          autoPlay
                          loop
                          muted
                          playsInline
                          preload="metadata"
                          style={{ display: 'block', width: '100%', height: 'auto' }}
                        />
                      </ChromeFrame>
                    ) : (
                      <>
                        <ClipSlot duration={s.duration} />
                        <ChromeFrame url={s.url}>
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img src={s.shot} alt={s.title} loading="lazy" />
                        </ChromeFrame>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ─────────── ARCHITECTURE ─────────── */}
        <section id="architecture" className="px-6 lg:px-8 py-32" style={{ borderTop: '1px solid var(--border)' }}>
          <div className="max-w-6xl mx-auto">
            <p className="label mb-4" style={{ color: 'var(--accent)' }}>Architecture</p>
            <h2
              className="font-display font-bold tracking-[-0.025em] mb-5"
              style={{ fontSize: 'clamp(2rem, 5vw, 3.5rem)' }}
            >
              How a ticker becomes a fair value.
            </h2>
            <p className="text-base sm:text-lg max-w-3xl mb-12" style={{ color: 'var(--t-med)' }}>
              Six stages. The DCF produces the headline. Comparables sit beside it as context. The factor model is in
              research mode — IC and t-stat are being measured walk-forward in <code className="font-mono text-sm">monitor.py</code>, not yet a user-facing signal.
            </p>

            <div className="card p-5 sm:p-6 inline-block max-w-full overflow-x-auto">
              <div className="flex items-stretch gap-2 w-fit">
                {PIPELINE.map((node, i) => {
                  const color = KIND_COLOR[node.kind]
                  return (
                    <div key={i} className="flex items-center gap-2 shrink-0">
                      <div
                        className="rounded-lg px-3 py-2.5 w-[150px]"
                        style={{
                          background: 'var(--bg)',
                          border: `1px solid ${color}`,
                          borderTopWidth: '3px',
                        }}
                      >
                        <p className="text-[12px] font-bold mb-0.5 leading-tight" style={{ color: 'var(--t-hi)' }}>{node.label}</p>
                        <p className="font-mono text-[10px] leading-tight" style={{ color: 'var(--t-med)' }}>{node.sub}</p>
                      </div>
                      {i < PIPELINE.length - 1 && (
                        <ArrowRight size={14} style={{ color: 'var(--t-low)' }} className="shrink-0" />
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </section>

        {/* ─────────── METHODOLOGY — five rules, condensed ─────────── */}
        <section id="methodology" className="px-6 lg:px-8 py-32" style={{ borderTop: '1px solid var(--border)' }}>
          <div className="max-w-5xl mx-auto">
            <p className="label mb-4" style={{ color: 'var(--accent)' }}>Methodology</p>
            <h2
              className="font-display font-bold tracking-[-0.025em] mb-16"
              style={{ fontSize: 'clamp(2rem, 5vw, 3.5rem)' }}
            >
              Five rules.
            </h2>

            <div className="space-y-10">
              {RULES.map((r) => (
                <div key={r.n} className="grid md:grid-cols-12 gap-6 pb-10" style={{ borderBottom: '1px solid var(--border)' }}>
                  <div className="md:col-span-2">
                    <p className="font-mono text-xs" style={{ color: 'var(--accent)' }}>{r.n}</p>
                  </div>
                  <div className="md:col-span-10">
                    <h3 className="text-lg sm:text-xl font-semibold mb-2 tracking-[-0.01em]" style={{ color: 'var(--t-hi)' }}>
                      {r.head}
                    </h3>
                    <p className="text-sm sm:text-base leading-relaxed" style={{ color: 'var(--t-med)' }}>
                      {r.body}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-12">
              <a
                href={GH_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm font-mono"
                style={{ color: 'var(--accent)' }}
              >
                Read the full methodology on GitHub
                <ArrowUpRight size={14} />
              </a>
            </div>
          </div>
        </section>

        {/* ─────────── STACK ─────────── */}
        <section className="px-6 lg:px-8 py-20" style={{ borderTop: '1px solid var(--border)' }}>
          <div className="max-w-5xl mx-auto">
            <p className="label mb-6">Stack</p>
            <div className="flex flex-wrap gap-2">
              {STACK.map((t) => (
                <span
                  key={t}
                  className="px-3 py-1.5 rounded-lg text-xs font-mono"
                  style={{
                    color: 'var(--t-med)',
                    background: 'var(--surface)',
                    border: '1px solid var(--border)',
                  }}
                >
                  {t}
                </span>
              ))}
            </div>
          </div>
        </section>

        {/* ─────────── LIMITATIONS — honest section ─────────── */}
        <section id="limits" className="px-6 lg:px-8 py-28" style={{ borderTop: '1px solid var(--border)' }}>
          <div className="max-w-5xl mx-auto">
            <p className="label mb-4" style={{ color: 'var(--accent)' }}>What this isn&rsquo;t (yet)</p>
            <h2
              className="font-display font-bold tracking-[-0.025em] mb-12"
              style={{ fontSize: 'clamp(1.75rem, 4vw, 2.75rem)' }}
            >
              Honest limits.
            </h2>

            <div className="grid md:grid-cols-2 gap-x-12 gap-y-8 text-sm sm:text-base leading-relaxed">
              <div>
                <p className="font-mono text-xs mb-2" style={{ color: 'var(--accent)' }}>01 &middot; Data</p>
                <p style={{ color: 'var(--t-med)' }}>
                  Fundamentals come from yfinance — free, but rate-limited and occasionally stale.
                  Some balance-sheet ratios returned by yfinance have unit inconsistencies; ratios known to be
                  unreliable (ROE, ROIC, D/E, Altman Z) are currently hidden from the UI rather than shown wrong.
                </p>
              </div>
              <div>
                <p className="font-mono text-xs mb-2" style={{ color: 'var(--accent)' }}>02 &middot; Hardcoded constants</p>
                <p style={{ color: 'var(--t-med)' }}>
                  Sub-sector multiples and a few WACC inputs are still hand-set. Every one of them lives in
                  <code className="font-mono text-xs"> HARDCODED_VALUES.md</code> with a phased plan to replace them with
                  live peer-comp computation.
                </p>
              </div>
              <div>
                <p className="font-mono text-xs mb-2" style={{ color: 'var(--accent)' }}>03 &middot; Factor model</p>
                <p style={{ color: 'var(--t-med)' }}>
                  The V/M/Q factor signal is in research mode. IC and t-stat tracking are wired up in
                  <code className="font-mono text-xs"> ml/monitor.py</code>, but the model isn&rsquo;t shown to end users
                  as a recommendation yet.
                </p>
              </div>
              <div>
                <p className="font-mono text-xs mb-2" style={{ color: 'var(--accent)' }}>04 &middot; Coverage</p>
                <p style={{ color: 'var(--t-med)' }}>
                  US-listed equities only. International tickers, ADRs without US listings, and derivatives are out of
                  scope. Banks and REITs use simpler P/B and P/FFO models — no full DCF for those archetypes.
                </p>
              </div>
              <div>
                <p className="font-mono text-xs mb-2" style={{ color: 'var(--accent)' }}>05 &middot; Not investment advice</p>
                <p style={{ color: 'var(--t-med)' }}>
                  The fair value depends on the assumptions. Change one input and the headline changes. AXIOM is a tool
                  for thinking through valuation, not a recommendation engine.
                </p>
              </div>
              <div>
                <p className="font-mono text-xs mb-2" style={{ color: 'var(--accent)' }}>06 &middot; Built solo</p>
                <p style={{ color: 'var(--t-med)' }}>
                  One person, learning in public. There are bugs. There are rough edges. The point is the
                  methodology and the willingness to write down what&rsquo;s actually under the hood.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ─────────── CTA ─────────── */}
        <section className="px-6 lg:px-8 py-32" style={{ borderTop: '1px solid var(--border)' }}>
          <div className="max-w-4xl mx-auto text-center">
            <h2
              className="font-display mb-6 mx-auto max-w-[22ch]"
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: 'clamp(2rem, 4.5vw, 3.25rem)',
                lineHeight: 1.05,
                letterSpacing: '-0.02em',
                fontWeight: 700,
              }}
            >
              The math is in the repo.{' '}
              <span style={{ color: 'var(--t-low)' }}>So are the limitations.</span>
            </h2>
            <p className="text-base sm:text-lg mb-12 max-w-xl mx-auto" style={{ color: 'var(--t-med)' }}>
              Every assumption is logged. Every formula is in Python you can read. The magic numbers have a file with their names on it.
            </p>
            <div className="flex flex-wrap gap-3 justify-center">
              <a href={GH_URL} target="_blank" rel="noopener noreferrer" className="btn-primary">
                <Github size={15} />
                View on GitHub
                <ArrowUpRight size={14} />
              </a>
              <a href={PORTFOLIO_URL} target="_blank" rel="noopener noreferrer" className="btn-ghost">
                <ExternalLink size={14} />
                More work →
              </a>
            </div>
          </div>
        </section>
      </main>

      <footer className="px-6 lg:px-8 py-10" style={{ borderTop: '1px solid var(--border)' }}>
        <div className="max-w-6xl mx-auto flex flex-wrap items-center justify-between gap-3">
          <p className="font-mono text-xs" style={{ color: 'var(--t-low)' }}>
            AXIOM &middot; Built by Subhankar Shukla &middot; {new Date().getFullYear()}
          </p>
          <div className="flex gap-6 text-xs" style={{ color: 'var(--t-low)' }}>
            <a href={GH_URL} target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">GitHub</a>
            <a href={LI_URL} target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">LinkedIn</a>
            <a href={PORTFOLIO_URL} target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Portfolio</a>
          </div>
        </div>
      </footer>
    </>
  )
}
