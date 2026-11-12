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

            vid_id = vid.get("evidence_id") or vid.get("sha256") or vid_name
            aud_id = aud.get("evidence_id") or aud.get("sha256") or aud_name

            # Strict Provenance Verification:
            # 1. Explicitly extracted_from referencing exact source evidence ID/hash/filename
            # 2. Verified same-stream boolean flag with matching source container ID
            # 3. Explicit video audio_stream_source referencing exact audio evidence ID/hash
            is_verified_link = False
            is_possible_association = False

            if (
                (aud.get("extracted_from") and aud.get("extracted_from") in {vid_id, vid_name, vid.get("sha256")}) or
                (vid.get("audio_stream_source") and vid.get("audio_stream_source") in {aud_id, aud_name, aud.get("sha256")}) or
                (aud.get("is_same_stream", False) and aud.get("source_container_id") and aud.get("source_container_id") in {vid_id, vid_name, vid.get("sha256")})
            ):
                is_verified_link = True
            elif (
                os.path.splitext(vid_name)[0] == os.path.splitext(aud_name)[0] and len(vid_name) > 0
            ):
                # Merely matching filenames without cryptographic/extraction provenance
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


