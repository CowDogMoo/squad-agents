# Troubleshooting Molecule scenarios

Read when a scenario fails for a reason outside the role itself.

**Idempotence fails but role works correctly**:

1. Run `molecule converge` twice manually
2. Check which tasks report `changed`
3. Add `changed_when: false` or use creates/removes

**Service facts empty**:

```yaml
# Must explicitly gather service facts
- name: Gather service facts
  ansible.builtin.service_facts:

- name: Check service
  ansible.builtin.assert:
    that: ansible_facts.services['nginx.service'].state == 'running'
```

**Container fails to start with systemd**:

```yaml
platforms:
  - name: instance
    image: geerlingguy/docker-ubuntu2204-ansible:latest
    pre_build_image: true
    privileged: true              # Required
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:rw  # Required
    cgroupns_mode: host           # Required for cgroups v2
    command: ""                   # Don't override entrypoint
```

**Role library/modules not available in verify.yml**:

```yaml
# Include role with empty task to make library available
- name: Verify
  hosts: all
  tasks:
    - name: Include role for library access
      ansible.builtin.include_role:
        name: my_role
        tasks_from: init.yml  # Empty task file
```
