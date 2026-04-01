# Ansible Molecule Agent

Autonomous agent for creating and analyzing Molecule test scenarios for Ansible roles.

## Usage

```bash
# Create Molecule tests for a role (fix mode)
squad run ansible-molecule --target ./roles/nginx

# Analyze existing Molecule tests (readonly mode)
squad run ansible-molecule --mode readonly --target ./roles
```

## Features

### Fix Mode (default)

- **Role Discovery** — Finds roles by locating `tasks/main.yml`
- **Scenario Creation** — Creates `molecule/default/` with proper structure
- **Verification Generation** — Writes `verify.yml` based on role tasks
- **Multi-Platform** — Configures Ubuntu and Rocky Linux platforms
- **Test Execution** — Runs `molecule test` to validate

### Readonly Mode

- **Coverage Analysis** — Identifies roles without Molecule tests
- **Quality Assessment** — Grades existing test scenarios
- **Anti-Pattern Detection** — Finds common testing mistakes
- **Recommendations** — Prioritized improvements

## Verification Patterns

The agent uses these verification strategies based on role tasks:

| Role Task | Verification |
|-----------|-------------|
| Package installation | `check_mode: true` with package module |
| Service management | `check_mode: true` + `wait_for:` port |
| File creation | `stat:` + `assert:` |
| Template rendering | `lineinfile:` check or content assertion |

## Output

### Fix Mode

```markdown
## Molecule Test Summary

**Role:** nginx
**Scenarios created:** 1
**Test result:** PASS

### Verifications Added

| Check | Type | Description |
|-------|------|-------------|
| nginx package | check_mode | Verify nginx is installed |
| nginx service | check_mode | Verify nginx is running |
| port 80 | wait_for | Verify nginx responds |
```

### Readonly Mode

```markdown
## Analysis Summary

- **Roles analyzed:** 5
- **Roles with Molecule:** 3
- **Roles without Molecule:** role_a, role_b
- **Total findings:** 8

## Coverage Report

| Role | Scenarios | Platforms | Verifications | Grade |
|------|-----------|-----------|---------------|-------|
| nginx | 1 | 2 | 5 | B |
```

## Knowledge Base

The agent references `ansible-molecule-guide.md` which covers:

- Scenario structure and configuration
- molecule.yml driver and platform options
- Verification patterns (check_mode, stat+assert, URI)
- Multi-platform testing strategies
- CI/CD integration (GitHub Actions, GitLab CI)
- Common anti-patterns to avoid

## Example

```bash
squad run --agent ansible-molecule --working-dir ./roles/nginx
```

### Input (roles/nginx/tasks/main.yml)

```yaml
- name: Install nginx
  ansible.builtin.apt:
    name: nginx
    state: present

- name: Copy nginx config
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
  notify: Restart nginx

- name: Start nginx
  ansible.builtin.service:
    name: nginx
    state: started
    enabled: true
```

### Generated (molecule/default/verify.yml)

```yaml
- name: Verify nginx role
  hosts: all
  gather_facts: false
  tasks:
    - name: Verify nginx is installed
      ansible.builtin.apt:
        name: nginx
        state: present
      check_mode: true
      register: nginx_pkg
      failed_when: nginx_pkg.changed

    - name: Verify nginx config exists
      ansible.builtin.stat:
        path: /etc/nginx/nginx.conf
      register: nginx_conf

    - name: Assert nginx config is present
      ansible.builtin.assert:
        that:
          - nginx_conf.stat.exists
          - nginx_conf.stat.size > 0

    - name: Verify nginx is running
      ansible.builtin.service:
        name: nginx
        state: started
      check_mode: true
      register: nginx_svc
      failed_when: nginx_svc.changed

    - name: Verify nginx responds on port 80
      ansible.builtin.wait_for:
        port: 80
        timeout: 10
```

## Constraints

- Only modifies files in `molecule/` directories
- Never changes role source code
- Requires at least 2 platforms (Debian + RedHat family)
- All modules must use FQCN
- Test sequence must include idempotence step
