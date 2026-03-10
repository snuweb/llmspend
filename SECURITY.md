# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in LLMSpend, please report it responsibly:

**Email:** saadaq@swarmintellect.com

Do not open a public GitHub issue for security vulnerabilities. I will acknowledge receipt within 48 hours and aim to release a fix within 7 days for critical issues.

## What LLMSpend Tracks

Per API call:
- Provider, model name, timestamp
- Input/output token counts
- Calculated cost in USD
- Latency in milliseconds
- Your custom tags (feature, user_id)
- Error type (sanitized — API keys are redacted)

## What LLMSpend Never Tracks

- Prompt content
- Response content
- API keys or authentication tokens
- Request/response headers
- IP addresses

## Data Storage

- **Local mode (default):** All data stays in `~/.llmspend/events.db` (SQLite). The directory is created with `0700` permissions (owner-only access).
- **Hosted mode (future):** Events are sent over HTTPS to the configured backend URL. The SDK warns if a non-HTTPS URL is configured.

## Design Principles

1. **Never crash the host application.** All tracking code runs inside try/except blocks.
2. **Never store sensitive content.** Only metadata (token counts, costs, timing) is recorded.
3. **Zero dependencies.** No third-party runtime packages that could introduce supply chain risk.
4. **Local-first.** Works completely offline. No account or network access required.
5. **Error sanitization.** API keys and tokens are redacted from error messages before storage.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |
