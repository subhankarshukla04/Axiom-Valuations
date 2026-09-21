import type { Metadata } from 'next'
import Link from 'next/link'
import { ArrowRight, ArrowUpRight, Github } from 'lucide-react'
import { SiteHeader, SiteFooter, BackLink, GH_URL } from '../_components/SiteChrome'

export const metadata: Metadata = {
  title: 'Archetypes | AXIOM',
  description:
    'The 9-archetype router: why different businesses get different valuation math, and the boundary calls that decide which framework a company gets.',
}

type Archetype = {
  name: string
  tag: string
  pattern: string
  approach: string
  terminal: string
  example: string
}

// Criteria, terminal-growth, and examples are lifted from
// INVESTMENT_BANKING_METHODOLOGY.md (the router's own classification rules).
const ARCHETYPES: Archetype[] = [
  {
    name: 'Hyper-Growth',
    tag: 'HYPER_GROWTH',
    pattern: 'Growth > 30%, margins still negative.',
    approach: 'Revenue multiples, not DCF. Earnings are too early to discount.',
    terminal: '4.0%',
    example: 'Uber / DoorDash-style land-grab',
  },
  {
    name: 'Growth',
    tag: 'GROWTH',
    pattern: 'Growth 15-30%, margins > 5%.',
    approach: 'Standard DCF with a growth premium and slow decay.',
    terminal: '3.5%',
    example: 'NVIDIA, Microsoft',
  },
  {
    name: 'Stable Growth',
    tag: 'STABLE_GROWTH',
    pattern: 'Growth 8-15%, strong margins > 15%.',
    approach: 'Traditional DCF, the textbook compounder case.',
    terminal: '3.0%',
    example: 'Apple, Alphabet',
  },
  {
    name: 'Mature',
    tag: 'MATURE',
    pattern: 'Growth < 8%, profitable > 10% margin.',
    approach: 'FCF focus, lower growth assumptions, faster decay.',
    terminal: '2.0%',
    example: 'Coca-Cola',
  },
  {
    name: 'Cyclical',
    tag: 'CYCLICAL',
    pattern: 'Cyclical sector with volatile through-cycle margins.',
    approach: 'Normalize to through-cycle metrics, never on the peak.',
    terminal: '2.0%',
    example: 'Auto OEMs, airlines',
  },
  {
    name: 'High CapEx',
    tag: 'HIGH_CAPEX',
    pattern: 'CapEx > 25% of revenue.',
    approach: 'Normalize to steady-state maintenance CapEx (~60% of current).',
    terminal: '3.0%',
    example: 'Utilities, semis mid-buildout',
  },
  {
    name: 'Distressed',
    tag: 'DISTRESSED',
    pattern: 'Negative / very low margins, declining revenue.',
    approach: 'Normalize to industry averages; discount current earnings entirely.',
    terminal: '2.0%',
    example: 'Intel (current)',
  },
  {
    name: 'Turnaround',
    tag: 'TURNAROUND',
    pattern: 'Depressed metrics, but a credible recovery path.',
    approach: 'Normalized margins plus an explicit turnaround discount.',
    terminal: '2.0%',
    example: 'Intel fab transition',
  },
  {
    name: 'Financial',
    tag: 'FINANCIAL',
    pattern: 'Financial-services business model.',
    approach: 'P/B and ROE framework. A bank has no free cash flow to DCF.',
    terminal: 'P/B · ROE',
    example: 'JPMorgan, Goldman',
  },
]

type Boundary = {
  ticker: string
  looks: string
  routes: string
  because: string
  source: string
}

// The boundary calls are the point of the page: two archetypes are always
// plausible; the router has to pick one, and the pick changes the number.
const BOUNDARIES: Boundary[] = [
  {
    ticker: 'GFL',
    looks: 'a defensive waste hauler: contracted municipal volumes, 6%+ pricing power, recession-resistant tonnage.',
    routes: 'CYCLICAL, not defensive-stable.',
    because:
      'GFL trades on defensive volumes but carries a cyclical balance sheet: ~4.0x net leverage, an M&A-driven growth engine, capex-intensive operations. The router credits the pricing durability but discounts for the leverage and execution risk. It lands fair value at $41.44, right on top of the ~$40 price, which is the honest read: fundamentals are fairly valued, the Street’s extra upside is an event bet.',
    source: 'live AXIOM run, gfl_facts.md',
  },
  {
    ticker: 'A bank',
    looks: 'a Mature compounder: ~7% growth, a fat ~29% margin, steady dividends. Every screen wants to DCF it.',
    routes: 'FINANCIAL, not Mature.',
    because:
      'You cannot DCF a bank. Deposits are not debt, loans are not capex, and “free cash flow” has no clean meaning when the balance sheet is the business. Routing a bank to a DCF produces a confident, wrong number. FINANCIAL swaps in a P/B and ROE framework instead, the multiple that actually governs how banks are valued.',
    source: 'methodology doc, Financial archetype',
  },
  {
    ticker: 'Intel',
    looks: 'a broken Mature business: 2.3% margin, -5% growth. Value it on what it earns today and it screens as nearly worthless.',
    routes: 'DISTRESSED / TURNAROUND, not Mature.',
    because:
      'The margin is depressed by a fab buildout, not by permanent decline. Valuing on trough earnings understates the business; the router normalizes EBITDA toward the ~25% industry level and CapEx toward ~12% maintenance, then applies a turnaround discount. The whole call hinges on one question, whether the depression is temporary or structural, and the archetype is where you answer it out loud.',
    source: 'methodology doc, Intel example',
  },
]

export default function ArchetypesPage() {
  return (
    <>
      <SiteHeader active="/archetypes" />
      <main className="pt-14">
        {/* HERO */}
        <section className="px-6 lg:px-8 pt-24 pb-16">
          <div className="max-w-5xl mx-auto">
            <div className="mb-8 fade-up"><BackLink /></div>
            <p className="label mb-4 fade-up" style={{ color: 'var(--accent)' }}>Archetype Router</p>
            <h1
              className="font-display font-bold tracking-[-0.025em] mb-8 fade-up max-w-[16ch]"
              style={{ fontSize: 'clamp(2.25rem, 5vw, 3.75rem)', lineHeight: 1.04 }}
            >
              Different businesses get different math.
            </h1>
            <p className="max-w-2xl text-base sm:text-lg leading-relaxed fade-up" style={{ color: 'var(--t-med)' }}>
              Before AXIOM discounts a single cash flow, it decides <em style={{ color: 'var(--t-hi)', fontStyle: 'normal' }}>what kind of company</em> it is looking at.
              Nine archetypes, each with its own formula, decay schedule, and terminal growth. A hyper-growth name gets
              revenue multiples; a bank gets P/B; a cyclical gets normalized through the cycle. The interesting part is not
              the nine buckets. It is the calls at the boundary between two of them.
            </p>
          </div>
        </section>

        {/* THE NINE */}
        <section className="px-6 lg:px-8 py-20" style={{ borderTop: '1px solid var(--border)' }}>
          <div className="max-w-6xl mx-auto">
            <p className="label mb-4" style={{ color: 'var(--accent)' }}>The nine</p>
            <h2 className="font-display font-bold tracking-[-0.025em] mb-3" style={{ fontSize: 'clamp(1.75rem, 4vw, 2.75rem)' }}>
              One router, nine frameworks.
            </h2>
            <p className="text-sm sm:text-base max-w-2xl mb-12" style={{ color: 'var(--t-med)' }}>
              Pattern in, framework out. Terminal growth shown per archetype, the single assumption that moves a DCF most.
            </p>

            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {ARCHETYPES.map((a) => (
                <div key={a.tag} className="card p-5 flex flex-col">
                  <div className="flex items-baseline justify-between gap-3 mb-3">
                    <h3 className="text-lg font-semibold tracking-[-0.01em]" style={{ color: 'var(--t-hi)' }}>{a.name}</h3>
                    <span
                      className="font-mono text-[10px] px-2 py-0.5 rounded shrink-0"
                      style={{ color: 'var(--accent)', background: 'var(--accent-10)', border: '1px solid var(--accent-20)' }}
                    >
                      g&nbsp;{a.terminal}
                    </span>
                  </div>
                  <p className="text-sm leading-relaxed mb-3" style={{ color: 'var(--t-hi)' }}>{a.pattern}</p>
                  <p className="text-sm leading-relaxed mb-4" style={{ color: 'var(--t-med)' }}>{a.approach}</p>
                  <div className="mt-auto flex items-center justify-between gap-3 pt-3" style={{ borderTop: '1px solid var(--border)' }}>
                    <span className="font-mono text-[10px] tracking-wide" style={{ color: 'var(--t-low)' }}>{a.tag}</span>
                    <span className="text-xs text-right" style={{ color: 'var(--t-low)' }}>{a.example}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* BOUNDARY CALLS */}
        <section className="px-6 lg:px-8 py-24" style={{ borderTop: '1px solid var(--border)' }}>
          <div className="max-w-5xl mx-auto">
            <p className="label mb-4" style={{ color: 'var(--accent)' }}>Boundary calls</p>
            <h2 className="font-display font-bold tracking-[-0.025em] mb-5" style={{ fontSize: 'clamp(1.75rem, 4vw, 2.75rem)' }}>
              Where the classification actually matters.
            </h2>
            <p className="text-base sm:text-lg max-w-2xl mb-16" style={{ color: 'var(--t-med)' }}>
              A clean case routes itself. The names worth arguing about sit between two archetypes, and the pick changes the
              answer by more than the discount rate ever will. Three of them:
            </p>

            <div className="space-y-14">
              {BOUNDARIES.map((b) => (
                <div key={b.ticker} className="grid lg:grid-cols-12 gap-6 lg:gap-10 pb-14" style={{ borderBottom: '1px solid var(--border)' }}>
                  <div className="lg:col-span-3">
                    <p className="font-display font-bold text-2xl mb-2" style={{ color: 'var(--t-hi)' }}>{b.ticker}</p>
                    <p className="font-mono text-[10px] tracking-wide" style={{ color: 'var(--accent)' }}>{b.routes}</p>
                  </div>
                  <div className="lg:col-span-9 space-y-4">
                    <p className="text-sm sm:text-base leading-relaxed">
                      <span className="font-mono text-xs mr-2" style={{ color: 'var(--t-low)' }}>LOOKS LIKE</span>
                      <span style={{ color: 'var(--t-med)' }}>{b.looks}</span>
                    </p>
                    <p className="text-sm sm:text-base leading-relaxed" style={{ color: 'var(--t-hi)' }}>{b.because}</p>
                    <p className="font-mono text-[10px]" style={{ color: 'var(--t-low)' }}>source · {b.source}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="px-6 lg:px-8 py-24" style={{ borderTop: '1px solid var(--border)' }}>
          <div className="max-w-4xl mx-auto">
            <h2 className="font-display font-bold tracking-[-0.025em] mb-6" style={{ fontSize: 'clamp(1.5rem, 3.5vw, 2.5rem)' }}>
              See a boundary call run end to end.
            </h2>
            <p className="text-base sm:text-lg mb-10 max-w-xl" style={{ color: 'var(--t-med)' }}>
              GFL is the worked example: the full path from archetype decision to a bear / base / bull fair value.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link href="/examples" className="btn-primary">
                Worked examples
                <ArrowRight size={14} />
              </Link>
              <a href={GH_URL} target="_blank" rel="noopener noreferrer" className="btn-ghost">
                <Github size={14} />
                The router in code
                <ArrowUpRight size={14} />
              </a>
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  )
}
