# Error handling

Read when the code uses `block`/`rescue`/`always`, `failed_when`, `changed_when` with real conditions, or `ignore_errors`.

## Block / Rescue / Always

```yaml
- name: Deploy application
  block:
    - name: Download application
      ansible.builtin.get_url:
        url: "{{ app_url }}"
        dest: /tmp/app.tar.gz

    - name: Extract application
      ansible.builtin.unarchive:
        src: /tmp/app.tar.gz
        dest: /opt/app
        remote_src: true

  rescue:
    - name: Log deployment failure
      ansible.builtin.debug:
        msg: "Deployment failed: {{ ansible_failed_task.name }}"

    - name: Rollback to previous version
      ansible.builtin.copy:
        src: /opt/app.backup
        dest: /opt/app
        remote_src: true

  always:
    - name: Clean up temp files
      ansible.builtin.file:
        path: /tmp/app.tar.gz
        state: absent

    - name: Send notification
      ansible.builtin.uri:
        url: "{{ webhook_url }}"
        method: POST
        body: '{"status": "completed"}'
```

## failed_when and changed_when

```yaml
- name: Check if service is running
  ansible.builtin.command: systemctl is-active nginx
  register: nginx_status
  changed_when: false
  failed_when: nginx_status.rc not in [0, 3]

- name: Run migration
  ansible.builtin.command: ./migrate.sh
  register: migration_result
  changed_when: "'Applied' in migration_result.stdout"
  failed_when: migration_result.rc != 0 and 'already up to date' not in migration_result.stdout
```

## ignore_errors (Use Sparingly)

```yaml
# Only use when failure is expected and handled
- name: Check optional service
  ansible.builtin.command: systemctl status optional-service
  register: optional_check
  ignore_errors: true

- name: Configure if available
  ansible.builtin.template:
    src: optional.conf.j2
    dest: /etc/optional/config
  when: optional_check is succeeded
```

Sources: [Ansible Error Handling](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_error_handling.html),
[Ansible Blocks](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_blocks.html)
