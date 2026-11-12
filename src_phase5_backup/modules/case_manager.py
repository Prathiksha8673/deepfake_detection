"""
DEEPFAKE X - Case & Investigation Management Engine
Provides persistent storage, lifecycle management, and metadata cataloging
for multimodal digital forensics investigations.
Zero-fabrication ISO/IEC 27037 compliant audit logging.
"""

import os
import json
import time
import uuid
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("deepfakex.case_manager")

CASES_DIR = "reports/investigations"
SECURE_VAULT_DIR = "reports/vault"

class CaseManager:
    _instance: Optional["CaseManager"] = None

    @classmethod
    def get_instance(cls) -> "CaseManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def compute_sha256(raw_bytes: bytes) -> str:
        import hashlib
        return hashlib.sha256(raw_bytes).hexdigest()

    def __init__(self):
        os.makedirs(CASES_DIR, exist_ok=True)
        os.makedirs(SECURE_VAULT_DIR, exist_ok=True)

    def create_case(
        self,
        title: str,
        investigator: str = "Lead Forensic Analyst",
        notes: str = ""
    ) -> Dict[str, Any]:
        """Create a new forensic investigation case container."""
        inv_id = f"DFX-{int(time.time())}-{str(uuid.uuid4())[:6].upper()}"
        case_data = {
            "investigation_id": inv_id,
            "title": title or f"Investigation {inv_id}",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "investigator": investigator,
            "status": "OPEN",
            "notes": notes,
            "evidence_inventory": [],
            "individual_results": {
                "images": [],
                "videos": [],
                "audios": []
            },
            "correlation_analysis": None,
            "reliability_assessment": None,
            "audit_trail": [
                {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                    "action": "CASE_INITIALIZED",
                    "details": f"Investigation {inv_id} created by {investigator}"
                }
            ]
        }
        self.save_case(case_data)
        return case_data

    def get_case_path(self, investigation_id: str) -> str:
        safe_id = "".join(c for c in investigation_id if c.isalnum() or c in "-_")
        return os.path.join(CASES_DIR, f"{safe_id}.json")

    def save_case(self, case_data: Dict[str, Any]) -> bool:
        inv_id = case_data.get("investigation_id")
        if not inv_id:
            return False
        case_data["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        path = self.get_case_path(inv_id)
        
        # Clean non-serializable objects (such as PIL Image thumbnails in video frame results)
        clean_copy = json.loads(json.dumps(case_data, default=lambda o: str(o) if not hasattr(o, '__dict__') else o.__dict__))
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(clean_copy, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to persist case {inv_id}: {e}")
            return False

    def load_case(self, investigation_id: str) -> Optional[Dict[str, Any]]:
        path = self.get_case_path(investigation_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load case {investigation_id}: {e}")
            return None

    def list_cases(self) -> List[Dict[str, Any]]:
        """List summary catalog of all registered forensic cases."""
        cases = []
        if not os.path.exists(CASES_DIR):
            return cases
        for filename in sorted(os.listdir(CASES_DIR), reverse=True):
            if filename.endswith(".json"):
                full_path = os.path.join(CASES_DIR, filename)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        cases.append({
                            "investigation_id": data.get("investigation_id"),
                            "title": data.get("title"),
                            "created_at": data.get("created_at"),
                            "status": data.get("status", "OPEN"),
                            "investigator": data.get("investigator"),
                            "evidence_count": len(data.get("evidence_inventory", [])),
                            "verdict": data.get("reliability_assessment", {}).get("verdict_category", "Pending Analysis")
                        })
                except Exception as ex:
                    logger.warning(f"Corrupt case file {filename}: {ex}")
        return cases

    def store_evidence_file(self, raw_bytes: bytes, filename: str, sha256_hash: str) -> str:
        """Store original evidence file in an isolated vault separate from analysis runs."""
        safe_hash = "".join(c for c in sha256_hash if c.isalnum())
        _, ext = os.path.splitext(filename.lower())
        vault_name = f"{safe_hash}{ext}"
        vault_path = os.path.join(SECURE_VAULT_DIR, vault_name)
        if not os.path.exists(vault_path):
            with open(vault_path, "wb") as f:
                f.write(raw_bytes)
        return vault_path
