"""
DEEPFAKE X - Case & Investigation Management Engine
Provides persistent storage, lifecycle management, and metadata cataloging
for multimodal digital forensics investigations.
Structured Forensic Evidence Handling with tamper-evident cryptographic hash chaining.
"""

import os
import json
import time
import uuid
import hashlib
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
        return hashlib.sha256(raw_bytes).hexdigest()

    def __init__(self):
        os.makedirs(CASES_DIR, exist_ok=True)
        os.makedirs(SECURE_VAULT_DIR, exist_ok=True)

    def _compute_audit_entry_hash(
        self,
        prev_hash: str,
        timestamp: str,
        action: str,
        details: str,
        evidence_id: Optional[str] = None
    ) -> str:
        payload = f"{prev_hash}|{timestamp}|{action}|{details}|{evidence_id or ''}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def add_audit_entry(
        self,
        case_data: Dict[str, Any],
        action: str,
        details: str,
        evidence_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Appends a cryptographically hash-chained entry to the case audit trail."""
        if "audit_trail" not in case_data:
            case_data["audit_trail"] = []

        now_ts = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        prev_hash = "GENESIS_ROOT_HASH"
        if case_data["audit_trail"]:
            prev_entry = case_data["audit_trail"][-1]
            prev_hash = prev_entry.get("event_hash", "UNKNOWN_PREV_HASH")

        entry_hash = self._compute_audit_entry_hash(
            prev_hash=prev_hash,
            timestamp=now_ts,
            action=action,
            details=details,
            evidence_id=evidence_id
        )

        entry = {
            "timestamp": now_ts,
            "action": action,
            "details": details,
            "evidence_id": evidence_id,
            "prev_hash": prev_hash,
            "event_hash": entry_hash
        }
        case_data["audit_trail"].append(entry)
        return entry

    def create_case(
        self,
        title: str,
        investigator: str = "Lead Forensic Analyst",
        notes: str = ""
    ) -> Dict[str, Any]:
        """Create a new forensic investigation case container with genesis audit block."""
        inv_id = f"DFX-{int(time.time())}-{str(uuid.uuid4())[:6].upper()}"
        now_ts = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

        case_data = {
            "investigation_id": inv_id,
            "title": title or f"Investigation {inv_id}",
            "created_at": now_ts,
            "updated_at": now_ts,
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
            "audit_trail": []
        }

        # Initialize genesis audit log entry
        self.add_audit_entry(
            case_data=case_data,
            action="CASE_INITIALIZED",
            details=f"Investigation {inv_id} created by {investigator}"
        )

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

    def load_case(self, investigation_id: str, record_reopen: bool = False, investigator: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Loads case and optionally appends a cryptographically verified CASE_REOPENED audit event."""
        path = self.get_case_path(investigation_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                case_data = json.load(f)
            
            if record_reopen:
                user_name = investigator or case_data.get("investigator", "Forensic Analyst")
                self.add_audit_entry(
                    case_data=case_data,
                    action="CASE_REOPENED",
                    details=f"Investigation {investigation_id} reopened for examination by {user_name}"
                )
                self.save_case(case_data)
                
            return case_data
        except Exception as e:
            logger.error(f"Failed to load case {investigation_id}: {e}")
            return None

    def log_report_exported(self, investigation_id: str, report_filename: str) -> bool:
        """Logs report export action in the audit trail."""
        case_data = self.load_case(investigation_id, record_reopen=False)
        if not case_data:
            return False
        self.add_audit_entry(
            case_data=case_data,
            action="REPORT_EXPORTED",
            details=f"Forensic PDF report {report_filename} exported from case archive"
        )
        return self.save_case(case_data)

    def log_evidence_accessed(self, investigation_id: str, evidence_id: str, details: str = "") -> bool:
        """Logs evidence item access event in the audit trail."""
        case_data = self.load_case(investigation_id, record_reopen=False)
        if not case_data:
            return False
        self.add_audit_entry(
            case_data=case_data,
            action="EVIDENCE_ACCESSED",
            details=details or f"Evidence {evidence_id} accessed for inspection",
            evidence_id=evidence_id
        )
        return self.save_case(case_data)

    def verify_audit_trail_integrity(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validates the cryptographic hash chain of the case audit trail."""
        trail = case_data.get("audit_trail", [])
        if not trail:
            return {"valid": True, "count": 0, "message": "No audit entries to verify."}

        prev_hash = "GENESIS_ROOT_HASH"
        for i, entry in enumerate(trail):
            recorded_prev = entry.get("prev_hash")
            recorded_event = entry.get("event_hash")
            ts = entry.get("timestamp", "")
            action = entry.get("action", "")
            details = entry.get("details", "")
            evidence_id = entry.get("evidence_id")

            # Validate chain linkage
            if recorded_prev != prev_hash:
                return {
                    "valid": False,
                    "tampered_index": i,
                    "action": action,
                    "message": f"Hash chain broken at index {i}: recorded prev_hash '{recorded_prev}' != expected '{prev_hash}'"
                }

            # Recalculate event hash
            expected_event_hash = self._compute_audit_entry_hash(
                prev_hash=prev_hash,
                timestamp=ts,
                action=action,
                details=details,
                evidence_id=evidence_id
            )

            if recorded_event != expected_event_hash:
                return {
                    "valid": False,
                    "tampered_index": i,
                    "action": action,
                    "message": f"Tampered audit entry at index {i}: event hash mismatch."
                }

            prev_hash = recorded_event

        return {"valid": True, "count": len(trail), "message": "All audit trail hashes verified intact."}

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

