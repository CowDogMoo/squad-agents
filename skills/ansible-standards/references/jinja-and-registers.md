# Registered results and Jinja2 templates

Read when the code reads registered return values (`stdout`, `rc`, `stdout_lines`) or ships Jinja2 templates and filters.

## Contents

- Register and return values
- Jinja2 templates

## Register and Return Values

### Common Return Values

```yaml
- name: Run command
  ansible.builtin.command: whoami
  register: result

# Access return values
- name: Show results
  ansible.builtin.debug:
    msg: |
      stdout: {{ result.stdout }}
      stderr: {{ result.stderr }}
      rc: {{ result.rc }}
      changed: {{ result.changed }}
      stdout_lines: {{ result.stdout_lines }}
```

### Best Practices

```yaml
# Use changed_when with register for commands
- name: Check status
  ansible.builtin.command: systemctl is-active nginx
  register: nginx_status
  changed_when: false
  failed_when: nginx_status.rc not in [0, 3]

# Use stdout_lines for multi-line output
- name: List files
  ansible.builtin.command: ls /opt
  register: files_list
  changed_when: false

- name: Process each file
  ansible.builtin.debug:
    msg: "Found: {{ item }}"
  loop: "{{ files_list.stdout_lines }}"
```

Sources: [Ansible Return Values](https://docs.ansible.com/ansible/latest/reference_appendices/common_return_values.html)

## Jinja2 Templates

### Template Best Practices

```jinja2
{# templates/app.conf.j2 #}
# Managed by Ansible - DO NOT EDIT
{# No timestamps: they change every run and break idempotence #}
# Host: {{ inventory_hostname }}

[application]
port = {{ app_port | default(8080) }}
host = {{ app_host | mandatory }}
debug = {{ app_debug | default(false) | lower }}

{% if app_features is defined %}
[features]
{% for feature in app_features %}
{{ feature.name }} = {{ feature.enabled | lower }}
{% endfor %}
{% endif %}
```

### Useful Filters

```yaml
# Default values
"{{ variable | default('fallback') }}"

# Type conversion
"{{ string_number | int }}"
"{{ value | bool }}"

# String operations
"{{ name | upper }}"
"{{ name | lower }}"
"{{ name | capitalize }}"
"{{ list | join(', ') }}"

# List operations
"{{ list | first }}"
"{{ list | last }}"
"{{ list | unique }}"
"{{ list | sort }}"

# JSON/YAML
"{{ dict | to_json }}"
"{{ dict | to_nice_yaml }}"

# Path operations
"{{ path | basename }}"
"{{ path | dirname }}"

# Password hashing
"{{ password | password_hash('sha512') }}"
```

Sources: [Ansible Templating](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_templating.html),
[Ansible Filters](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_filters.html)
