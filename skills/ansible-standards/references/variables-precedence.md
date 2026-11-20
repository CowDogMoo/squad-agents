# Variables and precedence

Read when the code under review relies on where a variable is defined: role defaults vs role vars, group_vars/host_vars overrides, extra vars, `default`/`mandatory` filters.

## Variable Precedence (Lowest to Highest)

1. Role defaults (`roles/x/defaults/main.yml`)
2. Inventory file or script group vars
3. `group_vars/all`
4. `group_vars/group_name`
5. Inventory file or script host vars
6. `host_vars/hostname`
7. Host facts / cached set_facts
8. Play vars
9. Play vars_prompt
10. Play vars_files
11. Role vars (`roles/x/vars/main.yml`)
12. Block vars
13. Task vars
14. include_vars
15. set_facts / registered vars
16. Role params
17. Include params
18. Extra vars (`-e`)

## Best Practices

```yaml
# Set defaults in role defaults
# roles/myapp/defaults/main.yml
myapp_port: 8080
myapp_user: myapp
myapp_log_level: info

# Override in group_vars for specific environments
# group_vars/production.yml
myapp_log_level: warn

# Use default filter for optional variables
port: "{{ custom_port | default(8080) }}"

# Use mandatory filter for required variables
database_password: "{{ db_pass | mandatory }}"
```

## Avoid Hardcoding

```yaml
# WRONG: Hardcoded values
- name: Create user
  ansible.builtin.user:
    name: john
    uid: 1001

# CORRECT: Use variables
- name: Create application user
  ansible.builtin.user:
    name: "{{ app_user }}"
    uid: "{{ app_user_uid }}"
```

Sources: [Ansible Variables Documentation](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_variables.html),
[Spacelift Ansible Variables Guide](https://spacelift.io/blog/ansible-variables)
