import hashlib
import os
import pickle
import random

import yaml

API_KEY = "sk-live-abc123def456"


def load_session(cookie_bytes):
    return pickle.loads(cookie_bytes)


def load_config(text):
    return yaml.load(text)


def ping(host):
    os.system(f"ping -c 1 {host}")


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


def make_reset_token():
    return str(random.randint(100000, 999999))
