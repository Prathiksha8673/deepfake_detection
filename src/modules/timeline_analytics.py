"""
DEEPFAKE X - Chronological Timeline Analytics Engine (Phase 6)
Parses case audit trails into verified chronological timelines.
Preserves the original audit-ledger sequence indices [0..N].
Validates the cryptographic SHA-256 hash chain prior to rendering.
Detects backwards and identical timestamps without silently reordering events.
Strictly distinguishes cryptographic hash integrity from timestamp accuracy and event veracity.

Pure CPU implementation: does NOT import PyTorch or initialize CUDA.
"""

import time
import datetime
from typing import Dict, Any, List, Optional


class TimelineAnalytics:
    _instance: Optional["TimelineAnalytics"] = None

    @classmethod
    def get_instance(cls) -> "TimelineAnalytics":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def parse_iso_timestamp(ts_str: str) -> Optional[float]:
        """
        Parses ISO/UTC timestamp strings into epoch seconds.
        Handles formats like '%Y-%m-%d %H:%M:%S UTC' and '%Y-%m-%dT%H:%M:%SZ'.
        """
        if not ts_str:
            return None
        formats = [
            "%Y-%m-%d %H:%M:%S UTC",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
        ]
        clean_str = ts_str.strip()
        for fmt in formats:
            try:
                dt = datetime.datetime.strptime(clean_str, fmt)
                return dt.replace(tzinfo=datetime.timezone.utc).timestamp()
            except ValueError:
                continue
        return None

    def build_chronological_timeline(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constructs an audit timeline from case data:
        1. Validates the SHA-256 cryptographic hash chain first.
        2. Preserves the original ledger sequence numbers (indices 0..N).
        3. Detects timestamp anomalies (backwards timestamps, identical timestamps).
        4. Calculates event latency without silently reordering records.
        5. Distinguishes cryptographic hash integrity from timestamp accuracy.
        """
        if not isinstance(case_data, dict):
            return {"error": "Invalid case_data: Expected dictionary", "status": "ERROR_INVALID_INPUT"}

        audit_trail = case_data.get("audit_trail", [])
        inv_id = case_data.get("investigation_id", "UNKNOWN_CASE")

        if not audit_trail:
            return {
                "investigation_id": inv_id,
                "status": "EMPTY_TIMELINE",
                "total_events": 0,
                "hash_chain_valid": True,
                "timeline_records": [],
                "timestamp_anomalies": [],
                "disclaimer": "No audit entries recorded in case container."
            }

        # 1. Cryptographic Hash Chain Validation
        from src.modules.case_manager import CaseManager
        case_mgr = CaseManager.get_instance()
        hash_check = case_mgr.verify_audit_trail_integrity(case_data)
        hash_chain_valid = hash_check.get("valid", False)

        timeline_records = []
        timestamp_anomalies = []

        prev_epoch: Optional[float] = None
        genesis_epoch: Optional[float] = None

        # 2. Iterate strictly preserving original ledger sequence [0..N]
        for seq_idx, entry in enumerate(audit_trail):
            raw_ts = entry.get("timestamp", "")
            action = entry.get("action", "UNKNOWN_ACTION")
            details = entry.get("details", "")
            evidence_id = entry.get("evidence_id")
            event_hash = entry.get("event_hash", "")
            prev_hash = entry.get("prev_hash", "")

            epoch = self.parse_iso_timestamp(raw_ts)

            # Check timestamp anomalies
            anomaly_flag = None
            inter_event_latency_sec = None

            if epoch is not None:
                if genesis_epoch is None:
                    genesis_epoch = epoch

                if prev_epoch is not None:
                    latency = epoch - prev_epoch
                    inter_event_latency_sec = round(latency, 2)

                    if latency < 0:
                        # Backwards timestamp detected!
                        anomaly_flag = "BACKWARDS_TIMESTAMP_DETECTED"
                        timestamp_anomalies.append({
                            "sequence_index": seq_idx,
                            "action": action,
                            "timestamp": raw_ts,
                            "previous_timestamp": audit_trail[seq_idx - 1].get("timestamp"),
                            "time_delta_seconds": inter_event_latency_sec,
                            "anomaly_type": "BACKWARDS_TIMESTAMP",
                            "description": (
                                f"Event #{seq_idx} ({action}) has a timestamp earlier than event #{seq_idx - 1} "
                                f"(negative delta of {latency:.2f}s). Original ledger sequence is preserved."
                            )
                        })
                    elif latency == 0:
                        anomaly_flag = "IDENTICAL_TIMESTAMP"
                        timestamp_anomalies.append({
                            "sequence_index": seq_idx,
                            "action": action,
                            "timestamp": raw_ts,
                            "anomaly_type": "IDENTICAL_TIMESTAMP",
                            "description": f"Event #{seq_idx} occurred within the same second as preceding event #{seq_idx - 1}."
                        })

                prev_epoch = epoch
            else:
                anomaly_flag = "UNPARSEABLE_TIMESTAMP"
                timestamp_anomalies.append({
                    "sequence_index": seq_idx,
                    "action": action,
                    "timestamp": raw_ts,
                    "anomaly_type": "UNPARSEABLE_TIMESTAMP",
                    "description": f"Timestamp format '{raw_ts}' could not be parsed to standard UTC epoch."
                })

            timeline_records.append({
                "sequence_index": seq_idx,
                "action": action,
                "timestamp_display": raw_ts,
                "epoch_seconds": epoch,
                "elapsed_from_genesis_sec": round(epoch - genesis_epoch, 2) if (epoch and genesis_epoch) else 0.0,
                "latency_from_prev_sec": inter_event_latency_sec,
                "evidence_id": evidence_id,
                "details": details,
                "event_hash": event_hash,
                "prev_hash": prev_hash,
                "timestamp_anomaly_flag": anomaly_flag,
            })

        total_span_sec = round(prev_epoch - genesis_epoch, 2) if (prev_epoch and genesis_epoch) else 0.0

        return {
            "investigation_id": inv_id,
            "status": "TIMELINE_VERIFIED",
            "total_events": len(timeline_records),
            "hash_chain_valid": hash_chain_valid,
            "hash_chain_details": hash_check.get("message", ""),
            "has_timestamp_anomalies": len(timestamp_anomalies) > 0,
            "timestamp_anomalies_count": len(timestamp_anomalies),
            "timestamp_anomalies": timestamp_anomalies,
            "total_investigation_span_seconds": total_span_sec,
            "timeline_records": timeline_records,
            "forensic_integrity_distinction": (
                "Cryptographic Distinction Notice: The validity of the SHA-256 hash chain confirms that no audit log entry "
                "has been modified, deleted, or inserted out of sequence since recording. It does NOT guarantee host clock accuracy, "
                "lack of NTP drift, or physical truthfulness of the recorded action statements."
            )
        }

