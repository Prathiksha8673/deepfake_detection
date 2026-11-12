"""
DEEPFAKE X - Forensic PDF Report Generator
Produces formal, cryptographically auditable, multi-page forensic reports.
Follows Structured Forensic Evidence Handling standards with detached SHA-256 integrity manifests.
"""

import os
import time
import json
import hashlib
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)

REPORTS_DIR = "reports/generated"

class ForensicReportGenerator:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        os.makedirs(REPORTS_DIR, exist_ok=True)

    @staticmethod
    def compute_file_sha256(filepath: str) -> str:
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def verify_report_integrity(pdf_path: str, manifest_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Verifies PDF file against its detached JSON cryptographic manifest.
        Returns validation status, recorded hash, computed hash, and discrepancy info.
        """
        if not os.path.exists(pdf_path):
            return {"valid": False, "reason": "PDF report file not found on disk."}

        target_manifest = manifest_path or f"{pdf_path}.manifest.json"
        if not os.path.exists(target_manifest):
            return {"valid": False, "reason": "Detached cryptographic manifest (.manifest.json) not found."}

        try:
            with open(target_manifest, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception as e:
            return {"valid": False, "reason": f"Manifest read failure: {str(e)}"}

        recorded_hash = manifest_data.get("sha256_hash", "")
        computed_hash = ForensicReportGenerator.compute_file_sha256(pdf_path)

        is_match = (recorded_hash.lower() == computed_hash.lower()) and len(recorded_hash) == 64
        return {
            "valid": is_match,
            "pdf_path": pdf_path,
            "manifest_path": target_manifest,
            "recorded_sha256": recorded_hash,
            "computed_sha256": computed_hash,
            "investigation_id": manifest_data.get("investigation_id"),
            "generation_timestamp": manifest_data.get("generation_timestamp"),
            "reason": "PDF SHA-256 digest verification successful." if is_match else "SECURITY ALERT: PDF digest mismatch with detached manifest!"
        }

    def generate_investigation_pdf(self, case_data: Dict[str, Any]) -> str:
        """
        Builds a comprehensive, formal forensic PDF incident report from investigation data.
        Generates detached SHA-256 cryptographic integrity manifest upon completion.
        Returns the absolute filesystem path of the generated PDF document.
        """
        inv_id = case_data.get("investigation_id", "UNKNOWN_CASE")
        filename = f"DEEPFAKE_X_REPORT_{inv_id}.pdf"
        pdf_path = os.path.join(REPORTS_DIR, filename)

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Cyber / Forensic Styling
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold",
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontSize=9.5,
            leading=12,
            textColor=colors.HexColor("#475569"),
            spaceAfter=12
        )
        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#0284c7"),
            fontName="Helvetica-Bold",
            spaceBefore=10,
            spaceAfter=5
        )
        body_style = ParagraphStyle(
            "BodyDark",
            parent=styles["Normal"],
            fontSize=8,
            leading=11.5,
            textColor=colors.HexColor("#1e293b")
        )
        callout_style = ParagraphStyle(
            "Callout",
            parent=styles["Normal"],
            fontSize=7.5,
            leading=10.5,
            textColor=colors.HexColor("#334155")
        )

        elements = []

        # Header Banner
        elements.append(Paragraph("DEEPFAKE X — FORENSIC MEDIA INTELLIGENCE REPORT", title_style))
        elements.append(Paragraph("STRUCTURED FORENSIC EVIDENCE EXAMINATION & METADATA AUDIT", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=10))

        rel_assessment = case_data.get("reliability_assessment") or {}
        overall_assessment = rel_assessment.get("verdict_category", "In Progress")

        # Investigation Metadata Block
        meta_table_data = [
            [
                Paragraph(f"<b>Investigation ID:</b> {inv_id}", body_style),
                Paragraph(f"<b>Date/Time:</b> {case_data.get('created_at', time.strftime('%Y-%m-%d %H:%M:%S UTC'))}", body_style),
            ],
            [
                Paragraph(f"<b>Case Title:</b> {case_data.get('title', 'N/A')}", body_style),
                Paragraph(f"<b>Investigator:</b> {case_data.get('investigator', 'Forensic Analyst')}", body_style),
            ],
            [
                Paragraph(f"<b>Overall Assessment:</b> <b>{overall_assessment}</b>", body_style),
                Paragraph(f"<b>Custody Standard:</b> Structured Forensic Evidence Handling", body_style),
            ]
        ]
        meta_table = Table(meta_table_data, colWidths=[270, 270])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 10))

        # Executive Evidentiary Assessment
        elements.append(Paragraph("1. EXECUTIVE EVIDENTIARY ASSESSMENT", section_heading))
        rel = case_data.get("reliability_assessment") or {}
        verdict = rel.get("verdict_category", "Pending Evaluation")
        strength = rel.get("evidence_strength", "N/A")
        rationale = rel.get("rationale", "No detailed rationale provided.")

        exec_text = f"<b>Forensic Category:</b> {verdict}<br/><b>Evidentiary Strength:</b> {strength}<br/><br/><b>Technical Rationale:</b> {rationale}"
        elements.append(Paragraph(exec_text, body_style))
        elements.append(Spacer(1, 8))

        # Evidence Inventory & Hashes
        elements.append(Paragraph("2. EVIDENCE INVENTORY & CHAIN OF CUSTODY (SHA-256)", section_heading))
        inventory = case_data.get("evidence_inventory", [])
        if inventory:
            inv_table_data = [["Filename", "Modality", "Size", "SHA-256 Digest"]]
            for item in inventory:
                inv_table_data.append([
                    Paragraph(item.get("filename", "N/A"), body_style),
                    Paragraph(item.get("modality", "N/A"), body_style),
                    Paragraph(item.get("file_size", "N/A"), body_style),
                    Paragraph(f"<font size='6'>{item.get('sha256', 'N/A')}</font>", body_style),
                ])
            inv_table = Table(inv_table_data, colWidths=[120, 70, 60, 290])
            inv_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ]))
            elements.append(inv_table)
        else:
            elements.append(Paragraph("No media items logged in inventory.", body_style))
        elements.append(Spacer(1, 10))

        # Individual Detection Summaries
        elements.append(Paragraph("3. DETECTOR INFERENCE FINDINGS (UNCALIBRATED SOFTMAX SCORES)", section_heading))
        ind = case_data.get("individual_results", {})
        
        # Image Results
        if ind.get("images"):
            elements.append(Paragraph("<b>Image Analysis (Swin Transformer Vision Backbone):</b>", body_style))
            for im in ind["images"]:
                elements.append(Paragraph(
                    f"• <b>{im.get('filename')}</b>: {im.get('classification')} | Synthetic: {im.get('artificial_prob')}% | Authentic: {im.get('human_prob')}% | Device: {im.get('device')}",
                    body_style
                ))
            elements.append(Spacer(1, 4))

        # Video Results
        if ind.get("videos"):
            elements.append(Paragraph("<b>Video Analysis (Uniform Frame Screening):</b>", body_style))
            for vd in ind["videos"]:
                s = vd.get("summary", {})
                elements.append(Paragraph(
                    f"• <b>{vd.get('filename')}</b>: Flagged {s.get('synthetic_flagged_count', 0)} / {s.get('total_analyzed_frames', 0)} frames synthetic | Mean Synthetic: {s.get('mean_synthetic_score')}% | Peak: {s.get('highest_synthetic_score')}%",
                    body_style
                ))
            elements.append(Spacer(1, 4))

        # Audio Results
        if ind.get("audios"):
            elements.append(Paragraph("<b>Audio Analysis (Wav2Vec 2.0 Sequence Classifier):</b>", body_style))
            for ad in ind["audios"]:
                elements.append(Paragraph(
                    f"• <b>{ad.get('filename')}</b>: {ad.get('classification')} | Synthetic: {ad.get('synthetic_score')}% | Authentic: {ad.get('authentic_score')}%",
                    body_style
                ))
            elements.append(Spacer(1, 4))

        # Cross-Modal Comparison Findings
        elements.append(Paragraph("4. METADATA & CONTAINER COMPARISON MATRIX", section_heading))
        correlations = case_data.get("correlation_analysis", {}).get("correlations", [])
        if correlations:
            corr_table_data = [["Media Pair", "Comparison Type", "Agreement", "Key Observation"]]
            for c in correlations:
                corr_table_data.append([
                    Paragraph(c.get("pair", ""), body_style),
                    Paragraph(c.get("relationship_type", ""), body_style),
                    Paragraph(c.get("detector_agreement", ""), body_style),
                    Paragraph(c.get("finding", ""), body_style),
                ])
            corr_table = Table(corr_table_data, colWidths=[110, 115, 75, 240])
            corr_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ]))
            elements.append(corr_table)
        else:
            elements.append(Paragraph("No cross-modal pairs evaluated.", body_style))
        elements.append(Spacer(1, 10))

        # =========================================================================
        # PHASE 6 STAGE 2 ENHANCEMENTS: FORENSIC INTELLIGENCE, COMPARISONS, TIMELINE
        # =========================================================================

        # Section 5: Grounded Forensic Explainability
        elements.append(Paragraph("5. GROUNDED FORENSIC EXPLAINABILITY & OPERATIONAL BOUNDS", section_heading))
        from src.modules.case_manager import CaseManager
        cm = CaseManager.get_instance()
        explanations = cm.get_forensic_explanations(case_data)
        has_any_exp = False

        for im_exp in explanations.get("images", []):
            if im_exp.get("status") != "UNAVAILABLE":
                has_any_exp = True
                u_interp = im_exp.get("output_interpretation", {})
                scores = u_interp.get("uncalibrated_softmax_scores", {})
                elements.append(Paragraph(
                    f"• <b>Image '{im_exp.get('evidence_target')}':</b> "
                    f"Architecture: {im_exp.get('pipeline_specification', {}).get('model_architecture')} | "
                    f"Score: Synthetic {scores.get('synthetic_probability_pct')}% / Authentic {scores.get('authentic_probability_pct')}% | "
                    f"Decision: {u_interp.get('assigned_classification')}<br/>"
                    f"&nbsp;&nbsp;<b>Preprocessing:</b> {im_exp.get('verified_preprocessing', {}).get('tensor_normalization')}<br/>"
                    f"&nbsp;&nbsp;<b>Raw Logits:</b> {u_interp.get('raw_logits')}<br/>"
                    f"&nbsp;&nbsp;<b>Key Limitation:</b> {im_exp.get('uncertainty_and_invalidation_factors', ['N/A'])[0]}",
                    body_style
                ))

        for vd_exp in explanations.get("videos", []):
            if vd_exp.get("status") != "UNAVAILABLE":
                has_any_exp = True
                out_vd = vd_exp.get("output_interpretation", {})
                samp = vd_exp.get("sampling_implementation", {})
                elements.append(Paragraph(
                    f"• <b>Video '{vd_exp.get('evidence_target')}':</b> "
                    f"Sampled {samp.get('actual_frames_sampled', 0)} frames ({samp.get('sampling_strategy')}) | "
                    f"Flagged Frames: {out_vd.get('flagged_frames_count')} | "
                    f"Mean Synthetic: {out_vd.get('mean_synthetic_score')}% | Peak: {out_vd.get('peak_synthetic_score')}% at {', '.join(out_vd.get('peak_timestamps', []))}<br/>"
                    f"&nbsp;&nbsp;<b>Raw Logits:</b> {out_vd.get('raw_logits')}<br/>"
                    f"&nbsp;&nbsp;<b>Key Limitation:</b> {vd_exp.get('uncertainty_and_invalidation_factors', ['N/A'])[1]}",
                    body_style
                ))

        for ad_exp in explanations.get("audios", []):
            if ad_exp.get("status") != "UNAVAILABLE":
                has_any_exp = True
                out_ad = ad_exp.get("output_interpretation", {})
                scores_ad = out_ad.get("uncalibrated_softmax_scores", {})
                elements.append(Paragraph(
                    f"• <b>Audio '{ad_exp.get('evidence_target')}':</b> "
                    f"Architecture: {ad_exp.get('pipeline_specification', {}).get('model_architecture')} | "
                    f"Classification: {out_ad.get('assigned_classification')} (Synthetic: {scores_ad.get('synthetic_score_pct')}%, Authentic: {scores_ad.get('authentic_score_pct')}%)<br/>"
                    f"&nbsp;&nbsp;<b>Preprocessing:</b> Polyphase resampled to {ad_exp.get('verified_preprocessing', {}).get('target_sampling_rate_hz')} Hz mono float32<br/>"
                    f"&nbsp;&nbsp;<b>Raw Logits:</b> {out_ad.get('raw_logits')}<br/>"
                    f"&nbsp;&nbsp;<b>Key Limitation:</b> {ad_exp.get('uncertainty_and_invalidation_factors', ['N/A'])[0]}",
                    body_style
                ))

        if not has_any_exp:
            elements.append(Paragraph("No detailed explainability outputs available for this case.", body_style))
        elements.append(Spacer(1, 10))

        # Section 6: Advanced Evidence Comparison & Provenance Lineage
        elements.append(Paragraph("6. ADVANCED EVIDENCE COMPARISON & PROVENANCE LINEAGE", section_heading))
        comparisons = cm.get_evidence_comparisons(case_data)
        lineage = comparisons.get("verified_lineage", {})
        v_stats = comparisons.get("video_temporal_statistics", [])
        a_comps = comparisons.get("audio_comparisons", [])

        # 6A: Verified Lineage
        elements.append(Paragraph("<b>A. Cryptographic Evidence Lineage (Strict Provenance):</b>", body_style))
        if lineage.get("verified_lineages"):
            for vl in lineage["verified_lineages"]:
                elements.append(Paragraph(
                    f"• <b>Child:</b> {vl.get('child_filename')} (SHA: {vl.get('child_sha256', '')[:12]}...) ➔ "
                    f"<b>Parent:</b> {vl.get('parent_filename')} | <b>Basis:</b> {vl.get('verification_basis')}",
                    body_style
                ))
        else:
            elements.append(Paragraph("• No verified parent-child evidence lineage detected (all media items ingested independently).", body_style))

        if lineage.get("unverified_associations"):
            for ua in lineage["unverified_associations"]:
                elements.append(Paragraph(
                    f"• <i>Unverified Association:</i> {ua.get('child_filename')} (Ref: {ua.get('unresolved_reference')}) — {ua.get('reason')}",
                    callout_style
                ))

        # 6B: Video Temporal Score Statistics
        if v_stats:
            elements.append(Spacer(1, 4))
            elements.append(Paragraph("<b>B. Video Temporal Detector-Score Analysis:</b>", body_style))
            for vs in v_stats:
                sm = vs.get("score_metrics", {})
                elements.append(Paragraph(
                    f"• <b>{vs.get('filename')}:</b> Evaluated {vs.get('total_frames_evaluated')} frames | "
                    f"Mean: {sm.get('mean_synthetic_score')}% | Std Dev: {sm.get('std_deviation')} pts | "
                    f"Range: [{sm.get('minimum_synthetic_score')}% - {sm.get('maximum_synthetic_score')}%] | "
                    f"Threshold Crossings (>50%): {vs.get('threshold_crossings_count')}<br/>"
                    f"&nbsp;&nbsp;<i>Notice:</i> Temporal score variance does NOT prove localized splicing or video manipulation.",
                    body_style
                ))

        # 6C: Separated Audio Comparisons
        if a_comps:
            elements.append(Spacer(1, 4))
            elements.append(Paragraph("<b>C. Separated Audio Stream Comparison:</b>", body_style))
            for ac in a_comps:
                tech = ac.get("technical_container_metadata", {})
                acoust = ac.get("acoustic_statistics", {})
                elements.append(Paragraph(
                    f"• <b>Pair {ac.get('pair')}:</b> Duration Delta: {tech.get('duration_delta_seconds')}s | "
                    f"Sample Rate Delta: {tech.get('sample_rate_delta_hz')} Hz | "
                    f"RMS Energy Delta: {acoust.get('rms_energy_delta')} (Ratio: {acoust.get('relative_energy_ratio')})<br/>"
                    f"&nbsp;&nbsp;<i>Notice:</i> Container metadata and acoustic energy similarity do NOT establish common recording origin.",
                    body_style
                ))
        elements.append(Spacer(1, 10))

        # Section 7: Audit Timeline Analytics
        elements.append(Paragraph("7. INVESTIGATION AUDIT TIMELINE ANALYTICS", section_heading))
        timeline = cm.get_timeline_analytics(case_data)
        chain_status = "VALID (Cryptographically Intact)" if timeline.get("hash_chain_valid") else "INVALID (Integrity Warning)"
        elements.append(Paragraph(
            f"<b>Ledger Sequence Integrity:</b> {chain_status} | "
            f"<b>Total Events Logged:</b> {timeline.get('total_events', 0)} | "
            f"<b>Investigation Span:</b> {timeline.get('total_investigation_span_seconds', 0.0)}s",
            body_style
        ))

        if timeline.get("timestamp_anomalies"):
            for an in timeline["timestamp_anomalies"]:
                elements.append(Paragraph(
                    f"⚠️ <b>Timestamp Anomaly:</b> Event #{an.get('sequence_index')} ({an.get('action')}) at {an.get('timestamp')}: {an.get('description')}",
                    callout_style
                ))

        t_records = timeline.get("timeline_records", [])
        if t_records:
            t_table_data = [["Seq", "Action", "Timestamp (UTC)", "Details", "Event Hash (Truncated)"]]
            for r in t_records:
                t_table_data.append([
                    Paragraph(str(r.get("sequence_index")), body_style),
                    Paragraph(r.get("action", ""), body_style),
                    Paragraph(r.get("timestamp_display", ""), body_style),
                    Paragraph(r.get("details", "")[:60] + ("..." if len(r.get("details", "")) > 60 else ""), body_style),
                    Paragraph(f"<font size='6'>{r.get('event_hash', '')[:16]}...</font>", body_style),
                ])
            t_table = Table(t_table_data, colWidths=[25, 110, 105, 200, 100])
            t_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ]))
            elements.append(t_table)
        elements.append(Paragraph(
            "<i>Cryptographic Integrity Notice: Hash-chain verification confirms consistency against the recorded hash sequence "
            "and detects modifications that invalidate the existing chain. It does not guarantee immutability or authenticity against "
            "an attacker with filesystem access who can rewrite the local ledger and recompute hashes, nor does it independently "
            "validate host clock accuracy or timestamp authenticity.</i>",
            callout_style
        ))
        elements.append(Spacer(1, 10))

        # Mandatory Forensic Disclaimers & Methodology (Section 8)
        elements.append(Paragraph("8. FORENSIC METHODOLOGY & EMPIRICAL DETECTOR LIMITATIONS", section_heading))
        disclaimer_text = (
            "<b>Forensic Evidentiary Disclaimer:</b> This report is generated strictly for investigative screening. "
            "Model scores reflect raw uncalibrated softmax activations of deep neural feature extractors and do not represent absolute mathematical truth.<br/>"
            "1. <b>Image Detection (Swin Transformer):</b> Susceptible to false negatives on novel generative diffusion and flow architectures.<br/>"
            "2. <b>Video Screening:</b> Performs uniform frame-level screening; does not constitute face-swap or lip-sync biometric proof.<br/>"
            "3. <b>Audio Detection (Wav2Vec2):</b> Known empirical vulnerability to modern neural flow-matching speech synthesis (e.g., ElevenLabs). "
            "Evaluated accuracy is vocoder-dependent; false negatives occur on state-of-the-art voice clones.<br/>"
            "4. <b>Cross-Modal Comparison:</b> Pairwise container comparison does not prove common origin or intentional manipulation without independent contextual corroborate."
        )
        elements.append(Paragraph(disclaimer_text, callout_style))

        # Build Document
        doc.build(elements)
        abs_pdf_path = os.path.abspath(pdf_path)

        # Generate Detached Cryptographic Manifest
        pdf_sha256 = self.compute_file_sha256(abs_pdf_path)
        manifest_path = f"{abs_pdf_path}.manifest.json"
        manifest_data = {
            "investigation_id": inv_id,
            "report_filename": os.path.basename(abs_pdf_path),
            "report_filepath": abs_pdf_path,
            "sha256_hash": pdf_sha256,
            "file_size_bytes": os.path.getsize(abs_pdf_path),
            "generation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "custody_standard": "Structured Forensic Evidence Handling (PDF SHA-256 digest verification)"
        }
        with open(manifest_path, "w", encoding="utf-8") as mf:
            json.dump(manifest_data, mf, indent=2)

        return abs_pdf_path

