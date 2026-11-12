"""
Comprehensive Regression Test Suite for Phase 5.3:
Strict Source Provenance, Corroboration Engine, Complete Audit Trail, and PDF Manifest Integrity.
"""

import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import unittest
from src.modules.case_manager import CaseManager
from src.modules.evidence_correlator import EvidenceCorrelator
from src.modules.reliability_engine import ForensicReliabilityEngine
from src.modules.report_generator import ForensicReportGenerator
from src.modules.image_detector import ImageForensicDetector
from src.modules.video_detector import VideoForensicPipeline
from src.modules.audio_detector import AudioForensicDetector

class TestPhase53Regression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case_mgr = CaseManager.get_instance()
        cls.correlator = EvidenceCorrelator.get_instance()
        cls.rel_engine = ForensicReliabilityEngine.get_instance()
        cls.report_gen = ForensicReportGenerator.get_instance()

    # -------------------------------------------------------------------------
    # TASK 1: STRICT SOURCE PROVENANCE
    # -------------------------------------------------------------------------
    def test_task1_matching_filenames_alone_do_not_establish_provenance(self):
        """1. Matching exact filenames alone do NOT establish verified provenance."""
        vid_res = [{"filename": "clip.mp4", "video_metadata": {"duration_seconds": 10.0}, "summary": {}}]
        aud_res = [{"filename": "clip.mp4", "audio_metadata": {"duration_seconds": 5.0}}]
        corr = self.correlator.correlate_evidence([], vid_res, aud_res)
        rec = corr["correlations"][0]
        self.assertEqual(rec["relationship_type"], "POSSIBLE_ASSOCIATION_NOT_VERIFIED")
        self.assertFalse(rec["is_source_linked"])
        self.assertFalse(rec["sync_anomaly_flag"])
        print("\n[STRICT PROVENANCE 1 PASSED] Exact filename matches alone do NOT establish provenance.")

    def test_task1_matching_filename_stems_do_not_establish_provenance(self):
        """2. Matching filename stems alone do NOT establish verified provenance."""
        vid_res = [{"filename": "interview_broadcast.mp4", "video_metadata": {"duration_seconds": 12.0}, "summary": {}}]
        aud_res = [{"filename": "interview_broadcast.wav", "audio_metadata": {"duration_seconds": 4.0}}]
        corr = self.correlator.correlate_evidence([], vid_res, aud_res)
        rec = corr["correlations"][0]
        self.assertEqual(rec["relationship_type"], "POSSIBLE_ASSOCIATION_NOT_VERIFIED")
        self.assertFalse(rec["is_source_linked"])
        self.assertFalse(rec["sync_anomaly_flag"])
        print("[STRICT PROVENANCE 2 PASSED] Matching filename stems alone do NOT establish provenance.")

    def test_task1_exact_source_evidence_id_establishes_provenance(self):
        """3. Exact source evidence IDs establish verified provenance."""
        vid_res = [{"evidence_id": "EVID-VID-001", "filename": "clipA.mp4", "video_metadata": {"duration_seconds": 10.0}, "summary": {}}]
        aud_res = [{"extracted_from": "EVID-VID-001", "filename": "trackX.wav", "audio_metadata": {"duration_seconds": 4.0}}]
        corr = self.correlator.correlate_evidence([], vid_res, aud_res)
        rec = corr["correlations"][0]
        self.assertEqual(rec["relationship_type"], "LINKED_AUDIO_VIDEO_STREAM_ANALYSIS")
        self.assertTrue(rec["is_source_linked"])
        self.assertTrue(rec["sync_anomaly_flag"])
        print("[STRICT PROVENANCE 3 PASSED] Exact source evidence IDs successfully establish verified provenance.")

    def test_task1_verified_source_hash_establishes_provenance(self):
        """4. Verified source SHA-256 hashes establish verified provenance."""
        vid_res = [{"sha256": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890", "filename": "camera.mp4", "video_metadata": {"duration_seconds": 10.0}, "summary": {}}]
        aud_res = [{"extracted_from": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890", "filename": "audio.wav", "audio_metadata": {"duration_seconds": 10.0}}]
        corr = self.correlator.correlate_evidence([], vid_res, aud_res)
        rec = corr["correlations"][0]
        self.assertEqual(rec["relationship_type"], "LINKED_AUDIO_VIDEO_STREAM_ANALYSIS")
        self.assertTrue(rec["is_source_linked"])
        self.assertFalse(rec["sync_anomaly_flag"])
        print("[STRICT PROVENANCE 4 PASSED] Verified SHA-256 source hash establishes provenance.")

    def test_task1_invalid_or_missing_source_identifier_fails_provenance(self):
        """5. Invalid, non-matching, or missing source identifiers do NOT establish provenance."""
        # Non-matching extracted_from
        vid_res = [{"evidence_id": "EVID-VID-CORRECT", "sha256": "HASH_CORRECT", "filename": "source.mp4", "video_metadata": {"duration_seconds": 10.0}, "summary": {}}]
        aud_res = [{"extracted_from": "EVID-VID-WRONG", "filename": "unrelated.wav", "audio_metadata": {"duration_seconds": 5.0}}]
        corr = self.correlator.correlate_evidence([], vid_res, aud_res)
        rec = corr["correlations"][0]
        self.assertEqual(rec["relationship_type"], "METADATA_AND_CONTAINER_COMPARISON")
        self.assertFalse(rec["is_source_linked"])
        self.assertFalse(rec["sync_anomaly_flag"])

        # Missing extracted_from and missing source container
        aud_res_missing = [{"filename": "other.wav", "audio_metadata": {"duration_seconds": 5.0}}]
        corr_missing = self.correlator.correlate_evidence([], vid_res, aud_res_missing)
        rec_missing = corr_missing["correlations"][0]
        self.assertFalse(rec_missing["is_source_linked"])
        print("[STRICT PROVENANCE 5 PASSED] Invalid, non-matching, and missing source identifiers do NOT establish provenance.")

    # -------------------------------------------------------------------------
    # TASK 2: RELIABILITY ENGINE CORROBORATION
    # -------------------------------------------------------------------------
    def test_task2_A_two_unrelated_flagged_files(self):
        """
        A. Synthetic image + synthetic audio without common verified provenance.
        Expected: Potential manipulation detected (NEVER Strong Evidence).
        """
        img_res = [{"filename": "ai_portrait.png", "is_synthetic": True, "confidence_pct": 95.0}]
        aud_res = [{
            "filename": "cloned_voice.wav",
            "audio_metadata": {"duration_seconds": 5.0},
            "is_synthetic": True,
            "confidence_pct": 92.0
        }]
        corr = self.correlator.correlate_evidence(img_res, [], aud_res)
        verdict = self.rel_engine.evaluate_investigation(img_res, [], aud_res, corr)
        self.assertNotEqual(verdict["verdict_category"], "Strong evidence of manipulation detected")
        self.assertEqual(verdict["verdict_category"], "Potential manipulation detected")
        self.assertIn("Uncorroborated Multiple Alerts", verdict["evidence_strength"])
        print("[TASK 2A PASSED] Two unrelated flagged files produced 'Potential manipulation detected', NOT Strong Evidence.")

    def test_task2_B_one_flagged_image_unrelated_authentic_media(self):
        """
        B. One flagged image and unrelated authentic video & audio.
        Expected: Conflicting forensic evidence (NEVER Strong Evidence).
        """
        img_res = [{"filename": "ai_portrait.png", "is_synthetic": True, "confidence_pct": 95.0}]
        vid_res = [{
            "filename": "cctv_real.mp4",
            "video_metadata": {"duration_seconds": 15.0},
            "summary": {"synthetic_flagged_count": 0, "total_analyzed_frames": 10, "mean_synthetic_score": 10.0}
        }]
        aud_res = [{
            "filename": "human_speech.wav",
            "audio_metadata": {"duration_seconds": 3.0},
            "is_synthetic": False,
            "confidence_pct": 98.0
        }]
        corr = self.correlator.correlate_evidence(img_res, vid_res, aud_res)
        verdict = self.rel_engine.evaluate_investigation(img_res, vid_res, aud_res, corr)
        self.assertNotEqual(verdict["verdict_category"], "Strong evidence of manipulation detected")
        self.assertEqual(verdict["verdict_category"], "Conflicting forensic evidence")
        print("[TASK 2B PASSED] One flagged image + unrelated authentic media produced 'Conflicting forensic evidence'.")

    def test_task2_C_corroborated_linked_media_strong_evidence(self):
        """
        C. Explicitly linked media (video + extracted audio track) both flagged synthetic.
        Expected: Strong evidence of manipulation detected.
        """
        vid_res = [{
            "filename": "fake_speech.mp4",
            "sha256": "HASH_VID_999",
            "video_metadata": {"duration_seconds": 10.0},
            "summary": {"synthetic_flagged_count": 5, "total_analyzed_frames": 10, "mean_synthetic_score": 75.0, "highest_synthetic_score": 88.0}
        }]
        aud_res = [{
            "filename": "fake_speech_track.wav",
            "extracted_from": "HASH_VID_999",
            "audio_metadata": {"duration_seconds": 10.0},
            "is_synthetic": True,
            "confidence_pct": 96.0
        }]
        corr = self.correlator.correlate_evidence([], vid_res, aud_res)
        verdict = self.rel_engine.evaluate_investigation([], vid_res, aud_res, corr)
        self.assertEqual(verdict["verdict_category"], "Strong evidence of manipulation detected")
        self.assertIn("Corroborated Multi-Source Forensic Indicators with Verified Provenance", verdict["evidence_strength"])
        print("[TASK 2C PASSED] Verified linked media corroboration produced 'Strong evidence of manipulation detected'.")

    # -------------------------------------------------------------------------
    # TASK 3: COMPLETE AUDIT EVENT COVERAGE & HASH CHAINING
    # -------------------------------------------------------------------------
    def test_task3_complete_audit_event_lifecycle(self):
        """
        Verify all 8 standardized audit events:
        1. CASE_INITIALIZED
        2. EVIDENCE_INGESTED
        3. EVIDENCE_HASHED
        4. EVIDENCE_ACCESSED
        5. ANALYSIS_EXECUTED
        6. REPORT_GENERATED
        7. REPORT_EXPORTED
        8. CASE_REOPENED
        """
        case = self.case_mgr.create_case("Full Audit Lifecycle Case", investigator="Forensic Officer")
        cid = case["investigation_id"]

        # 2. EVIDENCE_INGESTED
        self.case_mgr.log_evidence_ingested(case, "sample.jpg", "Image", "1.2 MB", "EVID-HASH-01")
        # 3. EVIDENCE_HASHED
        self.case_mgr.log_evidence_hashed(case, "sample.jpg", "EVID-HASH-01", "EVID-HASH-01")
        self.case_mgr.save_case(case)

        # 4. EVIDENCE_ACCESSED
        self.case_mgr.log_evidence_accessed(cid, "EVID-HASH-01", "Accessed for Swin Transformer scan")
        case = self.case_mgr.load_case(cid)

        # 5. ANALYSIS_EXECUTED
        self.case_mgr.log_analysis_executed(case, "Image", "sample.jpg", "Swin Transformer", "EVID-HASH-01")
        # 6. REPORT_GENERATED
        self.case_mgr.log_report_generated(case, f"REPORT_{cid}.pdf", "REPORT_HASH_999")
        self.case_mgr.save_case(case)
        # 7. REPORT_EXPORTED
        self.case_mgr.log_report_exported(cid, f"REPORT_{cid}.pdf")
        # 8. CASE_REOPENED
        reopened = self.case_mgr.load_case(cid, record_reopen=True, investigator="Auditor Jane")

        actions = [entry["action"] for entry in reopened["audit_trail"]]
        expected_actions = [
            "CASE_INITIALIZED",
            "EVIDENCE_INGESTED",
            "EVIDENCE_HASHED",
            "EVIDENCE_ACCESSED",
            "ANALYSIS_EXECUTED",
            "REPORT_GENERATED",
            "REPORT_EXPORTED",
            "CASE_REOPENED"
        ]
        for act in expected_actions:
            self.assertIn(act, actions, f"Missing required audit action: {act}")

        # Verify hash chain integrity across all 8 actions
        integrity = self.case_mgr.verify_audit_trail_integrity(reopened)
        self.assertTrue(integrity["valid"])
        self.assertEqual(integrity["count"], len(reopened["audit_trail"]))
        print("[TASK 3 PASSED] All 8 required audit trail events verified with valid cryptographic hash chaining.")

    # -------------------------------------------------------------------------
    # TASK 4: PDF MANIFEST VERIFICATION
    # -------------------------------------------------------------------------
    def test_task4_pdf_manifest_verification(self):
        """
        Verify manifest generation, clean match, byte tampering detection,
        and missing manifest error handling.
        """
        dummy_case = {
            "investigation_id": "TEST-MANIFEST-53",
            "title": "Manifest Test Case 5.3",
            "created_at": "2026-11-12 00:00:00 UTC",
            "investigator": "Test Lead",
            "status": "CLOSED",
            "evidence_inventory": [],
            "individual_results": {"images": [], "videos": [], "audios": []},
            "correlation_analysis": {"correlations": []},
            "reliability_assessment": {
                "verdict_category": "No strong evidence of manipulation detected",
                "evidence_strength": "Baseline",
                "rationale": "Test rationale"
            }
        }
        pdf_path = self.report_gen.generate_investigation_pdf(dummy_case)
        manifest_path = f"{pdf_path}.manifest.json"

        # 1. Clean Match
        clean_res = self.report_gen.verify_report_integrity(pdf_path)
        self.assertTrue(clean_res["valid"])

        # 2. Byte Tampering Detection
        with open(pdf_path, "ab") as f:
            f.write(b"TAMPER")
        tamper_res = self.report_gen.verify_report_integrity(pdf_path)
        self.assertFalse(tamper_res["valid"])
        self.assertIn("SECURITY ALERT", tamper_res["reason"])

        # 3. Missing Manifest Handling
        missing_res = self.report_gen.verify_report_integrity("non_existent_file.pdf")
        self.assertFalse(missing_res["valid"])
        self.assertIn("not found", missing_res["reason"])
        print("[TASK 4 PASSED] PDF manifest generation, clean verification, tampering alert, and missing file handling verified.")

if __name__ == "__main__":
    unittest.main()
