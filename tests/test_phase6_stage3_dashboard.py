"""
Stage 3 Automated Test Suite (tests/test_phase6_stage3_dashboard.py)
Validates Examiner Dashboard functionality, metrics accuracy, component rendering logic,
navigation destinations, and safe handling of missing/empty data.

Requirements verified:
1. Dashboard loads with an empty case collection.
2. Dashboard loads with multiple cases.
3. Evidence modality counts are correct.
4. Case selection displays the correct evidence.
5. Detector scores are displayed without modification.
6. Missing analytical results are handled gracefully.
7. Explainability integration works for all three modalities.
8. Evidence comparison integration works.
9. Invalid audit chain displays a warning.
10. Timeline preserves original event order.
11. PDF generation is accessible.
12. Detached manifest verification remains functional.
13. Existing navigation destinations remain available.
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from src.modules.case_manager import CaseManager
from src.modules.examiner_dashboard import ExaminerDashboard
from src.modules.report_generator import ForensicReportGenerator


class TestPhase6Stage3Dashboard(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.dashboard = ExaminerDashboard.get_instance()
        self.case_mgr = CaseManager.get_instance()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_dashboard_empty_cases_metrics(self):
        """1. Dashboard computes accurate metrics for an empty case collection."""
        metrics = self.dashboard.compute_dashboard_metrics([])
        self.assertEqual(metrics["total_cases"], 0)
        self.assertEqual(metrics["total_evidence"], 0)
        self.assertEqual(metrics["image_count"], 0)
        self.assertEqual(metrics["video_count"], 0)
        self.assertEqual(metrics["audio_count"], 0)
        self.assertEqual(metrics["completed_analysis"], 0)
        self.assertEqual(metrics["generated_reports"], 0)
        self.assertEqual(metrics["requires_examination"], 0)
        print("[STAGE 3.1 PASSED] Empty case metrics computed safely.")

    def test_02_and_03_dashboard_multiple_cases_and_modality_counts(self):
        """2 & 3. Dashboard loads multiple cases and computes accurate evidence modality counts."""
        sample_cases = [
            {
                "investigation_id": "TEST-CASE-A",
                "evidence_inventory": [
                    {"filename": "img1.png", "modality": "Image"},
                    {"filename": "vid1.mp4", "modality": "Video"},
                ],
                "individual_results": {
                    "images": [{"filename": "img1.png", "artificial_prob": 90.0}],
                    "videos": [{"filename": "vid1.mp4", "summary": {"mean_synthetic_score": 45.0}}]
                },
                "reliability_assessment": {"verdict_category": "Potential manipulation detected"}
            },
            {
                "investigation_id": "TEST-CASE-B",
                "evidence_inventory": [
                    {"filename": "aud1.wav", "modality": "Audio"},
                    {"filename": "img2.jpg", "modality": "Image"}
                ],
                "individual_results": {
                    "images": [],
                    "audios": [{"filename": "aud1.wav", "synthetic_score": 10.0}]
                },
                "reliability_assessment": {"verdict_category": "Authentic / Consistent Media"}
            }
        ]

        with patch.object(self.case_mgr, "load_case", side_effect=lambda inv_id, **kw: next((c for c in sample_cases if c["investigation_id"] == inv_id), None)):
            summaries = [{"investigation_id": c["investigation_id"]} for c in sample_cases]
            metrics = self.dashboard.compute_dashboard_metrics(summaries)

            self.assertEqual(metrics["total_cases"], 2)
            self.assertEqual(metrics["total_evidence"], 4)
            self.assertEqual(metrics["image_count"], 2)
            self.assertEqual(metrics["video_count"], 1)
            self.assertEqual(metrics["audio_count"], 1)
            self.assertEqual(metrics["completed_analysis"], 2)
            self.assertEqual(metrics["requires_examination"], 1)
            print("[STAGE 3.2-3.3 PASSED] Multiple case aggregation and modality counts verified.")

    def test_04_and_05_evidence_display_and_unmodified_scores(self):
        """4 & 5. Evidence displays correct entries and detector scores without fabrication or modification."""
        test_case = {
            "investigation_id": "TEST-SCORES-01",
            "evidence_inventory": [
                {"filename": "deepfake_face.png", "modality": "Image", "sha256": "HASH_IMG_1", "file_size": "1.2 MB"}
            ],
            "individual_results": {
                "images": [{
                    "filename": "deepfake_face.png",
                    "classification": "Model predicts AI-Generated Image",
                    "artificial_prob": 98.42,
                    "human_prob": 1.58
                }]
            }
        }

        # Mock streamlit to inspect rendering
        with patch("streamlit.dataframe") as mock_df:
            self.dashboard.render_evidence_intelligence_tab(test_case)
            self.assertTrue(mock_df.called)
            df_arg = mock_df.call_args[0][0]
            self.assertEqual(len(df_arg), 1)
            row = df_arg.iloc[0]
            self.assertEqual(row["Filename"], "deepfake_face.png")
            self.assertEqual(row["SHA-256 Digest"], "HASH_IMG_1")
            self.assertIn("98.42", row["Model Scores (Uncalibrated)"])
            self.assertIn("1.58", row["Model Scores (Uncalibrated)"])
            print("[STAGE 3.4-3.5 PASSED] Unmodified detector scores and evidence inventory displayed.")

    def test_06_missing_analytical_data_handled_gracefully(self):
        """6. Missing or empty analytical results are handled gracefully without exceptions."""
        empty_case = {"investigation_id": "TEST-EMPTY", "evidence_inventory": []}
        with patch("streamlit.info") as mock_info:
            self.dashboard.render_evidence_intelligence_tab(empty_case)
            self.dashboard.render_explainability_tab(empty_case)
            self.dashboard.render_comparison_tab(empty_case)
            self.dashboard.render_timeline_tab(empty_case)
            self.assertTrue(mock_info.called)
            print("[STAGE 3.6 PASSED] Missing analytical data handled safely across tabs.")

    def test_07_explainability_all_three_modalities(self):
        """7. Forensic explainability integration derives grounded schemas for images, videos, and audios."""
        rich_case = {
            "investigation_id": "RICH-CASE-EXP",
            "individual_results": {
                "images": [{
                    "status": "VERIFIED_AUTHENTIC_INFERENCE",
                    "filename": "sample.png",
                    "classification": "AI-Generated",
                    "artificial_prob": 95.0,
                    "human_prob": 5.0
                }],
                "videos": [{
                    "status": "SUCCESS_VERIFIED_VIDEO_SCAN",
                    "filename": "sample.mp4",
                    "classification": "Authentic",
                    "sampling_config": {"requested_frames": 5},
                    "summary": {"total_analyzed_frames": 5, "mean_synthetic_score": 10.0}
                }],
                "audios": [{
                    "status": "SUCCESS_VERIFIED_AUDIO_SCAN",
                    "filename": "sample.wav",
                    "classification": "Authentic",
                    "synthetic_score": 2.0,
                    "authentic_score": 98.0,
                    "audio_metadata": {"duration_seconds": 4.0}
                }]
            }
        }

        explanations = self.case_mgr.get_forensic_explanations(rich_case)
        self.assertEqual(len(explanations["images"]), 1)
        self.assertEqual(len(explanations["videos"]), 1)
        self.assertEqual(len(explanations["audios"]), 1)
        img_exp = explanations["images"][0]
        self.assertEqual(img_exp["modality"], "IMAGE")
        self.assertIn("Unavailable", img_exp["output_interpretation"]["raw_logits"])
        self.assertTrue(len(img_exp["uncertainty_and_invalidation_factors"]) > 0)
        print("[STAGE 3.7 PASSED] Explainability integration validated for all 3 modalities.")

    def test_08_evidence_comparison_integration(self):
        """8. Evidence comparison integration maps temporal statistics and verified lineage."""
        comp_case = {
            "investigation_id": "COMP-CASE",
            "evidence_inventory": [
                {"filename": "parent.mp4", "sha256": "PARENT_SHA", "modality": "Video"},
                {"filename": "child.wav", "sha256": "CHILD_SHA", "modality": "Audio", "extracted_from": "PARENT_SHA"}
            ],
            "individual_results": {
                "videos": [{
                    "filename": "parent.mp4",
                    "frame_results": [
                        {"frame_index": 1, "artificial_prob": 20.0},
                        {"frame_index": 2, "artificial_prob": 60.0}
                    ]
                }],
                "audios": []
            }
        }

        comps = self.case_mgr.get_evidence_comparisons(comp_case)
        self.assertEqual(comps["verified_lineage"]["total_verified_lineages"], 1)
        self.assertEqual(len(comps["verified_lineage"]["verified_lineages"]), 1)
        self.assertEqual(len(comps["video_temporal_statistics"]), 1)
        self.assertEqual(comps["video_temporal_statistics"][0]["threshold_crossings_count"], 1)
        print("[STAGE 3.8 PASSED] Evidence comparison, lineage, and video temporal analytics verified.")

    def test_09_and_10_timeline_invalid_chain_and_order_preservation(self):
        """9 & 10. Invalid hash chain displays clear warning and original sequence is strictly preserved."""
        # Ledger with broken hash
        tampered_case = {
            "investigation_id": "TAMPERED-CHAIN",
            "audit_trail": [
                {
                    "timestamp": "2026-11-12 10:00:00 UTC",
                    "action": "CASE_INITIALIZED",
                    "details": "Init",
                    "prev_hash": "GENESIS_ROOT_HASH",
                    "event_hash": "CORRECT_HASH_1"
                },
                {
                    "timestamp": "2026-11-12 09:00:00 UTC",  # Backwards timestamp
                    "action": "EVIDENCE_INGESTED",
                    "details": "Tampered entry",
                    "prev_hash": "WRONG_PREV_HASH",         # Tampered link
                    "event_hash": "TAMPERED_HASH_2"
                }
            ]
        }

        timeline = self.case_mgr.get_timeline_analytics(tampered_case)
        self.assertFalse(timeline["hash_chain_valid"])
        self.assertIn("Tampered audit entry", str(timeline.get("hash_chain_details", "")))

        # Check sequence preservation: original indices must be 0 then 1
        records = timeline["timeline_records"]
        self.assertEqual(records[0]["sequence_index"], 0)
        self.assertEqual(records[1]["sequence_index"], 1)
        self.assertEqual(records[0]["action"], "CASE_INITIALIZED")
        self.assertEqual(records[1]["action"], "EVIDENCE_INGESTED")

        with patch("streamlit.error") as mock_err:
            self.dashboard.render_timeline_tab(tampered_case)
            self.assertTrue(mock_err.called)
            self.assertIn("tampering or missing hash links detected", mock_err.call_args[0][0])
            print("[STAGE 3.9-3.10 PASSED] Invalid hash chain alert and sequence preservation verified.")

    def test_11_and_12_pdf_generation_and_manifest_verification(self):
        """11 & 12. PDF report generation is accessible and detached manifest verifies integrity."""
        test_case = {
            "investigation_id": "PDF-STAGE3-TEST",
            "title": "Stage 3 PDF Verification",
            "created_at": "2026-11-12 10:00:00 UTC",
            "investigator": "Test Auditor",
            "evidence_inventory": [],
            "individual_results": {},
            "correlation_analysis": {},
            "reliability_assessment": {},
            "audit_trail": [
                {
                    "timestamp": "2026-11-12 10:00:00 UTC",
                    "action": "CASE_INITIALIZED",
                    "details": "Init",
                    "prev_hash": "GENESIS_ROOT_HASH",
                    "event_hash": CaseManager.get_instance()._compute_audit_entry_hash("GENESIS_ROOT_HASH", "2026-11-12 10:00:00 UTC", "CASE_INITIALIZED", "Init", None)
                }
            ]
        }

        rep_gen = ForensicReportGenerator.get_instance()
        pdf_path = rep_gen.generate_investigation_pdf(test_case)
        self.assertTrue(os.path.exists(pdf_path))

        # Check manifest
        verif = ForensicReportGenerator.verify_report_integrity(pdf_path)
        self.assertTrue(verif["valid"])
        self.assertIn("PDF SHA-256 digest verification successful", verif["reason"])
        print("[STAGE 3.11-3.12 PASSED] PDF report generation and detached manifest integrity verified.")

    def test_13_navigation_destinations_remain_available(self):
        """13. Existing navigation destinations remain available in sidebar menu."""
        with open("src/components/sidebar.py", "r", encoding="utf-8") as f:
            code = f.read()

        required_destinations = [
            "Overview",
            "Examiner Dashboard",
            "Multimodal Investigation",
            "Cross-Modal Verification",
            "Case Management",
            "Image Analysis",
            "Video Analysis",
            "Audio Analysis",
            "Document Analysis",
            "Forensic Reports",
            "Settings"
        ]

        for dest in required_destinations:
            self.assertIn(dest, code, f"Destination {dest} missing from sidebar navigation!")
        print("[STAGE 3.13 PASSED] All 11 navigation destinations confirmed present and available.")


if __name__ == "__main__":
    unittest.main()
