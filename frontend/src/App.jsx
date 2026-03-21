export default function App() {
  return (
    <>
      {/* ── Nav ──────────────────────────────────── */}
      <nav className="nav">
        <div className="nav-logo">
          <span className="nav-logo-icon">$</span>
          LLMSpend
        </div>
        <div className="nav-links">
          <a href="https://github.com/snuweb/llmspend" target="_blank" rel="noopener">GitHub</a>
          <a href="https://github.com/snuweb/llmspend#quick-start" target="_blank" rel="noopener">Docs</a>
          <a href="https://github.com/snuweb/llmspend" target="_blank" rel="noopener" className="nav-cta">Get Started</a>
        </div>
      </nav>

      {/* ── Hero ─────────────────────────────────── */}
      <section className="hero section">
        <div className="hero-eyebrow">Open Source</div>
        <h1>Know where your<br />AI money goes</h1>
        <p className="hero-sub">
          Track LLM API costs per feature, per model, per user.
          Two lines of code. Works with Anthropic and OpenAI.
        </p>

        <div className="hero-actions">
          <a href="https://github.com/snuweb/llmspend" target="_blank" rel="noopener">
            <button className="btn-primary">pip install llmspend</button>
          </a>
          <a href="https://github.com/snuweb/llmspend" target="_blank" rel="noopener">
            <button className="btn-secondary">View on GitHub</button>
          </a>
        </div>

        <div className="code-block">
          <pre>{codeExample}</pre>
        </div>
      </section>

      {/* ── Problem ──────────────────────────────── */}
      <section className="problem section">
        <h2>The Problem</h2>
        <p className="problem-headline">
          Your Anthropic dashboard shows $847 this month.<br />
          Which feature caused it?
        </p>
        <p className="problem-sub">
          Provider billing shows totals. It doesn't show which endpoint
          costs $12/day, which user burned through your budget, or why
          Tuesday's bill was 4x normal. You find out when the invoice arrives.
        </p>
      </section>

      {/* ── Features ─────────────────────────────── */}
      <section className="features section">
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">$</div>
            <h3>Cost per feature</h3>
            <p>Tag API calls with feature names. See exactly which part of your app costs what. Stop guessing.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">&gt;</div>
            <h3>Per-model breakdown</h3>
            <p>Sonnet for summarization, Haiku for chat? See the cost split by model. Find where to optimize.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">!</div>
            <h3>Budget alerts</h3>
            <p>Get notified on Telegram, Slack, or email when daily spend exceeds your threshold. No more surprise bills.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">#</div>
            <h3>Per-user tracking</h3>
            <p>One power user sending 200 messages a day? You'll know. Attribute costs to individual users or sessions.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">~</div>
            <h3>Zero overhead</h3>
            <p>Async logging in a background thread. If our service is down, your app is unaffected. No proxy, no latency.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">*</div>
            <h3>Works offline</h3>
            <p>No backend? Logs to local SQLite. View costs with the CLI. Self-hosted dashboard coming soon.</p>
          </div>
        </div>
      </section>

      {/* ── CLI Preview ──────────────────────────── */}
      <section className="cli-section section">
        <h2>Built for Your Terminal</h2>
        <p className="cli-headline">Instant cost visibility. No dashboard needed.</p>

        <div className="cli-block">
          <pre>{cliExample}</pre>
        </div>
      </section>

      {/* ── How it works ─────────────────────────── */}
      <section className="how-section section">
        <h2>How It Works</h2>
        <p className="how-headline">Two lines. No config files. No environment variables.</p>

        <div className="how-steps">
          <div className="how-step">
            <div className="how-step-num">01</div>
            <h3>Wrap your client</h3>
            <p>Call monitor.wrap() on your Anthropic or OpenAI client. It returns the same object with tracking enabled. Your existing code doesn't change.</p>
          </div>
          <div className="how-step">
            <div className="how-step-num">02</div>
            <h3>Tag your calls</h3>
            <p>Add feature and user_id to any API call via the llmspend parameter. Optional — untagged calls are still tracked under your project.</p>
          </div>
          <div className="how-step">
            <div className="how-step-num">03</div>
            <h3>See your costs</h3>
            <p>Run llmspend stats in your terminal. Group by model, feature, or user. See where every dollar goes.</p>
          </div>
        </div>
      </section>

      {/* ── Dashboard Preview ────────────────────── */}
      <section className="dashboard-section section">
        <h2>What You'll See</h2>
        <p className="dashboard-headline">Real-time cost visibility without leaving your terminal — or use the self-hosted dashboard.</p>

        <div className="dashboard-preview">
          <div className="dash-card">
            <div className="dash-card-header">
              <span className="dash-card-title">Today's Spend</span>
              <span className="dash-card-badge">Live</span>
            </div>
            <div className="dash-card-value">$4.23</div>
            <div className="dash-card-sub">↑ 12% vs yesterday</div>
          </div>
          <div className="dash-card">
            <div className="dash-card-header">
              <span className="dash-card-title">API Calls</span>
              <span className="dash-card-badge">24h</span>
            </div>
            <div className="dash-card-value">1,847</div>
            <div className="dash-card-sub">Across 3 features</div>
          </div>
          <div className="dash-card">
            <div className="dash-card-header">
              <span className="dash-card-title">Top Feature</span>
              <span className="dash-card-badge">Cost</span>
            </div>
            <div className="dash-card-value">chatbot</div>
            <div className="dash-card-sub">$2.94 — 68% of spend</div>
          </div>
          <div className="dash-card">
            <div className="dash-card-header">
              <span className="dash-card-title">Avg Latency</span>
              <span className="dash-card-badge">p50</span>
            </div>
            <div className="dash-card-value">430ms</div>
            <div className="dash-card-sub">Haiku: 180ms · Sonnet: 1.2s</div>
          </div>
        </div>

        <div className="dash-table-wrap">
          <table className="dash-table">
            <thead>
              <tr>
                <th>Feature</th>
                <th>Model</th>
                <th>Calls</th>
                <th>Cost</th>
                <th>Avg Latency</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>chatbot</td><td>claude-haiku-4-5</td><td>1,234</td><td className="cost">$2.94</td><td>180ms</td></tr>
              <tr><td>summarizer</td><td>claude-sonnet-4-6</td><td>312</td><td className="cost">$1.87</td><td>1,240ms</td></tr>
              <tr><td>classifier</td><td>gpt-4o-mini</td><td>201</td><td className="cost">$0.42</td><td>95ms</td></tr>
              <tr><td>embeddings</td><td>text-embedding-3</td><td>100</td><td className="cost">$0.03</td><td>45ms</td></tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* ── Comparison ─────────────────────────────── */}
      <section className="compare-section section">
        <h2>Why not just use the provider dashboard?</h2>
        <div className="compare-grid">
          <div className="compare-card compare-them">
            <h3>Provider Dashboard</h3>
            <ul>
              <li>Total spend this month</li>
              <li>Per-model totals</li>
              <li>Invoice at end of month</li>
            </ul>
          </div>
          <div className="compare-card compare-us">
            <h3>LLMSpend</h3>
            <ul>
              <li>Cost per feature, per user, per call</li>
              <li>Real-time alerts before the bill arrives</li>
              <li>Which endpoint is burning your budget</li>
              <li>Cost trends and anomaly detection</li>
              <li>Works offline with local SQLite</li>
              <li>Open source — self-host everything</li>
            </ul>
          </div>
        </div>
      </section>

      {/* ── Open Source CTA ──────────────────────── */}
      <section className="oss-section section">
        <div className="oss-box">
          <h2>Free and open source</h2>
          <p>
            MIT licensed. No account required. No data leaves your machine
            unless you choose the hosted version. Self-host everything.
          </p>
          <div className="oss-actions">
            <a href="https://github.com/snuweb/llmspend" target="_blank" rel="noopener">
              <button className="btn-primary">pip install llmspend</button>
            </a>
            <a href="https://github.com/snuweb/llmspend" target="_blank" rel="noopener">
              <button className="btn-secondary">Star on GitHub</button>
            </a>
          </div>
        </div>
      </section>

      {/* ── Contact ────────────────────────────────── */}
      <section className="contact-section section">
        <h2>Get in Touch</h2>
        <p className="contact-sub">Questions, feedback, or want to contribute? Reach out.</p>
        <div className="contact-grid">
          <a href="https://github.com/snuweb/llmspend/issues" target="_blank" rel="noopener" className="contact-card">
            <div className="contact-icon">!</div>
            <h3>GitHub Issues</h3>
            <p>Bug reports, feature requests, and discussions.</p>
          </a>
          <a href="https://github.com/snuweb/llmspend" target="_blank" rel="noopener" className="contact-card">
            <div className="contact-icon">*</div>
            <h3>Contribute</h3>
            <p>PRs welcome. Check the README for contribution guidelines.</p>
          </a>
          <a href="https://github.com/snuweb/llmspend/discussions" target="_blank" rel="noopener" className="contact-card">
            <div className="contact-icon">@</div>
            <h3>Discussions</h3>
            <p>Questions, ideas, and general chat about LLMSpend.</p>
          </a>
        </div>
      </section>

      {/* ── Footer ───────────────────────────────── */}
      <footer className="footer">
        <div className="footer-links">
          <a href="https://github.com/snuweb/llmspend" target="_blank" rel="noopener">GitHub</a>
          <span>·</span>
          <a href="https://pypi.org/project/llmspend/" target="_blank" rel="noopener">PyPI</a>
          <span>·</span>
          <a href="https://github.com/snuweb/llmspend/issues" target="_blank" rel="noopener">Issues</a>
          <span>·</span>
          <a href="https://github.com/snuweb/llmspend/discussions" target="_blank" rel="noopener">Discuss</a>
        </div>
        <p>
          LLMSpend is open source software by{' '}
          <a href="https://github.com/snuweb" target="_blank" rel="noopener">snuweb</a>.
          {' '}MIT License.
        </p>
      </footer>
    </>
  )
}


// ── Code snippets (kept outside JSX for readability) ──

const codeExample = (
  <>
    <span className="code-comment">{'# pip install llmspend'}</span>{'\n'}
    <span className="code-keyword">import</span>{' anthropic\n'}
    <span className="code-keyword">from</span>{' llmspend '}
    <span className="code-keyword">import</span>{' monitor\n\n'}
    <span className="code-comment">{'# Wrap your client — 1 line'}</span>{'\n'}
    {'client = '}
    <span className="code-func">monitor.wrap</span>
    {'(anthropic.Anthropic(), project='}
    <span className="code-string">"my-app"</span>
    {')\n\n'}
    <span className="code-comment">{'# Use it exactly as before'}</span>{'\n'}
    {'response = client.messages.create(\n'}
    {'    model='}
    <span className="code-string">"claude-haiku-4-5-20251001"</span>
    {',\n'}
    {'    max_tokens='}
    <span className="code-num">500</span>
    {',\n'}
    {'    messages=[{'}
    <span className="code-string">"role"</span>
    {': '}
    <span className="code-string">"user"</span>
    {', '}
    <span className="code-string">"content"</span>
    {': '}
    <span className="code-string">"Hello"</span>
    {'}],\n'}
    {'    llmspend={'}
    <span className="code-string">"feature"</span>
    {': '}
    <span className="code-string">"chatbot"</span>
    {', '}
    <span className="code-string">"user_id"</span>
    {': '}
    <span className="code-string">"u_123"</span>
    {'},\n'}
    {')\n'}
    <span className="code-comment">{'# Cost, tokens, latency — tracked automatically'}</span>
  </>
)

const cliExample = (
  <>
    <span className="cli-prompt">$</span>{' '}
    <span className="cli-cmd">llmspend stats --last 7d --by feature</span>{'\n\n'}
    <span className="cli-header">{'  LLMSpend — Last 7d'}</span>{'\n'}
    <span className="cli-dim">{'  ──────────────────────────────────────────────────'}</span>{'\n'}
    {'  Total: '}<span className="cli-cost">$12.43</span>{' across 2,847 calls\n\n'}
    <span className="cli-dim">{'  Feature                  Calls       Cost   Avg ms'}</span>{'\n'}
    <span className="cli-dim">{'  ───────────────────────── ────── ────────── ────────'}</span>{'\n'}
    {'  chatbot                    1,893 '}<span className="cli-cost">{'  $8.94'}</span>{'     430ms\n'}
    {'  summarizer                   312 '}<span className="cli-cost">{'  $2.18'}</span>{'   1,240ms\n'}
    {'  classifier                   642 '}<span className="cli-cost">{'  $1.31'}</span>{'     180ms\n'}
  </>
)
