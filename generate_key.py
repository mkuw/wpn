import secrets

def save_secret_key(secret_key, filename='secret_key.txt'):
    with open(filename, 'w') as file:
        file.write(secret_key)

if __name__ == "__main__":
    save_secret_key(secrets.token_hex(32))
