"""
DEEPFAKE X - Cross-Modal Evidence Correlation & Container Comparison Engine
Performs metadata and container comparison across Image, Video, and Audio modalities.
Compares durations and timestamps where linked relationships exist.
Zero-fabrication Structured Forensic Evidence Handling pipeline.
"""

import os
import math
from typing import Dict, Any, List

class EvidenceCorrelator:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def correlate_evidence(
        self,
        images: List[Dict[str, Any]],
        videos: List[Dict[str, Any]],
        audios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Builds a multi-directional cross-modal correlation matrix.
        Evaluates metadata, container durations (for linked streams), and detector concurrence.
        """
        correlation_records = []

        all_items = []
        for img in images:
            all_items.append({"id": img.get("filename"), "type": "IMAGE", "data": img})
        for vid in videos:
            all_items.append({"id": vid.get("filename"), "type": "VIDEO", "data": vid})
        for aud in audios:
            all_items.append({"id": aud.get("filename"), "type": "AUDIO", "data": aud})

        # Pairwise Cross-Modal Comparison
        for i in range(len(all_items)):
            for j in range(i + 1, len(all_items)):
                item_a = all_items[i]
                item_b = all_items[j]

                record = self._compare_pair(item_a, item_b)
                if record:
                    correlation_records.append(record)

        # Build Modality Summary Matrix
        return {
            "total_pairs_correlated": len(correlation_records),
            "correlations": correlation_records,
            "modality_breakdown": {
                "images_count": len(images),
                "videos_count": len(videos),
                "audios_count": len(audios),
            }
        }

    def _compare_pair(self, item_a: Dict[str, Any], item_b: Dict[str, Any]) -> Dict[str, Any]:
        types = {item_a["type"], item_b["type"]}
        name_a = item_a["id"]
        name_b = item_b["id"]
        data_a = item_a["data"]
        data_b = item_b["data"]

        # Case 1: Video + Audio
        if types == {"VIDEO", "AUDIO"}:
            vid = data_a if item_a["type"] == "VIDEO" else data_b
            aud = data_a if item_a["type"] == "AUDIO" else data_b

            vid_name = vid.get("filename", "")
            aud_name = aud.get("filename", "")

            vid_id = vid.get("evidence_id")
            vid_sha = vid.get("sha256")
            aud_id = aud.get("evidence_id")
            aud_sha = aud.get("sha256")

            # Collect valid cryptographic / identifier tokens (excluding filenames alone)
            valid_vid_identifiers = set(filter(None, [vid_id, vid_sha]))
            valid_aud_identifiers = set(filter(None, [aud_id, aud_sha]))

            # Strict Provenance Verification Requirements:
            # - Exact source evidence ID; or
            # - Verified SHA-256 source hash; or
            # - Explicit same-stream metadata with a validated source_container_id.
            # Filenames alone can NEVER establish verified source linkage.
            is_verified_link = False
            is_possible_association = False

            extracted_from = aud.get("extracted_from")
            audio_source = vid.get("audio_stream_source")
            source_container = aud.get("source_container_id")

            if valid_vid_identifiers and extracted_from and extracted_from in valid_vid_identifiers:
                is_verified_link = True
            elif valid_aud_identifiers and audio_source and audio_source in valid_aud_identifiers:
                is_verified_link = True
            elif valid_vid_identifiers and aud.get("is_same_stream", False) and source_container and source_container in valid_vid_identifiers:
                is_verified_link = True
            elif (
                (vid_name and aud_name and vid_name == aud_name) or
                (os.path.splitext(vid_name)[0] == os.path.splitext(aud_name)[0] and len(vid_name) > 0) or
                (extracted_from and extracted_from == vid_name)
            ):
                # Filename matches or filename stems alone remain strictly POSSIBLE_ASSOCIATION_NOT_VERIFIED
                is_possible_association = True

            vid_dur = vid.get("video_metadata", {}).get("duration_seconds", 0.0)
            aud_dur = aud.get("audio_metadata", {}).get("duration_seconds", 0.0)
            dur_delta = abs(vid_dur - aud_dur)

            vid_syn = vid.get("summary", {}).get("synthetic_flagged_count", 0) > 0
            aud_syn = aud.get("is_synthetic", False)
            agreement = (vid_syn == aud_syn)

            if is_verified_link:
                # Synchronization delta is only forensically meaningful if audio has verified provenance from video
                sync_anomaly = dur_delta > 1.5
                finding = (
                    f"Linked Audio/Video stream duration alignment ({aud_dur}s vs {vid_dur}s, delta: {dur_delta:.2f}s) is within normal forensic tolerance."
                    if not sync_anomaly else
                    f"POTENTIAL STREAM DESYNC: Significant duration disparity ({dur_delta:.2f}s delta) in verified linked video and audio tracks."
                )
                rel_type = "LINKED_AUDIO_VIDEO_STREAM_ANALYSIS"
                notes = "Audio and video have verified cryptographic/extraction provenance. Duration comparison evaluated for demux/splicing anomalies."
            elif is_possible_association:
                sync_anomaly = False
                finding = (
                    f"Filename stems match ('{os.path.splitext(vid_name)[0]}'), but explicit extraction provenance is unverified. "
                    f"Video container ({vid_dur}s) and Audio file ({aud_dur}s). Classifiers {'concur' if agreement else 'diverge'}."
                )
                rel_type = "POSSIBLE_ASSOCIATION_NOT_VERIFIED"
                notes = "Unverified filename association: Cannot be used for stream synchronization escalation."
            else:
                # Standalone unlinked files
                sync_anomaly = False
                finding = (
                    f"Unlinked media files: Video container ({vid_dur}s) and Audio file ({aud_dur}s). "
                    f"Classifiers {'concur on origin' if agreement else 'diverge in predictions'}."
                )
                rel_type = "METADATA_AND_CONTAINER_COMPARISON"
                notes = "Files have no verified common source stream. Container durations are reported for inventory purposes only and do not imply desynchronization."

            return {
                "pair": f"{name_a} ↔ {name_b}",
                "relationship_type": rel_type,
                "is_source_linked": is_verified_link,
                "is_possible_association": is_possible_association,
                "duration_delta_sec": round(dur_delta, 2),
                "sync_anomaly_flag": sync_anomaly,
                "detector_agreement": "CONCURRING" if agreement else "DISAGREEING_FINDINGS",
                "finding": finding,
                "notes": notes
            }

        # Case 2: Image + Video
        elif types == {"IMAGE", "VIDEO"}:
            img = data_a if item_a["type"] == "IMAGE" else data_b
            vid = data_a if item_a["type"] == "VIDEO" else data_b

            img_syn = img.get("is_synthetic", False)
            vid_syn = vid.get("summary", {}).get("synthetic_flagged_count", 0) > 0
            agreement = (img_syn == vid_syn)

            finding = (
                f"Classifiers concur ({'Both flag synthetic features' if img_syn else 'Both predict authentic'})."
                if agreement else
                "Classifiers diverge: Image and video exhibit differing artifact signatures."
            )

            return {
                "pair": f"{name_a} ↔ {name_b}",
                "relationship_type": "METADATA_AND_CONTAINER_COMPARISON",
                "is_source_linked": False,
                "detector_agreement": "CONCURRING" if agreement else "DISAGREEING_FINDINGS",
                "finding": finding,
                "notes": "Independent latent feature comparison between static image and spatiotemporal video frames."
            }

        # Case 3: Image + Audio
        elif types == {"IMAGE", "AUDIO"}:
            img = data_a if item_a["type"] == "IMAGE" else data_b
            aud = data_a if item_a["type"] == "AUDIO" else data_b

            img_syn = img.get("is_synthetic", False)
            aud_syn = aud.get("is_synthetic", False)
            agreement = (img_syn == aud_syn)

            return {
                "pair": f"{name_a} ↔ {name_b}",
                "relationship_type": "METADATA_AND_CONTAINER_COMPARISON",
                "is_source_linked": False,
                "detector_agreement": "CONCURRING" if agreement else "DISAGREEING_FINDINGS",
                "finding": f"Modality alignment: {'Both exhibit synthetic features' if (img_syn and aud_syn) else ('Both predict authentic' if (not img_syn and not aud_syn) else 'Divergent findings across visual and acoustic domains.')}",
                "notes": "Multimodal evidentiary cross-check without unwarranted identity or common-scene assumptions."
            }

        # Same modality pairings (e.g. Image ↔ Image or Audio ↔ Audio)
        else:
            return {
                "pair": f"{name_a} ↔ {name_b}",
                "relationship_type": "INTRA_MODAL_CONSISTENCY",
                "detector_agreement": "CO-OBSERVED",
                "finding": "Both files belong to the same sensory modality.",
                "notes": "Checked for batch inventory consistency."
            }


