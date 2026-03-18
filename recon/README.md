# Recon Agent

Autonomous reconnaissance agent for bug bounty attack surface discovery.

## Purpose

This agent performs external reconnaissance on target organizations, discovering
the same attack surface that bug bounty hunters and security researchers see.
It systematically enumerates subdomains, services, technologies, and potential
security issues.

## What It Does

- **Subdomain enumeration** — Discovers all subdomains via CT logs, DNS, and
  passive sources
- **Service discovery** — Identifies live hosts, web services, and open ports
- **Technology fingerprinting** — Detects web servers, frameworks, CMS, CDN/WAF
- **Information gathering** — Checks security.txt, robots.txt, web archives
- **Attack surface mapping** — Categorizes findings by severity and priority
- **Scope assessment** — Identifies what's in/out of scope for bug bounty

## Usage

```bash
# Run reconnaissance on a domain
squad run --agent recon --prompt "Perform reconnaissance on example.com"

# Recon for an organization
squad run --agent recon --prompt "Perform reconnaissance on Acme Corp (acme.com)"
```

## Requirements

### Required (always available)

- `curl` — HTTP requests
- `jq` — JSON parsing
- `dig` or `host` — DNS queries

### Optional (enhanced capabilities)

- `subfinder` — Passive subdomain enumeration
- `httpx` — HTTP probing with tech detection
- `nmap` — Port scanning (requires authorization)
- `whatweb` — Technology fingerprinting
- `nuclei` — Vulnerability pattern matching

Install optional tools for better coverage:

```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
```

## Output

The agent produces a structured report containing:

1. **Reconnaissance Summary** — Target, timestamps, asset count
2. **Scope Assessment** — In-scope/out-of-scope assets, bug bounty details
3. **Attack Surface** — Subdomains, services, critical findings, endpoints
4. **Infrastructure Map** — Hosting providers, CDN/WAF, IP ranges
5. **Recommendations** — Priority targets, additional recon suggestions
6. **Raw Data** — Full subdomain lists, DNS records

## Ethical Use

This agent is for **authorized security testing only**:

- Only target organizations you have permission to test
- Respect bug bounty program scope and rules
- Do not exploit discovered vulnerabilities
- Report findings through proper channels
- Follow responsible disclosure practices

## Files

- `system.md` — Core identity, rules, and workflow
- `agent.md` — Execution rules and tool commands
- `task.md` — Default task instructions
- `references/recon-guide.md` — Comprehensive reconnaissance methodology
