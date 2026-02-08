# Bug Bounty Reconnaissance Guide

Comprehensive methodology for external attack surface discovery.

## Overview

Reconnaissance is the foundation of effective bug bounty hunting. This guide
covers techniques to discover an organization's external assets — subdomains,
services, technologies, and potential vulnerabilities — without exploitation.

**Core principle**: The more complete your recon, the higher your chances of
finding vulnerabilities others have missed.

## Reconnaissance Phases

### Phase 1: Passive Reconnaissance

Techniques that require NO direct contact with target infrastructure.

#### Certificate Transparency (CT) Logs

CT logs contain all SSL certificates issued for a domain. This reveals
subdomains the organization has deployed, including internal and forgotten ones.

```bash
# crt.sh query (most comprehensive)
curl -s "https://crt.sh/?q=%25.example.com&output=json" | \
  jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u

# Alternative: certspotter
curl -s "https://api.certspotter.com/v1/issuances?domain=example.com&include_subdomains=true" | \
  jq -r '.[].dns_names[]' | sort -u
```

**What to look for**:
- Wildcard certificates (`*.example.com`)
- Internal-sounding names (`internal.`, `vpn.`, `dev.`, `staging.`)
- Old certificates (may reveal deprecated but still-live services)
- Multiple certificate issuers (different teams/environments)

#### DNS Records

```bash
# Get all record types
dig example.com ANY +noall +answer

# Specific record types
dig example.com A +short          # IPv4 addresses
dig example.com AAAA +short       # IPv6 addresses
dig example.com MX +short         # Mail servers
dig example.com NS +short         # Name servers
dig example.com TXT +short        # SPF, DKIM, verification records
dig example.com SOA +short        # Start of authority
dig example.com CNAME +short      # Canonical names

# Reverse DNS
dig -x 1.2.3.4 +short

# Zone transfer attempt (rarely works but worth trying)
dig axfr example.com @ns1.example.com
```

**What to look for in TXT records**:
- SPF records reveal allowed mail senders
- DKIM selectors
- Domain verification for cloud services (Google, Microsoft, etc.)
- API keys or tokens (rare but happens)

#### Web Archives

```bash
# Wayback Machine CDX API
curl -s "https://web.archive.org/cdx/search/cdx?url=*.example.com/*&output=json&collapse=urlkey&fl=original" | \
  jq -r '.[]' | grep -v "^\[" | sort -u

# Alternative: common crawl (larger dataset)
# Use commoncrawl.org index API
```

**What to look for**:
- Old API endpoints
- Deprecated admin panels
- Previous site versions with vulnerabilities
- JavaScript files with hardcoded secrets

#### GitHub/GitLab Search

```bash
# Search for domain mentions (requires gh CLI auth)
gh search code "example.com" --limit 100

# Search for potential secrets
gh search code "example.com api_key" --limit 50
gh search code "example.com password" --limit 50
gh search code "example.com secret" --limit 50
```

**What to look for**:
- Configuration files with credentials
- Internal documentation mentioning infrastructure
- API documentation with endpoint details
- Old commits with removed but exposed secrets

#### Cloud Storage Enumeration

```bash
# S3 bucket patterns
aws s3 ls s3://example --no-sign-request
aws s3 ls s3://example-backup --no-sign-request
aws s3 ls s3://example-dev --no-sign-request
aws s3 ls s3://example-prod --no-sign-request
aws s3 ls s3://example-assets --no-sign-request
aws s3 ls s3://example-uploads --no-sign-request

# Common patterns to try
# {company}
# {company}-{env}  (dev, staging, prod, test)
# {company}-{asset} (assets, uploads, backup, logs, data)
# {product}-{company}
```

#### security.txt and robots.txt

```bash
# security.txt (standard locations)
curl -s https://example.com/.well-known/security.txt
curl -s https://example.com/security.txt

# robots.txt
curl -s https://example.com/robots.txt
```

**security.txt reveals**:
- Bug bounty program details
- Contact information
- Scope boundaries
- PGP keys for secure communication

**robots.txt reveals**:
- Hidden directories
- Admin panels
- API paths
- Content management paths

### Phase 2: Subdomain Enumeration

#### Subdomain Discovery Tools

```bash
# subfinder (passive, uses multiple sources)
subfinder -d example.com -all -silent -o subdomains.txt

# amass (passive mode)
amass enum -passive -d example.com -o amass-subdomains.txt

# assetfinder
assetfinder --subs-only example.com > assetfinder-subdomains.txt

# Combine and deduplicate
cat subdomains.txt amass-subdomains.txt assetfinder-subdomains.txt | \
  sort -u > all-subdomains.txt
```

#### DNS Resolution

```bash
# Resolve all discovered subdomains
cat all-subdomains.txt | while read sub; do
  ip=$(dig +short "$sub" A | head -1)
  if [ -n "$ip" ]; then
    echo "$sub,$ip"
  fi
done > resolved-subdomains.csv

# Using massdns for speed (if available)
massdns -r resolvers.txt -t A -o S all-subdomains.txt > massdns-output.txt

# Using dnsx (if available)
cat all-subdomains.txt | dnsx -silent -a -resp-only
```

#### Wildcard Detection

Some domains return valid responses for ANY subdomain query. Filter these:

```bash
# Test for wildcard
random=$(head /dev/urandom | tr -dc a-z | head -c 32)
dig +short "${random}.example.com" A

# If it resolves, the domain has wildcard DNS
# Filter out IPs that match the wildcard response
```

### Phase 3: Service Discovery

#### HTTP/HTTPS Probing

```bash
# httpx for web service detection
cat resolved-subdomains.csv | cut -d',' -f1 | \
  httpx -silent -status-code -title -tech-detect -o http-probe.txt

# curl-based probe (fallback)
while read domain; do
  status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "https://$domain")
  if [ "$status" != "000" ]; then
    echo "$domain,$status"
  fi
done < subdomains.txt
```

#### Technology Fingerprinting

```bash
# whatweb (if available)
whatweb -a 3 https://example.com

# httpx with tech detection
echo "example.com" | httpx -tech-detect -silent

# nuclei for technology detection
nuclei -l subdomains.txt -t technologies/
```

**Technologies to identify**:
- Web servers (nginx, Apache, IIS, cloudflare)
- Frameworks (React, Angular, Vue, Django, Rails, Laravel)
- CMS (WordPress, Drupal, Joomla, Shopify)
- CDN/WAF (Cloudflare, Akamai, AWS CloudFront, Fastly)
- Cloud providers (AWS, GCP, Azure, DigitalOcean)

#### Port Scanning

```bash
# nmap top ports (conservative)
nmap -sT -T3 --top-ports 100 -oN nmap-output.txt target.example.com

# nmap service detection
nmap -sV -sC --top-ports 1000 target.example.com

# masscan for speed (requires root, use carefully)
masscan -p1-65535 --rate 1000 -oG masscan-output.txt target-ip
```

**High-value ports**:
- 21 (FTP)
- 22 (SSH)
- 23 (Telnet)
- 25, 465, 587 (SMTP)
- 80, 443, 8080, 8443 (HTTP/S)
- 3306 (MySQL)
- 5432 (PostgreSQL)
- 6379 (Redis)
- 27017 (MongoDB)
- 9200 (Elasticsearch)

### Phase 4: JavaScript Analysis

JavaScript files are high-value reconnaissance targets. They often contain
hardcoded secrets, API endpoints, internal paths, and reveal application
architecture.

#### Discovering JavaScript Files

```bash
# From live site - extract all script sources
curl -s https://example.com | grep -oP 'src="[^"]+\.js[^"]*"' | \
  sed 's/src="//;s/"$//' | sort -u

# Using httpx to crawl and extract JS
echo "example.com" | httpx -silent -mc 200 | \
  hakrawler -js -plain -depth 2 2>/dev/null | \
  grep '\.js' | sort -u

# From Wayback Machine - historical JS files
curl -s "https://web.archive.org/cdx/search/cdx?url=example.com/*.js&output=json&collapse=urlkey" | \
  jq -r '.[1:][] | .[2]' | sort -u

# Using gau (Get All URLs) for comprehensive JS discovery
gau example.com --subs | grep '\.js$' | sort -u > js-files.txt

# Using waybackurls
waybackurls example.com | grep '\.js$' | sort -u >> js-files.txt
```

#### Fetching JavaScript Content

```bash
# Download all discovered JS files
mkdir -p js-files
while read url; do
  filename=$(echo "$url" | md5sum | cut -d' ' -f1).js
  curl -s "$url" -o "js-files/$filename"
  echo "$url -> $filename" >> js-files/manifest.txt
done < js-files.txt

# Fetch with proper headers (some sites block curl default UA)
curl -s -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  https://example.com/static/app.js -o app.js
```

#### Extracting API Endpoints

```bash
# grep for common API patterns
grep -orhE '["'"'"'](/api/[^"'"'"']+|/v[0-9]+/[^"'"'"']+)["'"'"']' js-files/ | \
  tr -d "\"'" | sort -u

# Extract full URLs
grep -orhE 'https?://[a-zA-Z0-9./?=_-]+' js-files/ | sort -u

# Find fetch/axios calls
grep -rh 'fetch\s*(' js-files/ | grep -oE '"[^"]+"' | tr -d '"' | sort -u
grep -rh 'axios\.' js-files/ | grep -oE '"[^"]+"' | tr -d '"' | sort -u

# Extract GraphQL endpoints and queries
grep -rhoE 'query\s+\w+|mutation\s+\w+|/graphql' js-files/ | sort -u
```

#### Extracting Secrets and Credentials

```bash
# API keys (common patterns)
grep -rhoE '[aA][pP][iI][-_]?[kK][eE][yY]["'"'"']?\s*[:=]\s*["'"'"'][a-zA-Z0-9_-]{16,}' js-files/

# AWS keys
grep -rhoE 'AKIA[0-9A-Z]{16}' js-files/

# Google API keys
grep -rhoE 'AIza[0-9A-Za-z_-]{35}' js-files/

# GitHub tokens
grep -rhoE 'gh[pousr]_[A-Za-z0-9_]{36,}' js-files/

# JWT tokens
grep -rhoE 'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*' js-files/

# Generic secrets
grep -rhioE '(secret|token|password|apikey|api_key|auth)["'"'"']?\s*[:=]\s*["'"'"'][^"'"'"']{8,}' js-files/

# Firebase configs
grep -rhoE 'firebaseConfig\s*=\s*\{[^}]+\}' js-files/

# Using trufflehog for comprehensive secret scanning
trufflehog filesystem js-files/ --only-verified
```

#### Extracting Internal Paths and Structure

```bash
# Internal paths (absolute)
grep -rhoE '"(/[a-zA-Z0-9_/-]+)"' js-files/ | tr -d '"' | sort -u

# Admin/internal endpoints
grep -rhiE '(admin|internal|debug|dev|staging|test)' js-files/ | \
  grep -oE '"[^"]*"' | tr -d '"' | sort -u

# Environment variables referenced
grep -rhoE 'process\.env\.[A-Z_]+|import\.meta\.env\.[A-Z_]+' js-files/ | sort -u

# Configuration objects
grep -rhE 'config\s*[:=]\s*\{' js-files/ -A 10
```

#### Source Map Analysis

Source maps (`.map` files) can reveal original, unminified source code.

```bash
# Find source map references in JS files
grep -rhoE '//# sourceMappingURL=\S+' js-files/

# Common source map patterns
for js_url in $(cat js-files.txt); do
  map_url="${js_url}.map"
  if curl -s --head "$map_url" | grep -q "200 OK"; then
    echo "Found: $map_url"
    curl -s "$map_url" -o "js-files/$(basename "$map_url")"
  fi
done

# Extract original source from source map
# Source maps contain "sources" array with original file paths
# and "sourcesContent" array with actual source code
jq -r '.sources[]' app.js.map
jq -r '.sourcesContent[]' app.js.map > original-source.js
```

#### Webpack/Build Artifact Analysis

Modern JS apps use bundlers that leave traces:

```bash
# Webpack chunk names reveal route structure
grep -rhoE 'webpackChunk[a-zA-Z_]+' js-files/

# Webpack public path (internal CDN/paths)
grep -rhoE '__webpack_public_path__\s*=\s*"[^"]*"' js-files/

# Dynamic imports reveal lazy-loaded routes
grep -rhoE 'import\s*\(\s*["'"'"'][^"'"'"']+["'"'"']\s*\)' js-files/

# React/Vue route definitions
grep -rhE 'path:\s*["'"'"'][^"'"'"']+["'"'"']' js-files/ | \
  grep -oE '"[^"]+"|'"'"'[^'"'"']+'"'" | tr -d "\"'" | sort -u
```

#### Automated JS Analysis Tools

```bash
# LinkFinder - extract endpoints from JS
python3 linkfinder.py -i https://example.com/app.js -o cli

# SecretFinder - find secrets in JS
python3 SecretFinder.py -i https://example.com/app.js -o cli

# JSParser
python3 JSParser.py -u https://example.com/app.js

# Retire.js - find vulnerable JS libraries
retire --jspath js-files/

# Using nuclei for JS-specific checks
nuclei -l js-files.txt -t exposures/tokens/
```

#### What to Look For in JS Files

| Category | Patterns | Severity |
|----------|----------|----------|
| API Keys | `api_key=`, `apiKey:`, `x-api-key` | CRITICAL |
| Auth tokens | JWT, bearer tokens, session IDs | CRITICAL |
| Internal URLs | `internal.`, `.local`, private IPs | HIGH |
| Debug flags | `debug: true`, `devMode`, `NODE_ENV` | HIGH |
| API endpoints | `/api/`, `/v1/`, hidden routes | MEDIUM |
| Cloud configs | AWS, Firebase, Azure configs | HIGH |
| Admin paths | `/admin`, `/dashboard`, `/manage` | MEDIUM |
| Error handlers | Stack traces, verbose errors | LOW |
| Comments | `TODO`, `FIXME`, `HACK`, dev notes | LOW |

#### Tool Installation

```bash
# Go tools
go install -v github.com/hakluke/hakrawler@latest
go install -v github.com/lc/gau/v2/cmd/gau@latest
go install -v github.com/tomnomnom/waybackurls@latest

# Python tools
pip install trufflehog
git clone https://github.com/GerbenJavado/LinkFinder.git
git clone https://github.com/m4ll0k/SecretFinder.git

# Node tools
npm install -g retire
```

### Phase 5: Analysis

#### Identifying High-Value Targets

**Development/Staging environments**:
- `dev.`, `staging.`, `test.`, `uat.`, `qa.`
- Often have weaker security controls
- May have debug modes enabled
- Could have default credentials

**Admin panels**:
- `/admin`, `/administrator`, `/wp-admin`
- `/dashboard`, `/portal`, `/management`
- `/console`, `/cpanel`, `/phpmyadmin`

**API endpoints**:
- `/api/`, `/v1/`, `/v2/`, `/graphql`
- API documentation (`/swagger`, `/docs`, `/api-docs`)
- May have authentication bypasses

**Forgotten assets**:
- Old marketing sites
- Acquired company domains
- Decommissioned services still running
- Beta/preview versions

#### Information Disclosure Patterns

**Common leaks to look for**:
- `.git` directory exposed
- `.env` files
- `config.php.bak`, `database.yml.example`
- Stack traces with file paths
- Error messages with internal IPs
- Comments in HTML/JS with internal URLs
- Source maps (`.map` files)

## Severity Guidelines

| Severity | Criteria | Examples |
|----------|----------|----------|
| CRITICAL | Direct path to compromise | Exposed credentials, admin access, RCE |
| HIGH | Significant security impact | Auth bypass, sensitive data exposure |
| MEDIUM | Information useful for attacks | Internal IPs, tech stack details, dev env |
| LOW | Minor security implications | Verbose errors, suboptimal headers |
| INFO | No direct security impact | General observations, scope notes |

## Scope Boundaries

**Typically IN scope**:
- Main domain and all subdomains (unless excluded)
- Company-owned IP ranges
- Mobile apps (if listed)
- APIs documented by the company

**Typically OUT of scope**:
- Third-party services (SaaS tools, CDNs)
- Shared hosting platforms
- Customer/user data
- Social engineering, phishing
- Physical security
- DoS/DDoS testing

**Always check**:
- `security.txt` for official scope
- Bug bounty platform program details
- Terms of service

## Tool Installation

```bash
# Go-based tools
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/tomnomnom/assetfinder@latest

# Amass
go install -v github.com/owasp-amass/amass/v4/...@master

# Package managers
brew install nmap whatweb jq dig     # macOS
apt install nmap whatweb jq dnsutils # Debian/Ubuntu
```

## Common Anti-Patterns

1. **Skipping passive recon** — Always gather everything you can passively first
2. **Ignoring old/archived data** — Historical data reveals forgotten assets
3. **Not validating findings** — Cross-reference before including in report
4. **Rate limiting yourself into blocks** — Go slow, especially on active probes
5. **Missing scope boundaries** — Always verify what's in/out of scope
6. **Ignoring error messages** — Stack traces contain valuable information
7. **Only checking port 80/443** — Other ports often have less protection

## References

- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Bug Bounty Hunter Methodology](https://github.com/jhaddix/tbhm)
- [HackerOne Hacker101](https://www.hacker101.com/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [Nahamsec's Resources](https://github.com/nahamsec/Resources-for-Beginner-Bug-Bounty-Hunters)
