---
name: grafana-dashboard-standards
description: "Standards for designing and auditing Grafana dashboards — the USE, RED and Four Golden Signals methodologies, visual hierarchy and accessibility, panel selection, navigation and sprawl control, query performance, and a dashboard maturity model. Use when building a dashboard, reviewing one, or judging whether a panel earns its place. Also loaded by the grafana-dashboard-audit agent as its knowledge base."
---
# Grafana Dashboard Best Practices

A comprehensive guide to creating effective, maintainable, and scalable Grafana dashboards based on official Grafana documentation and community best practices.

## Table of Contents

1. [Foundational Principles](#foundational-principles)
2. [Observability Methodologies](#observability-methodologies)
3. [Dashboard Design Guidelines](#dashboard-design-guidelines)
4. [Visual Hierarchy and Accessibility](#visual-hierarchy-and-accessibility)
5. [Panel Selection and Visualization Types](#panel-selection-and-visualization-types)
6. [Organization and Navigation](#organization-and-navigation)
7. [Management and Maintenance](#management-and-maintenance)
8. [Performance Optimization](#performance-optimization)
9. [Maturity Model](#maturity-model)

---

## Foundational Principles

### Know Your Purpose

Every dashboard should have a clear purpose. Ask yourself:

- **What story are you trying to tell?** Dashboards should present data in a logical progression (large to small, general to specific)
- **What question does this dashboard answer?** If it doesn't answer a question or tell a story, it shouldn't exist
- **Who is the audience?** Different roles have different needs:
  - Engineers prioritize system performance metrics
  - Product managers focus on user interaction data
  - Business stakeholders need high-level KPIs

### Reduce Cognitive Load

Design dashboards to minimize the mental effort required to interpret them:

- Graphs should be self-explanatory to viewers unfamiliar with the system
- Use clear labels and descriptions
- Avoid information overload - focus on what matters
- Include only the most relevant metrics that help make decisions quickly

### Consistency is Key

Once you establish design guidelines:

- Document them and share with your team
- Use template variables to maintain consistency
- Consider using scripting libraries (grafonnet, grafanalib) for programmatic dashboard generation
- Apply consistent naming conventions across all dashboards

---

## Observability Methodologies

Before creating dashboards, adopt one of these established monitoring strategies:

### USE Method (Infrastructure-Focused)

Best for monitoring infrastructure and resource health:

- **Utilization**: Percentage of time the resource is busy
- **Saturation**: Work queue length or system load
- **Errors**: Count of error events

*"The USE method tells you how happy your machines are"*

### RED Method (Service-Focused)

Best for monitoring services and user-facing applications:

- **Rate**: Requests per second
- **Errors**: Number of failing requests
- **Duration**: Latency measurements and distribution

*"The RED method tells you how happy your users are"*

**RED Method Dashboard Pattern:**

- Request and error rates on the left
- Latency duration on the right
- One row per service
- Row order reflects data flow

### Four Golden Signals

Comprehensive approach for user-facing systems:

- **Latency**: Time taken to service a request
- **Traffic**: Demand on your system (requests per second)
- **Errors**: Rate of failing requests
- **Saturation**: How full your service is (CPU, memory, I/O)

Choose the methodology that best fits your use case, document it, and maintain consistency across your dashboard ecosystem.

---

## Dashboard Design Guidelines

### Naming and Documentation

**Dashboard Names:**

- Use meaningful, descriptive names
- Prefix experimental dashboards with "TEST" or "TMP"
- Include your name or initials for ownership clarity
- Add relevant tags for easy discovery

**Documentation:**

- Add Text panels explaining the dashboard's purpose and usage
- Document individual panels with descriptions (visible on hover)
- Include links to runbooks or related documentation
- Specify the data sources and refresh intervals

### Meaningful Use of Color

- **Apply consistent color conventions**:
  - Blue/Green for good/normal values
  - Yellow/Orange for warnings
  - Red for critical/error states
- **Use thresholds** to automatically color code values
- **Avoid red-green combinations** for colorblind accessibility
- **Use saturated, distinct colors** to draw attention to important metrics

### Graph and Visualization Best Practices

**Axes and Scaling:**

- Normalize axes for fair comparisons (e.g., use percentages instead of raw numbers when comparing resources)
- Use both Y-axes when displaying metrics with different units or scales
- Set appropriate min/max values to avoid misleading visualizations

**Graph Types:**

- **Avoid stacking graphs** - stacked graphs can hide important data
- Use time series for temporal trends and patterns
- Use stat panels for single value snapshots
- Use gauges to show values relative to min/max thresholds

**Data Presentation:**

- Show data at appropriate granularity for the time range
- Use appropriate aggregation functions (avg, max, p95, etc.)
- Include sparklines in stat panels to show trends at a glance

---

## Visual Hierarchy and Accessibility

Guide viewers to important information through strategic design:

### Alignment

Follow natural reading patterns:

- In English-speaking contexts: left-to-right, top-to-bottom
- Place key metrics and KPIs in the upper-left area
- Group related metrics together

### Size

"The bigger the size of the component, the greater the perception of importance"

- Critical metrics should be larger and more prominent
- Supporting details can be smaller
- Use the full width of the dashboard for important visualizations

### Shape and Layout

- Complex shapes help elements stand out
- Use consistent panel sizes for related metrics
- Create visual separation between different sections
- Consider using rows to group related panels

### Accessibility

- Avoid red-green color combinations (colorblind users)
- Provide adequate contrast between text and background
- Use clear, readable fonts
- Include descriptive labels and units

---

## Panel Selection and Visualization Types

Choose the right visualization for your data type:

### Time Series Panels

**Best for:**

- Displaying temporal trends, patterns, and anomalies
- Metrics like latency, request rates, resource utilization
- Large numbers of time-based data points
- Identifying patterns over time

**Features:**

- X-axis shows time progression
- Y-axis shows metric magnitude
- Supports multiple series on one graph
- Ideal for correlation analysis

### Stat Panels

**Best for:**

- Displaying single values of interest (latest/current value)
- Monitoring key metrics at a glance (application health, bug counts, sales totals)
- Displaying aggregated data (average response time)
- Highlighting values outside normal thresholds

**Features:**

- Shows one large stat value
- Optional sparkline graph for trend context
- Background or value color based on thresholds
- Supports multiple values in compact format

### Gauge Panels

**Best for:**

- Presenting values relative to min/max ranges
- Visualizing progress toward a goal
- Comparing multiple values simultaneously
- Resource utilization (CPU, memory, disk)

**Types:**

- Standard radial gauge (single value)
- Horizontal/vertical bar gauge (multiple series)
- Three display modes for different use cases

### Bar Gauge Panels

Useful for:

- Comparing multiple values
- Progress visualization
- Displaying multiple series compactly (unlike standard gauge)

---

## Organization and Navigation

### Template Variables

**Use template variables to:**

- Eliminate dashboard duplication (no need for per-node dashboards)
- Make data sources configurable
- Enable filtering by environment, service, instance, etc.
- Create reusable dashboards across clusters

**Benefits:**

- Prevents dashboard sprawl
- Easier maintenance
- Consistent user experience
- Reduces storage and performance overhead

### Hierarchical Dashboard Structure

Implement drill-down capabilities:

1. **Top-level dashboards**: High-level overview of system health
2. **Service-level dashboards**: Specific service metrics and RED/USE methods
3. **Detailed dashboards**: Deep-dive into specific components or troubleshooting

**Navigation techniques:**

- Dashboard links in panels (drill-through on click)
- Panel links to related dashboards
- Dashboard list visualizations for easy navigation
- Text panels with markdown navigation menus
- URL parameters for customized views without duplication

### Cross-References and Linking

Create connections between related dashboards:

- Link from overview panels to detailed views
- Include "back" navigation to parent dashboards
- Use consistent URL parameters across dashboard hierarchy
- Add breadcrumb-style navigation in text panels

---

## Management and Maintenance

### Prevent Dashboard Sprawl

Dashboard sprawl is a common problem that reduces dashboard effectiveness:

**Prevention strategies:**

- **Regular audits**: Review and remove irrelevant or outdated dashboards
- **Prohibit casual copying**: Link to master dashboards with URL parameters instead
- **Track usage**: Use Grafana Enterprise features to identify unused dashboards
- **Clean up experiments**: Remove TEST/TMP dashboards when finished
- **Enforce naming conventions**: Make it easy to identify ownership and purpose

### Version Control

**Best practices:**

- Store dashboard JSON in version control (Git)
- Don't rely solely on Grafana's built-in versioning
- Use infrastructure-as-code approaches
- Enable code review for dashboard changes
- Tag releases to match application versions

### Dashboard Testing

- **Experiment in separate instances**: Use dev/staging Grafana instances
- **Validate with real data**: Test with production-like data volumes
- **Review with stakeholders**: Get feedback before promoting to production
- **Test across time ranges**: Ensure dashboards work with different time windows
- **Verify performance**: Check query execution times

### Consistency Through Automation

Use scripting libraries for standardized dashboards:

- **Grafonnet**: Jsonnet library for generating Grafana dashboards
- **Grafanalib**: Python library for building Grafana dashboards
- **Terraform/Pulumi**: Infrastructure-as-code for Grafana resources

**Benefits:**

- Ensures consistent patterns and styles
- Easier to maintain and update
- Version controlled dashboard definitions
- Reduces human error
- Enables automated dashboard generation

---

## Performance Optimization

### Refresh Rates

- Set refresh rates matching data change frequency
- Avoid unnecessary refreshing to reduce network and backend load
- Consider different refresh rates for different panels
- Use manual refresh for historical analysis dashboards

### Query Optimization

- Use appropriate time ranges and intervals
- Leverage recording rules for expensive queries
- Cache query results when possible
- Use query variables to reduce duplication
- Avoid overly complex or unoptimized queries

### Dashboard Complexity

- Limit number of panels per dashboard (aim for 20-30 max)
- Split complex dashboards into multiple focused dashboards
- Use shared queries when multiple panels need the same data
- Consider performance impact of transformations

---

## Maturity Model

Organizations typically evolve through these stages:

### Low Maturity: Dashboard Sprawl

- Uncontrolled dashboard creation
- Duplicated dashboards for different environments
- No naming conventions or organization
- Difficult to find relevant dashboards
- High maintenance burden

### Medium Maturity: Methodical Approach

- Adoption of RED/USE/Golden Signals methodology
- Template variables to prevent duplication
- Hierarchical organization with drill-downs
- Documented dashboard purposes
- Regular cleanup and maintenance

### High Maturity: Optimized Ecosystem

- Scripted dashboard generation (infrastructure-as-code)
- Comprehensive version control
- Automated testing and validation
- Deliberate curation and governance
- Strong observability culture
- Consistent patterns across all dashboards
- Observability-as-code practices

### Continuous Improvement

Observability requires ongoing iteration:

- Regularly reassess metrics based on evolving needs
- Optimize layouts based on user feedback
- Update methodologies as systems evolve
- Remove dashboards that no longer serve a purpose
- Stay current with Grafana features and best practices

---

## Quick Reference Checklist

When creating a new dashboard, ask yourself:

- [ ] Does this dashboard have a clear purpose?
- [ ] Have I identified the target audience?
- [ ] Does it follow our chosen methodology (RED/USE/Golden Signals)?
- [ ] Are template variables used to prevent duplication?
- [ ] Is the naming convention followed?
- [ ] Have I added documentation (dashboard and panel descriptions)?
- [ ] Are colors used meaningfully and consistently?
- [ ] Are axes normalized for fair comparisons?
- [ ] Is the visual hierarchy guiding viewers effectively?
- [ ] Are the right visualization types chosen for each metric?
- [ ] Is the refresh rate appropriate?
- [ ] Have I tested the dashboard with real data?
- [ ] Are drill-down links to related dashboards included?
- [ ] Is the dashboard version controlled?
- [ ] Have I verified accessibility (colorblind-friendly)?

---

## Sources

- [Grafana dashboard best practices | Grafana documentation](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/)
- [Getting started with Grafana: best practices to design your first dashboard | Grafana Labs](https://grafana.com/blog/2024/07/03/getting-started-with-grafana-best-practices-to-design-your-first-dashboard/)
- [Best practices for Grafana dashboards | GrafanaCON 2025](https://grafana.com/events/observabilitycon/2025/hands-on-labs/best-practices-to-level-up-your-grafana-dashboarding-skills/)
- [Best practices for dashboards - Amazon Managed Grafana](https://docs.aws.amazon.com/grafana/latest/userguide/v10-dash-bestpractices.html)
- [Dashboarding Best Practices - Grafana Learning Platform](https://learn.grafana.com/dashboarding-best-practices)
- [Grafana Observability Dashboards: Insight & Best Practices](https://www.groundcover.com/learn/observability/grafana-dashboards)
- [Visualizations | Grafana documentation](https://grafana.com/docs/grafana/latest/panels-visualizations/visualizations/)

---

*Last updated: 2026-01-05*
