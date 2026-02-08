Perform reconnaissance on the target organization.

Your goal is to discover the external attack surface — everything a bug bounty
hunter would see when scoping out this target.

## Required Steps

1. **Parse the target** — Extract root domain(s) and organization name
2. **Check security.txt and robots.txt** — Document bug bounty program if found
3. **Certificate transparency** — Query crt.sh for all issued certificates
4. **DNS enumeration** — Query A, AAAA, MX, TXT, NS, CNAME records
5. **Subdomain discovery** — Aggregate from CT logs, DNS, and tools (if available)
6. **Validate subdomains** — DNS resolve to filter live hosts
7. **HTTP probing** — Check for web services on discovered hosts
8. **Identify technologies** — Fingerprint web servers, frameworks, CMS
9. **Look for interesting endpoints** — Admin panels, APIs, dev environments
10. **Produce structured report** — Use the output format from system.md

## Constraints

- **Passive first**: Complete ALL passive recon before any active probing
- **Rate limit**: Wait between requests to avoid triggering defenses
- **Stay in scope**: Only enumerate assets belonging to the target
- **No exploitation**: Identify issues but do NOT exploit them
- **Document sources**: Every finding needs to show how it was discovered

## Tool Priority

Use these in order of preference based on availability:

1. **curl + jq** — Always available, use for crt.sh, web archives, API calls
2. **dig/host** — Always available, use for DNS queries
3. **subfinder** — If installed, best passive subdomain enumeration
4. **httpx** — If installed, best HTTP probing with tech detection
5. **nmap** — If installed and authorized, use for port scanning

If a preferred tool is missing, fall back to alternatives and note the limitation.

## Output

Produce a comprehensive attack surface report following the OUTPUT FORMAT in
system.md. Include:

- All discovered subdomains with resolution status
- Exposed services and versions
- Critical and high-severity findings
- Interesting endpoints and information disclosure
- Infrastructure details (hosting, CDN, WAF)
- Recommendations for further testing
- Raw data in collapsible sections
