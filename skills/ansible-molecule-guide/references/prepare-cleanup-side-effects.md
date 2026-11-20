# Prepare, cleanup, and side effects

Read when the scenario has prepare.yml, cleanup.yml, side_effect.yml, or a
custom multi-step test_sequence. These are valid advanced patterns; do not
flag them for existing.

## Contents

- Prepare playbook
- Cleanup playbook
- When to use prepare/cleanup
- Side effect playbook
- Advanced multi-step testing
- Multiple converge steps

## Prepare Playbook

Runs before converge to set up prerequisites:

```yaml
---
# prepare.yml
- name: Prepare
  hosts: all
  become: true
  gather_facts: true

  tasks:
    - name: Install required dependencies
      ansible.builtin.package:
        name:
          - python3
          - python3-pip
        state: present

    - name: Create required directories
      ansible.builtin.file:
        path: /opt/app
        state: directory
        mode: "0755"

    - name: Pre-populate configuration
      ansible.builtin.template:
        src: test-config.yml.j2
        dest: /etc/app/test-config.yml
```

## Cleanup Playbook

Runs after verify to clean up resources:

```yaml
---
# cleanup.yml
- name: Cleanup
  hosts: all
  become: true
  gather_facts: false

  tasks:
    - name: Remove test data
      ansible.builtin.file:
        path: /tmp/test-data
        state: absent

    - name: Stop test services
      ansible.builtin.service:
        name: test-service
        state: stopped
      ignore_errors: true
```

## When to Use Prepare/Cleanup

**Use prepare when:**

- Role requires pre-existing resources
- Testing upgrade scenarios
- Setting up test data

**Use cleanup when:**

- Tests create persistent resources
- Need to reset state between scenarios
- Running in shared environments

## Side Effect Playbook

The `side_effect.yml` playbook executes actions that produce side effects on instances.
It's designed for testing HA failover scenarios, service restarts, or configuration changes.

```yaml
---
# side_effect.yml
- name: Side Effect - Simulate failover
  hosts: all
  become: true
  tasks:
    - name: Stop primary service
      ansible.builtin.service:
        name: myapp
        state: stopped

    - name: Wait for failover
      ansible.builtin.pause:
        seconds: 10
```

## Advanced Multi-Step Testing

Molecule supports complex stateful testing with multiple side effects and verifications.
Actions can take optional arguments to specify different playbooks/tests:

```yaml
# molecule.yml
scenario:
  test_sequence:
    - converge
    - side_effect reboot.yaml        # Run specific side effect
    - verify after_reboot/           # Verify with tests in directory
    - side_effect alter_configs.yaml # Another side effect
    - converge                       # Re-converge after changes
    - verify test2.py test3.py       # Multiple test files
    - side_effect                    # Default side_effect.yml
    - verify                         # Default verify.yml
```

This pattern enables testing:

- **System reboots**: Verify state persists across restarts
- **Configuration drift**: Ensure role corrects manual changes
- **Upgrade scenarios**: Test transitions between versions
- **Failure recovery**: Validate HA and failover behavior

## Multiple Converge Steps

You can run converge multiple times with different configurations:

```yaml
scenario:
  test_sequence:
    - converge                    # Initial setup
    - converge upgrade.yml        # Upgrade scenario
    - idempotence
    - verify
```
