import Link from 'next/link'
import { ArrowLeft, Github } from 'lucide-react'

export const GH_URL = 'https://github.com/subhankarshukla04/Axiom-Valuations'
export const LI_URL = 'https://www.linkedin.com/in/subhankarshukla/'
export const PORTFOLIO_URL = 'https://subhankarshukla.vercel.app'

const NAV = [
  { label: 'Archetypes', href: '/archetypes' },
  { label: 'Examples', href: '/examples' },
  { label: 'Post-mortem', href: '/post-mortem' },
]

export function SiteHeader({ active }: { active?: string }) {
  return (
    <header
      className="fixed top-0 left-0 right-0 z-50"
      style={{ backdropFilter: 'blur(14px)', background: 'rgba(3,3,8,0.65)', borderBottom: '1px solid var(--border)' }}
    >
      <div className="max-w-6xl mx-auto px-6 lg:px-8 h-14 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-md flex items-center justify-center" style={{ background: 'var(--accent)', color: '#000' }}>
            <span className="font-display font-black text-sm">A</span>
          </div>
          <span className="font-display font-extrabold tracking-[0.18em] text-sm">AXIOM</span>
        </Link>
        <nav className="hidden md:flex items-center gap-8 text-sm" style={{ color: 'var(--t-med)' }}>
          {NAV.map((n) => (
            <Link
              key={n.href}
              href={n.href}
              className="transition-colors hover:text-white"
              style={active === n.href ? { color: 'var(--accent)' } : undefined}
            >
              {n.label}
            </Link>
          ))}
          <a href={GH_URL} target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors flex items-center gap-1.5">
            <Github size={14} /> GitHub
          </a>
        </nav>
      </div>
    </header>
  )
}

export function SiteFooter() {
  return (
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
  )
}

/** Small "back to overview" link used at the top of each deep-dive page. */
export function BackLink() {
  return (
    <Link
      href="/"
      className="inline-flex items-center gap-1.5 text-sm font-mono transition-colors hover:text-white"
      style={{ color: 'var(--t-low)' }}
    >
      <ArrowLeft size={14} /> AXIOM overview
    </Link>
  )
}
