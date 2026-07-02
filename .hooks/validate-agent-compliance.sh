#!/bin/bash
set -eo pipefail

# Validate agent compliance with the architecture guide.
# Checks line counts, required sections, manifest integrity,
# and template include usage for any agent directory containing
# staged changes.

RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m'

errors=0
warnings=0

error() {
	echo -e "${RED}  FAIL${NC} $1"
	errors=$((errors + 1))
}
warn() {
	echo -e "${YELLOW}  WARN${NC} $1"
	warnings=$((warnings + 1))
}
pass() { echo -e "${GREEN}  OK${NC}   $1"; }

# ---------------------------------------------------------------------------
# Collect unique agent directories from the files pre-commit passes in.
# Walk upward from each file to find the nearest agent.yaml.
# ---------------------------------------------------------------------------
find_agent_dir() {
	local path="$1"
	local dir
	dir=$(dirname "$path")
	while [ "$dir" != "." ] && [ "$dir" != "/" ]; do
		if [ -f "$dir/agent.yaml" ]; then
			echo "$dir"
			return
		fi
		dir=$(dirname "$dir")
	done
}

raw_dirs=""
for file in "$@"; do
	case "$file" in _templates/*) continue ;; esac
	adir=$(find_agent_dir "$file")
	if [ -n "$adir" ]; then
		raw_dirs="${raw_dirs}${adir}"$'\n'
	fi
done

AGENT_DIRS=()
while IFS= read -r d; do
	[ -n "$d" ] && AGENT_DIRS+=("$d")
done < <(echo "$raw_dirs" | sort -u)

if [ ${#AGENT_DIRS[@]} -eq 0 ]; then
	exit 0
fi

# ---------------------------------------------------------------------------
# Limits from docs/agent-architecture-guide.md
# ---------------------------------------------------------------------------
SYSTEM_MAX=300
AGENT_MAX=50
TASK_MAX=30

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
check_line_count() {
	local file="$1" max="$2" label="$3"
	if [ ! -f "$file" ]; then return; fi
	local count
	count=$(wc -l <"$file" | tr -d ' ')
	if [ "$count" -gt "$max" ]; then
		error "$label: ${count} lines (limit ${max})"
	else
		pass "$label: ${count} lines"
	fi
}

check_section() {
	local file="$1" pattern="$2" label="$3"
	if [ ! -f "$file" ]; then return; fi
	if grep -qiE "$pattern" "$file"; then
		pass "$label: present"
	else
		error "$label: missing"
	fi
}

# ---------------------------------------------------------------------------
# Per-agent checks
# ---------------------------------------------------------------------------
for dir in "${AGENT_DIRS[@]}"; do
	agent_name=$(basename "$dir")
	echo ""
	echo "=== ${agent_name} ==="

	yaml="${dir}/agent.yaml"
	if [ ! -f "$yaml" ]; then
		error "agent.yaml not found"
		continue
	fi

	# ---- Detect agent type ------------------------------------------------
	is_composed=false
	is_pipeline=false
	if grep -q '^stages:' "$yaml"; then
		is_composed=true
		# Pipeline = composed agent whose stages reference external agents
		if grep -qE '^\s+agent:' "$yaml" && ! grep -qE '^\s+entrypoint:' "$yaml"; then
			is_pipeline=true
		fi
	fi

	# ---- agent.yaml metadata ----------------------------------------------
	yaml_name=$(grep '^name:' "$yaml" | head -1 | sed 's/^name:[[:space:]]*//')
	yaml_version=$(grep '^version:' "$yaml" | head -1 | sed 's/^version:[[:space:]]*//')
	yaml_desc=$(grep '^description:' "$yaml" | head -1 | sed 's/^description:[[:space:]]*//')

	# Name matches directory
	if [ "$yaml_name" = "$agent_name" ]; then
		pass "name matches directory"
	else
		error "name '${yaml_name}' does not match directory '${agent_name}'"
	fi

	# Semver version
	if echo "$yaml_version" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
		pass "version: ${yaml_version}"
	else
		error "version '${yaml_version}' is not semver (X.Y.Z)"
	fi

	# Description present
	if [ -n "$yaml_desc" ]; then
		pass "description present"
	else
		error "description missing"
	fi

	# ---- Pipeline agents: no prompt files needed --------------------------
	if $is_pipeline; then
		# Validate stage agent references exist as siblings
		stage_agents=$(grep -E '^\s+agent:' "$yaml" | sed 's/.*agent:[[:space:]]*//')
		for sub in $stage_agents; do
			sibling="${dir}/../${sub}"
			if [ -d "$sibling" ] && [ -f "${sibling}/agent.yaml" ]; then
				pass "stage agent '${sub}' exists"
			else
				error "stage agent '${sub}' not found"
			fi
		done
		continue
	fi

	# ---- Leaf agent required fields ---------------------------------------
	if ! $is_composed; then
		for field in entrypoint wrapper task; do
			val=$(grep "^${field}:" "$yaml" | head -1 | sed "s/^${field}:[[:space:]]*//")
			if [ -n "$val" ]; then
				if [ -f "${dir}/${val}" ]; then
					pass "${field}: ${val}"
				else
					error "${field} file '${val}' not found"
				fi
			else
				error "${field} field missing from agent.yaml"
			fi
		done
	fi

	# ---- Collect prompt files to check ------------------------------------
	system_files=()
	agent_files=()
	task_files=()

	if $is_composed && ! $is_pipeline; then
		# Composed agent with inline stages: check stage files
		# Extract entrypoint/wrapper/task from each stage block
		while IFS= read -r ep; do
			ep="${ep##*entrypoint:}"
			ep="${ep#"${ep%%[![:space:]]*}"}"
			[ -n "$ep" ] && system_files+=("${dir}/${ep}")
		done < <(grep -E '^\s+entrypoint:' "$yaml")

		while IFS= read -r wp; do
			wp="${wp##*wrapper:}"
			wp="${wp#"${wp%%[![:space:]]*}"}"
			[ -n "$wp" ] && agent_files+=("${dir}/${wp}")
		done < <(grep -E '^\s+wrapper:' "$yaml")

		while IFS= read -r tk; do
			tk="${tk##*task:}"
			tk="${tk#"${tk%%[![:space:]]*}"}"
			[ -n "$tk" ] && task_files+=("${dir}/${tk}")
		done < <(grep -E '^\s+task:' "$yaml")
	else
		# Leaf agent
		system_files=("${dir}/system.md")
		agent_files=("${dir}/agent.md")
		task_files=("${dir}/task.md")
	fi

	# ---- Line count checks ------------------------------------------------
	for f in "${system_files[@]}"; do
		check_line_count "$f" "$SYSTEM_MAX" "$(basename "$f") line count"
	done
	for f in "${agent_files[@]}"; do
		check_line_count "$f" "$AGENT_MAX" "$(basename "$f") line count"
	done
	for f in "${task_files[@]}"; do
		check_line_count "$f" "$TASK_MAX" "$(basename "$f") line count"
	done

	# ---- Required sections in system.md -----------------------------------
	for f in "${system_files[@]}"; do
		[ ! -f "$f" ] && continue
		label="$(basename "$f")"
		check_section "$f" '^#.*(IDENTITY|IDENTITY and PURPOSE)' \
			"${label} section: IDENTITY"
		check_section "$f" '^#.*HARD RULES' \
			"${label} section: HARD RULES"
		check_section "$f" '^#.*WORKFLOW' \
			"${label} section: WORKFLOW"
		check_section "$f" '^#.*INPUT' \
			"${label} section: INPUT"

		# Output format: either inline section or include directive
		if grep -qE '(^#.*OUTPUT FORMAT|include.*output/.*format)' "$f"; then
			pass "${label} section: OUTPUT FORMAT"
		else
			error "${label} section: OUTPUT FORMAT missing"
		fi

		# Numbered hard rules
		if grep -qE '^\s*[0-9]+\.\s+\*\*' "$f"; then
			pass "${label}: hard rules are numbered"
		else
			warn "${label}: hard rules should be numbered (N. **Rule**)"
		fi
	done

	# ---- Required sections in agent.md ------------------------------------
	for f in "${agent_files[@]}"; do
		[ ! -f "$f" ] && continue
		label="$(basename "$f")"
		check_section "$f" '^#.*EXECUTION RULES' \
			"${label} section: EXECUTION RULES"
		check_section "$f" '^#.*OUTPUT COMPLIANCE' \
			"${label} section: OUTPUT COMPLIANCE"
	done

	# ---- Severity section check (warn only) --------------------------------
	# Inline severity definitions are the intended Claude-native form; the
	# legacy severity include is also accepted for un-migrated agents.
	for f in "${system_files[@]}"; do
		[ ! -f "$f" ] && continue
		label="$(basename "$f")"
		# Skip agents that don't use severity (e.g., scrub-comments)
		if grep -qiE 'severity|CRITICAL.*HIGH.*MEDIUM' "$f"; then
			if grep -qiE '^#+ *SEVERITY' "$f" || grep -q 'include "severity/standard.md"' "$f"; then
				pass "${label}: severity levels defined"
			else
				warn "${label}: mentions severity but has no SEVERITY LEVELS section"
			fi
		fi
	done

	# ---- Claude-native frontmatter checks -----------------------------------
	# Every prompt entrypoint must open with YAML frontmatter (name,
	# description, tools) so the same file loads as a Claude Code agent and
	# squad skips template rendering. system.md frontmatter name must match
	# the agent directory; stage files (*-system.md) carry their own names.
	for f in "${system_files[@]}"; do
		[ ! -f "$f" ] && continue
		label="$(basename "$f")"
		if [ "$(head -n 1 "$f")" != "---" ]; then
			error "${label}: missing YAML frontmatter (Claude-native format required)"
			continue
		fi
		# Pure-bash key checks: piping $fm into `grep -q` is unsafe under
		# `set -o pipefail` — grep exits on the first match, printf can
		# catch SIGPIPE (141), and the pipeline reports failure for a key
		# that IS present. Timing-dependent, so it flaked only in CI.
		fm=$(awk 'NR==1{next} /^---$/{exit} {print}' "$f")
		fm_name=""
		while IFS= read -r fm_line; do
			case "$fm_line" in
			name:*)
				fm_name="${fm_line#name:}"
				fm_name="${fm_name#"${fm_name%%[![:space:]]*}"}"
				;;
			esac
		done <<<"$fm"
		missing=""
		for key in name description tools; do
			case $'\n'"${fm}"$'\n' in
			*$'\n'"${key}:"*) ;;
			*) missing="${missing} ${key}" ;;
			esac
		done
		if [ -n "$missing" ]; then
			error "${label} frontmatter: missing key(s):${missing}"
		else
			pass "${label} frontmatter: name/description/tools present"
		fi
		if [ "$label" = "system.md" ] && [ -n "$fm_name" ] && [ "$fm_name" != "$agent_name" ]; then
			error "frontmatter name '${fm_name}' does not match directory '${agent_name}'"
		fi
	done

	# ---- Reference file existence -----------------------------------------
	while IFS= read -r line; do
		ref="${line#"${line%%[![:space:]]*}"}"
		ref="${ref#- }"
		[ -z "$ref" ] && continue
		if [ -f "${dir}/${ref}" ]; then
			pass "reference: ${ref}"
		else
			error "reference not found: ${ref}"
		fi
	done < <(grep -E '^\s+-\s+references/' "$yaml" 2>/dev/null || true)
done

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "=============================="
if [ $errors -gt 0 ]; then
	echo -e "${RED}FAILED${NC}: ${errors} error(s), ${warnings} warning(s)"
	exit 1
elif [ $warnings -gt 0 ]; then
	echo -e "${YELLOW}PASSED${NC} with ${warnings} warning(s)"
	exit 0
else
	echo -e "${GREEN}PASSED${NC}: all checks OK"
	exit 0
fi
