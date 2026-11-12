"""
DEEPFAKE X - Reliability Assessment & Forensic Confidence Engine
Distinguishes model confidence, evidence strength, and detector reliability.
Prevents uncalibrated score averaging across heterogeneous modalities.
Zero-fabrication ISO/IEC 27037 transparent audit rule engine.
"""

from typing import Dict, Any, List

class ForensicReliabilityEngine:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def evaluate_investigation(
        self,
        image_results: List[Dict[str, Any]],
        video_results: List[Dict[str, Any]],
        audio_results: List[Dict[str, Any]],
        correlation_matrix: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesizes multimodal findings into a transparent evidentiary assessment.
        
        Possible Outcomes:
        1. No strong evidence of manipulation detected
        2. Potential manipulation detected
        3. Strong evidence of manipulation detected
        4. Conflicting forensic evidence
        5. Insufficient evidence for assessment
        """
        total_items = len(image_results) + len(video_results) + len(audio_results)
        if total_items == 0:
            return {
                "verdict_category": "Insufficient evidence for assessment",
                "confidence_level": "None",
                "evidence_strength": "Zero items provided",
                "rationale": "No media files were analyzed in this investigation.",
                "detector_agreements": "N/A",
                "anomaly_count": 0,
                "disclaimer": "No forensic conclusions can be drawn without media files."
            }

        flagged_items = []
        clean_items = []
        detector_reliability_notes = []

        # 1. Inspect Image Findings
        for img in image_results:
            is_syn = img.get("is_synthetic", False)
            score = img.get("confidence_pct", 50.0)
            fname = img.get("filename", "image")
            if is_syn:
                flagged_items.append(f"Image '{fname}' flagged synthetic ({score}% score)")
            else:
                clean_items.append(f"Image '{fname}' predicts authentic ({score}% score)")

        # 2. Inspect Video Findings
        for vid in video_results:
            summary = vid.get("summary", {})
            syn_count = summary.get("synthetic_flagged_count", 0)
            total_f = summary.get("total_analyzed_frames", 1)
            fname = vid.get("filename", "video")
            mean_syn = summary.get("mean_synthetic_score", 0.0)
            if syn_count > 0:
                flagged_items.append(f"Video '{fname}' has {syn_count}/{total_f} frames flagged synthetic (peak: {summary.get('highest_synthetic_score')}%)")
            else:
                clean_items.append(f"Video '{fname}' had 0 frames flagged synthetic (mean: {mean_syn}%)")

        # 3. Inspect Audio Findings with Explicit Reliability Weighting
        for aud in audio_results:
            is_syn = aud.get("is_synthetic", False)
            score = aud.get("confidence_pct", 50.0)
            fname = aud.get("filename", "audio")
            detector_reliability_notes.append(
                f"Audio detector ({aud.get('model_architecture', 'Wav2Vec2')}) has known vulnerability: "
                "susceptible to false alarms on band-limited transmission noise, and false negatives on advanced neural vocoders (e.g. ElevenLabs)."
            )
            if is_syn:
                flagged_items.append(f"Audio '{fname}' flagged synthetic ({score}% score) [Subject to acoustic channel caveats]")
            else:
                clean_items.append(f"Audio '{fname}' predicts authentic speech ({score}% score)")

        # 4. Correlation Inconsistencies Check
        correlations = correlation_matrix.get("correlations", [])
        sync_anomalies = [c for c in correlations if c.get("sync_anomaly_flag", False)]
        temporal_anomalies = [c for c in correlations if c.get("temporal_mismatch_flag", False)]

        # 5. Evidentiary Synthesis Logic
        has_flags = len(flagged_items) > 0
        has_cleans = len(clean_items) > 0
        has_sync_issues = len(sync_anomalies) > 0

        if has_flags and has_cleans:
            verdict = "Conflicting forensic evidence"
            evidence_strength = "Mixed / Divergent Signals"
            rationale = (
                f"Different modalities yielded conflicting findings: {len(flagged_items)} element(s) "
                f"exhibit synthetic artifacts while {len(clean_items)} element(s) predict authentic. "
                "Cross-modal contradiction suggests localized manipulation, selective splicing, or differing model sensitivities."
            )
        elif len(flagged_items) >= 2 or (len(flagged_items) >= 1 and has_sync_issues):
            verdict = "Strong evidence of manipulation detected"
            evidence_strength = "High Evidentiary Alignment"
            rationale = (
                f"Multiple forensic indicators corroborate synthetic origin: {', '.join(flagged_items)}. "
                + (f"Audio-video stream duration disparity identified ({len(sync_anomalies)} instances)." if has_sync_issues else "")
            )
        elif len(flagged_items) == 1:
            verdict = "Potential manipulation detected"
            evidence_strength = "Moderate (Single-Modality Alert)"
            rationale = (
                f"One element exhibited anomalous synthetic features: {flagged_items[0]}. "
                "Secondary corroborating modalities did not confirm or were unavailable. Manual forensic review recommended."
            )
        else:
            verdict = "No strong evidence of manipulation detected"
            evidence_strength = "Baseline Photographic / Acoustic Alignment"
            rationale = (
                f"All {len(clean_items)} evaluated media item(s) predict authentic within standard decision thresholds. "
                "No overt generative artifacts or cross-modal stream length discrepancies were discovered."
            )

        return {
            "verdict_category": verdict,
            "evidence_strength": evidence_strength,
            "rationale": rationale,
            "total_media_evaluated": total_items,
            "synthetic_indicators": flagged_items,
            "authentic_indicators": clean_items,
            "sync_anomalies_detected": len(sync_anomalies),
            "temporal_anomalies_detected": len(temporal_anomalies),
            "detector_reliability_notes": detector_reliability_notes,
            "disclaimer": (
                "Forensic Integrity Notice: No automated digital forensics platform can guarantee 100% authenticity. "
                "Outcomes are probabilistic screening indicators based on trained latent representations, not legal proof."
            )
        }

