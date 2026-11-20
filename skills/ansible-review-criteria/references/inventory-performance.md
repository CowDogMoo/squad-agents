# Inventory and performance

Read when the change touches inventory layout, group_vars/host_vars organization, fact gathering and caching, SSH pipelining, forks, or play strategy.

## Contents

- Inventory best practices
- Performance

## Inventory Best Practices

### Directory Structure

```
inventory/
├── production/
│   ├── hosts.yml
│   ├── group_vars/
│   │   ├── all.yml
│   │   ├── webservers.yml
│   │   └── databases.yml
│   └── host_vars/
│       └── web01.example.com.yml
└── staging/
    ├── hosts.yml
    ├── group_vars/
    │   └── all.yml
    └── host_vars/
```

### YAML Inventory Format

```yaml
# inventory/production/hosts.yml
all:
  children:
    webservers:
      hosts:
        web01.example.com:
        web02.example.com:
      vars:
        http_port: 80
    databases:
      hosts:
        db01.example.com:
          mysql_port: 3306
```

### Variable Organization

```yaml
# group_vars/all.yml - Common defaults
ntp_servers:
  - 0.pool.ntp.org
  - 1.pool.ntp.org

# group_vars/webservers.yml - Web server specific
nginx_worker_processes: auto
nginx_worker_connections: 1024

# host_vars/web01.example.com.yml - Host specific
nginx_worker_processes: 4  # Override for this host
```

### Best Practices

1. Use version control for inventory
2. Separate environments (production, staging, development)
3. Use dynamic inventory for cloud providers
4. Set common defaults in `group_vars/all.yml`
5. Host vars override group vars

Sources: [Ansible Inventory Guide](https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_inventory.html)

## Performance

### Fact Gathering

```yaml
# Disable if not needed
- hosts: webservers
  gather_facts: false
  tasks:
    - name: Quick task
      ansible.builtin.ping:

# Gather only what you need
- hosts: webservers
  gather_subset:
    - network
    - virtual
```

### Fact Caching

```ini
# ansible.cfg
[defaults]
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 86400
```

### SSH Pipelining

```ini
# ansible.cfg
[ssh_connection]
pipelining = True
```

### Parallelism

```ini
# ansible.cfg
[defaults]
forks = 20  # Default is 5
```

### Strategy

```yaml
# Free strategy - tasks run as fast as possible
- hosts: webservers
  strategy: free
  tasks:
    - name: Independent task
      ansible.builtin.package:
        name: nginx
```

Sources: [Ansible Tuning](https://docs.openstack.org/kolla-ansible/latest/user/ansible-tuning.html),
[Spacelift Best Practices](https://spacelift.io/blog/ansible-best-practices)
