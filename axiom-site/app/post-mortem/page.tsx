import type { Metadata } from 'next'
import Link from 'next/link'
import { ArrowRight, ArrowUpRight, Github } from 'lucide-react'
import { SiteHeader, SiteFooter, BackLink, GH_URL } from '../_components/SiteChrome'

export const metadata: Metadata = {
  title: 'Post-mortem | AXIOM',
  description:
    'Why the ML correction layer got deleted: the number labelled DCF Fair Value was a blend plus a machine-learning multiplier. The rebuild, in three pivots.',
}

type Pivot = {
  n: string
  title: string
  before: string
  after: string
}

// All content lifted from valuation_app/AXIOM_STORY.md.
const PIVOTS: Pivot[] = [
  {
    n: '01',
    title: 'Make the DCF honest.',
    before:
      'The headline blended a DCF with EV/EBITDA and P/E, then multiplied the result by an ML “correction factor.” Each step made sense locally: add multiples for context, blend them in, patch the errors with ML. The sum was a number with no clean financial meaning.',
    after:
      'Stripped back to a single DCF: PV of ten years of free cash flow, plus terminal value, plus cash, minus debt, over shares. No blending, no multiplier, no analyst anchor. The sensitivity table now runs the same formula, so the headline and the table can never disagree again. Deleted the calibrator, the blend weights, the analyst anchor, and a backtest file that hardcoded a 9.5% WACC for every company regardless of sector or leverage.',
  },
  {
    n: '02',
    title: 'ML should learn the signal, not patch the output.',
    before:
      'The old model learned “when our prediction was wrong by X%, correct future predictions by X%.” That is circular: it patches its own mistakes without understanding why it was wrong. It could never generalise, because it was trained on its own error, not on the market.',
    after:
      'Rebuilt around three cross-sectional factors, each Z-scored within sub-sector. Value: DCF price over market price, minus one. Momentum: 12-month return versus the sector ETF, dropping the most recent month, the Jegadeesh-Titman factor. Quality: free-cash-flow yield. The model now learns what actually predicts sector-relative outperformance, not how far off it was last year.',
  },
  {
    n: '03',
    title: 'Measure what a ranking model is for.',
    before:
      'Evaluation was mean absolute error on price predictions. That is meaningless for a ranking model. A model can be 30% off on price and still be an excellent signal if it ranks the winners above the losers.',
    after:
      'Switched to Information Coefficient, the rank correlation between predicted attractiveness and subsequent excess return. Real signal means IC above zero with a t-statistic of at least 2. Added hit rate by quintile: does the top quintile actually beat the median? The report now says whether the model adds value, instead of flattering it.',
  },
]

export default function PostMortemPage() {
  return (
    <>
      <SiteHeader active="/post-mortem" />
      <main className="pt-14">
        {/* HERO */}
        <section className="px-6 lg:px-8 pt-24 pb-16">
          <div className="max-w-5xl mx-auto">
            <div className="mb-8 fade-up"><BackLink /></div>
            <p className="label mb-4 fade-up" style={{ color: 'var(--accent)' }}>Post-mortem</p>
            <h1
              className="font-display font-bold tracking-[-0.025em] mb-8 fade-up max-w-[18ch]"
              style={{ fontSize: 'clamp(2.25rem, 5vw, 3.75rem)', lineHeight: 1.04 }}
            >
              The number said DCF. It wasn&rsquo;t a DCF.
            </h1>
            <p className="max-w-2xl text-base sm:text-lg leading-relaxed fade-up" style={{ color: 'var(--t-med)' }}>
              The most important thing I shipped on AXIOM was a deletion. The layer that made the demo look smartest, a
              machine-learning correction on top of the valuation, was the layer that made the headline number a lie. Here
              is what was wrong, and the three pivots that fixed it.
            </p>
          </div>
        </section>

        {/* THE TELL */}
        <section className="px-6 lg:px-8 py-20" style={{ borderTop: '1px solid var(--border)' }}>
          <div className="max-w-4xl mx-auto">
            <p className="label mb-6" style={{ color: 'var(--accent)' }}>The tell</p>
            <p
              className="font-display font-bold tracking-[-0.025em] leading-[1.15] mb-10"
              style={{ fontSize: 'clamp(1.5rem, 3.5vw, 2.5rem)', color: 'var(--t-hi)' }}
            >
              The headline read <span style={{ color: 'var(--red)' }}>$531</span>. The real DCF was{' '}
              <span style={{ color: 'var(--green)' }}>$380</span>. The sensitivity table below it, running an honest DCF,
              agreed with the $380, and quietly contradicted the number at the top of the page.
            </p>
            <p className="text-base leading-relaxed max-w-2xl" style={{ color: 'var(--t-med)' }}>
              That $151 gap was multiple expansion and ML fudging, stacked on a cell labelled <em style={{ color: 'var(--t-hi)', fontStyle: 'normal' }}>DCF Fair Value</em>.
              It was not dishonest by design; it grew one reasonable step at a time. But once a page argues with itself, the
              only fix is to tear out the thing that has no clean interpretation, even when it is the part that demos well.
            </p>
          </div>
        </section>

        {/* PIVOTS */}
        <section className="px-6 lg:px-8 py-20" style={{ borderTop: '1px solid var(--border)' }}>
          <div className="max-w-5xl mx-auto">
            <p className="label mb-4" style={{ color: 'var(--accent)' }}>The rebuild</p>
            <h2 className="font-display font-bold tracking-[-0.025em] mb-16" style={{ fontSize: 'clamp(1.75rem, 4vw, 2.75rem)' }}>
              Three pivots.
            </h2>

            <div className="space-y-16">
              {PIVOTS.map((p) => (
                <div key={p.n} className="grid lg:grid-cols-12 gap-6 lg:gap-10">
                  <div className="lg:col-span-4 lg:sticky lg:top-24 self-start">
                    <p className="font-mono text-xs mb-3" style={{ color: 'var(--accent)' }}>{p.n} / 03</p>
                    <h3 className="font-display font-bold tracking-[-0.02em] leading-tight" style={{ fontSize: 'clamp(1.35rem, 2.5vw, 1.9rem)' }}>
                      {p.title}
                    </h3>
                  </div>
                  <div className="lg:col-span-8 space-y-5">
                    <div>
                      <p className="font-mono text-[10px] mb-2" style={{ color: 'var(--red)' }}>BEFORE</p>
                      <p className="text-sm sm:text-base leading-relaxed" style={{ color: 'var(--t-med)' }}>{p.before}</p>
                    </div>
                    <div>
                      <p className="font-mono text-[10px] mb-2" style={{ color: 'var(--green)' }}>AFTER</p>
                      <p className="text-sm sm:text-base leading-relaxed" style={{ color: 'var(--t-hi)' }}>{p.after}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* STILL WAITING */}
        <section className="px-6 lg:px-8 py-20" style={{ borderTop: '1px solid var(--border)' }}>
          <div className="max-w-4xl mx-auto">
            <p className="label mb-4" style={{ color: 'var(--accent)' }}>What&rsquo;s still waiting on time</p>
            <h2 className="font-display font-bold tracking-[-0.025em] mb-8" style={{ fontSize: 'clamp(1.5rem, 3.5vw, 2.5rem)' }}>
              The signal stays hidden until the data earns it.
            </h2>
            <p className="text-base leading-relaxed max-w-2xl mb-6" style={{ color: 'var(--t-med)' }}>
              The factor infrastructure is live: three signals computed daily across the tracked universe and logged to disk,
              retrained on price history since 2022. But the ranking is not shown to users, and won&rsquo;t be, until it clears a
              statistically significant IC (t-stat of at least 2) over at least 24 months of out-of-sample data.
            </p>
            <p className="text-base leading-relaxed max-w-2xl" style={{ color: 'var(--t-med)' }}>
              A fourth factor, whether a company&rsquo;s margin is improving or declining, needs twelve months of daily
              snapshots before it can be computed. That data arrives in 2027. Until then it stays out of the model rather
              than getting faked in.
            </p>
          </div>
        </section>

        {/* ONE-LINER */}
        <section className="px-6 lg:px-8 py-28" style={{ borderTop: '1px solid var(--border)' }}>
          <div className="max-w-4xl mx-auto">
            <p className="label mb-8" style={{ color: 'var(--accent)' }}>The honest one-liner</p>
            <p
              className="font-display font-bold tracking-[-0.025em] leading-[1.2] mb-6"
              style={{ fontSize: 'clamp(1.4rem, 3vw, 2.1rem)', color: 'var(--t-low)' }}
            >
              From: <span style={{ color: 'var(--t-hi)' }}>apply a DCF, blend it with multiples, slap an ML multiplier on top, call it DCF Fair Value.</span>
            </p>
            <p
              className="font-display font-bold tracking-[-0.025em] leading-[1.2]"
              style={{ fontSize: 'clamp(1.4rem, 3vw, 2.1rem)', color: 'var(--t-low)' }}
            >
              To: <span style={{ color: 'var(--accent)' }}>run a clean DCF, score companies on three independent factors, let the data say whether the model works.</span>
            </p>
          </div>
        </section>

        {/* CTA */}
        <section className="px-6 lg:px-8 py-24" style={{ borderTop: '1px solid var(--border)' }}>
          <div className="max-w-4xl mx-auto">
            <div className="flex flex-wrap gap-3">
              <Link href="/archetypes" className="btn-primary">
                How the router picks the math
                <ArrowRight size={14} />
              </Link>
              <a href={GH_URL} target="_blank" rel="noopener noreferrer" className="btn-ghost">
                <Github size={14} />
                Read the code
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
