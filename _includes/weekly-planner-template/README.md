# weekly-planner template

A starter `weekly-planner` agent for users with a shared Google Calendar and
a Google Doc family planner. Copy this directory into a new agent dir, fill
in the four required vars, and wire up your Google MCP servers.

## What it does

Each run:

1. Reads a rolling Google Doc planner (one section per week).
2. Picks the most recent week.
3. Sanity-checks that the week's column dates match the upcoming Mon-Sat.
4. Parses Commitments and Dinner rows into Calendar events.
5. Creates the events on the configured calendar with the configured
   attendees, skipping any duplicates.

It does **not** do the GROCERIES table writeback that the personal
weekly-planner agent does — that's a more opinionated feature tied to
recipe-URL extraction. If you want it, layer the
[`extract-recipe-grocery-list`](https://github.com/cowdogmoo/squad-skills/tree/main/extract-recipe-grocery-list)
skill on top once this basic version is working.

## Prerequisites

- A Google Doc planner with the schema documented in the
  [`bootstrap-weekly-planner-doc`](https://github.com/cowdogmoo/squad-skills/tree/main/bootstrap-weekly-planner-doc)
  skill (run that skill's `scripts/setup.py` to create one).
- A Google Calendar you have write access to.
- A Google Drive + Calendar MCP server. The Google-hosted MCP endpoints
  (`calendarmcp.googleapis.com`, `drivemcp.googleapis.com`) are
  allowlisted to Anthropic's product and reject third-party OAuth flows,
  so most users run a small local stdio MCP server that wraps the Google
  v3 REST APIs.

## Setup

```bash
# 1. Copy the template into a new agent dir.
cp -r _includes/weekly-planner-template my-weekly-planner

# 2. Edit agent.yaml — wire up the gdrive + gcal MCP servers at the
#    bottom of the file (replace the commented-out example block with
#    your actual command + env).
$EDITOR my-weekly-planner/agent.yaml

# 3. Run it, passing the four required vars.
squad run --agent my-weekly-planner \
    --var PlannerDocId=<file_id> \
    --var CalendarId=<calendar_id> \
    --var AttendeeEmails=person1@example.com,person2@example.com \
    --var Timezone=America/Denver
```

## Required vars

| Var | Type | Example | Notes |
|---|---|---|---|
| `PlannerDocId` | string | `1wOTsLdEym...` | Google Doc file_id, from the bootstrap skill or your Drive URL bar. |
| `CalendarId` | string | `family12345@group.calendar.google.com` | Calendar where events get created. The agent does NOT use "primary"; pick a calendar explicitly. |
| `AttendeeEmails` | string (comma-separated) | `a@x.com,b@x.com` | Every event created will include each of these as attendees. |
| `Timezone` | string (IANA) | `America/Denver` | Timezone for created events. Date math uses this implicitly via Google Calendar. |

## Customization

The prompt in `agent.yaml` is the customization surface. Common edits:

- **Change the heading regex.** If your doc uses something other than
  `WEEKLY FAMILY PLANNER · Week of <date>` (e.g. `WEEKLY PLANNER` without
  FAMILY), update Step 1.2 to match.
- **Add/remove planner rows.** The default rows are Commitments,
  Childcare, Dinner, Notes. If you have more (Iris outings, dog walks,
  whatever), add the parsing rules under Step 2.
- **Disable freezer reminders.** Delete the entire
  "Dinner row — recipe links and freezer reminders" subsection if you
  don't do meal prep.
- **Switch from Sun-Sat to Mon-Sun.** Update Step 0 (TARGET_WEEK
  computation) and Step 1.4 (column date check). The bootstrap-skill
  doc is Sun-Sat too — you'd need to regenerate the doc with a
  different starting day too.

## Status: untested as a template

The personal version this is forked from runs weekly. This generic
template has been parameterized but not yet exercised end-to-end as a
copy-and-customize starting point. If you hit issues, file them at
https://github.com/cowdogmoo/squad-agents/issues.

## Related

- [`bootstrap-weekly-planner-doc`](https://github.com/cowdogmoo/squad-skills/tree/main/bootstrap-weekly-planner-doc) skill — creates the Google Doc this agent reads from.
- [`extract-recipe-grocery-list`](https://github.com/cowdogmoo/squad-skills/tree/main/extract-recipe-grocery-list) skill — parses recipe URLs into a deduplicated grocery list (the next layer if you want GROCERIES table writeback).
