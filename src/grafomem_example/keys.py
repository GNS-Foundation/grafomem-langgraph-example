import json
import os
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

KEY_FILE = ".grafomem_id.json"

def load_or_create_identity():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            data = json.load(f)
            private_bytes = bytes.fromhex(data["private_key_hex"])
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_bytes)
            public_key = private_key.public_key()
            trusted_keys = {}
            for k, v in data.get("trusted_keys", {}).items():
                trusted_keys[k] = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(v))
            return private_key, public_key, data["key_id"], trusted_keys
            
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    key_id = "local_user_1"
    
    # Return actual key objects
    trusted_keys = {key_id: public_key}
    
    # Serialize for JSON
    trusted_keys_hex = {key_id: public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    ).hex()}
    
    with open(KEY_FILE, "w") as f:
        json.dump({
            "private_key_hex": private_bytes.hex(),
            "key_id": key_id,
            "trusted_keys": trusted_keys_hex
        }, f)
        
    return private_key, public_key, key_id, trusted_keys
