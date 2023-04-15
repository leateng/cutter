import bcrypt

password = b"liteng"
# salt = bcrypt.gensalt()
salt = b"123"
hashed = bcrypt.hashpw(bytes(password), salt)

print(f"password={password} salt={salt} hashed={hashed}")
