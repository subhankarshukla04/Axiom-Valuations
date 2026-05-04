import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AXIOM — Honest equity valuation, in your browser.',
  description:
    'A clean DCF, multiples as labelled context, and a factor-based ranking signal — built around one rule: the headline number has to mean what it says.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-theme="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&family=Syne:wght@500;600;700;800&display=swap"
        />
      </head>
      <body>
        <div className="bg-orbs" aria-hidden>
          <span className="orb orb-1" />
          <span className="orb orb-2" />
          <span className="orb orb-3" />
        </div>
        {children}
      </body>
    </html>
  )
}
