# Multi-platform testing

Read when the role supports more than one OS family, or when platforms use
systemd containers or platform groups. Testing across platforms catches
platform-specific bugs.

## Contents

- Platform selection
- Platform groups
- Systemd container requirements
- Single-platform anti-pattern

Testing across multiple platforms catches platform-specific bugs.

## Platform Selection

Test all platforms your role supports:

```yaml
platforms:
  # Debian-family
  - name: ubuntu-20
    image: geerlingguy/docker-ubuntu2004-ansible:latest
    pre_build_image: true
    groups: [debian]

  - name: ubuntu-22
    image: geerlingguy/docker-ubuntu2204-ansible:latest
    pre_build_image: true
    groups: [debian]

  - name: debian-11
    image: geerlingguy/docker-debian11-ansible:latest
    pre_build_image: true
    groups: [debian]

  # RedHat-family
  - name: rocky-8
    image: geerlingguy/docker-rockylinux8-ansible:latest
    pre_build_image: true
    groups: [redhat]

  - name: rocky-9
    image: geerlingguy/docker-rockylinux9-ansible:latest
    pre_build_image: true
    groups: [redhat]

  - name: fedora-39
    image: geerlingguy/docker-fedora39-ansible:latest
    pre_build_image: true
    groups: [redhat]
```

## Platform Groups

Use groups for platform-specific tests:

```yaml
# verify.yml
- name: Verify on Debian
  hosts: debian
  tasks:
    - name: Check apt package
      ansible.builtin.package:
        name: nginx
        state: present
      check_mode: true

- name: Verify on RedHat
  hosts: redhat
  tasks:
    - name: Check yum package
      ansible.builtin.package:
        name: nginx
        state: present
      check_mode: true
```

## Systemd Container Requirements

For containers running systemd:

```yaml
platforms:
  - name: ubuntu-systemd
    image: geerlingguy/docker-ubuntu2204-ansible:latest
    pre_build_image: true
    privileged: true
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:rw
    cgroupns_mode: host
    command: ""
```

## Single Platform Anti-Pattern

**Problem**: Only testing on one platform when role supports multiple

```yaml
# BAD - Role supports Debian and RedHat but only tests Ubuntu
platforms:
  - name: ubuntu
    image: geerlingguy/docker-ubuntu2204-ansible:latest
```

**Solution**: Test all supported platforms

```yaml
# GOOD - Tests both OS families
platforms:
  - name: ubuntu-22
    image: geerlingguy/docker-ubuntu2204-ansible:latest
    groups: [debian]

  - name: rocky-9
    image: geerlingguy/docker-rockylinux9-ansible:latest
    groups: [redhat]
```
