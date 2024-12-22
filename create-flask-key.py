import secrets

key = secrets.token_hex(32)
print(key)

# Use it to create the Flask key!