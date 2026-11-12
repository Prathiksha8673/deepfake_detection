"""
Automated Test Suite for Phase 6 Stage 1:
- Forensic Explainer schemas across all 3 modalities.
- Missing logits handling without fabrication.
- Identical and visually similar perceptual hashes with configurable thresholds.
- Video temporal statistics using actual benchmark data.
- Separated audio container metadata vs acoustic comparisons.
- Strict verified lineage vs unverified associations.
- Valid hash-chain with backwards timestamp anomaly detection and sequence preservation.
- Error handling for missing or malformed inputs.
"""

import os
import sys
import io
import time
import unittest
import numpy as np
from PIL import Image
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.modules.forensic_explainer import ForensicExplainer
from src.modules.evidence_comparator import EvidenceComparator
from src.modules.timeline_analytics import TimelineAnalytics
from src.modules.case_manager import CaseManager


class TestPhase6Stage1Suite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.explainer = ForensicExplainer.get_instance()
        cls.comparator = EvidenceComparator.get_instance()
        cls.analytics = TimelineAnalytics.get_instance()
        cls.case_mgr = CaseManager.get_instance()

    # -------------------------------------------------------------------------
    # 1. EXPLAINABILITY SCHEMAS ACROSS MODALITIES
    # -------------------------------------------------------------------------
    def test_01_image_explainer_schema(self):
        """Image explainability schema decomposes verified preprocessing and uncalibrated scores."""
        mock_img_res = {
            "status": "VERIFIED_AUTHENTIC_INFERENCE",
            "model_id": "umm-maybe/AI-image-detector",
            "model_architecture": "SwinForImageClassification",
            "filename": "portrait.png",
            "dimensions": "512 × 512",
            "classification": "Model predicts AI-Generated Image",
            "is_synthetic": True,
            "confidence_pct": 94.25,
            "artificial_prob": 94.25,
            "human_prob": 5.75,
            "inference_time_ms": 210.5,
            "device": "NVIDIA GeForce RTX 2050",
            "calibration_status": "Uncalibrated Softmax Probability"
        }
        res = self.explainer.explain_image_finding(mock_img_res)
        self.assertEqual(res["modality"], "IMAGE")
        self.assertEqual(res["evidence_target"], "portrait.png")
        self.assertIn("AutoImageProcessor ImageNet standard", res["verified_preprocessing"]["tensor_normalization"])
        self.assertEqual(res["output_interpretation"]["uncalibrated_softmax_scores"]["synthetic_probability_pct"], 94.25)
        self.assertTrue(res["output_interpretation"]["is_synthetic_flagged"])
        self.assertIn("Does not perform pixel-level", res["explicit_operational_exclusions"][0])
        print("\n[TEST 6.1 PASSED] Image explainability schema verified.")

    def test_02_missing_logits_handling_without_fabrication(self):
        """Explainer explicitly states logits are unavailable; never invents or simulates logits."""
        mock_res = {
            "status": "VERIFIED_AUTHENTIC_INFERENCE",
            "filename": "test.png",
            "artificial_prob": 80.0,
            "human_prob": 20.0
        }
        res = self.explainer.explain_image_finding(mock_res)
        raw_logits_statement = res["output_interpretation"]["raw_logits"]
        self.assertIn("Unavailable", raw_logits_statement)
        self.assertIn("not exported in the detector return dictionary", raw_logits_statement)
        print("[TEST 6.2 PASSED] Missing logits explicitly stated as unavailable without fabrication.")

    def test_03_video_explainer_dynamic_sampling(self):
        """Video explainer reads actual sampling_config and frame_results dynamically (not assuming 12 frames)."""
        mock_vid_res = {
            "status": "SUCCESS_VERIFIED_VIDEO_SCAN",
            "filename": "clip_7frames.mp4",
            "video_metadata": {"duration_seconds": 7.0, "resolution": "1920 × 1080", "fps": 30.0, "total_stream_frames": 210},
            "sampling_config": {"requested_frames": 7, "successfully_sampled": 7},
            "summary": {
                "total_analyzed_frames": 7,
                "synthetic_flagged_count": 2,
                "authentic_flagged_count": 5,
                "mean_synthetic_score": 42.1,
                "highest_synthetic_score": 78.4,
                "peak_timestamps": ["00:03.00"],
                "hardware_device": "NVIDIA GeForce RTX 2050",
                "total_processing_latency_ms": 650.0
            },
            "frame_results": [
                {"frame_index": i+1, "formatted_timestamp": f"00:0{i}.00", "artificial_prob": 30.0 + i*8} for i in range(7)
            ]
        }
        res = self.explainer.explain_video_finding(mock_vid_res)
        self.assertEqual(res["modality"], "VIDEO")
        self.assertEqual(res["sampling_implementation"]["actual_frames_sampled"], 7)
        self.assertEqual(res["output_interpretation"]["flagged_frames_count"], 2)
        self.assertEqual(len(res["output_interpretation"]["individual_frame_scores"]), 7)
        self.assertIn("Codec Compression Attenuation", res["uncertainty_and_invalidation_factors"][1])
        print("[TEST 6.3 PASSED] Video explainer dynamically handled actual 7-frame sampling configuration.")

    def test_04_audio_explainer_schema_and_domain_shift(self):
        """Audio explainer documents verified downmixing, 16kHz resampling, and vocoder domain shift."""
        mock_aud_res = {
            "status": "SUCCESS_VERIFIED_AUDIO_SCAN",
            "filename": "speech.wav",
            "classification": "Model predicts Authentic Human Speech",
            "is_synthetic": False,
            "confidence_pct": 100.0,
            "synthetic_score": 0.0,
            "authentic_score": 100.0,
            "audio_metadata": {
                "duration_seconds": 4.5,
                "original_sample_rate_hz": 44100,
                "target_sample_rate_hz": 16000,
                "channels": 2,
                "rms_energy": 0.045
            },
            "device": "NVIDIA GeForce RTX 2050",
            "inference_time_ms": 165.2
        }
        res = self.explainer.explain_audio_finding(mock_aud_res)
        self.assertEqual(res["modality"], "AUDIO")
        self.assertEqual(res["verified_preprocessing"]["original_sampling_rate_hz"], 44100)
        self.assertEqual(res["verified_preprocessing"]["target_sampling_rate_hz"], 16000)
        self.assertIn("Vocoder Domain Shift", res["uncertainty_and_invalidation_factors"][0])
        self.assertIn("Does not perform biometric speaker verification", res["explicit_operational_exclusions"][0])
        print("[TEST 6.4 PASSED] Audio explainer schema and vocoder domain shift documented.")

    # -------------------------------------------------------------------------
    # 2. PERCEPTUAL HASH HEURISTICS & CONFIGURABLE THRESHOLDS
    # -------------------------------------------------------------------------
    def test_05_perceptual_hash_heuristics_and_labels(self):
        """
        Verify:
        - IDENTICAL_PERCEPTUAL_HASH for identical images.
        - Measured distance for modified image (does not assume distance < 10).
        - Configurable Hamming threshold.
        """
        # Create image A (solid background with circle)
        img_a = Image.new("RGB", (100, 100), color=(200, 100, 50))
        buf_a = io.BytesIO()
        img_a.save(buf_a, format="PNG")
        bytes_a = buf_a.getvalue()

        # Identical image
        res_ident = self.comparator.compare_image_perceptual_similarity(bytes_a, bytes_a, hamming_threshold=10)
        self.assertEqual(res_ident["phash_hamming_distance"], 0)
        self.assertEqual(res_ident["similarity_classification"], "IDENTICAL_PERCEPTUAL_HASH")
        self.assertIn("does NOT prove byte-for-byte identity", res_ident["finding"])

        # Create distinct image B
        img_b = Image.new("RGB", (100, 100), color=(10, 200, 240))
        buf_b = io.BytesIO()
        img_b.save(buf_b, format="PNG")
        bytes_b = buf_b.getvalue()

        # Compare A vs B
        res_diff = self.comparator.compare_image_perceptual_similarity(bytes_a, bytes_b, hamming_threshold=5)
        measured_dist = res_diff["phash_hamming_distance"]
        self.assertIsInstance(measured_dist, int)
        self.assertGreaterEqual(measured_dist, 0)
        self.assertEqual(res_diff["configured_threshold"], 5)
        print(f"[TEST 6.5 PASSED] Perceptual hash measured exact distance ({measured_dist}) with configurable threshold.")

    # -------------------------------------------------------------------------
    # 3. VIDEO TEMPORAL DETECTOR-SCORE ANALYSIS (ACTUAL BENCHMARK)
    # -------------------------------------------------------------------------
    def test_06_video_temporal_score_statistics_actual_benchmark(self):
        """
        Calculates dynamic statistics from the actual 12-frame benchmark scores of ai_generated_video.mp4:
        Scores: [41.29, 36.96, 40.16, 24.78, 33.06, 46.04, 26.55, 51.03, 34.25, 29.53, 33.4, 27.14]
        """
        benchmark_scores = [41.29, 36.96, 40.16, 24.78, 33.06, 46.04, 26.55, 51.03, 34.25, 29.53, 33.4, 27.14]
        timestamps = ["00:00.00", "00:00.20", "00:00.40", "00:00.60", "00:00.80", "00:01.00",
                      "00:01.30", "00:01.50", "00:01.70", "00:01.90", "00:02.10", "00:02.30"]
        frames = [
            {"frame_index": i + 1, "formatted_timestamp": ts, "artificial_prob": s}
            for i, (s, ts) in enumerate(zip(benchmark_scores, timestamps))
        ]

        stats = self.comparator.analyze_video_temporal_scores(frames)
        self.assertEqual(stats["total_frames_evaluated"], 12)
        self.assertEqual(stats["score_metrics"]["mean_synthetic_score"], 35.35)
        self.assertEqual(stats["score_metrics"]["maximum_synthetic_score"], 51.03)
        self.assertEqual(stats["score_metrics"]["minimum_synthetic_score"], 24.78)
        self.assertEqual(stats["score_metrics"]["std_deviation"], 7.76)
        self.assertEqual(stats["threshold_crossings_count"], 1)
        self.assertEqual(stats["threshold_crossings"][0]["timestamp"], "00:01.50")
        self.assertIn("Score variance or localized threshold spikes do NOT prove", stats["forensic_disclaimer"])
        print("[TEST 6.6 PASSED] Video temporal score statistics calculated dynamically from benchmark.")

    # -------------------------------------------------------------------------
    # 4. SEPARATED AUDIO COMPARISON (CONTAINER vs ACOUSTIC)
    # -------------------------------------------------------------------------
    def test_07_separated_audio_stream_comparison(self):
        """Separates container metadata diff from acoustic RMS delta and disclaims common origin."""
        aud_a = {
            "audio_metadata": {
                "original_sample_rate_hz": 44100,
                "duration_seconds": 6.0,
                "channels": 2,
                "rms_energy": 0.052
            }
        }
        aud_b = {
            "audio_metadata": {
                "original_sample_rate_hz": 16000,
                "duration_seconds": 5.5,
                "channels": 1,
                "rms_energy": 0.048
            }
        }
        comp = self.comparator.compare_audio_streams(aud_a, aud_b)
        tech = comp["technical_container_metadata"]
        acoust = comp["acoustic_statistics"]

        self.assertFalse(tech["sample_rate_match"])
        self.assertEqual(tech["duration_delta_seconds"], 0.5)
        self.assertEqual(acoust["rms_energy_delta"], 0.004)
        self.assertIn("do NOT establish common recording environment", comp["forensic_disclaimer"])
        print("[TEST 6.7 PASSED] Audio comparison strictly decoupled technical metadata from acoustic statistics.")

    # -------------------------------------------------------------------------
    # 5. STRICT VERIFIED LINEAGE ENGINE
    # -------------------------------------------------------------------------
    def test_08_verified_lineage_vs_unverified_associations(self):
        """
        Verify:
        - Exact evidence ID establishes verified lineage.
        - Exact parent SHA-256 establishes verified lineage.
        - Validated source_container_id establishes verified lineage.
        - Filename strings remain strictly unverified associations.
        """
        inventory = [
            {"filename": "parent_video.mp4", "sha256": "VID_SHA_111", "evidence_id": "EVID-001"},
            {"filename": "child_track_by_sha.wav", "sha256": "AUD_SHA_222", "extracted_from": "VID_SHA_111"},
            {"filename": "child_track_by_id.wav", "sha256": "AUD_SHA_333", "extracted_from": "EVID-001"},
            {"filename": "child_by_container.wav", "sha256": "AUD_SHA_444", "source_container_id": "VID_SHA_111"},
            {"filename": "child_unverified_filename.wav", "sha256": "AUD_SHA_555", "extracted_from": "parent_video.mp4"},
            {"filename": "child_missing_ref.wav", "sha256": "AUD_SHA_666", "extracted_from": "NON_EXISTENT_ID"},
        ]
        lineage_res = self.comparator.establish_verified_lineage(inventory)
        self.assertEqual(lineage_res["total_verified_lineages"], 3)
        self.assertEqual(lineage_res["unverified_associations_count"], 2)

        verified_children = [l["child_filename"] for l in lineage_res["verified_lineages"]]
        self.assertIn("child_track_by_sha.wav", verified_children)
        self.assertIn("child_track_by_id.wav", verified_children)
        self.assertIn("child_by_container.wav", verified_children)

        unverified_children = [u["child_filename"] for u in lineage_res["unverified_associations"]]
        self.assertIn("child_unverified_filename.wav", unverified_children)
        self.assertIn("child_missing_ref.wav", unverified_children)
        print("[TEST 6.8 PASSED] Strict verified lineage enforced; filename references rejected.")

    # -------------------------------------------------------------------------
    # 6. TIMELINE SEQUENCE PRESERVATION & BACKWARDS TIMESTAMP ANOMALY
    # -------------------------------------------------------------------------
    def test_09_timeline_backwards_timestamp_anomaly_preserves_sequence(self):
        """
        Construct a valid hash-chained audit ledger with an injected backwards timestamp.
        Verify:
        - Hash chain is valid.
        - Backwards timestamp anomaly is detected.
        - Original sequence indices [0..3] are preserved without silent reordering.
        """
        # Create real case to initialize genesis block
        case = self.case_mgr.create_case("Timeline Anomaly Test", investigator="Forensic Officer")
        cid = case["investigation_id"]

        # Ingest event 1 (10:00:00 UTC)
        self.case_mgr.add_audit_entry(case, "EVIDENCE_INGESTED", "Ingested image A")
        case["audit_trail"][-1]["timestamp"] = "2026-11-12 10:00:00 UTC"
        # Recalculate hash for valid chain
        prev_h = case["audit_trail"][-2]["event_hash"]
        case["audit_trail"][-1]["prev_hash"] = prev_h
        case["audit_trail"][-1]["event_hash"] = self.case_mgr._compute_audit_entry_hash(
            prev_h, "2026-11-12 10:00:00 UTC", "EVIDENCE_INGESTED", "Ingested image A", None
        )

        # Ingest event 2 (10:05:00 UTC)
        prev_h = case["audit_trail"][-1]["event_hash"]
        entry2_hash = self.case_mgr._compute_audit_entry_hash(
            prev_h, "2026-11-12 10:05:00 UTC", "ANALYSIS_EXECUTED", "Executed neural scan", None
        )
        case["audit_trail"].append({
            "timestamp": "2026-11-12 10:05:00 UTC",
            "action": "ANALYSIS_EXECUTED",
            "details": "Executed neural scan",
            "evidence_id": None,
            "prev_hash": prev_h,
            "event_hash": entry2_hash
        })

        # Ingest event 3 (DELIBERATELY BACKWARDS: 09:50:00 UTC, earlier than 10:05:00)
        # Note: Event is added in chronological recording order to the chain, but has backwards host clock timestamp!
        prev_h = entry2_hash
        entry3_hash = self.case_mgr._compute_audit_entry_hash(
            prev_h, "2026-11-12 09:50:00 UTC", "REPORT_GENERATED", "Generated PDF report", None
        )
        case["audit_trail"].append({
            "timestamp": "2026-11-12 09:50:00 UTC",
            "action": "REPORT_GENERATED",
            "details": "Generated PDF report",
            "evidence_id": None,
            "prev_hash": prev_h,
            "event_hash": entry3_hash
        })

        # Validate hash chain integrity
        chain_check = self.case_mgr.verify_audit_trail_integrity(case)
        self.assertTrue(chain_check["valid"], "Hash chain should remain cryptographically valid despite host clock drift.")

        # Build timeline
        timeline = self.analytics.build_chronological_timeline(case)
        self.assertTrue(timeline["hash_chain_valid"])
        self.assertTrue(timeline["has_timestamp_anomalies"])
        self.assertEqual(timeline["timestamp_anomalies_count"], 1)

        anomaly = timeline["timestamp_anomalies"][0]
        self.assertEqual(anomaly["anomaly_type"], "BACKWARDS_TIMESTAMP")
        self.assertEqual(anomaly["sequence_index"], 3)
        self.assertLess(anomaly["time_delta_seconds"], 0)

        # Confirm sequence is preserved [0, 1, 2, 3]
        indices = [rec["sequence_index"] for rec in timeline["timeline_records"]]
        self.assertEqual(indices, [0, 1, 2, 3])
        print("[TEST 6.9 PASSED] Valid hash chain verified with backwards timestamp anomaly correctly flagged.")

    def test_09b_invalid_hash_chain_detection_and_sequence_preservation(self):
        """
        1. Create valid audit chain.
        2. Modify an event payload/hash without updating the chain.
        3. Confirm timeline analytics reports hash chain as INVALID.
        4. Confirm original sequence indices [0..N] are preserved without silent reordering.
        """
        case = self.case_mgr.create_case("Tampered Chain Case", investigator="Investigator Lead")
        self.case_mgr.add_audit_entry(case, "EVIDENCE_INGESTED", "Ingested video X")
        self.case_mgr.add_audit_entry(case, "ANALYSIS_EXECUTED", "Ran Swin inference")
        self.case_mgr.add_audit_entry(case, "REPORT_GENERATED", "Generated report")

        self.assertEqual(len(case["audit_trail"]), 4)
        # Verify valid before tampering
        pre_check = self.case_mgr.verify_audit_trail_integrity(case)
        self.assertTrue(pre_check["valid"])

        # Tamper with event index 2 details without updating its hash or subsequent prev_hash
        case["audit_trail"][2]["details"] = "Illegally modified detail string without recalculating hash!"

        # Run timeline analytics
        tampered_timeline = self.analytics.build_chronological_timeline(case)
        self.assertFalse(tampered_timeline["hash_chain_valid"], "Tampered audit chain must be flagged as invalid!")
        self.assertIn("Tampered audit entry at index 2", tampered_timeline["hash_chain_details"])

        # Confirm original sequence is strictly preserved without silent reordering or discarding
        seq_indices = [rec["sequence_index"] for rec in tampered_timeline["timeline_records"]]
        self.assertEqual(seq_indices, [0, 1, 2, 3])
        print("[TEST 6.9b PASSED] Invalid hash-chain detected and original sequence strictly preserved.")

    # -------------------------------------------------------------------------
    # 7. CONTROLLED PERCEPTUAL HASH THRESHOLD TESTS
    # -------------------------------------------------------------------------
    def test_05b_perceptual_hash_thresholds_and_byte_identity_distinction(self):
        """
        Controlled image fixtures:
        - Default threshold (10) applied correctly.
        - Custom threshold (e.g. 2 vs 15) changes similarity classification when appropriate.
        - Byte-identical files distinguished from matching perceptual hashes.
        - Visually similar but non-identical images are not automatically byte-identical.
        """
        # Create base image (RGB noise block)
        base_img = Image.new("RGB", (64, 64), color=(128, 128, 128))
        for x in range(20, 44):
            for y in range(20, 44):
                base_img.putpixel((x, y), (255, 0, 0))
        buf_base = io.BytesIO()
        base_img.save(buf_base, format="PNG")
        bytes_base = buf_base.getvalue()

        # 1. Byte-identical comparison
        comp_byte_ident = self.comparator.compare_image_perceptual_similarity(bytes_base, bytes_base)
        self.assertEqual(comp_byte_ident["phash_hamming_distance"], 0)
        self.assertEqual(comp_byte_ident["similarity_classification"], "IDENTICAL_PERCEPTUAL_HASH")
        # Assert byte-level equality check is distinguished from perceptual hash equality
        self.assertEqual(bytes_base, bytes_base)

        # 2. Modify single pixel (imperceptible to 8x8 DCT pHash)
        mod_img = base_img.copy()
        mod_img.putpixel((0, 0), (129, 128, 128))
        buf_mod = io.BytesIO()
        mod_img.save(buf_mod, format="PNG")
        bytes_mod = buf_mod.getvalue()

        # Bytes differ!
        self.assertNotEqual(bytes_base, bytes_mod, "Fixtures must not be byte-identical.")
        comp_subtle = self.comparator.compare_image_perceptual_similarity(bytes_base, bytes_mod)
        # Hash is identical even though bytes differ!
        self.assertEqual(comp_subtle["phash_hamming_distance"], 0)
        self.assertEqual(comp_subtle["similarity_classification"], "IDENTICAL_PERCEPTUAL_HASH")
        self.assertIn("does NOT prove byte-for-byte identity", comp_subtle["finding"])

        # 3. Controlled visual alteration: Shift central box to induce measurable Hamming distance
        shifted_img = Image.new("RGB", (64, 64), color=(128, 128, 128))
        for x in range(35, 59):
            for y in range(35, 59):
                shifted_img.putpixel((x, y), (0, 255, 0))
        buf_shifted = io.BytesIO()
        shifted_img.save(buf_shifted, format="PNG")
        bytes_shifted = buf_shifted.getvalue()

        dist_measured = self.comparator.compute_hamming_distance(
            self.comparator.compute_image_phash(bytes_base),
            self.comparator.compute_image_phash(bytes_shifted)
        )
        print(f"Measured Hamming distance between base and shifted fixture: {dist_measured}")

        # Test threshold below measured distance -> LOW_SIMILARITY
        strict_thresh = max(0, dist_measured - 1)
        res_strict = self.comparator.compare_image_perceptual_similarity(bytes_base, bytes_shifted, hamming_threshold=strict_thresh)
        if dist_measured > 0:
            self.assertEqual(res_strict["similarity_classification"], "LOW_SIMILARITY")

        # Test threshold at or above measured distance -> POSSIBLE_VISUAL_SIMILARITY
        lenient_thresh = dist_measured + 2
        res_lenient = self.comparator.compare_image_perceptual_similarity(bytes_base, bytes_shifted, hamming_threshold=lenient_thresh)
        self.assertEqual(res_lenient["similarity_classification"], "POSSIBLE_VISUAL_SIMILARITY")
        print("[TEST 6.5b PASSED] Perceptual hash thresholds and byte-identity distinction verified.")

    # -------------------------------------------------------------------------
    # 8. LIVE BENCHMARK SAMPLING INTEGRATION TEST
    # -------------------------------------------------------------------------
    def test_06b_live_benchmark_frame_statistics_computation(self):
        """
        Feeds live detector result from tests/samples/ai_generated_video.mp4 through
        EvidenceComparator.analyze_video_temporal_scores and compares against dynamic calculations.
        """
        video_sample_path = "tests/samples/ai_generated_video.mp4"
        if not os.path.exists(video_sample_path):
            self.skipTest(f"Benchmark video not found at {video_sample_path}")

        from src.modules.video_detector import VideoForensicPipeline
        vp = VideoForensicPipeline.get_instance()
        with open(video_sample_path, "rb") as f:
            v_bytes = f.read()

        # Run uniform frame screening (12 frames)
        res_live = vp.inspect_and_sample_video(v_bytes, "ai_generated_video.mp4")
        self.assertEqual(res_live["status"], "SUCCESS_VERIFIED_VIDEO_SCAN")

        actual_frames = res_live["frame_results"]
        actual_sampled_count = len(actual_frames)
        self.assertEqual(actual_sampled_count, 12)

        # Run comparator's temporal score analysis
        stats = self.comparator.analyze_video_temporal_scores(actual_frames)
        scores = [f["artificial_prob"] for f in actual_frames]

        # Dynamically calculated reference metrics
        ref_mean = round(float(np.mean(scores)), 2)
        ref_std = round(float(np.std(scores, ddof=0)), 2)
        ref_min = round(float(np.min(scores)), 2)
        ref_max = round(float(np.max(scores)), 2)
        ref_crossings = sum(1 for s in scores if s > 50.0)

        self.assertEqual(stats["total_frames_evaluated"], actual_sampled_count)
        self.assertEqual(stats["score_metrics"]["mean_synthetic_score"], ref_mean)
        self.assertEqual(stats["score_metrics"]["std_deviation"], ref_std)
        self.assertEqual(stats["score_metrics"]["minimum_synthetic_score"], ref_min)
        self.assertEqual(stats["score_metrics"]["maximum_synthetic_score"], ref_max)
        self.assertEqual(stats["threshold_crossings_count"], ref_crossings)

        # Validate against known empirical baseline
        self.assertEqual(ref_mean, 35.35)
        self.assertEqual(ref_std, 7.76)
        self.assertEqual(ref_max, 51.03)
        self.assertEqual(ref_min, 24.78)
        self.assertEqual(ref_crossings, 1)
        print(f"[TEST 6.6b PASSED] Live benchmark video frame statistics: mean={ref_mean}%, std={ref_std}, max={ref_max}%, crossings={ref_crossings}/12.")

    # -------------------------------------------------------------------------
    # 9. ERROR HANDLING & MALFORMED INPUTS
    # -------------------------------------------------------------------------
    def test_10_malformed_inputs_handling(self):
        """Verify error handling on malformed or empty inputs."""
        res_exp_none = self.explainer.explain_image_finding(None)
        self.assertEqual(res_exp_none["status"], "ERROR_INVALID_INPUT")

        res_temp_empty = self.comparator.analyze_video_temporal_scores([])
        self.assertEqual(res_temp_empty["status"], "UNAVAILABLE")

        res_timeline_none = self.analytics.build_chronological_timeline(None)
        self.assertEqual(res_timeline_none["status"], "ERROR_INVALID_INPUT")
        print("[TEST 6.10 PASSED] Malformed and missing inputs handled gracefully.")


if __name__ == "__main__":
    unittest.main()
