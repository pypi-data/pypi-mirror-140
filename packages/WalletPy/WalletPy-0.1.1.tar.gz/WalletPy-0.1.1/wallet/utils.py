def calculate_hash(data, hash_function="sha256"):
    from Crypto.Hash import RIPEMD160, SHA256
    from Crypto.Hash import RIPEMD160

    if type(data) == str:
        data = bytearray(data, "utf-8")
    if hash_function == "sha256":
        hash = SHA256.new()
        hash.update(data)
        return hash.hexdigest()
    if hash_function == "ripemd160":
        hash = RIPEMD160.new()
        hash.update(data)
        return hash.hexdigest()