"""
DEEPFAKE X - Reliability Assessment & Forensic Confidence Engine
Distinguishes model confidence, evidence strength, and detector reliability.
Prevents uncalibrated score averaging across heterogeneous modalities.
Zero-fabrication Structured Forensic Evidence Handling rule engine.
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
        
        Evaluates 5 standardized forensic categories:
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
                flagged_items.append(f"Image '{fname}' flagged synthetic ({score}% uncalibrated score)")
            else:
                clean_items.append(f"Image '{fname}' predicts authentic ({score}% uncalibrated score)")

        # 2. Inspect Video Findings
        for vid in video_results:
            summary = vid.get("summary", {})
            syn_count = summary.get("synthetic_flagged_count", 0)
            total_f = summary.get("total_analyzed_frames", 1)
            fname = vid.get("filename", "video")
            mean_syn = summary.get("mean_synthetic_score", 0.0)
            peak_syn = summary.get("highest_synthetic_score", 0.0)
            if syn_count > 0:
                flagged_items.append(f"Video '{fname}' has {syn_count}/{total_f} frames flagged synthetic (peak: {peak_syn}%)")
            else:
                clean_items.append(f"Video '{fname}' had 0 frames flagged synthetic (mean: {mean_syn}%)")

        # 3. Inspect Audio Findings with Explicit Reliability Weighting
        for aud in audio_results:
            is_syn = aud.get("is_synthetic", False)
            score = aud.get("confidence_pct", 50.0)
            fname = aud.get("filename", "audio")
            detector_reliability_notes.append(
                f"Audio detector ({aud.get('model_architecture', 'Wav2Vec2')}) known operational bounds: "
                "Reliable on legacy vocoders and acoustic formants; high false-negative risk on modern flow-matching voice clones (e.g., ElevenLabs)."
            )
            if is_syn:
                flagged_items.append(f"Audio '{fname}' flagged synthetic ({score}% uncalibrated score) [Subject to vocoder limitations]")
            else:
                clean_items.append(f"Audio '{fname}' predicts authentic speech ({score}% uncalibrated score)")

        # 4. Check for Verified Linked Stream Anomalies ONLY
        correlations = correlation_matrix.get("correlations", [])
        verified_sync_anomalies = [
            c for c in correlations 
            if c.get("sync_anomaly_flag", False) and c.get("relationship_type") == "LINKED_AUDIO_VIDEO_STREAM_ANALYSIS"
        ]

        # 5. Evidentiary Synthesis Logic
        # Rules:
        # A. If both flagged items AND clean items exist -> "Conflicting forensic evidence"
        # B. If flagged >= 2 independent corroborated modalities (or verified linked stream desync with >= 1 flagged) -> "Strong evidence of manipulation detected"
        # C. If flagged == 1 (and 0 clean items, e.g. single file evaluated or single flagged modality without counter-evidence) -> "Potential manipulation detected"
        # D. If flagged == 0 and clean > 0 -> "No strong evidence of manipulation detected"
        
        has_flags = len(flagged_items) > 0
        has_cleans = len(clean_items) > 0
        has_verified_stream_anomaly = len(verified_sync_anomalies) > 0

        if has_flags and has_cleans:
            verdict = "Conflicting forensic evidence"
            evidence_strength = "Mixed / Divergent Cross-Modal Signals"
            rationale = (
                f"Modality detectors yielded contradictory findings: {len(flagged_items)} element(s) "
                f"exhibit synthetic indicators ({'; '.join(flagged_items)}), while {len(clean_items)} element(s) "
                f"predict authentic ({'; '.join(clean_items)}). "
                "Because findings diverge across modalities, this cannot be classified as strong evidence of manipulation. "
                "Localized manipulation, selective splicing, or differing detector sensitivities may be responsible; manual examination is recommended."
            )
        elif len(flagged_items) >= 2 or (len(flagged_items) >= 1 and has_verified_stream_anomaly):
            verdict = "Strong evidence of manipulation detected"
            evidence_strength = "Corroborated Multi-Source Forensic Indicators"
            rationale = (
                f"Multiple independent forensic indicators corroborate synthetic origin: {'; '.join(flagged_items)}. "
                + (f"In addition, verified audio-video stream desynchronization was identified in {len(verified_sync_anomalies)} linked stream(s)." if has_verified_stream_anomaly else "")
            )
        elif len(flagged_items) == 1:
            verdict = "Potential manipulation detected"
            evidence_strength = "Moderate (Single-Modality Alert, No Corroboration)"
            rationale = (
                f"A single isolated media item exhibited synthetic indicators: {flagged_items[0]}. "
                "No secondary corroborated modalities confirmed this finding. Uncalibrated detector alerts require independent verification."
            )
        else:
            verdict = "No strong evidence of manipulation detected"
            evidence_strength = "Consistent Authentic Signatures Across Tested Modalities"
            rationale = (
                f"All {len(clean_items)} evaluated media item(s) predict authentic within standard decision thresholds. "
                "No overt generative artifacts or verified stream container anomalies were detected."
            )

        return {
            "verdict_category": verdict,
            "evidence_strength": evidence_strength,
            "rationale": rationale,
            "total_media_evaluated": total_items,
            "synthetic_indicators": flagged_items,
            "authentic_indicators": clean_items,
            "sync_anomalies_detected": len(verified_sync_anomalies),
            "detector_reliability_notes": detector_reliability_notes,
            "disclaimer": (
                "Forensic Integrity Notice: Automated digital forensics detection is probabilistic and exploratory. "
                "Outcomes reflect uncalibrated neural model activations and container heuristics, not legal or definitive proof."
            )
        }


