"""
Examiner Dashboard Module (Phase 6 Stage 3)
DeepfakeX — Advanced Forensic Intelligence, Explainability and Investigation Analytics.

Provides interactive examiner-facing components to inspect:
- Investigation overview metrics across registered case records.
- Evidence inventory & detector findings.
- Model explainability & uncalibrated score decomposition (ForensicExplainer).
- Evidence comparison, temporal video analytics, audio comparison & verified lineage (EvidenceComparator).
- Cryptographic audit timeline and sequence preservation (TimelineAnalytics).
- Forensic PDF report generation and detached SHA-256 manifest verification.

STRICT SCIENTIFIC AND ETHICAL RULES:
- Never invents scores, Grad-CAM overlays, or fake cases.
- Never confuses perceptual hash similarity with byte identity.
- Never treats filenames alone as verified provenance.
- Never claims local hash chains prove host clock veracity or ledger immutability against filesystem access.
"""

import os
import json
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional

from src.modules.case_manager import CaseManager
from src.modules.forensic_explainer import ForensicExplainer
from src.modules.evidence_comparator import EvidenceComparator
from src.modules.timeline_analytics import TimelineAnalytics
from src.modules.report_generator import ForensicReportGenerator


class ExaminerDashboard:
    """Examiner Dashboard controller for deep forensic case inspection."""

    _instance: Optional["ExaminerDashboard"] = None

    def __init__(self):
        self.case_mgr = CaseManager.get_instance()
        self.explainer = ForensicExplainer.get_instance()
        self.comparator = EvidenceComparator.get_instance()
        self.timeline_analytics = TimelineAnalytics.get_instance()
        self.report_gen = ForensicReportGenerator.get_instance()

    @classmethod
    def get_instance(cls) -> "ExaminerDashboard":
        if cls._instance is None:
            cls._instance = ExaminerDashboard()
        return cls._instance

    # -------------------------------------------------------------------------
    # Core Data Aggregation & Metrics
    # -------------------------------------------------------------------------
    def compute_dashboard_metrics(self, all_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Computes accurate forensic metrics derived purely from actual stored case records.
        Does not fabricate cases or counts.
        """
        total_cases = len(all_cases)
        total_evidence = 0
        modality_counts = {"Image": 0, "Video": 0, "Audio": 0}
        completed_analysis_cases = 0
        generated_reports_cases = 0
        requires_examination_cases = 0

        for c_summary in all_cases:
            inv_id = c_summary.get("investigation_id")
            c_data = self.case_mgr.load_case(inv_id, record_reopen=False)
            if not c_data:
                continue

            inv = c_data.get("evidence_inventory", [])
            total_evidence += len(inv)

            for item in inv:
                m = str(item.get("modality", "")).capitalize()
                if m in modality_counts:
                    modality_counts[m] += 1

            ind = c_data.get("individual_results") or {}
            has_results = bool(ind.get("images") or ind.get("videos") or ind.get("audios"))
            if has_results:
                completed_analysis_cases += 1

            rel = c_data.get("reliability_assessment") or {}
            verdict = rel.get("verdict_category", "")
            if verdict in [
                "Strong evidence of manipulation detected",
                "Potential manipulation detected",
                "Conflicting forensic evidence"
            ]:
                requires_examination_cases += 1

            rep_path = c_data.get("report_pdf_path")
            if rep_path and os.path.exists(rep_path):
                generated_reports_cases += 1

        return {
            "total_cases": total_cases,
            "total_evidence": total_evidence,
            "image_count": modality_counts["Image"],
            "video_count": modality_counts["Video"],
            "audio_count": modality_counts["Audio"],
            "completed_analysis": completed_analysis_cases,
            "generated_reports": generated_reports_cases,
            "requires_examination": requires_examination_cases,
        }

    # -------------------------------------------------------------------------
    # UI Renderers
    # -------------------------------------------------------------------------
    def render(self):
        """Main entry point for the Examiner Dashboard."""
        st.markdown(
            """
            <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(56, 189, 248, 0.2); padding-bottom: 12px; margin-bottom: 16px;">
                <div>
                    <h2 style="color: #38bdf8; margin: 0; font-size: 1.65rem; font-weight: 700;">
                        🔬 Forensic Examiner Dashboard
                    </h2>
                    <p style="color: #94a3b8; font-size: 0.85rem; margin: 4px 0 0 0;">
                        Structured case examination, detector explainability, cross-evidence intelligence & audit trail analytics.
                    </p>
                </div>
                <div>
                    <span class="status-pill status-ready" style="font-size: 0.75rem; letter-spacing: 0.05em;">
                        PHASE 6 FORENSIC INTELLIGENCE
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        all_cases = self.case_mgr.list_cases()

        # Section A: Investigation Overview
        self.render_overview_section(all_cases)

        if not all_cases:
            st.info("ℹ️ No investigation cases registered in the system archive. Create or process a case in Multimodal Investigation to begin analysis.")
            return

        # Case Selection
        st.markdown("---")
        case_options = [c["investigation_id"] for c in all_cases]
        selected_id = st.selectbox(
            "Select Target Investigation Case for In-Depth Examination",
            options=case_options,
            key="examiner_dashboard_case_selector"
        )

        if not selected_id:
            return

        active_case = self.case_mgr.load_case(selected_id, record_reopen=False)
        if not active_case:
            st.error(f"Failed to load case data for investigation: {selected_id}")
            return

        # Examination Tabs
        tabs = st.tabs([
            "📊 Case Overview",
            "🔍 Evidence Intelligence",
            "🧠 Forensic Explainability",
            "⚖️ Evidence Comparison & Lineage",
            "⏱️ Audit Timeline Analytics",
            "📑 Report & Manifest Verification"
        ])

        with tabs[0]:
            self.render_case_metadata_tab(active_case)
        with tabs[1]:
            self.render_evidence_intelligence_tab(active_case)
        with tabs[2]:
            self.render_explainability_tab(active_case)
        with tabs[3]:
            self.render_comparison_tab(active_case)
        with tabs[4]:
            self.render_timeline_tab(active_case)
        with tabs[5]:
            self.render_reports_tab(active_case)

    # -------------------------------------------------------------------------
    # Section A: Investigation Overview Metrics
    # -------------------------------------------------------------------------
    def render_overview_section(self, all_cases: List[Dict[str, Any]]):
        """Renders high-level overview metrics across the case database."""
        metrics = self.compute_dashboard_metrics(all_cases)

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            st.metric("Total Cases", metrics["total_cases"])
        with c2:
            st.metric("Total Evidence", metrics["total_evidence"])
        with c3:
            st.metric("Images / Videos / Audio", f"{metrics['image_count']} / {metrics['video_count']} / {metrics['audio_count']}")
        with c4:
            st.metric("Analyzed Cases", metrics["completed_analysis"])
        with c5:
            st.metric("Reports Generated", metrics["generated_reports"])
        with c6:
            st.metric("Requires Review", metrics["requires_examination"])

        if all_cases:
            # Modality and status charts
            col_chart1, col_chart2 = st.columns([1, 1])
            with col_chart1:
                df_mod = pd.DataFrame([
                    {"Modality": "Images", "Count": metrics["image_count"]},
                    {"Modality": "Videos", "Count": metrics["video_count"]},
                    {"Modality": "Audio", "Count": metrics["audio_count"]},
                ])
                if df_mod["Count"].sum() > 0:
                    fig_mod = px.pie(
                        df_mod,
                        names="Modality",
                        values="Count",
                        title="Evidence Modality Distribution",
                        hole=0.4,
                        color_discrete_sequence=["#38bdf8", "#818cf8", "#c084fc"]
                    )
                    fig_mod.update_layout(
                        margin=dict(t=40, b=10, l=10, r=10),
                        height=220,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#94a3b8")
                    )
                    st.plotly_chart(fig_mod, use_container_width=True)
                else:
                    st.caption("No evidence items logged across cases yet.")

            with col_chart2:
                statuses = {}
                for c in all_cases:
                    s = c.get("status", "OPEN")
                    statuses[s] = statuses.get(s, 0) + 1
                df_status = pd.DataFrame([{"Status": k, "Count": v} for k, v in statuses.items()])
                fig_status = px.bar(
                    df_status,
                    x="Status",
                    y="Count",
                    title="Case Workflow Status Distribution",
                    color="Status",
                    color_discrete_sequence=["#0284c7", "#10b981", "#f59e0b", "#ef4444"]
                )
                fig_status.update_layout(
                    margin=dict(t=40, b=10, l=10, r=10),
                    height=220,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#94a3b8"),
                    showlegend=False
                )
                st.plotly_chart(fig_status, use_container_width=True)

    # -------------------------------------------------------------------------
    # Tab 0: Case Overview Metadata
    # -------------------------------------------------------------------------
    def render_case_metadata_tab(self, case_data: Dict[str, Any]):
        """Renders case summary and overall verdict."""
        st.markdown("#### 📋 Investigation Metadata")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"**Investigation ID:** `{case_data.get('investigation_id')}`")
            st.markdown(f"**Case Title:** {case_data.get('title', 'N/A')}")
            st.markdown(f"**Lead Examiner:** {case_data.get('investigator', 'Forensic Analyst')}")
            st.markdown(f"**Status:** `{case_data.get('status', 'OPEN')}`")
        with col2:
            st.markdown(f"**Created UTC:** {case_data.get('created_at', 'N/A')}")
            st.markdown(f"**Updated UTC:** {case_data.get('updated_at', 'N/A')}")
            rel = case_data.get("reliability_assessment") or {}
            verdict = rel.get("verdict_category", "Pending Evaluation")
            st.markdown(f"**Forensic Verdict:** **{verdict}**")
            st.markdown(f"**Evidentiary Strength:** {rel.get('evidence_strength', 'N/A')}")

        if rel.get("rationale"):
            st.info(f"**Technical Assessment Rationale:**\n\n{rel.get('rationale')}")

    # -------------------------------------------------------------------------
    # Tab 1: Evidence Intelligence
    # -------------------------------------------------------------------------
    def render_evidence_intelligence_tab(self, case_data: Dict[str, Any]):
        """Renders evidence items with verified hashes, detector labels, and scores."""
        st.markdown("#### 🗃️ Evidence Custody Inventory & Detector Activations")

        inventory = case_data.get("evidence_inventory", [])
        if not inventory:
            st.info("No evidence records present in this case.")
            return

        ind = case_data.get("individual_results") or {}
        img_dict = {im.get("filename"): im for im in ind.get("images", []) if isinstance(im, dict)}
        vid_dict = {vd.get("filename"): vd for vd in ind.get("videos", []) if isinstance(vd, dict)}
        aud_dict = {ad.get("filename"): ad for ad in ind.get("audios", []) if isinstance(ad, dict)}

        records = []
        for item in inventory:
            fn = item.get("filename", "")
            mod = item.get("modality", "")
            sha = item.get("sha256", "N/A")
            fsize = item.get("file_size", "N/A")

            # Resolve detector output
            det_label = "Not Inferred"
            det_score = "N/A"
            status = "Registered In Custody"

            if fn in img_dict:
                d = img_dict[fn]
                det_label = d.get("classification", "Unknown")
                det_score = f"Synthetic: {d.get('artificial_prob')}% | Human: {d.get('human_prob')}%"
                status = "Analysis Complete"
            elif fn in vid_dict:
                d = vid_dict[fn]
                s = d.get("summary", {})
                det_label = d.get("classification", "Unknown")
                det_score = f"Mean: {s.get('mean_synthetic_score')}% | Peak: {s.get('highest_synthetic_score')}%"
                status = "Analysis Complete"
            elif fn in aud_dict:
                d = aud_dict[fn]
                det_label = d.get("classification", "Unknown")
                det_score = f"Synthetic: {d.get('synthetic_score')}% | Authentic: {d.get('authentic_score')}%"
                status = "Analysis Complete"

            records.append({
                "Filename": fn,
                "Modality": mod,
                "Size": fsize,
                "SHA-256 Digest": sha,
                "Detector Verdict": det_label,
                "Model Scores (Uncalibrated)": det_score,
                "Status": status
            })

        df = pd.DataFrame(records)
        st.dataframe(df, use_container_width=True)

        st.caption("Notice: Model scores reflect raw uncalibrated softmax outputs of neural feature extractors, not absolute mathematical truth.")

    # -------------------------------------------------------------------------
    # Tab 2: Forensic Explainability
    # -------------------------------------------------------------------------
    def render_explainability_tab(self, case_data: Dict[str, Any]):
        """Renders grounded forensic explanations via ForensicExplainer."""
        st.markdown("#### 🧠 Grounded Inference Attribution & Operational Bounds")
        st.caption("Derived via ForensicExplainer. Explanations reflect verified detector architectures and documented empirical bounds.")

        explanations = self.case_mgr.get_forensic_explanations(case_data)
        if explanations.get("status") == "UNAVAILABLE":
            st.warning("Forensic explanation unavailable: malformed case structure.")
            return

        imgs = explanations.get("images", [])
        vids = explanations.get("videos", [])
        auds = explanations.get("audios", [])

        if not imgs and not vids and not auds:
            st.info("No detector inferences found in this case to explain.")
            return

        # Image Explanations
        if imgs:
            st.markdown("##### 🖼️ Image Detector Inferences (Swin Transformer)")
            for exp in imgs:
                if exp.get("status") == "UNAVAILABLE":
                    st.info(f"Image Explanation: {exp.get('reason', 'Analysis unavailable')}")
                    continue
                pipe = exp.get("pipeline_specification", {})
                prep = exp.get("verified_preprocessing", {})
                out = exp.get("output_interpretation", {})
                with st.expander(f"Image: {exp.get('evidence_target')} — {out.get('assigned_classification')}", expanded=True):
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.markdown(f"**Target Modality:** {exp.get('modality')}")
                        st.markdown(f"**Backbone:** `{pipe.get('model_architecture')}`")
                        st.markdown(f"**Execution Hardware:** {pipe.get('execution_hardware')}")
                        soft = out.get("uncalibrated_softmax_scores", {})
                        st.markdown(f"**Synthetic Probability:** {soft.get('synthetic_probability_pct')}%")
                        st.markdown(f"**Authentic Probability:** {soft.get('authentic_probability_pct')}%")
                    with c2:
                        st.markdown(f"**Input Dimensions:** {prep.get('input_resolution')}")
                        st.markdown(f"**Color Space:** {prep.get('color_space')}")
                        st.markdown(f"**Input Normalization:** {prep.get('tensor_normalization')}")
                        st.markdown(f"**Spatial Resizing:** {prep.get('spatial_resizing')}")

                    st.markdown(f"**Raw Logits:** *{out.get('raw_logits')}*")

                    uncert = exp.get("uncertainty_and_invalidation_factors", [])
                    if uncert:
                        st.markdown("**Uncertainty & Invalidation Factors:**")
                        for u in uncert:
                            st.markdown(f"- ⚠️ {u}")

                    excl = exp.get("explicit_operational_exclusions", [])
                    if excl:
                        st.markdown("**Explicit Operational Bounds:**")
                        for ex in excl:
                            st.markdown(f"- • {ex}")

        # Video Explanations
        if vids:
            st.markdown("##### 🎬 Video Screening Inferences (OpenCV + Frame Swin)")
            for exp in vids:
                if exp.get("status") == "UNAVAILABLE":
                    st.info(f"Video Explanation: {exp.get('reason', 'Analysis unavailable')}")
                    continue
                pipe = exp.get("pipeline_specification", {})
                sampling = exp.get("sampling_implementation", {})
                out = exp.get("output_interpretation", {})
                telemetry = exp.get("container_telemetry", {})
                with st.expander(f"Video: {exp.get('evidence_target')} — Flagged {out.get('flagged_frames_count')}/{sampling.get('actual_frames_sampled')} frames", expanded=True):
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.markdown(f"**Framing Pipeline:** {pipe.get('frame_extractor')}")
                        st.markdown(f"**Sampling Policy:** {sampling.get('sampling_strategy')}")
                        st.markdown(f"**Seek Mechanism:** {sampling.get('seek_mechanism')}")
                        st.markdown(f"**Sampled Frame Count:** {sampling.get('actual_frames_sampled')}")
                    with c2:
                        st.markdown(f"**Duration:** {telemetry.get('duration_seconds')}s | FPS: {telemetry.get('fps')}")
                        st.markdown(f"**Resolution:** {telemetry.get('resolution')}")
                        st.markdown(f"**Mean Synthetic Score:** {out.get('mean_synthetic_score')}%")
                        st.markdown(f"**Peak Synthetic Score:** {out.get('peak_synthetic_score')}%")

                    st.markdown(f"**Raw Logits:** *{out.get('raw_logits')}*")

                    uncert = exp.get("uncertainty_and_invalidation_factors", [])
                    if uncert:
                        st.markdown("**Video Forensic Limitations:**")
                        for u in uncert:
                            st.markdown(f"- ⚠️ {u}")

                    excl = exp.get("explicit_operational_exclusions", [])
                    if excl:
                        st.markdown("**Operational Exclusions:**")
                        for ex in excl:
                            st.markdown(f"- • {ex}")

        # Audio Explanations
        if auds:
            st.markdown("##### 🎙️ Audio Classifier Inferences (Wav2Vec 2.0)")
            for exp in auds:
                if exp.get("status") == "UNAVAILABLE":
                    st.info(f"Audio Explanation: {exp.get('reason', 'Analysis unavailable')}")
                    continue
                pipe = exp.get("pipeline_specification", {})
                prep = exp.get("verified_preprocessing", {})
                out = exp.get("output_interpretation", {})
                with st.expander(f"Audio: {exp.get('evidence_target')} — {out.get('assigned_classification')}", expanded=True):
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.markdown(f"**Acoustic Backbone:** `{pipe.get('model_architecture')}`")
                        st.markdown(f"**Execution Hardware:** {pipe.get('execution_hardware')}")
                        soft = out.get("uncalibrated_softmax_scores", {})
                        st.markdown(f"**Synthetic Probability:** {soft.get('synthetic_score_pct')}%")
                        st.markdown(f"**Authentic Probability:** {soft.get('authentic_score_pct')}%")
                    with c2:
                        st.markdown(f"**Resampling Rate:** {prep.get('target_sampling_rate_hz')} Hz")
                        st.markdown(f"**Channel Handling:** {prep.get('downmixing')}")
                        st.markdown(f"**Energy Safeguard:** {prep.get('energy_validation')}")

                    st.markdown(f"**Raw Logits:** *{out.get('raw_logits')}*")

                    uncert = exp.get("uncertainty_and_invalidation_factors", [])
                    if uncert:
                        st.markdown("**Vocoder Domain Shift & Uncertainty:**")
                        for u in uncert:
                            st.markdown(f"- ⚠️ {u}")

                    excl = exp.get("explicit_operational_exclusions", [])
                    if excl:
                        st.markdown("**Explicit Exclusions:**")
                        for ex in excl:
                            st.markdown(f"- • {ex}")

    # -------------------------------------------------------------------------
    # Tab 3: Evidence Comparison & Lineage
    # -------------------------------------------------------------------------
    def render_comparison_tab(self, case_data: Dict[str, Any]):
        """Renders evidence comparisons, temporal video scores, and verified lineage."""
        st.markdown("#### ⚖️ Evidence Comparison, Temporal Variance & Provenance Lineage")

        comps = self.case_mgr.get_evidence_comparisons(case_data)
        if comps.get("status") == "UNAVAILABLE":
            st.warning("Evidence comparison data unavailable.")
            return

        # 1. Verified Lineage
        st.markdown("##### 🔗 Cryptographic Provenance & Lineage Analysis")
        st.caption("Provenance strictly requires verified source hashes, evidence IDs, or container links. Filenames alone NEVER establish lineage.")
        lineage = comps.get("verified_lineage", {})
        pairs = lineage.get("verified_lineages", [])
        unverified = lineage.get("unverified_associations", [])
        all_pairs = pairs + unverified
        if all_pairs:
            lineage_records = []
            for lp in all_pairs:
                lineage_records.append({
                    "Child Evidence": lp.get("child_filename"),
                    "Parent Evidence": lp.get("parent_filename"),
                    "Relationship": lp.get("relationship"),
                    "Verified Status": "VERIFIED PROVENANCE" if lp.get("verified_provenance") else "UNVERIFIED ASSOCIATION",
                    "Linkage Basis": lp.get("provenance_type")
                })
            st.dataframe(pd.DataFrame(lineage_records), use_container_width=True)
        else:
            st.info("No parent-child or stream-extraction relationships detected in this case inventory.")

        # 2. Video Temporal Frame Score Analysis
        st.markdown("##### 📈 Video Temporal Score Statistics Across Sampled Frames")
        v_stats = comps.get("video_temporal_statistics", [])
        if v_stats:
            for vs in v_stats:
                with st.expander(f"Video: {vs.get('filename')}", expanded=True):
                    c1, c2, c3, c4 = st.columns(4)
                    metrics_dict = vs.get("score_metrics", {})
                    with c1:
                        st.metric("Total Sampled Frames", vs.get("total_frames_evaluated", 0))
                    with c2:
                        st.metric("Mean Score", f"{metrics_dict.get('mean_synthetic_score', 0.0)}%")
                    with c3:
                        st.metric("Score Std Dev", f"{metrics_dict.get('std_deviation', 0.0)}")
                    with c4:
                        st.metric("Threshold Crossings", vs.get("threshold_crossings_count", 0))

                    # Plot temporal frame scores if frames exist
                    ind = case_data.get("individual_results") or {}
                    for vd in ind.get("videos", []):
                        if vd.get("filename") == vs.get("filename") and vd.get("frame_results"):
                            fr = vd["frame_results"]
                            df_fr = pd.DataFrame([
                                {
                                    "Frame Index": f.get("frame_index"),
                                    "Timestamp": f.get("formatted_timestamp", f"{f.get('timestamp_sec', 0)}s"),
                                    "Synthetic Score (%)": f.get("artificial_prob", f.get("synthetic_score", 0.0))
                                }
                                for f in fr
                            ])
                            fig_ts = px.line(
                                df_fr,
                                x="Frame Index",
                                y="Synthetic Score (%)",
                                markers=True,
                                title=f"Frame-by-Frame Softmax Trajectory: {vs.get('filename')}",
                                color_discrete_sequence=["#ef4444"]
                            )
                            fig_ts.add_hline(y=50.0, line_dash="dash", line_color="#f59e0b", annotation_text="50% Classification Threshold")
                            fig_ts.update_layout(
                                margin=dict(t=40, b=10, l=10, r=10),
                                height=260,
                                paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)",
                                font=dict(color="#94a3b8")
                            )
                            st.plotly_chart(fig_ts, use_container_width=True)
        else:
            st.info("No video frame sequences present to analyze temporal statistics.")

        # 3. Separated Audio Stream Comparison
        st.markdown("##### 🎙️ Separated Audio Stream Comparisons")
        a_comps = comps.get("audio_comparisons", [])
        if a_comps:
            for ac in a_comps:
                with st.expander(f"Audio Pair: {ac.get('pair')}", expanded=True):
                    c_tech, c_acoust = st.columns([1, 1])
                    with c_tech:
                        st.markdown("**Technical Container Comparison:**")
                        tech = ac.get("technical_container_comparison", {})
                        st.markdown(f"- Duration Delta: `{tech.get('duration_delta_seconds')}s`")
                        st.markdown(f"- Sample Rate Delta: `{tech.get('sample_rate_delta_hz')} Hz`")
                        st.markdown(f"- Channels Match: `{tech.get('channels_match')}`")
                    with c_acoust:
                        st.markdown("**Acoustic Energy Comparison:**")
                        acoust = ac.get("acoustic_statistics_comparison", {})
                        st.markdown(f"- RMS Energy Delta: `{acoust.get('rms_energy_delta')}`")
                        st.markdown(f"- Relative Energy Ratio: `{acoust.get('relative_energy_ratio')}`")
                        st.markdown(f"- Energy Disparity Flag: `{acoust.get('energy_disparity_flag')}`")

                    st.caption("Notice: Container metadata match and acoustic energy proximity do NOT establish identical recording origin.")
        else:
            st.info("Requires at least two audio streams in the investigation for comparative analysis.")

    # -------------------------------------------------------------------------
    # Tab 4: Investigation Timeline Analytics
    # -------------------------------------------------------------------------
    def render_timeline_tab(self, case_data: Dict[str, Any]):
        """Renders cryptographic audit timeline and sequence preservation."""
        st.markdown("#### ⏱️ Cryptographic Audit Ledger & Chronological Timeline")

        timeline = self.case_mgr.get_timeline_analytics(case_data)
        if timeline.get("status") == "UNAVAILABLE":
            st.warning("Audit timeline analytics unavailable.")
            return

        is_valid = timeline.get("hash_chain_valid", False)
        if is_valid:
            st.success(f"🔒 **Audit Chain Cryptographically Valid:** {timeline.get('total_events', 0)} sequential events intact.")
        else:
            reason = timeline.get("hash_chain_details", "") or "Ledger sequence tampering or broken hash link detected."
            st.error(f"⚠️ **Hash Chain Alert:** Ledger sequence tampering or missing hash links detected! {reason}")

        st.caption(
            "Cryptographic Notice: Hash-chain verification confirms consistency against the recorded hash sequence "
            "and detects modifications that invalidate the existing chain. It does not guarantee immutability against "
            "an attacker with filesystem access who can rewrite the local ledger and recompute hashes, nor does it independently "
            "validate host clock accuracy or timestamp authenticity."
        )

        # Timestamp anomalies
        anomalies = timeline.get("timestamp_anomalies", [])
        if anomalies:
            st.markdown("##### ⚠️ Detected Timestamp Anomalies")
            for an in anomalies:
                st.warning(f"Event #{an.get('sequence_index')} ({an.get('action')}) at {an.get('timestamp')}: {an.get('description')}")

        # Events table
        records = timeline.get("timeline_records", [])
        if records:
            st.markdown("##### 📜 Chronological Audit Ledger (Sequence Strictly Preserved)")
            df_timeline = pd.DataFrame([
                {
                    "Seq #": r.get("sequence_index"),
                    "Action": r.get("action"),
                    "Timestamp (UTC)": r.get("timestamp_display"),
                    "Evidence ID": r.get("evidence_id") or "N/A",
                    "Event Hash (Truncated)": f"{r.get('event_hash', '')[:16]}..." if r.get('event_hash') else "N/A",
                    "Details": r.get("details")
                }
                for r in records
            ])
            st.dataframe(df_timeline, use_container_width=True)

            # Timeline visualization
            df_plot = pd.DataFrame([
                {
                    "Action": r.get("action"),
                    "Timestamp": r.get("timestamp_display"),
                    "Sequence": r.get("sequence_index")
                }
                for r in records
            ])
            fig_tl = px.scatter(
                df_plot,
                x="Sequence",
                y="Action",
                color="Action",
                title="Investigation Audit Event Trajectory",
                labels={"Sequence": "Ledger Event Sequence Index", "Action": "Forensic Action"}
            )
            fig_tl.update_layout(
                margin=dict(t=40, b=10, l=10, r=10),
                height=260,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"),
                showlegend=False
            )
            st.plotly_chart(fig_tl, use_container_width=True)
        else:
            st.info("No audit entries recorded for this case.")

    # -------------------------------------------------------------------------
    # Tab 5: Report Management & Manifest Verification
    # -------------------------------------------------------------------------
    def render_reports_tab(self, case_data: Dict[str, Any]):
        """Allows generating PDF reports and verifying detached SHA-256 manifests."""
        st.markdown("#### 📑 Forensic PDF Report Generation & Manifest Verification")

        inv_id = case_data.get("investigation_id")
        current_pdf_path = case_data.get("report_pdf_path")

        c1, c2 = st.columns([1, 1])

        with c1:
            st.markdown("##### 📄 Report Generation")
            if st.button("Generate Formal Incident Report (PDF)", type="primary", key="btn_gen_report"):
                with st.spinner("Compiling multi-page incident report with explainability & comparison matrices..."):
                    try:
                        pdf_path = self.report_gen.generate_investigation_pdf(case_data)
                        case_data["report_pdf_path"] = pdf_path
                        pdf_sha = ForensicReportGenerator.compute_file_sha256(pdf_path)
                        self.case_mgr.log_report_generated(case_data, os.path.basename(pdf_path), pdf_sha)
                        self.case_mgr.save_case(case_data)
                        st.success(f"Report generated successfully: `{os.path.basename(pdf_path)}`")
                        current_pdf_path = pdf_path
                    except Exception as e:
                        st.error(f"Report generation error: {e}")

            if current_pdf_path and os.path.exists(current_pdf_path):
                with open(current_pdf_path, "rb") as f_pdf:
                    st.download_button(
                        label=f"📥 Download Incident Report ({os.path.basename(current_pdf_path)})",
                        data=f_pdf.read(),
                        file_name=os.path.basename(current_pdf_path),
                        mime="application/pdf",
                        key="btn_dl_report"
                    )

        with c2:
            st.markdown("##### 🛡️ Cryptographic Manifest Verification")
            if current_pdf_path and os.path.exists(current_pdf_path):
                manifest_path = f"{current_pdf_path}.manifest.json"
                if os.path.exists(manifest_path):
                    with open(manifest_path, "r", encoding="utf-8") as mf:
                        manifest_json = json.load(mf)
                    st.markdown(f"**Recorded SHA-256 Digest:** `{manifest_json.get('sha256_hash')}`")
                    st.markdown(f"**Generation Timestamp:** `{manifest_json.get('generation_timestamp')}`")

                    # Live verification
                    res = ForensicReportGenerator.verify_report_integrity(current_pdf_path)
                    if res.get("valid"):
                        st.success("✅ **Manifest Verification Valid:** PDF SHA-256 matches detached cryptographic manifest exactly.")
                    else:
                        st.error(f"❌ **Manifest Verification Failed:** {res.get('reason')}")
                else:
                    st.warning("Detached manifest file (.manifest.json) not found for this report.")
            else:
                st.info("No generated report present for this case yet. Click 'Generate Formal Incident Report' to compile one.")
