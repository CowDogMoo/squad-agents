# TASK

Find this repository's Grafana dashboard JSON and audit each one against
observability best practices.

# SCOPE

- Glob for dashboard JSON, including provisioning directories
- Parse structure: panels, rows, variables, datasources, refresh, time range
- Assess against the methodology that fits the dashboard's purpose (USE, RED,
  or the Four Golden Signals)
- Check units, thresholds, legends, axes, panel fitness, and query cost
- Rate each dashboard's maturity and justify it

# PRIORITIES

1. **Incident usability** - would this mislead someone paged at 3am
2. **Query cost** - unbounded ranges, high-cardinality group-bys, missing
   `$__rate_interval`
3. **Correctness** - hardcoded datasource UIDs, orphaned variables, panels
   that silently return no data
4. **Legibility** - units, thresholds, legend clutter, axis scales

# CONSTRAINTS

- Do NOT modify dashboard JSON unless the caller explicitly asked for fixes
- Do NOT report a finding without a panel id and a concrete fix
- Do NOT penalize a deliberately simple dashboard for missing features its
  purpose does not need
- Do NOT estimate counts - read them from the JSON
