import { useState, useEffect } from 'react'

export default function App() {
  const [stars, setStars] = useState(null)
  const [clones, setClones] = useState(null)
  useEffect(() => {
    fetch('https://api.github.com/repos/snuweb/llmspend')
      .then(r => r.json())
      .then(d => { if (d.stargazers_count != null) setStars(d.stargazers_count) })
      .catch(() => {})
  }, [])

  return (
    <>
      {/* ── Nav ──────────────────────────────────── */}
      <nav className="nav">
        <div className="nav-inner">
          <a href="/" className="nav-brand">
            <span className="nav-mark">llm</span>spend
          </a>
          <div className="nav-links">
            <a href="#features">Features</a>
            <a href="#pricing">Pricing</a>
            <a href="https://github.com/snuweb/llmspend" target="_blank" rel="noopener">GitHub{stars != null ? ` (${stars})` : ''}</a>
            <a href="https://github.com/snuweb/llmspend#readme" target="_blank" rel="noopener">Docs</a>
            <a href="https://github.com/snuweb/llmspend" target="_blank" rel="noopener" className="nav-cta">Get Started</a>
          </div>
        </div>
      </nav>

      {/* ── Hero ─────────────────────────────────── */}
      <section className="hero">
        <div className="hero-inner">
          <div className="hero-badge">Open Source · MIT Licensed · 6 Providers</div>
          <h1>Stop overpaying<br />for AI inference</h1>
          <p className="hero-sub">
            LLMSpend tracks your LLM costs per feature, per model, per user — then routes
            each call to the cheapest model that works. Two lines of code. Average savings: 40–60%.
          </p>
          <div className="hero-actions">
            <a href="https://github.com/snuweb/llmspend" target="_blank" rel="noopener">
              <button className="btn-primary">
                <span className="btn-icon">$</span> pip install llmspend
              </button>
            </a>
            <a href="https://github.com/snuweb/llmspend" target="_blank" rel="noopener">
              <button className="btn-ghost">View on GitHub →</button>
            </a>
          </div>
          <div className="hero-proof">
            <span>Works with</span>
            <span className="proof-provider">Anthropic</span>
            <span className="proof-dot" />
            <span className="proof-provider">OpenAI</span>
            <span className="proof-dot" />
            <span className="proof-provider">Google</span>
            <span className="proof-dot" />
            <span className="proof-provider">Groq</span>
            <span className="proof-dot" />
            <span className="proof-provider">Mistral</span>
            <span className="proof-dot" />
            <span className="proof-provider">DeepSeek</span>
          </div>
        </div>
      </section>

      {/* ── Code ─────────────────────────────────── */}
      <section className="code-section">
        <div className="code-inner">
          <div className="code-block">
            <div className="code-header">
              <div className="code-dots"><span /><span /><span /></div>
              <span className="code-filename">app.py</span>
            </div>
            <pre className="code-body">{codeSnippet}</pre>
          </div>
          <div className="code-block">
            <div className="code-header">
              <div className="code-dots"><span /><span /><span /></div>
              <span className="code-filename">terminal</span>
            </div>
            <pre className="code-body">{cliSnippet}</pre>
          </div>
        </div>
      </section>

      {/* ── Problem ──────────────────────────────── */}
      <section className="problem">
        <div className="problem-inner">
          <h2>The problem with AI costs</h2>
          <div className="problem-grid">
            <div className="problem-card">
              <div className="problem-num">70%</div>
              <p>of LLM calls don't need the most expensive model</p>
            </div>
            <div className="problem-card">
              <div className="problem-num">$0</div>
              <p>visibility into which feature or user is burning your budget</p>
            </div>
            <div className="problem-card">
              <div className="problem-num">5–10×</div>
              <p>what most teams overpay by using one model for everything</p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Features ─────────────────────────────── */}
      <section className="features" id="features">
        <div className="features-inner">
          <h2>Everything you need to control AI costs</h2>
          <div className="features-grid">
            {[
              { title: 'Cost per feature', desc: 'Tag API calls with feature names. See exactly which part of your app costs what.' },
              { title: 'Per-user attribution', desc: 'One user burning 60% of your budget? Know instantly. Attribute costs to individual users or sessions.' },
              { title: 'Model breakdown', desc: 'Sonnet for reasoning, Haiku for chat. See the cost split by model and find where to downgrade.' },
              { title: 'Budget alerts', desc: 'Get notified when daily spend exceeds your threshold. Telegram, Slack, email, or webhook.' },
              { title: 'Smart routing', desc: 'Coming soon — automatically route each call to the cheapest model that can handle the task.' },
              { title: 'Works offline', desc: 'No backend needed. Logs to local SQLite. View costs with the CLI. Your data never leaves your machine.' },
            ].map((f, i) => (
              <div key={i} className="feature-card">
                <h3>{f.title}</h3>
                <p>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How it works ─────────────────────────── */}
      <section className="how">
        <div className="how-inner">
          <h2>Two lines. That's it.</h2>
          <div className="how-steps">
            <div className="how-step">
              <div className="step-num">1</div>
              <div>
                <h3>Wrap your client</h3>
                <p>One function call. Returns the same API. Your existing code doesn't change.</p>
              </div>
            </div>
            <div className="how-step">
              <div className="step-num">2</div>
              <div>
                <h3>Ship and see costs</h3>
                <p>Every API call is tracked automatically. Run <code>llmspend stats</code> or open the dashboard.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Dashboard Preview ────────────────────── */}
      <section className="dash">
        <div className="dash-inner">
          <h2>Real-time cost intelligence</h2>
          <div className="dash-grid">
            <div className="dash-card"><div className="dash-label">Today</div><div className="dash-value">$4.23</div><div className="dash-sub">↑ 12% vs yesterday</div></div>
            <div className="dash-card"><div className="dash-label">Calls</div><div className="dash-value">1,847</div><div className="dash-sub">3 features</div></div>
            <div className="dash-card"><div className="dash-label">Top cost</div><div className="dash-value">chatbot</div><div className="dash-sub">$2.94 — 68%</div></div>
            <div className="dash-card"><div className="dash-label">Latency</div><div className="dash-value">430ms</div><div className="dash-sub">p50</div></div>
          </div>
          <div className="dash-table">
            <table>
              <thead><tr><th>Feature</th><th>Model</th><th>Calls</th><th>Cost</th><th>Latency</th></tr></thead>
              <tbody>
                <tr><td>chatbot</td><td>claude-haiku-4-5</td><td>1,234</td><td className="green">$2.94</td><td>180ms</td></tr>
                <tr><td>summarizer</td><td>claude-sonnet-4-6</td><td>312</td><td className="green">$1.87</td><td>1.2s</td></tr>
                <tr><td>classifier</td><td>gpt-4o-mini</td><td>201</td><td className="green">$0.42</td><td>95ms</td></tr>
                <tr><td>embeddings</td><td>text-embedding-3</td><td>100</td><td className="green">$0.03</td><td>45ms</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* ── Pricing ──────────────────────────────── */}
      <section className="pricing" id="pricing">
        <div className="pricing-inner">
          <h2>Simple pricing</h2>
          <p className="pricing-sub">Start free. Upgrade when you need smart routing.</p>
          <div className="pricing-grid">
            <div className="pricing-card">
              <h3>Open Source</h3>
              <div className="pricing-price">$0</div>
              <div className="pricing-period">forever</div>
              <ul>
                <li>Cost tracking per feature, model, user</li>
                <li>CLI + local dashboard</li>
                <li>6 providers supported</li>
                <li>Local SQLite — data stays on your machine</li>
                <li>Unlimited API calls</li>
                <li>MIT licensed</li>
              </ul>
              <a href="https://github.com/snuweb/llmspend" target="_blank" rel="noopener">
                <button className="btn-ghost btn-full">pip install llmspend</button>
              </a>
            </div>
            <div className="pricing-card pricing-featured">
              <div className="pricing-badge">Coming Soon</div>
              <h3>Smart Router</h3>
              <div className="pricing-price">15%</div>
              <div className="pricing-period">of savings</div>
              <ul>
                <li>Everything in Open Source</li>
                <li>Automatic model routing per task</li>
                <li>Multi-provider optimization</li>
                <li>Save 40–60% on inference costs</li>
                <li>Hosted dashboard + alerts</li>
                <li>You only pay when we save you money</li>
              </ul>
              <button className="btn-primary btn-full" disabled>Join Waitlist</button>
            </div>
          </div>
        </div>
      </section>

      {/* ── Providers ────────────────────────────── */}
      <section className="providers">
        <div className="providers-inner">
          <h2>Supports every major provider</h2>
          <div className="provider-grid">
            {['Anthropic', 'OpenAI', 'Google Gemini', 'Groq', 'Mistral', 'DeepSeek'].map(p => (
              <div key={p} className="provider-pill">{p}</div>
            ))}
          </div>
          <p className="provider-help">Missing yours? <a href="https://github.com/snuweb/llmspend/blob/main/CONTRIBUTING.md" target="_blank" rel="noopener">Add it in ~20 lines</a></p>
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────── */}
      <section className="final-cta">
        <div className="cta-inner">
          <h2>Your AI bill is higher than it needs to be</h2>
          <p>Install LLMSpend. See where the money goes. Keep more of it.</p>
          <div className="cta-actions">
            <a href="https://github.com/snuweb/llmspend" target="_blank" rel="noopener">
              <button className="btn-primary">Get Started — Free</button>
            </a>
          </div>
        </div>
      </section>

      {/* ── Footer ───────────────────────────────── */}
      <footer className="footer">
        <div className="footer-inner">
          <div className="footer-brand">
            <span className="nav-mark">llm</span>spend
          </div>
          <div className="footer-links">
            <a href="https://github.com/snuweb/llmspend" target="_blank" rel="noopener">GitHub</a>
            <a href="https://pypi.org/project/llmspend/" target="_blank" rel="noopener">PyPI</a>
            <a href="https://github.com/snuweb/llmspend/blob/main/CONTRIBUTING.md" target="_blank" rel="noopener">Contributing</a>
            <a href="https://github.com/snuweb/llmspend/issues" target="_blank" rel="noopener">Issues</a>
            <a href="https://github.com/snuweb/llmspend/discussions" target="_blank" rel="noopener">Discussions</a>
          </div>
          <div className="footer-legal">
            <p>MIT License · No data collection · Your infrastructure, your data</p>
            <p>© 2026 LLMSpend</p>
          </div>
        </div>
      </footer>
    </>
  )
}

const codeSnippet = (
  <>
    <span className="c-kw">from</span>{' llmspend '}
    <span className="c-kw">import</span>{' monitor\n'}
    <span className="c-kw">import</span>{' anthropic\n\n'}
    <span className="c-cm">{'# One line to start tracking'}</span>{'\n'}
    {'client = '}
    <span className="c-fn">monitor.wrap</span>
    {'(anthropic.Anthropic(), project='}
    <span className="c-str">"my-app"</span>
    {')\n\n'}
    <span className="c-cm">{'# Use it exactly as before'}</span>{'\n'}
    {'response = client.messages.create(\n'}
    {'    model='}
    <span className="c-str">"claude-sonnet-4-6"</span>
    {',\n'}
    {'    max_tokens='}
    <span className="c-num">500</span>
    {',\n'}
    {'    messages=[{'}
    <span className="c-str">"role"</span>
    {': '}
    <span className="c-str">"user"</span>
    {', '}
    <span className="c-str">"content"</span>
    {': '}
    <span className="c-str">"Hello"</span>
    {'}],\n'}
    {'    llmspend={'}
    <span className="c-str">"feature"</span>
    {': '}
    <span className="c-str">"chatbot"</span>
    {', '}
    <span className="c-str">"user_id"</span>
    {': '}
    <span className="c-str">"u_123"</span>
    {'},\n'}
    {')\n'}
    <span className="c-cm">{'# Cost, tokens, latency — tracked automatically'}</span>
  </>
)

const cliSnippet = (
  <>
    <span className="c-dim">{'$'}</span>{' llmspend stats --last 7d --by feature\n\n'}
    {'  '}
    <span className="c-hd">LLMSpend — Last 7 days</span>
    {'\n'}
    <span className="c-dim">{'  ────────────────────────────────────────────────'}</span>{'\n'}
    {'  Total: '}
    <span className="c-cost">$12.43</span>
    {' across 2,847 calls\n\n'}
    <span className="c-dim">{'  Feature               Calls       Cost    Avg ms'}</span>{'\n'}
    <span className="c-dim">{'  ──────────────────── ────── ────────── ─────────'}</span>{'\n'}
    {'  chatbot                1,893 '}
    <span className="c-cost">{'  $8.94'}</span>
    {'      430ms\n'}
    {'  summarizer               312 '}
    <span className="c-cost">{'  $2.18'}</span>
    {'    1,240ms\n'}
    {'  classifier               642 '}
    <span className="c-cost">{'  $1.31'}</span>
    {'      180ms\n'}
  </>
)
