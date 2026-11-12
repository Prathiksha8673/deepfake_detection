"""
DEEPFAKE X - Grounded Forensic Explainability Engine (Phase 6)
Provides rigorous, scientifically grounded explainability for neural detector results.
Decomposes verified preprocessing, uncalibrated softmax scores, and discrete classifications.
Explicitly documents operational uncertainty and model exclusions without fabricating
logits, attention maps, or latent manifold representations.
"""

from typing import Dict, Any, List, Optional


class ForensicExplainer:
    _instance: Optional["ForensicExplainer"] = None

    @classmethod
    def get_instance(cls) -> "ForensicExplainer":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def explain_image_finding(self, image_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decomposes image forensic inference based strictly on ImageForensicDetector return schema.
        """
        if not isinstance(image_result, dict):
            return {"error": "Invalid input: image_result must be a dictionary.", "status": "ERROR_INVALID_INPUT"}

        if image_result.get("status") != "VERIFIED_AUTHENTIC_INFERENCE":
            return {
                "status": "UNAVAILABLE",
                "reason": f"Image detection did not succeed or returned error: {image_result.get('error', 'Incomplete analysis')}"
            }

        filename = image_result.get("filename", "image_evidence")
        classification = image_result.get("classification", "Unknown")
        is_synthetic = image_result.get("is_synthetic", False)
        artificial_prob = image_result.get("artificial_prob", 0.0)
        human_prob = image_result.get("human_prob", 0.0)
        dimensions = image_result.get("dimensions", "Unknown")
        device = image_result.get("device", "Unknown")
        latency_ms = image_result.get("inference_time_ms", 0.0)
        arch = image_result.get("model_architecture", "SwinForImageClassification")
        model_id = image_result.get("model_id", "umm-maybe/AI-image-detector")

        return {
            "modality": "IMAGE",
            "evidence_target": filename,
            "pipeline_specification": {
                "model_id": model_id,
                "model_architecture": arch,
                "execution_hardware": device,
                "inference_latency_ms": latency_ms,
            },
            "verified_preprocessing": {
                "color_space": "RGB conversion enforced via PIL (grayscale converted to RGB)",
                "input_resolution": dimensions,
                "tensor_normalization": "AutoImageProcessor ImageNet standard (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])",
                "spatial_resizing": "Standard Swin Transformer patch partition (224 × 224 input tensor)",
            },
            "output_interpretation": {
                "raw_logits": "Unavailable (raw neural logits are internal to the model execution context and not exported in the detector return dictionary)",
                "uncalibrated_softmax_scores": {
                    "synthetic_probability_pct": artificial_prob,
                    "authentic_probability_pct": human_prob,
                    "probability_sum_pct": round(artificial_prob + human_prob, 2),
                },
                "decision_threshold": "Fixed operational threshold at 50.0% (synthetic if artificial_prob > human_prob)",
                "assigned_classification": classification,
                "is_synthetic_flagged": is_synthetic,
            },
            "uncertainty_and_invalidation_factors": [
                "Uncalibrated Softmax Activations: Probabilities reflect normalized exponential outputs of a discriminative linear head, not true frequentist probabilities of generation.",
                "Out-of-Distribution Degradation: Vision transformers trained on diffusion and GAN models (e.g., Midjourney, SD 1.5) exhibit domain shift and false negatives on novel architectures (Flux, SDXL) or unseen rendering engines.",
                "Lossy Compression Dampening: Heavy JPEG re-compression, social media transcoding, or spatial downsampling can erase high-frequency generator artifacts, artificially lowering synthetic confidence.",
            ],
            "explicit_operational_exclusions": [
                "Does not perform pixel-level generative artifact localization or spatial segmentation.",
                "Does not identify the specific prompt, creator, platform, or generator version used.",
                "Does not prove legal authenticity or human intent; results serve advisory forensic screening purposes only.",
            ],
        }

    def explain_video_finding(self, video_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decomposes uniform video frame screening based strictly on VideoForensicPipeline return schema.
        Reads actual sampling_config and frame_results dynamically.
        """
        if not isinstance(video_result, dict):
            return {"error": "Invalid input: video_result must be a dictionary.", "status": "ERROR_INVALID_INPUT"}

        if video_result.get("status") != "SUCCESS_VERIFIED_VIDEO_SCAN":
            return {
                "status": "UNAVAILABLE",
                "reason": f"Video analysis did not succeed: {video_result.get('error', 'Incomplete scan')}"
            }

        filename = video_result.get("filename", "video_evidence")
        summary = video_result.get("summary", {})
        meta = video_result.get("video_metadata", {})
        sampling_cfg = video_result.get("sampling_config", {})
        frames = video_result.get("frame_results", [])

        total_sampled = summary.get("total_analyzed_frames", len(frames))
        synthetic_count = summary.get("synthetic_flagged_count", 0)
        authentic_count = summary.get("authentic_flagged_count", 0)
        mean_score = summary.get("mean_synthetic_score", 0.0)
        highest_score = summary.get("highest_synthetic_score", 0.0)
        peak_ts = summary.get("peak_timestamps", [])

        # Extract per-frame score list
        frame_scores = [f.get("artificial_prob", 0.0) for f in frames] if frames else []

        return {
            "modality": "VIDEO",
            "evidence_target": filename,
            "pipeline_specification": {
                "frame_extractor": "OpenCV VideoCapture (cv2.VideoCapture) from temporary container",
                "frame_detector_backbone": "Swin Transformer (umm-maybe/AI-image-detector)",
                "execution_hardware": summary.get("hardware_device", "Unknown"),
                "total_processing_latency_ms": summary.get("total_processing_latency_ms", 0.0),
                "screening_scope": summary.get("screening_scope", "Frame-Level Latent Artifact Screening"),
            },
            "container_telemetry": {
                "duration_seconds": meta.get("duration_seconds", 0.0),
                "resolution": meta.get("resolution", "Unknown"),
                "fps": meta.get("fps", 0.0),
                "total_stream_frames": meta.get("total_stream_frames", 0),
            },
            "sampling_implementation": {
                "requested_frames": sampling_cfg.get("requested_frames", 0),
                "actual_frames_sampled": total_sampled,
                "sampling_strategy": "Uniform temporal spacing (step_msec = duration / requested_frames)",
                "seek_mechanism": "Primary cv2.CAP_PROP_POS_MSEC seeking with fallback to cv2.CAP_PROP_POS_FRAMES seeking",
                "timestamp_reporting": "Actual decoded frame timestamps via cv2.CAP_PROP_POS_MSEC (not assumed target timestamps)",
            },
            "output_interpretation": {
                "raw_logits": "Unavailable (raw neural logits are internal to the model execution context and not exported in the detector return dictionary)",
                "frame_level_threshold": "Fixed operational threshold at 50.0% artificial probability",
                "flagged_frames_count": synthetic_count,
                "authentic_frames_count": authentic_count,
                "mean_synthetic_score": mean_score,
                "peak_synthetic_score": highest_score,
                "peak_timestamps": peak_ts,
                "individual_frame_scores": frame_scores,
            },
            "uncertainty_and_invalidation_factors": [
                "Temporal Sparsity: Uniform sampling analyses discrete keyframes; manipulations localized between sampled intervals will not be captured.",
                "Codec Compression Attenuation: H.264/H.265 temporal inter-frame prediction (P-frames, B-frames) and macroblock quantization attenuate high-frequency generative artifacts, suppressing synthetic scores.",
                "Variable Frame Rates (VFR): Variable frame rates or container timestamp jitter may introduce seeking drift.",
            ],
            "explicit_operational_exclusions": [
                "Does not perform facial landmark tracking, eye-gaze tracking, or head-pose consistency verification.",
                "Does not perform lip-sync synchronization analysis or acoustic-phonetic correlation.",
                "Does not detect face-swap boundary blending, mask feathering, or spatiotemporal flicker.",
            ],
        }

    def explain_audio_finding(self, audio_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decomposes acoustic voice cloning inference based strictly on AudioForensicDetector return schema.
        """
        if not isinstance(audio_result, dict):
            return {"error": "Invalid input: audio_result must be a dictionary.", "status": "ERROR_INVALID_INPUT"}

        if audio_result.get("status") != "SUCCESS_VERIFIED_AUDIO_SCAN":
            return {
                "status": "UNAVAILABLE",
                "reason": f"Audio analysis did not succeed: {audio_result.get('error', 'Incomplete scan')}"
            }

        filename = audio_result.get("filename", "audio_evidence")
        classification = audio_result.get("classification", "Unknown")
        is_synthetic = audio_result.get("is_synthetic", False)
        syn_score = audio_result.get("synthetic_score", 0.0)
        auth_score = audio_result.get("authentic_score", 0.0)
        confidence_pct = audio_result.get("confidence_pct", 0.0)
        device = audio_result.get("device", "Unknown")
        latency_ms = audio_result.get("inference_time_ms", 0.0)
        meta = audio_result.get("audio_metadata", {})

        return {
            "modality": "AUDIO",
            "evidence_target": filename,
            "pipeline_specification": {
                "model_id": "MelodyMachine/Deepfake-audio-detection-V2",
                "model_architecture": "Wav2Vec 2.0 Sequence Classification (Wav2Vec2ForSequenceClassification)",
                "execution_hardware": device,
                "inference_latency_ms": latency_ms,
            },
            "verified_preprocessing": {
                "audio_decoding": "soundfile (sf.read) as float32 array",
                "downmixing": "Stereo-to-mono arithmetic averaging across channels (no aggressive amplitude normalization)",
                "target_sampling_rate_hz": meta.get("target_sample_rate_hz", 16000),
                "original_sampling_rate_hz": meta.get("original_sample_rate_hz", 0),
                "resampling_method": "Polyphase non-destructive resampling (scipy.signal.resample) when original != 16000 Hz",
                "energy_validation": f"RMS energy safeguard: {meta.get('rms_energy', 0.0)} (minimum threshold 0.001)",
            },
            "output_interpretation": {
                "raw_logits": "Unavailable (raw neural logits are internal to the model execution context and not exported in the detector return dictionary)",
                "class_index_mapping": "Class 0 = fake (synthetic/cloned), Class 1 = real (authentic human speech)",
                "uncalibrated_softmax_scores": {
                    "synthetic_score_pct": syn_score,
                    "authentic_score_pct": auth_score,
                    "probability_sum_pct": round(syn_score + auth_score, 2),
                },
                "decision_threshold": "Fixed operational threshold at 50.0% (synthetic if synthetic_score > authentic_score)",
                "assigned_classification": classification,
                "is_synthetic_flagged": is_synthetic,
                "model_confidence_pct": confidence_pct,
            },
            "uncertainty_and_invalidation_factors": [
                "Vocoder Domain Shift (Empirical False Negatives): The Wav2Vec2 backbone was trained on legacy TTS and vocoders (HiFi-GAN, WaveNet); empirical benchmarks demonstrate 0.0% synthetic scores (100% false negative) on modern flow-matching neural voice clones (ElevenLabs).",
                "Acoustic Channel Sensitivity: Telephony bandpass filtering (300-3400 Hz), lossy audio codecs (MP3/AAC compression at low bitrates), and historical radio distortion induce out-of-distribution feature responses that can trigger false alarms.",
                "Non-Speech Noise: Background acoustic noise, reverberation, and instrumental music can confound self-supervised speech representations.",
            ],
            "explicit_operational_exclusions": [
                "Does not perform biometric speaker verification or individual voiceprint matching.",
                "Does not identify the person speaking or establish individual identity.",
                "Does not verify linguistic semantics, phonetic truthfulness, or generative speech script intent.",
            ],
        }

