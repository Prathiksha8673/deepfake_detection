"""
Regression test suite for DeepfakeX Phase 5.2 Forensic Integrity Corrections.
Tests A through G as specified in user requirements.
"""

import os
import json
import unittest
from src.modules.case_manager import CaseManager
from src.modules.evidence_correlator import EvidenceCorrelator
from src.modules.reliability_engine import ForensicReliabilityEngine
from src.modules.report_generator import ForensicReportGenerator
from src.modules.image_detector import ImageForensicDetector
from src.modules.video_detector import VideoForensicPipeline
from src.modules.audio_detector import AudioForensicDetector

class TestPhase52Integrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case_mgr = CaseManager.get_instance()
        cls.correlator = EvidenceCorrelator.get_instance()
        cls.rel_engine = ForensicReliabilityEngine.get_instance()
        cls.report_gen = ForensicReportGenerator.get_instance()

    def test_A_isolated_flagged_image_unrelated_video_audio(self):
        """
        TEST A: 1 flagged image + unrelated 10s video (authentic) + 4s audio (authentic).
        Requirement: Must NOT trigger 'Strong evidence of manipulation detected'.
        Must trigger 'Conflicting forensic evidence'.
        Duration delta between unrelated video & audio must NOT be flagged as a stream desync anomaly.
        """
        img_res = [{"filename": "flagged_art.png", "is_synthetic": True, "confidence_pct": 94.2}]
        vid_res = [{
            "filename": "unrelated_10s_cam.mp4",
            "video_metadata": {"duration_seconds": 10.0},
            "summary": {"synthetic_flagged_count": 0, "total_analyzed_frames": 10, "mean_synthetic_score": 12.0, "highest_synthetic_score": 18.0}
        }]
        aud_res = [{
            "filename": "unrelated_4s_voice.wav",
            "audio_metadata": {"duration_seconds": 4.0},
            "is_synthetic": False,
            "confidence_pct": 89.1,
            "model_architecture": "Wav2Vec2"
        }]

        corr = self.correlator.correlate_evidence(img_res, vid_res, aud_res)
        # Check that unrelated files do NOT trigger sync_anomaly_flag
        for c in corr["correlations"]:
            self.assertFalse(c.get("sync_anomaly_flag", False), f"Unrelated pair {c['pair']} incorrectly flagged sync anomaly!")
            if c.get("relationship_type") == "METADATA_AND_CONTAINER_COMPARISON":
                self.assertFalse(c.get("is_source_linked", True))

        verdict = self.rel_engine.evaluate_investigation(img_res, vid_res, aud_res, corr)
        self.assertNotEqual(verdict["verdict_category"], "Strong evidence of manipulation detected", "Defect reproduced: Premature escalation to Strong Evidence!")
        self.assertEqual(verdict["verdict_category"], "Conflicting forensic evidence")
        self.assertEqual(verdict["sync_anomalies_detected"], 0)
        print("\n[TEST A PASSED] Isolated flagged image + unrelated media did NOT escalate to Strong Evidence. Correctly yielded 'Conflicting forensic evidence'.")

    def test_B_authentic_image_synthetic_audio_authentic_video(self):
        """
        TEST B: Authentic image + synthetic audio + authentic video.
        Requirement: Verdict must be 'Conflicting forensic evidence'.
        """
        img_res = [{"filename": "real_photo.jpg", "is_synthetic": False, "confidence_pct": 98.5}]
        vid_res = [{
            "filename": "real_surveillance.mp4",
            "video_metadata": {"duration_seconds": 8.0},
            "summary": {"synthetic_flagged_count": 0, "total_analyzed_frames": 10, "mean_synthetic_score": 5.0, "highest_synthetic_score": 9.0}
        }]
        aud_res = [{
            "filename": "synth_clone.wav",
            "audio_metadata": {"duration_seconds": 5.0},
            "is_synthetic": True,
            "confidence_pct": 99.1,
            "model_architecture": "Wav2Vec2"
        }]

        corr = self.correlator.correlate_evidence(img_res, vid_res, aud_res)
        verdict = self.rel_engine.evaluate_investigation(img_res, vid_res, aud_res, corr)
        self.assertEqual(verdict["verdict_category"], "Conflicting forensic evidence")
        self.assertIn("Mixed / Divergent", verdict["evidence_strength"])
        print("[TEST B PASSED] Authentic image + synthetic audio + authentic video yielded 'Conflicting forensic evidence'.")

    def test_C_linked_video_and_extracted_audio(self):
        """
        TEST C: Video with explicitly linked audio track.
        Case 1: Desynchronized (10s video vs 4s audio).
        Case 2: Synchronized (10s video vs 9.8s audio).
        """
        vid_res = [{
            "evidence_id": "EVID-VID-INTERVIEW-01",
            "sha256": "VID_SHA_INTERVIEW",
            "filename": "interview.mp4",
            "video_metadata": {"duration_seconds": 10.0},
            "summary": {"synthetic_flagged_count": 1, "total_analyzed_frames": 10, "mean_synthetic_score": 55.0, "highest_synthetic_score": 82.0}
        }]
        # Case 1: Linked desync
        aud_linked_desync = [{
            "filename": "interview_track0.wav",
            "extracted_from": "EVID-VID-INTERVIEW-01",
            "audio_metadata": {"duration_seconds": 4.0},
            "is_synthetic": True,
            "confidence_pct": 91.0,
            "model_architecture": "Wav2Vec2"
        }]
        corr_desync = self.correlator.correlate_evidence([], vid_res, aud_linked_desync)
        vid_aud_corr = corr_desync["correlations"][0]
        self.assertEqual(vid_aud_corr["relationship_type"], "LINKED_AUDIO_VIDEO_STREAM_ANALYSIS")
        self.assertTrue(vid_aud_corr["sync_anomaly_flag"])

        # Case 2: Linked in-sync
        aud_linked_sync = [{
            "filename": "interview_track0.wav",
            "extracted_from": "VID_SHA_INTERVIEW",
            "audio_metadata": {"duration_seconds": 9.8},
            "is_synthetic": True,
            "confidence_pct": 91.0,
            "model_architecture": "Wav2Vec2"
        }]
        corr_sync = self.correlator.correlate_evidence([], vid_res, aud_linked_sync)
        self.assertFalse(corr_sync["correlations"][0]["sync_anomaly_flag"])
        print("[TEST C PASSED] Explicitly linked audio/video track correctly verified for stream desync.")

    def test_F_chain_of_custody_and_audit_trail(self):
        """
        TEST F: Case initialization, reopening, evidence access, report export, and hash chain verification.
        """
        case = self.case_mgr.create_case(title="Regression Audit Case", investigator="Test Lead")
        cid = case["investigation_id"]

        # Append evidence access
        self.case_mgr.log_evidence_accessed(cid, "EVID-001", "Accessed original wav file")
        # Reopen case
        reopened = self.case_mgr.load_case(cid, record_reopen=True, investigator="Auditor Bob")
        # Log export
        self.case_mgr.log_report_exported(cid, f"DEEPFAKE_X_REPORT_{cid}.pdf")

        final_case = self.case_mgr.load_case(cid)
        trail = final_case["audit_trail"]
        self.assertGreaterEqual(len(trail), 4)

        # Verify integrity
        integrity = self.case_mgr.verify_audit_trail_integrity(final_case)
        self.assertTrue(integrity["valid"])
        self.assertEqual(integrity["count"], len(trail))

        # Test tamper detection
        final_case["audit_trail"][1]["details"] = "Illegally altered audit detail!"
        tamper_check = self.case_mgr.verify_audit_trail_integrity(final_case)
        self.assertFalse(tamper_check["valid"])
        self.assertEqual(tamper_check["tampered_index"], 1)
        print("[TEST F PASSED] Hash-chained audit trail created, verified, and tamper detection confirmed.")

    def test_G_pdf_report_manifest_integrity_and_tampering(self):
        """
        TEST G: PDF generation, detached manifest verification, and tamper detection.
        """
        dummy_case = {
            "investigation_id": "TEST-MANIFEST-001",
            "title": "Manifest Integrity Verification",
            "created_at": "2026-11-12 00:00:00 UTC",
            "investigator": "Forensic Officer",
            "status": "CLOSED",
            "evidence_inventory": [
                {"filename": "test.png", "modality": "IMAGE", "file_size": "100 KB", "sha256": "abcdef1234567890"}
            ],
            "individual_results": {
                "images": [{"filename": "test.png", "classification": "AI-Generated Image", "artificial_prob": 95.0, "human_prob": 5.0, "device": "cuda:0"}],
                "videos": [],
                "audios": []
            },
            "correlation_analysis": {"correlations": []},
            "reliability_assessment": {
                "verdict_category": "Potential manipulation detected",
                "evidence_strength": "Single modality alert",
                "rationale": "Single image flagged."
            }
        }
        pdf_path = self.report_gen.generate_investigation_pdf(dummy_case)
        manifest_path = f"{pdf_path}.manifest.json"
        self.assertTrue(os.path.exists(pdf_path))
        self.assertTrue(os.path.exists(manifest_path))

        # Check clean verification
        check_clean = self.report_gen.verify_report_integrity(pdf_path)
        self.assertTrue(check_clean["valid"])
        self.assertEqual(check_clean["recorded_sha256"], check_clean["computed_sha256"])

        # Tamper simulation: Append 1 byte to the generated PDF
        with open(pdf_path, "ab") as f:
            f.write(b"\x00")

        check_tampered = self.report_gen.verify_report_integrity(pdf_path)
        self.assertFalse(check_tampered["valid"])
        self.assertNotEqual(check_tampered["recorded_sha256"], check_tampered["computed_sha256"])
        print("[TEST G PASSED] Detached SHA-256 PDF manifest verified and byte tampering successfully caught.")

if __name__ == "__main__":
    unittest.main()
