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

      {/* ── Footer ───────────────────────────────── */}
      <footer className="footer">
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
