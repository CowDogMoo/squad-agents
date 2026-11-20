# molecule.yml configuration

Read when auditing molecule.yml drivers, platforms, provisioner settings, or
test_sequence variants. The core verify and idempotence rules live in
SKILL.md.

## Contents

- Configuration hierarchy
- Environment variable substitution
- Complete example
- Key sections: dependency, driver, platforms, provisioner, scenario
- Additional settings: prerun, role_name_check

The `molecule.yml` file is the central configuration entrypoint for Molecule.

## Configuration Hierarchy

Settings are inherited from multiple levels (most specific wins):

1. `$HOME/.config/molecule/config.yml` - Global defaults for all projects
2. Project root `config.yml` - Project-level defaults
3. `extensions/molecule/config.yml` - Collection-specific defaults
4. `molecule/*/molecule.yml` - Scenario-specific overrides

Empty `molecule.yml` files inherit the complete configuration from parent configs.

## Environment Variable Substitution

Molecule supports shell-style variable substitution in `molecule.yml`:

```yaml
platforms:
  - name: ${MOLECULE_INSTANCE_NAME:-default}
    image: "geerlingguy/docker-${MOLECULE_DISTRO:-ubuntu2204}-ansible:latest"

provisioner:
  env:
    MY_VAR: ${MY_VAR}           # Simple substitution
    WITH_DEFAULT: ${VAR:-default}  # Default if unset or empty
    LITERAL: $$NOT_A_VAR       # Escaped dollar sign
```

Avoid the `MOLECULE_` prefix for custom variables - it's reserved.

## Complete Example

```yaml
---
dependency:
  name: galaxy
  options:
    requirements-file: requirements.yml

driver:
  name: docker

platforms:
  - name: ubuntu-22
    image: geerlingguy/docker-ubuntu2204-ansible:latest
    pre_build_image: true
    privileged: true
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:rw
    cgroupns_mode: host
    command: ""
    groups:
      - debian

  - name: rocky-9
    image: geerlingguy/docker-rockylinux9-ansible:latest
    pre_build_image: true
    privileged: true
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:rw
    cgroupns_mode: host
    command: ""
    groups:
      - redhat

provisioner:
  name: ansible
  log: true
  config_options:
    defaults:
      callbacks_enabled: profile_tasks
      fact_caching: jsonfile
      fact_caching_connection: /tmp/facts_cache
    ssh_connection:
      pipelining: true
  inventory:
    group_vars:
      all:
        ansible_user: root
  playbooks:
    converge: converge.yml
    verify: verify.yml
    prepare: prepare.yml

verifier:
  name: ansible

scenario:
  test_sequence:
    - dependency
    - cleanup
    - destroy
    - syntax
    - create
    - prepare
    - converge
    - idempotence
    - verify
    - cleanup
    - destroy
```

## Key Sections

### dependency

Installs role and collection dependencies:

```yaml
dependency:
  name: galaxy
  options:
    requirements-file: requirements.yml
    # Force reinstall
    force: true
```

### driver

Specifies the infrastructure driver:

```yaml
# Docker (most common)
driver:
  name: docker

# Podman (rootless, no daemon required)
driver:
  name: podman

# Delegated (Molecule's built-in default; you supply create/destroy playbooks)
driver:
  name: delegated
```

The docker and podman drivers ship in `molecule-plugins`, not in Molecule
itself: install `molecule-plugins[docker]` or `molecule-plugins[podman]`.
Podman runs rootless with no daemon; Docker has wider tooling support.

### platforms

Defines test instances:

```yaml
platforms:
  - name: instance-name
    image: docker/image:tag
    pre_build_image: true      # Use image as-is, don't build
    privileged: true           # Required for systemd
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:rw
    cgroupns_mode: host        # For cgroups v2
    command: ""                # Override default command
    groups:                    # Ansible inventory groups
      - webservers
    docker_networks:           # Custom networks
      - name: molecule_net
```

### provisioner

Configures Ansible execution:

```yaml
provisioner:
  name: ansible
  log: true
  config_options:
    defaults:
      callbacks_enabled: profile_tasks
      verbosity: 1
  env:
    ANSIBLE_DIFF_ALWAYS: "true"
  inventory:
    host_vars:
      instance-name:
        custom_var: value
    group_vars:
      all:
        common_var: value
```

### scenario

Controls test execution sequence and scenario behavior:

```yaml
scenario:
  name: default
  test_sequence:
    - dependency    # Install dependencies
    - cleanup       # Initial cleanup
    - destroy       # Destroy existing instances
    - syntax        # Syntax check
    - create        # Create instances
    - prepare       # Run prepare playbook
    - converge      # Apply the role
    - idempotence   # Run converge again, fail on changes
    - verify        # Run verification
    - cleanup       # Final cleanup
    - destroy       # Destroy instances
```

The `idempotence` step is mandatory unless the scenario documents why it is skipped.

**Task Filtering Tags**:

Skip tasks during specific Molecule phases using tags:

| Tag | Effect |
|-----|--------|
| `molecule-notest` | Skip task in ALL Molecule phases |
| `notest` | Alias for `molecule-notest` |
| `molecule-idempotence-notest` | Skip ONLY during idempotence check |

```yaml
# In your role task
- name: Seed database (not idempotent)
  ansible.builtin.command: /usr/bin/seed-db
  tags:
    - molecule-idempotence-notest  # Only skip during idempotence

- name: Task not suitable for containers
  ansible.builtin.reboot:
  tags:
    - molecule-notest  # Skip in all Molecule runs
```

**Shared State Between Scenarios**:

Enable resource sharing between scenarios to reduce execution time:

```yaml
# In molecule.yml
shared_state: true  # Access resources created by default scenario
```

When enabled, scenarios can access infrastructure created by the default scenario,
eliminating per-scenario setup/teardown overhead.

**Custom Sequences**:

Define separate sequences for different operations:

```yaml
scenario:
  create_sequence:
    - dependency
    - create
    - prepare
  converge_sequence:
    - converge
  destroy_sequence:
    - destroy
  test_sequence:
    - dependency
    - cleanup
    - destroy
    - syntax
    - create
    - prepare
    - converge
    - idempotence
    - verify
    - cleanup
    - destroy
```

### Additional Settings

**Prerun Configuration**:

Molecule automatically installs dependencies via prerun. Disable if needed:

```yaml
prerun: false
```

**Role Name Check**:

By default, Molecule validates role names follow `namespace.role` standard.
Relax validation for non-conforming roles:

```yaml
role_name_check: 1  # Enable relaxed validation
```

**Note**: Following the namespace and role naming standard is strongly recommended.
