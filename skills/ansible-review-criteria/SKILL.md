---
name: ansible-review-criteria
description: "Review criteria for Ansible playbooks and roles — the Zen of Ansible, YAML formatting, naming conventions, task structure, variables, conditionals, loops, handlers, error handling, idempotency, and role structure. Use when reviewing or refactoring Ansible code. Also loaded by the ansible-review agent as its knowledge base."
---
# Idiomatic Ansible Review Criteria

Criteria for reviewing Ansible playbooks, roles, and tasks: style, naming,
FQCN, idempotency, security, and the anti-patterns to flag. Collection
structure, `galaxy.yml`, and role `argument_specs` are covered by the
ansible-standards skill. Molecule suites are covered by the
ansible-molecule-guide skill.

## Read-when index

This file is the core. Topic files live in `references/` under this skill's
base directory. Read one only when its condition applies:

- Read `references/variables-precedence.md` when a finding depends on where a
  variable is defined (role defaults vs role vars, group_vars, host_vars,
  extra vars) or on `default`/`mandatory` filters.
- Read `references/control-flow.md` when the code uses compound or
  registered-result `when` conditions, loops beyond a simple list
  (`loop_control`, flattening, dict loops), handlers with `listen` or
  `flush_handlers`, tags, or `include_tasks`/`import_tasks`.
- Read `references/error-handling.md` when the code uses
  `block`/`rescue`/`always`, `failed_when`, or `ignore_errors`.
- Read `references/roles.md` when reviewing role directory layout,
  `meta/main.yml` dependencies and platforms, or Galaxy versioning.
- Read `references/jinja-and-registers.md` when the code reads registered
  return values or ships Jinja2 templates and filters.
- Read `references/inventory-performance.md` when the change touches inventory
  layout, group_vars/host_vars organization, fact gathering or caching, SSH
  pipelining, forks, or play strategy.

## The Zen of Ansible

- **Ansible is not Python.** YAML is a poor fit for programming logic.
- **Playbooks are not for programming.** Most users are not programmers.
- **Clear is better than cluttered.**
- **Concise is better than verbose.**
- **Simple is better than complex.**
- **Readability counts.**
- **Practicality beats purity.**

Sources: [Red Hat Good Practices](https://redhat-cop.github.io/automation-good-practices/),
[Ansible Best Practices Guide](https://timgrt.github.io/Ansible-Best-Practices/)

## YAML formatting

ansible-lint and yamllint enforce most of this; flag it only when it changes
meaning or a linter would fail.

- 2-space indentation, never tabs.
- Booleans are `true`/`false`, not `yes`/`no` or `1`/`0`.
- Ansible YAML files use `.yml`; Jinja2 templates use `.j2`.
- `|` keeps newlines, `>` folds them; `|-` strips and `|+` keeps the trailing
  newline.

## Naming conventions

- **Variables:** snake_case (`http_port`), never camelCase or kebab-case.
- **Roles:** lowercase snake_case, singular (`nginx_server`,
  `database_backup`).
- **Role variables:** prefix public variables with the role name
  (`nginx_port` in `defaults/main.yml`); prefix internal variables with a
  double underscore (`__nginx_config_path`).
- **Tasks:** every task has a `name:`, no exceptions.
  1. Start with an action verb (install, configure, create, remove, ensure).
  2. Sentence case (`name[casing]` in ansible-lint enforces capitalization).
  3. Unique within a play.
  4. No templating in names (`name: "Install {{ package }}"`).
  5. A comment above an unnamed task is not a name.

Sources: [Ansible Lint name rules](https://docs.ansible.com/projects/lint/rules/name/)

## Task structure

Recommended key order: `name`, module (FQCN), module parameters,
`become`/`become_user`, `when`, `register`, `changed_when`/`failed_when`,
`notify`, `tags`, `loop`.

One task per action. A block named "Install and configure nginx" wrapping
twenty unrelated tasks is too broad.

Rules from the reference files that come up in most reviews:

- No `{{ }}` in `when`: `when: enable_tls | bool`, not
  `when: "{{ enable_tls }}"`. Use `| bool` for values that may be strings.
- Prefer `loop` over `with_items`; `loop` does not flatten, so add
  `| flatten(1)` when needed.
- Restarts belong in handlers triggered by `notify`, so they run only when
  something changed. Handlers run once, in definition order.
- `import_tasks` cannot loop; use `include_tasks` for loops and dynamic file
  names.

## Collections and FQCN

Every module with a known collection namespace uses its fully qualified name:
`ansible.builtin.copy`, `ansible.posix.acl`, `community.general.*`,
`amazon.aws.ec2_instance_info`. Short names (`copy:`) are ambiguous. Do not
rely on a play-level `collections:` keyword to make short names resolve.

Collections used by the code are declared in `requirements.yml` and installed
with `ansible-galaxy collection install -r requirements.yml`.

Sources: [Ansible FQCN Lint Rule](https://docs.ansible.com/projects/lint/rules/fqcn/)

## Idempotency

Running a playbook twice gives the same result: the first run makes changes,
later runs report `ok` with no changes.

```yaml
# WRONG: always reports changed
- name: Create directory
  ansible.builtin.command: mkdir -p /opt/myapp

# CORRECT: use the module
- name: Create directory
  ansible.builtin.file:
    path: /opt/myapp
    state: directory
    mode: "0755"

# If command/shell is necessary, guard it with creates/removes
- name: Initialize database
  ansible.builtin.command: /opt/db/init.sh
  args:
    creates: /opt/db/.initialized

# Or check, then act
- name: Check current hostname
  ansible.builtin.command: hostname
  register: current_hostname
  changed_when: false

- name: Set hostname
  ansible.builtin.command: hostnamectl set-hostname "{{ target_hostname }}"
  when: current_hostname.stdout != target_hostname
```

- Packages: `state: present`, not `latest`, unless the role exists to apply
  updates.
- Files and services: declare the end state (`state: directory`,
  `state: started`, `enabled: true`).
- Read-only `command`/`shell` tasks get `changed_when: false`.

## Security

### Secrets and Vault

- Never commit secrets in plain text in vars, defaults, or inventory. Encrypt
  them with `ansible-vault create`/`encrypt`/`edit` and load them with
  `vars_files`.
- Supply the vault password at run time (`--ask-vault-pass` or
  `--vault-password-file`), never from the repo.

### no_log

Any task that receives a password, token, or key gets `no_log: true`, so the
value does not appear in output or logs:

```yaml
- name: Set database password
  community.mysql.mysql_user:
    name: app_user
    password: "{{ db_password }}"
    priv: "app_db.*:ALL"
  no_log: true
```

### Privilege escalation

Escalate at task level where possible. Play-level `become: true` grants root
to tasks that do not need it. Use `become_user` to drop to a service account
instead of root when that is enough.

### Other security checks

- Prefer modules over `shell`/`command`; flag `shell:` that interpolates
  untrusted variables (command injection).
- Validate input from external sources (for example with
  `ansible.builtin.assert`).
- Set `mode` on created files; sensitive files get restrictive modes such as
  `"0600"` with an explicit `owner` and `group`.

Sources: [Ansible Vault](https://docs.ansible.com/ansible/latest/vault_guide/index.html),
[Privilege Escalation](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_privilege_escalation.html)

## Testing and validation

- `ansible-lint` on playbooks and roles. A `.ansible-lint` with
  `profile: production` is a good baseline; every `skip_list` entry needs a
  comment explaining why.
- `ansible-playbook site.yml --check --diff` previews changes without
  applying them.
- `ansible.builtin.assert` with `fail_msg` validates inputs early:

```yaml
- name: Validate configuration
  ansible.builtin.assert:
    that:
      - app_port > 1024
      - app_user is defined
      - app_user | length > 0
    fail_msg: "Invalid configuration: port must be > 1024 and user must be defined"
    quiet: true
```

- Molecule: see the ansible-molecule-guide skill.

## Common anti-patterns

1. **shell/command where a module exists.** `shell: apt-get install nginx -y`
   becomes `ansible.builtin.apt` with `state: present`.
2. **Short module names.** `copy:` becomes `ansible.builtin.copy:`.
3. **Hardcoded values.** Users, UIDs, ports, and paths belong in role
   variables (`"{{ app_user }}"`), not literals.
4. **Missing task names.**
5. **`import_tasks` with `loop`.** Use `include_tasks`.
6. **Secrets in plain text.** Move them to a vault-encrypted vars file.
7. **Ignoring errors without handling them.** `ignore_errors: true` on its own
   is a silent failure. Handle the failure with `block`/`rescue`, or allow
   specific outcomes with `failed_when: result.rc not in [0, 2]`.
   `failed_when: false` is suppression, not handling: use it only when a
   non-zero rc is expected, and act on the registered result afterwards.
8. **Non-idempotent tasks.** `shell: echo "config=value" >> /etc/app.conf`
   becomes `ansible.builtin.lineinfile` with `path` and `line`.
9. **Overusing `become: true`.** Play-level become when only some tasks need
   root. Move it to the tasks that need it.
10. **Restarting without handlers.** A restart task after a template runs on
    every play. Notify a handler instead:

```yaml
- name: Update config
  ansible.builtin.template:
    src: app.conf.j2
    dest: /etc/app/app.conf
    mode: "0644"
  notify: Restart app

# handlers/main.yml
- name: Restart app
  ansible.builtin.service:
    name: app
    state: restarted
```

Sources: [Ansible Lint Rules](https://docs.ansible.com/projects/lint/rules/)

## Severity

Report findings on the consumer agent's scale:

- **CRITICAL**: affects correctness or security, or causes crashes or data loss
- **HIGH**: significant reliability or maintainability issue
- **MEDIUM**: best-practice violation with real impact
- **LOW**: minor improvement
- **INFO**: optimization suggestion

## Review checklist

### Every task file

- [ ] Every task has a sentence-case, action-verb `name:` with no templating
- [ ] Every module with a known namespace uses FQCN
- [ ] No `shell`/`command` where a module exists
- [ ] Every `command`/`shell` task has `creates`/`removes` or `changed_when`
- [ ] No `{{ }}` in `when`; string booleans use `| bool`
- [ ] `loop` rather than `with_*`; `include_tasks` for looped includes
- [ ] `mode` set on tasks that create files or directories
- [ ] `ignore_errors` only with real handling

### Security

- [ ] No plain-text secrets in vars, defaults, inventory, or templates
- [ ] `no_log: true` on every task that handles credentials
- [ ] `become` scoped to the tasks that need it
- [ ] No untrusted variables interpolated into `shell:`
- [ ] Sensitive files created with restrictive `mode`, `owner`, and `group`

### Roles

- [ ] Public variables prefixed with the role name; internal ones with `__`
- [ ] Defaults in `defaults/main.yml`, not hardcoded in tasks
- [ ] Restarts and reloads done by handlers via `notify`; every notified
      handler exists
- [ ] Packages use `state: present` unless the role applies updates
