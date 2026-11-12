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

    # -------------------------------------------------------------------------
    # Phase 6 Stage 2: Forensic Intelligence Helpers
    # Distinguishes derived analytical results from original evidence & detections
    # -------------------------------------------------------------------------
    def get_forensic_explanations(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Derives or retrieves grounded forensic explanations for all media in the case.
        Handles missing or malformed analytical data safely without modifying original evidence.
        """
        if not isinstance(case_data, dict):
            return {"status": "UNAVAILABLE", "reason": "Invalid case_data provided."}

        # Check if already computed in derived container
        if "derived_intelligence" in case_data and "explanations" in case_data["derived_intelligence"]:
            return case_data["derived_intelligence"]["explanations"]

        from src.modules.forensic_explainer import ForensicExplainer
        explainer = ForensicExplainer.get_instance()
        ind = case_data.get("individual_results", {})

        explanations = {
            "images": [explainer.explain_image_finding(im) for im in ind.get("images", []) if isinstance(im, dict)],
            "videos": [explainer.explain_video_finding(vd) for vd in ind.get("videos", []) if isinstance(vd, dict)],
            "audios": [explainer.explain_audio_finding(ad) for ad in ind.get("audios", []) if isinstance(ad, dict)],
        }
        return explanations

    def get_evidence_comparisons(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Derives or retrieves deterministic evidence comparisons, temporal video scores,
        separated audio metrics, and verified lineage mapping.
        Preserves strict Phase 5.3 provenance validation rules.
        """
        if not isinstance(case_data, dict):
            return {"status": "UNAVAILABLE", "reason": "Invalid case_data provided."}

        if "derived_intelligence" in case_data and "comparisons" in case_data["derived_intelligence"]:
            return case_data["derived_intelligence"]["comparisons"]

        from src.modules.evidence_comparator import EvidenceComparator
        comparator = EvidenceComparator.get_instance()

        inventory = case_data.get("evidence_inventory", [])
        lineage = comparator.establish_verified_lineage(inventory)

        # Video temporal score statistics across actual sampled frames
        ind = case_data.get("individual_results", {})
        video_temporal_stats = []
        for vd in ind.get("videos", []):
            if isinstance(vd, dict):
                frames = vd.get("frame_results", [])
                stats = comparator.analyze_video_temporal_scores(frames)
                stats["filename"] = vd.get("filename", "video")
                video_temporal_stats.append(stats)

        # Separated audio comparisons
        audios = ind.get("audios", [])
        audio_comparisons = []
        for i in range(len(audios)):
            for j in range(i + 1, len(audios)):
                if isinstance(audios[i], dict) and isinstance(audios[j], dict):
                    comp = comparator.compare_audio_streams(audios[i], audios[j])
                    comp["pair"] = f"{audios[i].get('filename')} ↔ {audios[j].get('filename')}"
                    audio_comparisons.append(comp)

        return {
            "verified_lineage": lineage,
            "video_temporal_statistics": video_temporal_stats,
            "audio_comparisons": audio_comparisons,
        }

    def get_timeline_analytics(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Derives or retrieves chronological audit timeline analytics.
        Preserves original ledger sequence, validates hash chain, and flags timestamp anomalies.
        """
        if not isinstance(case_data, dict):
            return {"status": "UNAVAILABLE", "reason": "Invalid case_data provided."}

        if "derived_intelligence" in case_data and "timeline" in case_data["derived_intelligence"]:
            return case_data["derived_intelligence"]["timeline"]

        from src.modules.timeline_analytics import TimelineAnalytics
        analytics = TimelineAnalytics.get_instance()
        return analytics.build_chronological_timeline(case_data)

    def attach_derived_intelligence(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attaches derived Phase 6 analytical intelligence into a segregated container
        without altering original evidence inventory, raw detector findings, or audit entries.
        """
        if not isinstance(case_data, dict):
            return case_data

        case_data["derived_intelligence"] = {
            "explanations": self.get_forensic_explanations(case_data),
            "comparisons": self.get_evidence_comparisons(case_data),
            "timeline": self.get_timeline_analytics(case_data),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        }
        return case_data

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

    def log_evidence_ingested(self, case_data: Dict[str, Any], filename: str, modality: str, file_size: str, evidence_id: Optional[str] = None) -> Dict[str, Any]:
        """Logs evidence ingestion event in the audit trail."""
        return self.add_audit_entry(
            case_data=case_data,
            action="EVIDENCE_INGESTED",
            details=f"Evidence ingested into case custody: {filename} ({modality}, {file_size})",
            evidence_id=evidence_id or filename
        )

    def log_evidence_hashed(self, case_data: Dict[str, Any], filename: str, sha256_hash: str, evidence_id: Optional[str] = None) -> Dict[str, Any]:
        """Logs evidence cryptographic SHA-256 fingerprinting event."""
        return self.add_audit_entry(
            case_data=case_data,
            action="EVIDENCE_HASHED",
            details=f"SHA-256 digest computed for {filename}: {sha256_hash}",
            evidence_id=evidence_id or filename
        )

    def log_analysis_executed(self, case_data: Dict[str, Any], modality: str, filename: str, model_name: str, evidence_id: Optional[str] = None) -> Dict[str, Any]:
        """Logs inference analysis execution event for a specific evidence item."""
        return self.add_audit_entry(
            case_data=case_data,
            action="ANALYSIS_EXECUTED",
            details=f"Neural analysis executed on {filename} ({modality}) using {model_name}",
            evidence_id=evidence_id or filename
        )

    def log_report_generated(self, case_data: Dict[str, Any], report_filename: str, report_sha256: str) -> Dict[str, Any]:
        """Logs report generation event with detached manifest digest."""
        return self.add_audit_entry(
            case_data=case_data,
            action="REPORT_GENERATED",
            details=f"Forensic PDF report {report_filename} generated (Manifest SHA-256: {report_sha256})"
        )

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

