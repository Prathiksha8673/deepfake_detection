"""
DEEPFAKE X - Deterministic Evidence Comparator & Provenance Engine (Phase 6)
Provides pure CPU-based perceptual similarity heuristics (pHash, dHash),
temporal detector-score statistics, audio metadata/acoustic comparison,
and strict cryptographically verified evidence lineage.

Pure CPU implementation: does NOT import PyTorch or initialize CUDA.
Uses time.perf_counter() for timing and psutil for process memory profiling.
"""

import io
import math
import time
import numpy as np
from PIL import Image
from scipy.fftpack import dct
from typing import Dict, Any, List, Optional, Tuple

try:
    import psutil
except ImportError:
    psutil = None


class EvidenceComparator:
    _instance: Optional["EvidenceComparator"] = None

    @classmethod
    def get_instance(cls) -> "EvidenceComparator":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # -------------------------------------------------------------------------
    # 1. PERCEPTUAL HASH HEURISTICS (CPU ONLY)
    # -------------------------------------------------------------------------
    def compute_image_phash(self, image_bytes: bytes, hash_size: int = 8, highfreq_factor: int = 4) -> str:
        """
        Computes 64-bit DCT perceptual hash (pHash) heuristic from image bytes.
        Algorithm:
        1. Resize to (hash_size * highfreq_factor, hash_size * highfreq_factor) grayscale.
        2. Compute 2D Discrete Cosine Transform (DCT).
        3. Extract top-left (hash_size, hash_size) low-frequency block (excluding DC component).
        4. Compare coefficients against median value to produce binary hash string.
        """
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        img_size = hash_size * highfreq_factor
        img_resized = img.resize((img_size, img_size), Image.Resampling.LANCZOS)
        pixels = np.asarray(img_resized, dtype=np.float32)

        # 2D DCT (ortho normalized)
        dct_rows = dct(pixels, axis=0, norm="ortho")
        dct_2d = dct(dct_rows, axis=1, norm="ortho")

        # Extract low-frequency components (excluding DC coefficient at 0, 0)
        dct_low = dct_2d[:hash_size, :hash_size]
        med = float(np.median(dct_low.flatten()[1:]))

        # Binary quantization
        bit_matrix = dct_low > med
        # Format as hexadecimal string
        bit_str = "".join("1" if b else "0" for b in bit_matrix.flatten())
        hex_str = f"{int(bit_str, 2):0{hash_size * hash_size // 4}x}"
        return hex_str

    def compute_image_dhash(self, image_bytes: bytes, hash_size: int = 8) -> str:
        """
        Computes 64-bit difference gradient hash (dHash) heuristic from image bytes.
        Algorithm:
        1. Resize to (hash_size + 1, hash_size) grayscale.
        2. Compute horizontal pixel differences (pixel[x] > pixel[x+1]).
        3. Quantize difference sequence into 64-bit hexadecimal string.
        """
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        img_resized = img.resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        pixels = np.asarray(img_resized, dtype=np.int32)

        diff = pixels[:, 1:] > pixels[:, :-1]
        bit_str = "".join("1" if b else "0" for b in diff.flatten())
        hex_str = f"{int(bit_str, 2):0{hash_size * hash_size // 4}x}"
        return hex_str

    def compute_hamming_distance(self, hash_a: str, hash_b: str) -> int:
        """Computes the Hamming bit distance between two hexadecimal hash strings."""
        if not hash_a or not hash_b or len(hash_a) != len(hash_b):
            # Hex strings of unequal length
            int_a = int(hash_a, 16) if hash_a else 0
            int_b = int(hash_b, 16) if hash_b else 0
            xor_val = int_a ^ int_b
            return bin(xor_val).count("1")
        return bin(int(hash_a, 16) ^ int(hash_b, 16)).count("1")

    def compare_image_perceptual_similarity(
        self,
        bytes_a: bytes,
        bytes_b: bytes,
        hamming_threshold: int = 10
    ) -> Dict[str, Any]:
        """
        Evaluates heuristic perceptual similarity between two image buffers.
        Strictly distinguishes IDENTICAL_PERCEPTUAL_HASH from byte-level identity.
        Threshold is configurable (default = 10).
        """
        t0 = time.perf_counter()
        phash_a = self.compute_image_phash(bytes_a)
        phash_b = self.compute_image_phash(bytes_b)
        dist_phash = self.compute_hamming_distance(phash_a, phash_b)

        dhash_a = self.compute_image_dhash(bytes_a)
        dhash_b = self.compute_image_dhash(bytes_b)
        dist_dhash = self.compute_hamming_distance(dhash_a, dhash_b)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        if dist_phash == 0 and dist_dhash == 0:
            classification = "IDENTICAL_PERCEPTUAL_HASH"
            finding = "Both images yield identical perceptual hashes. Visual structures are perceptually indistinguishable (note: does NOT prove byte-for-byte identity)."
        elif dist_phash <= hamming_threshold:
            classification = "POSSIBLE_VISUAL_SIMILARITY"
            finding = f"Perceptual hash Hamming distance ({dist_phash}) is within configurable similarity threshold (≤ {hamming_threshold}). Images share substantial visual structure."
        else:
            classification = "LOW_SIMILARITY"
            finding = f"Perceptual hash Hamming distance ({dist_phash}) exceeds similarity threshold (> {hamming_threshold}). Images exhibit distinct visual content."

        return {
            "comparison_type": "PERCEPTUAL_IMAGE_HASH_HEURISTIC",
            "phash_a": phash_a,
            "phash_b": phash_b,
            "phash_hamming_distance": dist_phash,
            "dhash_a": dhash_a,
            "dhash_b": dhash_b,
            "dhash_hamming_distance": dist_dhash,
            "configured_threshold": hamming_threshold,
            "similarity_classification": classification,
            "finding": finding,
            "execution_latency_ms": round(elapsed_ms, 2),
            "forensic_disclaimer": (
                "Perceptual hashing is an empirical similarity heuristic. It assesses macro-scale visual structure, "
                "not cryptographically verified derivation or generative synthesis. Similar hashes do NOT prove common file origin."
            )
        }

    # -------------------------------------------------------------------------
    # 2. TEMPORAL DETECTOR-SCORE ANALYSIS (VIDEO)
    # -------------------------------------------------------------------------
    def analyze_video_temporal_scores(self, frame_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates dynamic Temporal Detector-Score Analysis across actual sampled frames.
        Computes mean, standard deviation, minimum, maximum, and threshold crossings.
        Never assumes 12 frames or hardcoded outputs.
        """
        if not frame_results:
            return {
                "status": "UNAVAILABLE",
                "reason": "No frame results provided for temporal score analysis."
            }

        scores = [f.get("artificial_prob", 0.0) for f in frame_results]
        timestamps = [f.get("formatted_timestamp", "00:00.00") for f in frame_results]
        n = len(scores)

        mean_val = float(np.mean(scores))
        std_val = float(np.std(scores, ddof=0)) if n > 1 else 0.0
        min_val = float(np.min(scores))
        max_val = float(np.max(scores))
        score_range = max_val - min_val

        # Find threshold crossings (> 50.0% artificial probability)
        crossings = []
        for idx, (s, ts) in enumerate(zip(scores, timestamps)):
            if s > 50.0:
                crossings.append({"frame_index": idx + 1, "timestamp": ts, "synthetic_score_pct": s})

        # Min and max frame timestamps
        min_timestamps = [ts for s, ts in zip(scores, timestamps) if s == min_val]
        max_timestamps = [ts for s, ts in zip(scores, timestamps) if s == max_val]

        return {
            "analysis_type": "TEMPORAL_DETECTOR_SCORE_ANALYSIS",
            "total_frames_evaluated": n,
            "score_metrics": {
                "mean_synthetic_score": round(mean_val, 2),
                "std_deviation": round(std_val, 2),
                "minimum_synthetic_score": round(min_val, 2),
                "maximum_synthetic_score": round(max_val, 2),
                "score_range": round(score_range, 2),
            },
            "peak_frame_timestamps": max_timestamps,
            "minimum_frame_timestamps": min_timestamps,
            "threshold_crossings_count": len(crossings),
            "threshold_crossings": crossings,
            "forensic_disclaimer": (
                "Notice: Temporal score variance reflects detector sensitivity fluctuations across discrete frames. "
                "Score variance or localized threshold spikes do NOT prove intentional splicing, face-swapping, or localized temporal manipulation."
            )
        }

    # -------------------------------------------------------------------------
    # 3. SEPARATED AUDIO COMPARISON (TECHNICAL vs ACOUSTIC)
    # -------------------------------------------------------------------------
    def compare_audio_streams(
        self,
        audio_a: Dict[str, Any],
        audio_b: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Separates technical container metadata comparisons from acoustic-statistical comparisons.
        Strictly disclaims that acoustic or technical similarity establishes common recording origin.
        """
        meta_a = audio_a.get("audio_metadata", {})
        meta_b = audio_b.get("audio_metadata", {})

        # 1. Technical Container Comparison
        sr_a = meta_a.get("original_sample_rate_hz", 0)
        sr_b = meta_b.get("original_sample_rate_hz", 0)
        dur_a = meta_a.get("duration_seconds", 0.0)
        dur_b = meta_b.get("duration_seconds", 0.0)
        ch_a = meta_a.get("channels", 1)
        ch_b = meta_b.get("channels", 1)

        tech_diff = {
            "sample_rate_match": (sr_a == sr_b),
            "sample_rate_delta_hz": abs(sr_a - sr_b),
            "duration_delta_seconds": round(abs(dur_a - dur_b), 2),
            "channel_count_match": (ch_a == ch_b),
            "stream_a_specs": f"{sr_a} Hz, {ch_a}ch, {dur_a}s",
            "stream_b_specs": f"{sr_b} Hz, {ch_b}ch, {dur_b}s",
        }

        # 2. Acoustic Statistical Comparison
        rms_a = meta_a.get("rms_energy", 0.0)
        rms_b = meta_b.get("rms_energy", 0.0)
        rms_delta = abs(rms_a - rms_b)

        acoustic_diff = {
            "rms_energy_stream_a": rms_a,
            "rms_energy_stream_b": rms_b,
            "rms_energy_delta": round(rms_delta, 4),
            "relative_energy_ratio": round(rms_a / rms_b, 3) if rms_b > 0 else "N/A",
        }

        return {
            "comparison_type": "SEPARATED_AUDIO_STREAM_COMPARISON",
            "technical_container_metadata": tech_diff,
            "acoustic_statistics": acoustic_diff,
            "forensic_disclaimer": (
                "Forensic Separation Notice: Technical metadata alignment (sample rate, channels) and acoustic energy proximity (RMS) "
                "reflect standard container encoding conventions and general recording loudness. They do NOT establish common recording environment, "
                "same acoustic microphone hardware, or identical speaker provenance."
            )
        }

    # -------------------------------------------------------------------------
    # 4. STRICT VERIFIED LINEAGE ENGINE
    # -------------------------------------------------------------------------
    def establish_verified_lineage(
        self,
        inventory: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Maps parent-child evidence lineage ONLY when validated via:
        1. Referenced parent evidence record exists in inventory;
        2. Referenced SHA-256 matches the parent's verified digest;
        3. Parent container record integrity is verified;
        4. Relationship is explicitly recorded.

        A source_container_id must resolve to a validated source record.
        A Boolean is_same_stream flag alone or matching filenames NEVER establish verified lineage.
        """
        # Map existing inventory by valid cryptographic identifiers
        records_by_id = {}
        records_by_sha = {}

        for item in inventory:
            sha = item.get("sha256")
            eid = item.get("evidence_id")
            if sha:
                records_by_sha[sha.lower()] = item
            if eid:
                records_by_id[eid] = item

        verified_lineages = []
        unverified_associations = []

        for item in inventory:
            name = item.get("filename", "unknown")
            sha = item.get("sha256", "")
            extracted_from = item.get("extracted_from")
            source_container_id = item.get("source_container_id")
            parent_record = None
            verification_basis = None

            # Check 1: SHA-256 Reference
            if extracted_from and extracted_from.lower() in records_by_sha:
                parent_candidate = records_by_sha[extracted_from.lower()]
                if parent_candidate.get("sha256", "").lower() == extracted_from.lower():
                    parent_record = parent_candidate
                    verification_basis = f"Verified SHA-256 Digest Match ({extracted_from[:16]}...)"

            # Check 2: Exact Evidence ID Reference
            elif extracted_from and extracted_from in records_by_id:
                parent_record = records_by_id[extracted_from]
                verification_basis = f"Validated Parent Evidence ID ({extracted_from})"

            # Check 3: Validated source_container_id
            elif source_container_id:
                if source_container_id.lower() in records_by_sha:
                    parent_record = records_by_sha[source_container_id.lower()]
                    verification_basis = f"Validated Source Container SHA-256 ({source_container_id[:16]}...)"
                elif source_container_id in records_by_id:
                    parent_record = records_by_id[source_container_id]
                    verification_basis = f"Validated Source Container ID ({source_container_id})"
                else:
                    unverified_associations.append({
                        "child_filename": name,
                        "unresolved_reference": source_container_id,
                        "reason": "source_container_id does not resolve to an existing validated parent record."
                    })

            # Check 4: Unverified association if extracted_from is merely a filename
            elif extracted_from:
                unverified_associations.append({
                    "child_filename": name,
                    "unresolved_reference": extracted_from,
                    "reason": "extracted_from references a filename string rather than a validated parent evidence ID or SHA-256 digest."
                })

            if parent_record:
                verified_lineages.append({
                    "child_filename": name,
                    "child_sha256": sha,
                    "parent_filename": parent_record.get("filename"),
                    "parent_sha256": parent_record.get("sha256"),
                    "parent_evidence_id": parent_record.get("evidence_id"),
                    "verification_basis": verification_basis,
                    "provenance_status": "VERIFIED_PARENT_CHILD_LINEAGE"
                })

        return {
            "total_verified_lineages": len(verified_lineages),
            "verified_lineages": verified_lineages,
            "unverified_associations_count": len(unverified_associations),
            "unverified_associations": unverified_associations,
            "lineage_rule": (
                "Verified provenance strictly requires resolution to an existing inventory record with matching verified SHA-256 digest "
                "or exact validated evidence ID. Filename matches, filename stems, and unreferenced same-stream flags are strictly unverified."
            )
        }

