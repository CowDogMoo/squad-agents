# Role structure

Read when reviewing role layout, `meta/main.yml` dependencies and platforms, or Galaxy versioning. Collection structure, `galaxy.yml`, and `argument_specs` are covered by the ansible-standards skill.

## Standard Directory Layout

```
roles/
└── my_role/
    ├── defaults/
    │   └── main.yml      # Default variables (lowest precedence)
    ├── files/
    │   └── app.conf      # Static files for copy module
    ├── handlers/
    │   └── main.yml      # Handler definitions
    ├── meta/
    │   └── main.yml      # Role metadata, dependencies
    ├── tasks/
    │   └── main.yml      # Main task list
    ├── templates/
    │   └── config.j2     # Jinja2 templates
    ├── tests/
    │   ├── inventory
    │   └── test.yml      # Test playbook
    ├── vars/
    │   └── main.yml      # Role variables (high precedence)
    └── README.md         # Documentation
```

## Role Design Principles

1. **Single responsibility** — one role, one purpose
2. **Self-contained** — include all necessary tasks, templates, files
3. **Configurable** — expose variables in defaults/
4. **Documented** — README with examples

## Role Dependencies (meta/main.yml)

```yaml
galaxy_info:
  author: Your Name
  description: Role description
  license: MIT
  min_ansible_version: "2.10"
  platforms:
    - name: Ubuntu
      versions:
        - focal
        - jammy
    - name: EL
      versions:
        - "8"
        - "9"

dependencies:
  - role: common
  - role: firewall
    vars:
      firewall_allowed_ports:
        - 80
        - 443
```

## Galaxy Versioning

- Use strict **X.Y.Z** format (e.g., 1.0.0, 2.1.3)
- Follow semantic versioning

Sources: [Ansible Roles](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_reuse_roles.html),
[Galaxy Developer Guide](https://docs.ansible.com/projects/ansible/latest/galaxy/dev_guide.html)
