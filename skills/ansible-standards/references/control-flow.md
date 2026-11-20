# Control flow: conditionals, loops, handlers, tags, includes

Read when the code uses `when` with compound or registered-result conditions, loops (`loop_control`, flattening, dict loops), handlers (`listen`, `flush_handlers`), tags, or `include_tasks`/`import_tasks`.

## Contents

- Conditionals
- Loops
- Handlers
- Tags
- include_tasks vs import_tasks

## Conditionals

### Boolean Handling

```yaml
# For string booleans, use | bool filter
- name: Enable feature
  ansible.builtin.debug:
    msg: Feature enabled
  when: enable_feature | bool

# Direct boolean variables don't need filter
- name: Skip if disabled
  ansible.builtin.debug:
    msg: Running
  when: is_enabled  # Already a boolean
```

### Syntax

```yaml
# CORRECT: No {{ }} in when clauses
when: ansible_os_family == "Debian"

# WRONG: Using {{ }} in when
when: "{{ ansible_os_family == 'Debian' }}"  # Wrong!
```

### Multiple Conditions

```yaml
# Using 'and' (both must be true)
when:
  - ansible_os_family == "RedHat"
  - ansible_distribution_major_version | int >= 8

# Using 'or'
when: ansible_os_family == "Debian" or ansible_os_family == "Ubuntu"

# Complex logic
when: >
  (ansible_os_family == "RedHat" and ansible_distribution_major_version | int >= 8)
  or
  (ansible_os_family == "Debian" and ansible_distribution_major_version | int >= 10)
```

### Testing Variables

```yaml
# Check if defined
when: my_var is defined

# Check if undefined
when: my_var is not defined

# Check if empty
when: my_var | length > 0

# Check task results
when: previous_task is succeeded
when: previous_task is failed
when: previous_task is skipped
when: previous_task is changed
```

Sources: [Ansible Conditionals](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_conditionals.html)

## Loops

### Prefer `loop` Over `with_items`

```yaml
# CORRECT: Modern loop syntax
- name: Install packages
  ansible.builtin.package:
    name: "{{ item }}"
    state: present
  loop:
    - nginx
    - certbot
    - python3

# LEGACY: with_items (still works but prefer loop)
- name: Install packages
  ansible.builtin.package:
    name: "{{ item }}"
    state: present
  with_items:
    - nginx
    - certbot
```

### Loop Control

```yaml
- name: Create users
  ansible.builtin.user:
    name: "{{ item.name }}"
    groups: "{{ item.groups }}"
  loop: "{{ users }}"
  loop_control:
    label: "{{ item.name }}"  # Show only name in output
    pause: 2                   # Pause between iterations
    index_var: idx             # Access loop index
```

### Flattening Behavior

```yaml
# with_items flattens single level automatically
# loop does NOT flatten - add | flatten(1) if needed
- name: Install packages
  ansible.builtin.package:
    name: "{{ item }}"
  loop: "{{ package_lists | flatten(1) }}"
```

### Dictionary Loops

```yaml
- name: Create users with attributes
  ansible.builtin.user:
    name: "{{ item.key }}"
    comment: "{{ item.value.comment }}"
  loop: "{{ users | dict2items }}"
```

Sources: [Ansible Loops](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_loops.html)

## Handlers

### Basic Handler Pattern

```yaml
# In tasks
- name: Update nginx configuration
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
  notify: Restart nginx

# In handlers/main.yml
- name: Restart nginx
  ansible.builtin.service:
    name: nginx
    state: restarted
  become: true
```

### Handler Best Practices

1. **Unique names** — handlers must have globally unique names
2. **Order matters** — handlers run in definition order, not notification order
3. **Single execution** — handlers run once regardless of how many times notified

### Using `listen` for Handler Groups

```yaml
# Multiple handlers can listen to the same topic
handlers:
  - name: Restart nginx
    ansible.builtin.service:
      name: nginx
      state: restarted
    listen: web server changed

  - name: Clear nginx cache
    ansible.builtin.file:
      path: /var/cache/nginx
      state: absent
    listen: web server changed

# Task notifies the topic
- name: Update config
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
  notify: web server changed
```

### Flushing Handlers

```yaml
# Force handlers to run immediately
- name: Update critical config
  ansible.builtin.template:
    src: app.conf.j2
    dest: /etc/app/app.conf
  notify: Restart application

- name: Flush handlers
  ansible.builtin.meta: flush_handlers

- name: Run health check
  ansible.builtin.uri:
    url: http://localhost:8080/health
```

Sources: [Ansible Handlers](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_handlers.html)

## Tags Best Practices

### Special Tags

- `always` — runs unless explicitly skipped with `--skip-tags always`
- `never` — skipped unless explicitly requested with `--tags never`

```yaml
- name: Always run health check
  ansible.builtin.uri:
    url: http://localhost/health
  tags:
    - always
    - health

- name: Debug task (only when requested)
  ansible.builtin.debug:
    var: all_vars
  tags:
    - never
    - debug
```

### Tag Best Practices

1. Always add a specific named tag alongside `always` or `never`
2. Use consistent tag names across playbooks
3. Document tag meanings in README

```bash
# Run only specific tags
ansible-playbook site.yml --tags "deploy,config"

# Skip specific tags
ansible-playbook site.yml --skip-tags "debug"

# List available tags
ansible-playbook site.yml --list-tags
```

Sources: [Ansible Tags](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_tags.html)

## include_tasks vs import_tasks

### Key Differences

| Feature | `import_tasks` | `include_tasks` |
|---------|----------------|-----------------|
| Processing | Static (parse time) | Dynamic (runtime) |
| Loops | Not supported | Supported |
| Conditionals | Applied to each task | Applied to include itself |
| Tags | Inherited by imported tasks | Not inherited |
| `--list-tasks` | Shows tasks | Doesn't show tasks |

### When to Use Each

```yaml
# Use import_tasks for static includes
- import_tasks: common.yml

# Use include_tasks for dynamic/looped includes
- include_tasks: user.yml
  loop: "{{ users }}"
  loop_control:
    loop_var: user

# Use include_tasks with conditionals
- include_tasks: "{{ ansible_os_family | lower }}.yml"
```

### General Recommendation

Prefer `include_tasks` unless you specifically need static parsing behavior.
The limitations of `import_tasks` (no loops, no dynamic file names) are more
impactful than the minor overhead of dynamic includes.

Sources: [Ansible Include vs Import](https://docs.ansible.com/projects/ansible/2.9/user_guide/playbooks_reuse_includes.html)
