---
name: python-security-guide
description: "Security guide for Python — static-analysis tooling, common vulnerabilities, insecure deserialization, web framework security, cryptography, supply-chain risk, secrets management, and a security checklist. Use when security-auditing or hardening Python code. Also loaded by the python-security-injection and python-security-resources agents as their knowledge base."
---
# Python Security: Comprehensive Guide to Identifying and Patching Vulnerabilities

## Table of Contents

1. [Introduction](#introduction)
2. [Security Tools and Analysis](#security-tools-and-analysis)
3. [Common Vulnerabilities](#common-vulnerabilities)
4. [Insecure Deserialization](#insecure-deserialization)
5. [Web Framework Security](#web-framework-security)
6. [Cryptography Best Practices](#cryptography-best-practices)
7. [Dependency Security and Supply Chain](#dependency-security-and-supply-chain)
8. [Secrets Management](#secrets-management)
9. [Security Checklist](#security-checklist)

---

## Introduction

Python is one of the most widely used programming languages, powering web applications, data pipelines, APIs, and automation scripts. Despite Python's readability and productivity benefits, security vulnerabilities can arise from misuse of standard library functions, insecure third-party dependencies, or unsafe coding patterns.

### Key Security Principles

- Never trust user-controlled input — validate and sanitize at every boundary
- Avoid dangerous built-ins: `eval`, `exec`, `pickle`, `yaml.load` with untrusted data
- Use the `secrets` module for security-sensitive random values, never `random`
- Keep dependencies pinned and audited (requirements.txt with hashes, pip-audit, safety)
- Prefer parameterized queries over string interpolation in SQL
- Run `bandit` and `pip-audit` as part of CI/CD

---

## Security Tools and Analysis

### 1. Bandit - Static Security Analysis

**Bandit** is the standard static analysis tool for Python security. It parses AST nodes and matches them against known-insecure patterns, assigning severity and confidence levels.

**Installation:**

```bash
pip install bandit
```

**Usage:**

```bash
# Scan all Python files recursively
bandit -r . -f txt

# Output as JSON
bandit -r . -f json -o bandit-report.json

# Target specific vulnerability IDs
bandit -r . -t B301,B302,B303

# Exclude test directories
bandit -r . --exclude ./tests,./venv
```

**Key Test IDs:**

- B101: `assert` used as security control
- B102: `exec` usage
- B103: Setting permissive file permissions
- B104: Binding to all interfaces (0.0.0.0)
- B105/B106/B107: Hardcoded passwords
- B201: Flask debug=True
- B301/B302: Pickle/marshal deserialization
- B303/B304: MD5/SHA1 for security use
- B305: Cipher feedback mode
- B307: `eval` usage
- B320: XML lxml library usage
- B324: Use of hashlib with insecure algorithm
- B501/B502: SSL/TLS misconfigurations
- B601/B602: Shell injection via subprocess
- B608: Hardcoded SQL expressions
- B701: Jinja2 autoescape disabled
- B702: Use of Mako templates

**Resources:**

- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Bandit GitHub Repository](https://github.com/PyCQA/bandit)

### 2. pip-audit - Dependency Vulnerability Scanning

**pip-audit** scans installed packages against the PyPA Advisory Database and OSV database.

**Installation:**

```bash
pip install pip-audit
```

**Usage:**

```bash
# Audit current environment
pip-audit

# Audit a requirements file
pip-audit -r requirements.txt

# Output as JSON
pip-audit -r requirements.txt -f json -o audit.json

# Fix automatically where possible
pip-audit --fix
```

**Resources:**

- [pip-audit GitHub Repository](https://github.com/pypa/pip-audit)

### 3. Safety - Dependency Vulnerability Database

**Safety** checks Python dependencies against a curated database of known vulnerabilities.

**Installation:**

```bash
pip install safety
```

**Usage:**

```bash
# Check installed packages
safety check

# Check a requirements file
safety check -r requirements.txt

# Output as JSON
safety check --json
```

### 4. Semgrep - Advanced SAST

**Semgrep** provides pattern-based static analysis with community-maintained Python security rules.

**Installation:**

```bash
pip install semgrep
```

**Usage:**

```bash
# Use the Python security ruleset
semgrep --config=p/python-security .

# Use OWASP Top 10 rules
semgrep --config=p/owasp-top-ten .

# Run all community security rules
semgrep --config=p/r2c-security-audit .
```

**Resources:**

- [Semgrep Python Rules](https://semgrep.dev/p/python-security)

### 5. mypy - Type Checking for Security

Strong typing can prevent entire categories of security bugs related to type confusion.

```bash
pip install mypy
mypy --strict src/
```

---

## Common Vulnerabilities

### 1. Injection Attacks

#### SQL Injection

**Vulnerability:**
String interpolation or f-strings used to construct SQL queries allow attackers to manipulate query structure and execute arbitrary SQL.

**Vulnerable Code:**

```python
# NEVER DO THIS
def get_user(db, username):
    query = f"SELECT * FROM users WHERE username='{username}'"
    db.execute(query)

# OR THIS
query = "SELECT * FROM users WHERE username='" + username + "'"
db.execute(query)

# OR THIS
query = "SELECT * FROM users WHERE username='%s'" % username
db.execute(query)
```

**Secure Code:**

```python
# Use parameterized queries (DB-API 2.0 standard)
def get_user(db, username):
    query = "SELECT * FROM users WHERE username = %s"
    db.execute(query, (username,))

# SQLite uses ? placeholders
db.execute("SELECT * FROM users WHERE username = ?", (username,))

# SQLAlchemy ORM (preferred for complex apps)
from sqlalchemy import select
stmt = select(User).where(User.username == username)
result = session.execute(stmt)

# SQLAlchemy text() with bound parameters
from sqlalchemy import text
stmt = text("SELECT * FROM users WHERE username = :name")
result = db.execute(stmt, {"name": username})
```

**Detection:** `bandit -t B608`

**Resources:**

- [Python SQL Injection Prevention](https://realpython.com/prevent-python-sql-injection/)
- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)

#### Command Injection

**Vulnerability:**
User-controlled input passed to shell commands allows arbitrary command execution.

**Vulnerable Code:**

```python
import os
import subprocess

# NEVER DO THIS
def run_ping(host):
    os.system(f"ping -c 4 {host}")

# OR THIS
def run_ping(host):
    subprocess.call(f"ping -c 4 {host}", shell=True)

# OR THIS
def run_command(cmd):
    os.popen(cmd)
```

**Secure Code:**

```python
import subprocess
import shlex

# Pass arguments as a list, never use shell=True with user input
def run_ping(host):
    # Validate input first
    import re
    if not re.match(r'^[a-zA-Z0-9.\-]+$', host):
        raise ValueError("Invalid hostname")
    subprocess.run(["ping", "-c", "4", host], check=True, capture_output=True)

# If shell=True is absolutely required, use shlex.quote
def run_safe(user_input):
    safe_input = shlex.quote(user_input)
    subprocess.run(f"echo {safe_input}", shell=True, check=True)
```

**Detection:** `bandit -t B601,B602,B605,B606,B607`

#### Server-Side Template Injection (SSTI)

**Vulnerability:**
User input rendered directly in templates allows template engine code execution.

**Vulnerable Code:**

```python
from jinja2 import Environment

# NEVER render user input as a template string
def render_greeting(name):
    env = Environment()
    template = env.from_string(f"Hello {name}!")  # SSTI if name contains {{ }}
    return template.render()

# OR in Flask
@app.route('/greet')
def greet():
    name = request.args.get('name')
    return render_template_string(f"<h1>Hello {name}</h1>")  # SSTI vulnerable
```

**Secure Code:**

```python
from jinja2 import Environment, select_autoescape

# Pass data as variables, never as part of the template string
def render_greeting(name):
    env = Environment(autoescape=select_autoescape(['html', 'xml']))
    template = env.from_string("Hello {{ name }}!")
    return template.render(name=name)  # name is safely passed as a variable

# In Flask, use render_template with a file, not render_template_string with user data
@app.route('/greet')
def greet():
    name = request.args.get('name', '')
    return render_template('greet.html', name=name)
```

**Detection:** `semgrep --config=p/python-security` (rule: python.flask.security.injection.tainted-template-string)

### 2. Cross-Site Scripting (XSS)

**Vulnerability:**
User content rendered in HTML responses without escaping allows script injection.

**Vulnerable Code:**

```python
# Flask - bypassing autoescaping
from flask import Markup

@app.route('/user')
def show_user():
    name = request.args.get('name')
    return Markup(f"<p>Hello {name}</p>")  # XSS - Markup disables escaping

# Django - marking unsafe content as safe
from django.utils.safestring import mark_safe

def view(request):
    name = request.GET.get('name')
    return HttpResponse(mark_safe(f"<p>{name}</p>"))  # XSS

# Jinja2 - autoescape disabled
env = Environment(autoescape=False)
```

**Secure Code:**

```python
# Flask - use Jinja2 escaping (default in render_template)
from markupsafe import escape

@app.route('/user')
def show_user():
    name = request.args.get('name', '')
    safe_name = escape(name)  # Explicitly escape
    return f"<p>Hello {safe_name}</p>"

# Or use templates (autoescape is on by default in Flask)
@app.route('/user')
def show_user():
    name = request.args.get('name', '')
    return render_template('user.html', name=name)  # Jinja2 auto-escapes

# Django - templates auto-escape by default, never use mark_safe on user data
def view(request):
    name = request.GET.get('name', '')
    return render(request, 'user.html', {'name': name})
```

### 3. Path Traversal

**Vulnerability:**
User-controlled filenames used in file operations allow reading/writing arbitrary files.

**Vulnerable Code:**

```python
import os

def read_user_file(filename):
    # Vulnerable: filename can be "../../etc/passwd"
    path = "/var/www/uploads/" + filename
    with open(path) as f:
        return f.read()

# Flask send_file without validation
@app.route('/download')
def download():
    filename = request.args.get('file')
    return send_file(f"/uploads/{filename}")  # Path traversal
```

**Secure Code:**

```python
import os
from pathlib import Path

BASE_DIR = Path("/var/www/uploads").resolve()

def read_user_file(filename):
    # Resolve the full path and verify it's within the base directory
    requested = (BASE_DIR / filename).resolve()

    # Check that resolved path starts with base directory
    if not str(requested).startswith(str(BASE_DIR) + os.sep):
        raise PermissionError("Access denied: path traversal detected")

    with open(requested) as f:
        return f.read()

# Flask - use send_from_directory for safe file serving
from flask import send_from_directory

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory("/uploads", filename)  # Flask validates the path
```

**Detection:** `bandit -t B102` and manual review

---

## Insecure Deserialization

This is one of Python's most dangerous vulnerability classes. Several built-in modules can execute arbitrary code during deserialization of untrusted data.

### pickle / cPickle

**Vulnerability:**
`pickle.loads()` executes arbitrary Python bytecode. Never deserialize untrusted pickle data.

**Vulnerable Code:**

```python
import pickle

# NEVER deserialize data from untrusted sources
def load_session(data):
    return pickle.loads(data)  # RCE if data is attacker-controlled

# Cookie-based pickle deserialization
@app.route('/load')
def load():
    session_data = request.cookies.get('session')
    import base64
    obj = pickle.loads(base64.b64decode(session_data))  # Critical RCE
```

**Secure Code:**

```python
import json

# Use JSON for simple data structures
def load_session(data):
    return json.loads(data)

# For complex objects, use safe serialization libraries
import marshmallow

class UserSchema(marshmallow.Schema):
    id = marshmallow.fields.Int()
    name = marshmallow.fields.Str()

schema = UserSchema()
user = schema.loads(json_data)

# If pickle is absolutely required (internal use only, never from external input):
import base64
import hmac
import hashlib
import os
import pickle

SECRET = os.environ['PICKLE_HMAC_SECRET'].encode()

def safe_dumps(obj):
    data = pickle.dumps(obj)
    sig = hmac.new(SECRET, data, hashlib.sha256).hexdigest()
    return sig + ":" + base64.b64encode(data).decode()

def safe_loads(payload):
    sig, _, encoded = payload.partition(":")
    data = base64.b64decode(encoded)
    expected = hmac.new(SECRET, data, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        raise ValueError("Invalid signature")
    return pickle.loads(data)
```

**Detection:** `bandit -t B301,B302`

### yaml.load()

**Vulnerability:**
`yaml.load()` without an explicit Loader can deserialize Python objects and execute code.

**Vulnerable Code:**

```python
import yaml

# NEVER use yaml.load() without SafeLoader
config = yaml.load(user_input)           # Dangerous
config = yaml.load(user_input, Loader=yaml.FullLoader)  # Still unsafe: allows !!python/object/apply: RCE in PyYAML < 5.2
config = yaml.load(user_input, Loader=yaml.UnsafeLoader)  # Explicitly dangerous
```

**Secure Code:**

```python
import yaml

# Always use SafeLoader for untrusted input
config = yaml.safe_load(user_input)

# Or explicitly specify SafeLoader
config = yaml.load(user_input, Loader=yaml.SafeLoader)

# For structured config, use pydantic or marshmallow after safe_load
from pydantic import BaseModel

class Config(BaseModel):
    host: str
    port: int

raw = yaml.safe_load(config_text)
config = Config(**raw)
```

**Detection:** `bandit -t B506`

### eval() and exec()

**Vulnerability:**
`eval()` and `exec()` with user input execute arbitrary Python code.

**Vulnerable Code:**

```python
# NEVER use eval/exec with user-controlled input
def calculate(expression):
    return eval(expression)  # RCE: expression can be "__import__('os').system('rm -rf /')"

def run_script(code):
    exec(code)  # Critical RCE
```

**Secure Code:**

```python
import ast
import operator

# For safe math expressions, use ast.literal_eval or a safe parser
def calculate(expression):
    # ast.literal_eval only handles literals, not expressions
    # For math, use a proper expression parser
    try:
        tree = ast.parse(expression, mode='eval')
        return SafeEvalVisitor().visit(tree)
    except Exception:
        raise ValueError("Invalid expression")

# Even better: use a math library
import numexpr
result = numexpr.evaluate(expression)  # Restricted to numeric expressions

# For configuration, use ast.literal_eval for Python literals
config = ast.literal_eval(config_string)  # Only parses strings, bytes, numbers, tuples, lists, dicts, sets, booleans, None
```

**Detection:** `bandit -t B307`

---

## Web Framework Security

### Django

**Common Issues:**

```python
# settings.py - NEVER do this in production
DEBUG = True                          # Exposes stack traces and config
SECRET_KEY = "hardcoded-secret-key"  # Rotate immediately if leaked
ALLOWED_HOSTS = ['*']                 # Allows host header injection
CSRF_COOKIE_SECURE = False            # Cookie sent over HTTP
SESSION_COOKIE_SECURE = False         # Session cookie sent over HTTP
```

**Secure Django Settings:**

```python
import os
from pathlib import Path

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']  # Load from environment
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ['DJANGO_ALLOWED_HOSTS'].split(',')

# Security headers
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

**CSRF Protection:**

```python
# Django CSRF is enabled by default via middleware
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',  # Must be present
    ...
]

# Vulnerable: exempt a view from CSRF (only do this for APIs with token auth)
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Only if using stateless token authentication
def api_endpoint(request):
    ...
```

### Flask

**Vulnerable Flask App:**

```python
from flask import Flask
app = Flask(__name__)
app.secret_key = "dev"  # Hardcoded, weak secret key
app.debug = True         # Never in production
```

**Secure Flask App:**

```python
import os
from flask import Flask
from flask_talisman import Talisman

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

# Add security headers
csp = {
    'default-src': "'self'",
    'script-src': "'self'",
}
Talisman(app, content_security_policy=csp, force_https=True)

# Never enable debug in production
if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')
```

### FastAPI

**Vulnerable FastAPI:**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Overly permissive CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allows any origin
    allow_credentials=True,     # Sends cookies cross-origin
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Secure FastAPI:**

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()

# Restrict CORS to known origins
ALLOWED_ORIGINS = os.environ['ALLOWED_ORIGINS'].split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not validate_jwt(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return token

@app.get("/protected")
async def protected_route(token: str = Depends(verify_token)):
    return {"message": "authenticated"}
```

---

## Cryptography Best Practices

### Password Hashing

**Vulnerable Code:**

```python
import hashlib

# NEVER use these for passwords
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()      # Weak, no salt

def hash_password(password):
    return hashlib.sha1(password.encode()).hexdigest()     # Weak, no salt

def hash_password(password):
    salt = "static_salt"
    return hashlib.sha256((salt + password).encode()).hexdigest()  # Static salt, not a KDF
```

**Secure Code:**

```python
import bcrypt
import os

# bcrypt (recommended for passwords)
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

# argon2-cffi (OWASP recommended since 2023)
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(time_cost=2, memory_cost=65536, parallelism=2)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, password)
    except VerifyMismatchError:
        return False

# scrypt via hashlib (built-in since Python 3.6)
import hashlib, os

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    hashed = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
    return salt.hex() + ":" + hashed.hex()
```

### Secure Random Numbers

**Vulnerable Code:**

```python
import random

# NEVER use random for security-sensitive values
token = random.randint(100000, 999999)         # Predictable
token = str(random.random())                   # Predictable
session_id = ''.join(random.choices('abcdef', k=32))  # Predictable
```

**Secure Code:**

```python
import secrets

# Use secrets for all security-sensitive random values
token = secrets.token_hex(32)                  # 64-char hex string
token = secrets.token_urlsafe(32)              # URL-safe base64
otp = secrets.randbelow(900000) + 100000       # 6-digit OTP

# Secure comparison (timing-safe)
if secrets.compare_digest(user_token, expected_token):
    # authenticated
    pass
```

### Encryption

**Vulnerable Code:**

```python
from Crypto.Cipher import AES

# NEVER use ECB mode (no IV, patterns visible)
key = b"hardcoded_key_16"  # Hardcoded key
cipher = AES.new(key, AES.MODE_ECB)
ciphertext = cipher.encrypt(plaintext)
```

**Secure Code:**

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# Option 1: Fernet (symmetric, authenticated encryption - recommended for most use cases)
key = Fernet.generate_key()  # Store this securely
fernet = Fernet(key)
ciphertext = fernet.encrypt(plaintext.encode())
plaintext = fernet.decrypt(ciphertext).decode()

# Option 2: AES-GCM (for fine-grained control)
key = os.urandom(32)  # 256-bit key, generated fresh
nonce = os.urandom(12)  # 96-bit nonce, never reuse with same key
aesgcm = AESGCM(key)
ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
plaintext = aesgcm.decrypt(nonce, ciphertext, None)
```

### TLS / SSL

**Vulnerable Code:**

```python
import requests, ssl

# NEVER disable certificate verification
response = requests.get(url, verify=False)

# NEVER use deprecated SSL versions
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Deprecated, insecure

# NEVER skip hostname verification
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
```

**Secure Code:**

```python
import requests, ssl, certifi

# Always verify certificates (default in requests)
response = requests.get(url)  # verify=True is the default

# Specify cert bundle explicitly if needed
response = requests.get(url, verify=certifi.where())

# For httpx
import httpx
response = httpx.get(url)  # verify=True is the default

# Secure SSL context
context = ssl.create_default_context()
context.minimum_version = ssl.TLSVersion.TLSv1_2
context.verify_mode = ssl.CERT_REQUIRED
context.check_hostname = True
```

---

## Dependency Security and Supply Chain

### Pinning Dependencies

**Vulnerable:**

```
# requirements.txt - unpinned, vulnerable to supply chain attacks
requests
flask
django
```

**Secure:**

```
# requirements.txt - pinned with hashes
requests==2.31.0 \
    --hash=sha256:58cd2187423839a1b5cb... \
    --hash=sha256:942c5a758f98d790eae...
flask==3.0.0 \
    --hash=sha256:...
```

**Generate hashes:**

```bash
pip-compile --generate-hashes requirements.in > requirements.txt
```

### Auditing Dependencies

```bash
# Check for known vulnerabilities
pip-audit -r requirements.txt

# Safety database check
safety check -r requirements.txt

# OSV Scanner
osv-scanner -r requirements.txt

# GitHub Dependabot (add .github/dependabot.yml)
```

### Supply Chain Attack Prevention

```python
# pyproject.toml - use trusted indexes only
[tool.pip]
index-url = "https://pypi.org/simple/"
trusted-host = "pypi.org"

# Avoid --extra-index-url without checking package priority
# Dependency confusion attacks exploit extra index URLs
```

---

## Secrets Management

### Vulnerable Patterns

```python
# NEVER hardcode secrets
API_KEY = "sk-abc123secret"
DB_PASSWORD = "SuperSecret123!"
JWT_SECRET = "my-jwt-secret"

# NEVER commit .env files with real secrets
# NEVER log secrets
import logging
logging.info(f"Connecting with password: {db_password}")

# NEVER pass secrets as command-line arguments
subprocess.run(["curl", "-H", f"Authorization: Bearer {token}", url])
```

### Secure Secrets Handling

```python
import os
from typing import Optional

# Load from environment variables
def get_secret(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(f"Required secret '{key}' not set in environment")
    return value

API_KEY = get_secret('API_KEY')
DB_PASSWORD = get_secret('DB_PASSWORD')

# Use python-dotenv for local development only (never commit .env to git)
from dotenv import load_dotenv
load_dotenv()  # Loads .env file if present, safe to call

# For production: use a secrets manager
# AWS Secrets Manager
import boto3
client = boto3.client('secretsmanager', region_name='us-east-1')
secret = client.get_secret_value(SecretId='my-app/db-password')['SecretString']

# HashiCorp Vault
import hvac
client = hvac.Client(url='https://vault.example.com', token=os.environ['VAULT_TOKEN'])
secret = client.secrets.kv.v2.read_secret_version(path='my-app/db')['data']['data']['password']
```

### Protecting Secrets in Logs

```python
import logging
import re

class SensitiveDataFilter(logging.Filter):
    PATTERNS = [
        (re.compile(r'password=\S+', re.I), 'password=***'),
        (re.compile(r'token=\S+', re.I), 'token=***'),
        (re.compile(r'Authorization:\s*Bearer\s+\S+', re.I), 'Authorization: Bearer ***'),
        (re.compile(r'"password"\s*:\s*"[^"]*"', re.I), '"password": "***"'),
    ]

    def filter(self, record):
        for pattern, replacement in self.PATTERNS:
            record.msg = pattern.sub(replacement, str(record.msg))
        return True

logging.getLogger().addFilter(SensitiveDataFilter())
```

---

## Security Checklist

### General Security

- [ ] No use of `eval()` or `exec()` with user-controlled input
- [ ] No use of `pickle`, `marshal`, or `shelve` for untrusted data
- [ ] `yaml.safe_load()` used instead of `yaml.load()`
- [ ] Debug mode disabled in production
- [ ] Error messages do not expose internal details

### Input Validation

- [ ] All SQL queries use parameterized statements
- [ ] `subprocess` calls never use `shell=True` with user input
- [ ] File paths validated against base directory before access
- [ ] User input validated with Pydantic, marshmallow, or cerberus
- [ ] URL inputs validated before making outbound requests (SSRF prevention)

### Authentication and Session Management

- [ ] Passwords hashed with bcrypt, argon2, or scrypt
- [ ] Session tokens generated with `secrets` module
- [ ] Session cookies have `Secure`, `HttpOnly`, and `SameSite` flags
- [ ] CSRF protection enabled for state-changing endpoints
- [ ] Authentication required on all protected routes

### Cryptography

- [ ] No MD5 or SHA-1 for security purposes
- [ ] `secrets` module used for all security-sensitive random values
- [ ] TLS certificate verification enabled (no `verify=False`)
- [ ] AES-GCM or Fernet used for symmetric encryption
- [ ] Keys generated fresh, never hardcoded

### Web Framework

- [ ] Django: `DEBUG=False`, `SECRET_KEY` from env, `ALLOWED_HOSTS` set
- [ ] Flask: `SECRET_KEY` from env, `SESSION_COOKIE_SECURE=True`
- [ ] FastAPI: CORS restricted to known origins, authentication dependencies used
- [ ] Security headers set (CSP, HSTS, X-Frame-Options, X-Content-Type-Options)

### Dependencies

- [ ] Dependencies pinned with hashes in requirements.txt
- [ ] `pip-audit` or `safety` run in CI/CD
- [ ] `bandit` scan in CI/CD pipeline
- [ ] No packages installed from untrusted indexes

### Secrets Management

- [ ] No hardcoded credentials, API keys, or tokens in source code
- [ ] Secrets loaded from environment variables or secrets manager
- [ ] `.env` files listed in `.gitignore`
- [ ] Secrets not logged or exposed in error messages
- [ ] Secret scanning enabled on repository (GitHub secret scanning, trufflehog)

---

## Additional Resources

- [Python Security Best Practices](https://python.org/dev/security/)
- [OWASP Python Security Project](https://owasp.org/www-project-python-security/)
- [Bandit Rules Reference](https://bandit.readthedocs.io/en/latest/plugins/index.html)
- [Python Cryptography Library](https://cryptography.io/)
- [OWASP Top 10](https://owasp.org/Top10/)
- [PyPA Advisory Database](https://github.com/pypa/advisory-database)
- [CWE Top 25 Most Dangerous Software Weaknesses](https://cwe.mitre.org/top25/)
