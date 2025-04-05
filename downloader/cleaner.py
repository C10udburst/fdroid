import os
import hashlib

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def remove_duplicate_apks(directory):
    seen_hashes = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".apk"):
                file_path = os.path.join(root, file)
                file_hash = calculate_sha256(file_path)
                if file_hash in seen_hashes:
                    os.remove(file_path)
                    print(f"Removed duplicate: {file_path}")
                else:
                    seen_hashes[file_hash] = file_path