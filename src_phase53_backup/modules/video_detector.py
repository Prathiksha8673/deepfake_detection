"""
DEEPFAKE X - Video Deepfake Screening Pipeline
Frame-level synthetic artifact extraction & neural screening.
Zero-fabrication ISO/IEC 27037 compliant architecture.
Integrates with OpenCV for timestamp-based decoding and reuses
ImageForensicDetector for GPU-accelerated Swin Transformer inference.
"""

import os
import cv2
import time
import hashlib
import tempfile
import logging
from typing import Dict, Any, List, Optional
from PIL import Image

from src.modules.image_detector import ImageForensicDetector

logger = logging.getLogger("deepfakex.video_detector")

DEFAULT_MAX_DURATION_SECONDS = 60.0
DEFAULT_MAX_FILESIZE_BYTES = 100 * 1024 * 1024  # 100 MB
DEFAULT_SAMPLE_FRAMES = 12

class VideoForensicPipeline:
    _instance: Optional["VideoForensicPipeline"] = None

    @classmethod
    def get_instance(cls) -> "VideoForensicPipeline":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # Obtain singleton image detector instance (reuses model in VRAM)
        self.detector = ImageForensicDetector.get_instance()

    @staticmethod
    def compute_sha256(file_bytes: bytes) -> str:
        return hashlib.sha256(file_bytes).hexdigest()

    def inspect_and_sample_video(
        self,
        video_bytes: bytes,
        filename: str,
        num_frames: int = DEFAULT_SAMPLE_FRAMES,
        max_duration: float = DEFAULT_MAX_DURATION_SECONDS,
        max_size_bytes: int = DEFAULT_MAX_FILESIZE_BYTES,
    ) -> Dict[str, Any]:
        """
        Validates video file parameters, extracts metadata, performs uniform timestamp-based
        frame sampling, and runs frame-level neural inference.
        Safely manages temporary files with guaranteed cleanup.
        """
        start_pipeline = time.perf_counter()
        file_size = len(video_bytes)
        sha256_hash = self.compute_sha256(video_bytes)

        # 1. Size Validation
        if file_size > max_size_bytes:
            return {
                "error": f"File size ({file_size / (1024*1024):.2f} MB) exceeds maximum allowed limit of {max_size_bytes / (1024*1024):.0f} MB.",
                "status": "ERROR_FILE_TOO_LARGE",
                "sha256": sha256_hash,
            }

        if file_size == 0:
            return {
                "error": "Uploaded video file is empty (0 bytes).",
                "status": "ERROR_EMPTY_FILE",
                "sha256": sha256_hash,
            }

        # 2. Extension validation
        _, ext = os.path.splitext(filename.lower())
        if ext not in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
            return {
                "error": f"Unsupported video container format '{ext}'. Expected MP4, MOV, or AVI.",
                "status": "ERROR_UNSUPPORTED_FORMAT",
                "sha256": sha256_hash,
            }

        # 3. Create safe temporary file for OpenCV decoding
        temp_fd, temp_path = tempfile.mkstemp(suffix=ext)
        try:
            with os.fdopen(temp_fd, "wb") as f_out:
                f_out.write(video_bytes)

            cap = cv2.VideoCapture(temp_path)
            if not cap.isOpened():
                return {
                    "error": "Failed to decode video stream. The video codec may be corrupted or unsupported by OpenCV.",
                    "status": "ERROR_CODEC_DECODE_FAILED",
                    "sha256": sha256_hash,
                }

            # 4. Extract stream properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Handle variable or unreliably reported FPS
            if fps <= 0 or fps is None:
                fps = 25.0  # standard fallback estimate

            duration = total_frames / fps if (total_frames > 0 and fps > 0) else 0.0

            if duration > max_duration:
                cap.release()
                return {
                    "error": f"Video duration ({duration:.1f}s) exceeds maximum allowed screening limit of {max_duration:.0f}s.",
                    "status": "ERROR_DURATION_EXCEEDED",
                    "sha256": sha256_hash,
                    "duration_sec": round(duration, 2),
                }

            if total_frames <= 0:
                cap.release()
                return {
                    "error": "Video contains 0 decodable frames.",
                    "status": "ERROR_ZERO_FRAMES",
                    "sha256": sha256_hash,
                }

            # 5. Determine target timestamps for uniform frame sampling
            num_to_sample = min(num_frames, max(1, total_frames))
            if num_to_sample == 1 or duration <= 0.0:
                target_msecs = [0.0]
            else:
                step_msec = (duration * 1000.0) / float(num_to_sample)
                target_msecs = [i * step_msec for i in range(num_to_sample)]

            sampled_frames_data: List[Dict[str, Any]] = []

            for idx, target_ms in enumerate(target_msecs):
                cap.set(cv2.CAP_PROP_POS_MSEC, target_ms)
                ret, frame_bgr = cap.read()

                # Fallback to frame index seeking if millisecond seek fails
                if not ret or frame_bgr is None:
                    target_frame_idx = int((target_ms / (duration * 1000.0 if duration > 0 else 1.0)) * total_frames)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, min(target_frame_idx, total_frames - 1))
                    ret, frame_bgr = cap.read()

                if not ret or frame_bgr is None:
                    logger.warning(f"Frame at target {target_ms:.1f}ms could not be read; skipping.")
                    continue

                actual_msec = cap.get(cv2.CAP_PROP_POS_MSEC)
                timestamp_sec = actual_msec / 1000.0 if actual_msec > 0 else (target_ms / 1000.0)
                formatted_ts = f"{int(timestamp_sec // 60):02d}:{timestamp_sec % 60:05.2f}"

                # Convert OpenCV BGR to PIL RGB
                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                pil_frame = Image.fromarray(frame_rgb)

                # Execute real neural frame inference
                pred = self.detector.analyze_image(pil_frame)

                # Create lightweight thumbnail for UI rendering
                thumb = pil_frame.copy()
                thumb.thumbnail((256, 256))

                sampled_frames_data.append({
                    "frame_index": idx + 1,
                    "target_timestamp_sec": round(target_ms / 1000.0, 2),
                    "reported_timestamp_sec": round(timestamp_sec, 2),
                    "formatted_timestamp": formatted_ts,
                    "thumbnail": thumb,
                    "classification": pred.get("classification", "Unknown"),
                    "is_synthetic": pred.get("is_synthetic", False),
                    "confidence_pct": pred.get("confidence_pct", 0.0),
                    "artificial_prob": pred.get("artificial_prob", 0.0),
                    "human_prob": pred.get("human_prob", 0.0),
                    "inference_time_ms": pred.get("inference_time_ms", 0.0),
                    "device": pred.get("device", "CPU"),
                })

            cap.release()

        finally:
            # Safe temporary file cleanup
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as e:
                    logger.error(f"Failed to remove temporary video file {temp_path}: {e}")

        total_sampled = len(sampled_frames_data)
        if total_sampled == 0:
            return {
                "error": "Unable to extract any decodable frames from the video container.",
                "status": "ERROR_NO_FRAMES_EXTRACTED",
                "sha256": sha256_hash,
            }

        # 6. Aggregate Forensic Metrics
        synthetic_count = sum(1 for f in sampled_frames_data if f["is_synthetic"])
        authentic_count = total_sampled - synthetic_count
        art_scores = [f["artificial_prob"] for f in sampled_frames_data]
        mean_synthetic_score = sum(art_scores) / total_sampled
        max_synthetic_score = max(art_scores)

        # Identify frames with the highest synthetic score
        peak_frames = [f for f in sampled_frames_data if f["artificial_prob"] == max_synthetic_score]
        peak_timestamps = [f["formatted_timestamp"] for f in peak_frames]

        total_elapsed = (time.perf_counter() - start_pipeline) * 1000.0

        return {
            "status": "SUCCESS_VERIFIED_VIDEO_SCAN",
            "filename": filename,
            "sha256": sha256_hash,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "video_metadata": {
                "duration_seconds": round(duration, 2),
                "resolution": f"{width} × {height}",
                "fps": round(fps, 2),
                "total_stream_frames": total_frames,
            },
            "sampling_config": {
                "requested_frames": num_frames,
                "successfully_sampled": total_sampled,
            },
            "summary": {
                "total_analyzed_frames": total_sampled,
                "synthetic_flagged_count": synthetic_count,
                "authentic_flagged_count": authentic_count,
                "mean_synthetic_score": round(mean_synthetic_score, 2),
                "highest_synthetic_score": round(max_synthetic_score, 2),
                "peak_timestamps": peak_timestamps,
                "hardware_device": self.detector.device_name,
                "total_processing_latency_ms": round(total_elapsed, 2),
                "screening_scope": "Frame-Level Latent Artifact Screening (Not temporal / face-swap biometrics)",
            },
            "frame_results": sampled_frames_data,
        }

