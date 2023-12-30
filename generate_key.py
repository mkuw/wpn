#!/usr/bin/python

from lib.utils import generate_secret_key, save_secret_key

if __name__ == "__main__":
    KEY = generate_secret_key()
    save_secret_key(KEY)
