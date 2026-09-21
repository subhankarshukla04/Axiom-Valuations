import type { Metadata } from 'next'
import Link from 'next/link'
import { ArrowRight, ArrowUpRight, Github } from 'lucide-react'
import { SiteHeader, SiteFooter, BackLink, GH_URL } from '../_components/SiteChrome'

export const metadata: Metadata = {
  title: 'Worked examples | AXIOM',
  description:
    'GFL run end to end: archetype decision, method blend, and a bear / base / bull fair value, plus archetype reference cases for Apple, NVIDIA, and Intel.',
}

// GFL figures are a live AXIOM run, cited to gfl-2026-08/axiom_output.md + gfl_facts.md.
const GFL_SCENARIOS = [
  { label: 'Bear', value: '$35.62', tone: 'var(--red)' },
  { label: 'Base', value: '$41.44', tone: 'var(--accent)' },
  { label: 'Bull', value: '$53.25', tone: 'var(--green)' },
]

const GFL_BLEND = [
  { method: 'Clean DCF', weight: '50%', ev: '$13.7B' },
  { method: 'EV / EBITDA', weight: '25%', ev: '$19.9B' },
  { method: 'P / E', weight: '25%', ev: '$6.0B' },
]

// Reference cases are illustrative, drawn from INVESTMENT_BANKING_METHODOLOGY.md
// (2024/2025 vintage) to show how each archetype changes the treatment, not live runs.
const REFERENCE = [
  {
    ticker: 'AAPL',
    archetype: 'Stable Growth',
    inputs: '8% growth · 25.7% margin · beta 1.25',
    treatment: 'Standard DCF, 3.0% terminal, brand-premium multiple.',
    value: '~$2.8-3.2T',
    read: 'fairly valued',
  },
  {
    ticker: 'NVDA',
    archetype: 'Growth',
    inputs: '95% growth · 48.9% margin · beta 1.68',
    treatment: 'Growth premium, slow 88% decay, 3.5% terminal.',
    value: '~$1.3-1.5T',
    read: 'depends on AI durability',
  },
  {
    ticker: 'INTC',
    archetype: 'Distressed',
    inputs: '-5% growth · 2.3% margin · 45% capex',
    treatment: 'Normalize EBITDA to ~25%, capex to ~12%; turnaround discount.',
    value: '~$220-280B',
    read: 'if the transition works',
  },
]

export default function ExamplesPage() {
  return (
    <>
      <SiteHeader active="/examples" />
      <main className="pt-14">
        {/* HERO */}
        <section className="px-6 lg:px-8 pt-24 pb-16">
          <div className="max-w-5xl mx-auto">
            <div className="mb-8 fade-up"><BackLink /></div>
            <p className="label mb-4 fade-up" style={{ color: 'var(--accent)' }}>Worked examples</p>
            <h1
              className="font-display font-bold tracking-[-0.025em] mb-8 fade-up max-w-[15ch]"
              style={{ fontSize: 'clamp(2.25rem, 5vw, 3.75rem)', lineHeight: 1.04 }}
            >
              One ticker, all the way through.
            </h1>
            <p className="max-w-2xl text-base sm:text-lg leading-relaxed fade-up" style={{ color: 'var(--t-med)' }}>
              GFL is the flagship: a real run, every number traceable, from the archetype call to a bear / base / bull fair
              value. Below it, three reference cases show how the same engine treats an Apple, an NVIDIA, and an Intel
              differently, because they are different kinds of company.
            </p>
          </div>
        </section>

        {/* GFL FLAGSHIP */}
        <section className="px-6 lg:px-8 py-16" style={{ borderTop: '1px solid var(--border)' }}>
          <div className="max-w-5xl mx-auto">
            <div className="flex flex-wrap items-center gap-3 mb-8">
              <span className="font-display font-bold text-2xl" style={{ color: 'var(--t-hi)' }}>GFL Environmental</span>
              <span
                className="font-mono text-[10px] px-2 py-0.5 rounded"
                style={{ color: 'var(--accent)', background: 'var(--accent-10)', border: '1px solid var(--accent-20)' }}
              >
                CYCLICAL · industrial_cong
              </span>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded" style={{ color: 'var(--t-med)', border: '1px solid var(--border-2)' }}>
                WACC 8.2%
              </span>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded" style={{ color: 'var(--t-med)', border: '1px solid var(--border-2)' }}>
                HOLD
              </span>
            </div>

            {/* bear / base / bull */}
            <div className="grid grid-cols-3 gap-3 sm:gap-4 mb-4">
              {GFL_SCENARIOS.map((s) => (
                <div key={s.label} className="card p-5 text-center">
                  <p className="font-mono text-[10px] uppercase tracking-[0.2em] mb-2" style={{ color: 'var(--t-low)' }}>{s.label}</p>
                  <p className="font-display font-bold" style={{ fontSize: 'clamp(1.4rem, 4vw, 2.4rem)', color: s.tone }}>{s.value}</p>
                </div>
              ))}
            </div>
            <p className="text-sm mb-12" style={{ color: 'var(--t-low)' }}>
              Base fair value <span style={{ color: 'var(--t-hi)' }}>$41.44</span> vs a ~$39.26 price, about +5.6%. Right on top of the tape.
            </p>

            {/* method blend */}
            <div className="grid lg:grid-cols-2 gap-10">
              <div>
                <p className="label mb-4" style={{ color: 'var(--accent)' }}>How the base is built</p>
                <div className="card overflow-hidden">
                  {GFL_BLEND.map((b, i) => (
                    <div
                      key={b.method}
                      className="flex items-center justify-between px-5 py-3.5 text-sm"
                      style={i < GFL_BLEND.length ? { borderBottom: '1px solid var(--border)' } : undefined}
                    >
                      <span style={{ color: 'var(--t-hi)' }}>{b.method}</span>
                      <span className="flex items-center gap-4">
                        <span className="font-mono text-xs" style={{ color: 'var(--t-low)' }}>{b.weight}</span>
                        <span className="font-mono" style={{ color: 'var(--t-med)' }}>{b.ev}</span>
                      </span>
                    </div>
                  ))}
                  <div className="flex items-center justify-between px-5 py-3.5 text-sm" style={{ background: 'var(--surface)' }}>
                    <span className="font-semibold" style={{ color: 'var(--t-hi)' }}>Blended equity</span>
                    <span className="font-mono font-semibold" style={{ color: 'var(--accent)' }}>$14.96B ($41.44/sh)</span>
                  </div>
                </div>
                <p className="font-mono text-[10px] mt-3" style={{ color: 'var(--t-low)' }}>
                  source · live AXIOM run, gfl_facts.md (FY26 guidance midpoint, CAD to USD 0.73, net debt $6.87B, 361M sh)
                </p>
              </div>

              <div>
                <p className="label mb-4" style={{ color: 'var(--accent)' }}>The call the archetype forces</p>
                <p className="text-sm sm:text-base leading-relaxed mb-4" style={{ color: 'var(--t-hi)' }}>
                  GFL trades on defensive volumes but carries a cyclical balance sheet. Routing it CYCLICAL credits the pricing
                  durability and discounts for ~4.0x leverage and M&amp;A execution risk. The engine lands at $41, right on the
                  price.
                </p>
                <p className="text-sm sm:text-base leading-relaxed" style={{ color: 'var(--t-med)' }}>
                  The Street sits near $55, Buy-heavy. That ~$14 gap over the price reads as a capitalised take-private premium,
                  not operating value. On fundamentals, GFL is fairly valued, which is the whole, falsifiable point.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* REFERENCE CASES */}
        <section className="px-6 lg:px-8 py-20" style={{ borderTop: '1px solid var(--border)' }}>
          <div className="max-w-5xl mx-auto">
            <p className="label mb-4" style={{ color: 'var(--accent)' }}>Reference cases</p>
            <h2 className="font-display font-bold tracking-[-0.025em] mb-3" style={{ fontSize: 'clamp(1.75rem, 4vw, 2.75rem)' }}>
              Same engine, different math.
            </h2>
            <p className="text-sm sm:text-base max-w-2xl mb-10" style={{ color: 'var(--t-med)' }}>
              Illustrative, from the methodology doc rather than a live run, enough to show that the archetype, not the
              analyst, decides the treatment.
            </p>

            <div className="space-y-3">
              {REFERENCE.map((r) => (
                <div key={r.ticker} className="card p-5 grid sm:grid-cols-12 gap-4 items-center">
                  <div className="sm:col-span-2">
                    <p className="font-display font-bold text-lg" style={{ color: 'var(--t-hi)' }}>{r.ticker}</p>
                    <p className="font-mono text-[10px]" style={{ color: 'var(--accent)' }}>{r.archetype}</p>
                  </div>
                  <div className="sm:col-span-4">
                    <p className="font-mono text-xs" style={{ color: 'var(--t-med)' }}>{r.inputs}</p>
                  </div>
                  <div className="sm:col-span-4">
                    <p className="text-sm" style={{ color: 'var(--t-med)' }}>{r.treatment}</p>
                  </div>
                  <div className="sm:col-span-2 sm:text-right">
                    <p className="font-mono text-sm" style={{ color: 'var(--t-hi)' }}>{r.value}</p>
                    <p className="text-[11px]" style={{ color: 'var(--t-low)' }}>{r.read}</p>
                  </div>
                </div>
              ))}
            </div>
            <p className="font-mono text-[10px] mt-4" style={{ color: 'var(--t-low)' }}>
              source · INVESTMENT_BANKING_METHODOLOGY.md, 2024/2025 vintage · illustrative, not current fair values
            </p>
          </div>
        </section>

        {/* CTA */}
        <section className="px-6 lg:px-8 py-24" style={{ borderTop: '1px solid var(--border)' }}>
          <div className="max-w-4xl mx-auto">
            <div className="flex flex-wrap gap-3">
              <Link href="/archetypes" className="btn-primary">
                Why GFL routes cyclical
                <ArrowRight size={14} />
              </Link>
              <a href={GH_URL} target="_blank" rel="noopener noreferrer" className="btn-ghost">
                <Github size={14} />
                Run it yourself
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
