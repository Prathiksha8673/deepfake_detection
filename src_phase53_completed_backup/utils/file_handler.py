import hashlib
import time
from typing import Dict, Any
import pandas as pd

def compute_file_hashes(file_bytes: bytes) -> Dict[str, str]:
    """Compute cryptographic hashes for forensic integrity validation."""
    return {
        "MD5": hashlib.md5(file_bytes).hexdigest(),
        "SHA-1": hashlib.sha1(file_bytes).hexdigest(),
        "SHA-256": hashlib.sha256(file_bytes).hexdigest(),
    }

def format_file_size(size_bytes: int) -> str:
    """Format bytes into human-readable size string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def extract_forensic_metadata(uploaded_file) -> Dict[str, Any]:
    """Extract standard file metadata for chain-of-custody logging."""
    file_bytes = uploaded_file.getvalue()
    hashes = compute_file_hashes(file_bytes)
    return {
        "Filename": uploaded_file.name,
        "File Type": uploaded_file.type or "Unknown / Binary",
        "File Size": format_file_size(len(file_bytes)),
        "Raw Size (Bytes)": len(file_bytes),
        "Ingestion Timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "MD5 Hash": hashes["MD5"],
        "SHA-1 Hash": hashes["SHA-1"],
        "SHA-256 Hash": hashes["SHA-256"],
        "Custody Status": "Cryptographically Sealed & Ingested",
    }
