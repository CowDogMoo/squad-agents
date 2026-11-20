---
name: ansible-molecule-guide
description: "Molecule testing for Ansible roles and collections — scenario structure, molecule.yml configuration, converge and verify playbooks, multi-platform matrices, idempotence testing, prepare/cleanup, and side-effect patterns. Use when writing a Molecule scenario or strengthening verify.yml assertions. Also loaded by the ansible-molecule agent as its knowledge base."
---
# Molecule Testing Guide

What a good Molecule suite looks like, and how to judge one. The core rule:
**assert outcomes, not file existence.** A verify.yml that only proves a file
is present does not prove the role works.

## Read-when index

This file is the core. Topic files live in `references/` under this skill's
base directory. Read one only when its condition applies:

- Read `references/molecule-yml.md` when auditing molecule.yml itself:
  config hierarchy, `${VAR}` substitution, drivers, platform keys,
  provisioner, test_sequence variants, `shared_state`, `prerun`,
  `role_name_check`.
- Read `references/multi-platform.md` when the role supports more than one OS
  family, or when platforms use systemd containers or platform groups.
- Read `references/prepare-cleanup-side-effects.md` when the scenario has
  prepare.yml, cleanup.yml, side_effect.yml, or a custom multi-step
  test_sequence.
- Read `references/troubleshooting.md` when a scenario fails for a reason
  outside the role itself: empty service facts, systemd containers that do
  not start, role modules missing in verify.yml.

## Testing philosophy

Molecule follows the four-phase test pattern:

1. **Setup** (create, prepare): provision a clean, isolated instance.
2. **Exercise** (converge): apply the content under test.
3. **Verify** (verify): check the desired outcomes were achieved.
4. **Teardown** (destroy): remove everything that was created.

Principles a suite is judged against:

1. Every role has a scenario. Untested roles are unreliable roles.
2. Tests assert outcomes. Checking existence is not enough.
3. Idempotence is mandatory. A second converge must report no changes.
4. Every platform the role claims to support is tested.
5. Tests are isolated and reproducible: no dependence on external systems,
   identical results locally and in CI, fast enough for CI.

## Scenario structure

```text
roles/my_role/molecule/
├── default/               # Default scenario (required)
│   ├── molecule.yml       # Platforms, provisioner, test_sequence
│   ├── converge.yml       # Applies the role with test variables
│   ├── verify.yml         # Asserts the role's outcomes
│   ├── prepare.yml        # Prerequisites before converge (optional)
│   ├── cleanup.yml        # Teardown of external resources (optional)
│   ├── side_effect.yml    # Disruption for stateful tests (optional)
│   └── requirements.yml   # Role/collection dependencies
└── security/              # Extra scenarios: security, upgrade, minimal...
```

### Converge essentials

- Keep it minimal: apply the role and nothing else. Prerequisites belong in
  prepare.yml.
- Use FQCN for every module, including in test playbooks.
- Include the role by name, or with
  `"{{ lookup('env', 'MOLECULE_PROJECT_DIRECTORY') | basename }}"`, or by
  collection path (`my_namespace.my_collection.my_role`).
- Set test overrides in play `vars`; never edit role defaults for a test.
- Set `become: true` at play level when the role needs privilege, and
  `gather_facts: true` when it uses facts.

## Verify depth

**Every verify.yml must contain `ansible.builtin.assert` (or
`ansible.builtin.fail` with a real condition).** Registering a result without
asserting on it verifies nothing.

For each thing the role does, verify.yml checks the outcome, not a proxy:

| Role action | Strong check | Weak check (flag it) |
|---|---|---|
| Installs a package | `package` with `check_mode: true` + `failed_when: result.changed` | `stat` on a binary path |
| Installs a binary | `stat` + assert `exists`, `executable`, `mode` | `stat` + `exists` only |
| Writes config | `slurp` + assert expected settings in `content \| b64decode` | `stat` + `exists` only |
| Creates dirs/files | assert `mode`, `pw_name` (owner) | existence only |
| Manages a service | `service_facts` + assert `state == 'running'` and `status == 'enabled'` | none, or `systemctl` without assert |
| Opens a port | `wait_for` port, assert not failed | none |
| Serves HTTP | `uri` with `status_code` and content assertion | port check only |
| Sets env vars | `slurp` the profile/env file + assert | none |

Core patterns:

```yaml
- name: Verify
  hosts: all
  become: true
  gather_facts: true
  vars_files:
    - ../../defaults/main.yml   # use role values, not hardcoded copies

  tasks:
    - name: Check nginx is installed
      ansible.builtin.package:
        name: nginx
        state: present
      check_mode: true
      register: nginx_pkg
      failed_when: nginx_pkg.changed

    - name: Gather service facts
      ansible.builtin.service_facts:

    - name: Assert nginx is running and enabled
      ansible.builtin.assert:
        that:
          - "'nginx.service' in ansible_facts.services"
          - "ansible_facts.services['nginx.service'].state == 'running'"
          - "ansible_facts.services['nginx.service'].status == 'enabled'"
        fail_msg: "nginx is not running or not enabled"

    - name: Stat config file
      ansible.builtin.stat:
        path: /etc/nginx/nginx.conf
      register: nginx_conf_stat

    - name: Read config file
      ansible.builtin.slurp:
        src: /etc/nginx/nginx.conf
      register: nginx_conf

    - name: Assert config exists with correct mode and content
      ansible.builtin.assert:
        that:
          - nginx_conf_stat.stat.exists
          - nginx_conf_stat.stat.mode == '0644'
          - "('listen ' ~ nginx_port) in (nginx_conf.content | b64decode)"
        fail_msg: "nginx.conf missing, wrong mode, or not listening on {{ nginx_port }}"

    - name: Query health endpoint
      ansible.builtin.uri:
        url: "http://localhost:{{ nginx_port }}/"
        return_content: true
      register: http_check
      retries: 3
      delay: 5
      until: http_check.status == 200
```

Rules that go with these patterns:

- `service_facts` must run before any `ansible_facts.services` lookup; service
  keys carry the `.service` suffix.
- `gather_facts: true` (or an explicit facts task) when anything reads
  `ansible_facts`.
- Every assert has a `fail_msg` that names what broke.
- Load role values with `vars_files` instead of hardcoding ports, paths, or
  users that can drift from defaults.
- Test observable behavior. Internal markers or temp files the role happens to
  create are implementation details.

Verifier choice: the `ansible` verifier (default since Molecule v3) suits
small YAML suites. `testinfra` (Python) suits large, looping, or parametrized
suites. `goss` is a fast YAML alternative. All of them must assert outcomes.

## Idempotence

Molecule runs converge a second time; if any task reports `changed`, the
`idempotence` step fails. That catches tasks that always report changed and
state bugs that would bite on the next production run.

- A standard full `test_sequence` must include `idempotence` between
  `converge` and `verify`. Leaving it out needs a documented reason.
- Do not add `idempotence` to custom or partial sequences (create- or
  converge-only) that exist for another purpose.

Common failures and fixes:

| Cause | Fix |
|---|---|
| Read-only `command`/`shell` (status, queries) | `changed_when: false` |
| State-changing `command`/`shell` with no guard | `args: creates:` / `removes:`, or `changed_when` on real output (`"'Applied' in result.stdout"`) |
| Template with dynamic content (timestamps, random values) | static header text |

Task-level tags for Molecule runs:

| Tag | Effect |
|---|---|
| `molecule-idempotence-notest` | skip only during the idempotence step |
| `molecule-notest` (alias `notest`) | skip in every Molecule phase |

Use `molecule-idempotence-notest` for tasks that legitimately change every
run (seeding a database), and `molecule-notest` for tasks that cannot run in a
container (reboot). A tagged task is a documented exception, not a finding.

## Anti-patterns

1. **No verify.yml.** The scenario converges and proves nothing. Add one with
   assertions on the role's outcomes.
2. **Registered checks with no assert.** A `stat` or `command` that registers
   a result and stops there. Add an assert on the registered value.
3. **Existence-only assertions.** `stat.exists` on a config file or binary
   with no mode, owner, or content check. Strengthen per the verify table.
4. **Missing `idempotence`** in a standard full test_sequence.
5. **Single platform on a multi-platform role.** The role's
   `meta/main.yml` lists Debian and RedHat families but only Ubuntu is
   tested. Add a platform per supported family.
6. **Short module names** in converge, verify, or prepare. Use FQCN
   (`stat:` becomes `ansible.builtin.stat:`).
7. **Facts used but not gathered.** `ansible_facts.services` read with no
   `service_facts` task, or `gather_facts: false` with fact lookups.
8. **Hardcoded values** in verify.yml (port 80) that do not match role
   defaults. Load `../../defaults/main.yml` and use the variables.
9. **Testing implementation details.** Asserting an internal marker file
   instead of the service, endpoint, or config the user relies on.
10. **Setup work in converge.** Installing prerequisites or creating
    directories before including the role. Move it to prepare.yml.
11. **Test-only dependencies always installed.** Guard test helper roles in
    `meta/main.yml` with `when: lookup('env', 'MOLECULE_FILE') | length > 0`.

## Quality checklist

### molecule.yml

- [ ] Driver configured (docker, podman, or delegated)
- [ ] One platform per OS family the role supports, with groups for
      family-specific checks
- [ ] `pre_build_image: true` on pre-baked `*-ansible` images
- [ ] Privileged mode and cgroup mount for systemd containers
- [ ] `test_sequence` includes `idempotence`
- [ ] Dependencies declared in requirements.yml when needed

### converge.yml

- [ ] All modules use FQCN
- [ ] Role included by name or basename lookup
- [ ] Test variables in play vars, role defaults untouched
- [ ] `become` and `gather_facts` set when the role needs them
- [ ] Minimal: only what applies the role

### verify.yml

- [ ] Has assertions, not just registered checks
- [ ] Tests outcomes (mode, owner, content, running state, responses), not
      just existence
- [ ] All modules use FQCN
- [ ] `gather_facts: true` when using `ansible_facts`; `service_facts` before
      service checks
- [ ] `check_mode: true` with `failed_when` on package checks
- [ ] Meaningful `fail_msg` on every assertion
- [ ] `vars_files` loads role defaults when referencing role variables
- [ ] Tests observable behavior, not implementation details

### prepare.yml (if used)

- [ ] Only prerequisite setup, no duplication of role tasks
- [ ] Minimal and fast

### Idempotence

- [ ] `changed_when: false` on read-only commands
- [ ] `creates`/`removes` or a real `changed_when` on state-changing commands
- [ ] No dynamic content in templates
- [ ] `molecule-idempotence-notest` only on legitimately non-idempotent tasks

### General

- [ ] `molecule syntax`, ansible-lint, and yamllint pass
- [ ] Clear, actionable failure messages
- [ ] Every supported platform tested
