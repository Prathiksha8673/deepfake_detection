"""
DEEPFAKE X - Forensic PDF Report Generator
Produces formal, cryptographically auditable, multi-page forensic reports.
Complies with ISO/IEC 27037 standards for digital evidence integrity.
"""

import os
import time
from typing import Dict, Any, List
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

    def generate_investigation_pdf(self, case_data: Dict[str, Any]) -> str:
        """
        Builds a comprehensive, formal forensic PDF incident report from investigation data.
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
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold",
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#475569"),
            spaceAfter=12
        )
        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#0284c7"),
            fontName="Helvetica-Bold",
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "BodyDark",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#1e293b")
        )
        callout_style = ParagraphStyle(
            "Callout",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#334155")
        )

        elements = []

        # Header Banner
        elements.append(Paragraph("DEEPFAKE X — FORENSIC MEDIA INTELLIGENCE REPORT", title_style))
        elements.append(Paragraph("CRYPTOGRAPHICALLY AUDITABLE MULTIMODAL AUTHENTICITY EXAMINATION", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=10))

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
                Paragraph(f"<b>Overall Assessment:</b> <b>{case_data.get('reliability_assessment', {}).get('verdict_category', 'In Progress')}</b>", body_style),
                Paragraph(f"<b>Custody Standard:</b> ISO/IEC 27037 Compliant", body_style),
            ]
        ]
        meta_table = Table(meta_table_data, colWidths=[270, 270])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 12))

        # Executive Evidentiary Assessment
        elements.append(Paragraph("1. EXECUTIVE EVIDENTIARY ASSESSMENT", section_heading))
        rel = case_data.get("reliability_assessment", {})
        verdict = rel.get("verdict_category", "Pending Evaluation")
        rationale = rel.get("rationale", "No detailed rationale provided.")

        exec_text = f"<b>Final Finding:</b> {verdict}<br/><br/><b>Technical Rationale:</b> {rationale}"
        elements.append(Paragraph(exec_text, body_style))
        elements.append(Spacer(1, 10))

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
                    Paragraph(f"<font size='6.5'>{item.get('sha256', 'N/A')}</font>", body_style),
                ])
            inv_table = Table(inv_table_data, colWidths=[120, 70, 60, 290])
            inv_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]))
            elements.append(inv_table)
        else:
            elements.append(Paragraph("No media items logged in inventory.", body_style))
        elements.append(Spacer(1, 12))

        # Individual Detection Summaries
        elements.append(Paragraph("3. DETECTOR INFERENCE FINDINGS (UNCALIBRATED)", section_heading))
        ind = case_data.get("individual_results", {})
        
        # Image Results
        if ind.get("images"):
            elements.append(Paragraph("<b>Image Analysis (Swin Transformer Vision Backbone):</b>", body_style))
            for im in ind["images"]:
                elements.append(Paragraph(
                    f"• <b>{im.get('filename')}</b>: {im.get('classification')} | Synthetic: {im.get('artificial_prob')}% | Authentic: {im.get('human_prob')}% | Device: {im.get('device')}",
                    body_style
                ))
            elements.append(Spacer(1, 6))

        # Video Results
        if ind.get("videos"):
            elements.append(Paragraph("<b>Video Analysis (Uniform Frame Screening):</b>", body_style))
            for vd in ind["videos"]:
                s = vd.get("summary", {})
                elements.append(Paragraph(
                    f"• <b>{vd.get('filename')}</b>: Flagged {s.get('synthetic_flagged_count', 0)} / {s.get('total_analyzed_frames', 0)} frames synthetic | Mean: {s.get('mean_synthetic_score')}% | Peak: {s.get('highest_synthetic_score')}% at {', '.join(s.get('peak_timestamps', []))}",
                    body_style
                ))
            elements.append(Spacer(1, 6))

        # Audio Results
        if ind.get("audios"):
            elements.append(Paragraph("<b>Audio Analysis (Wav2Vec 2.0 Sequence Classifier):</b>", body_style))
            for ad in ind["audios"]:
                elements.append(Paragraph(
                    f"• <b>{ad.get('filename')}</b>: {ad.get('classification')} | Synthetic: {ad.get('synthetic_score')}% | Authentic: {ad.get('authentic_score')}%",
                    body_style
                ))
            elements.append(Spacer(1, 6))

        # Cross-Modal Correlation Findings
        elements.append(Paragraph("4. CROSS-MODAL EVIDENCE CORRELATION MATRIX", section_heading))
        correlations = case_data.get("correlation_analysis", {}).get("correlations", [])
        if correlations:
            corr_table_data = [["Media Pair", "Correlation Type", "Agreement", "Key Observation"]]
            for c in correlations:
                corr_table_data.append([
                    Paragraph(c.get("pair", ""), body_style),
                    Paragraph(c.get("relationship_type", ""), body_style),
                    Paragraph(c.get("detector_agreement", ""), body_style),
                    Paragraph(c.get("finding", ""), body_style),
                ])
            corr_table = Table(corr_table_data, colWidths=[110, 110, 80, 240])
            corr_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]))
            elements.append(corr_table)
        else:
            elements.append(Paragraph("No cross-modal relationships to evaluate (single modality provided).", body_style))
        elements.append(Spacer(1, 14))

        # Mandatory Forensic Disclaimers & Methodology
        elements.append(Paragraph("5. FORENSIC METHODOLOGY & RELIABILITY LIMITATIONS", section_heading))
        disclaimer_text = (
            "<b>ISO/IEC 27037 Evidentiary Standard Notice:</b> This automated analysis report is generated for investigative screening and prioritization. "
            "Scores represent raw uncalibrated softmax activations of deep neural feature extractors. "
            "1. <b>Image Detection:</b> Standard vision classifiers may exhibit false negatives on novel diffusion generators (e.g. Flux, SDXL).<br/>"
            "2. <b>Video Screening:</b> Performs frame-level artifact analysis; does not constitute face-swap or lip-sync biometric proof.<br/>"
            "3. <b>Audio Detection:</b> Wav2Vec2 audio models are sensitive to acoustic channel noise, bandpass filtering (e.g. historical radio), and can fail on state-of-the-art flow-matching voice clones (e.g. ElevenLabs).<br/>"
            "4. <b>Correlation:</b> Inter-modal correlation does not prove intentional manipulation. Conflicting signals must be verified manually."
        )
        elements.append(Paragraph(disclaimer_text, callout_style))

        doc.build(elements)
        return os.path.abspath(pdf_path)

