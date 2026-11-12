import streamlit as st
import pandas as pd
from PIL import Image
import io

from src.components.sidebar import load_custom_css, render_sidebar
from src.components.cards import page_header, coming_soon_card
from src.utils.file_handler import extract_forensic_metadata
from src.modules.image_detector import ImageForensicDetector
from src.modules.video_detector import VideoForensicPipeline
from src.modules.audio_detector import AudioForensicDetector
from src.modules.case_manager import CaseManager
from src.modules.evidence_correlator import EvidenceCorrelator
from src.modules.reliability_engine import ForensicReliabilityEngine
from src.modules.report_generator import ForensicReportGenerator
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(
    page_title="DEEPFAKE X – Multimodal Media Forensics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Inject Cyber Theme CSS
load_custom_css()

# 3. Session State Initialization for File Evidence Registry
if "evidence_registry" not in st.session_state:
    st.session_state.evidence_registry = {
        "images": [],
        "videos": [],
        "audios": [],
        "documents": [],
    }

# 4. Render Unified Navigation Sidebar
current_page = render_sidebar()

# -------------------------------------------------------------
# PAGE ROUTING
# -------------------------------------------------------------

if current_page == "Overview":
    page_header(
        title="DEEPFAKE X Intelligence Hub",
        subtitle="Multimodal Synthetic Media Forensics, Provenance Verification & Authenticity Defense Platform",
        badge="SYSTEM OPERATIONAL"
    )

    # Top KPI Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            """
            <div class="cyber-card">
                <div class="metric-label">FORENSIC SUITES</div>
                <div class="metric-value">7 MODES</div>
                <span style="font-size: 0.75rem; color: #34d399;">● Full Multimodal Support</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m2:
        total_files = sum(len(files) for files in st.session_state.evidence_registry.values())
        st.markdown(
            f"""
            <div class="cyber-card">
                <div class="metric-label">INGESTED EVIDENCE</div>
                <div class="metric-value">{total_files} ITEMS</div>
                <span style="font-size: 0.75rem; color: #22d3ee;">● Cryptographically Sealed</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            """
            <div class="cyber-card">
                <div class="metric-label">ACCELERATION HARDWARE</div>
                <div class="metric-value">RTX 2050</div>
                <span style="font-size: 0.75rem; color: #a855f7;">● Dedicated Tensor Cores</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            """
            <div class="cyber-card">
                <div class="metric-label">PROVENANCE PROTOCOL</div>
                <div class="metric-value">C2PA / W3C</div>
                <span style="font-size: 0.75rem; color: #22d3ee;">● Content Credentials V2</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Core System Architecture & Modalities
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown("### 🔬 Multi-Modal Forensic Capabilities")
        st.markdown(
            """
            <div class="cyber-card">
                <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem;">
                    <thead>
                        <tr style="border-bottom: 1px solid rgba(34, 211, 238, 0.2); text-align: left; color: #94a3b8;">
                            <th style="padding: 8px 4px;">Modality</th>
                            <th style="padding: 8px 4px;">Target Artifacts</th>
                            <th style="padding: 8px 4px;">Verification Methodology</th>
                            <th style="padding: 8px 4px;">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                            <td style="padding: 10px 4px; font-weight: 600; color: #22d3ee;">Image Forensics</td>
                            <td style="color: #cbd5e1;">Diffusion, GAN, Midjourney</td>
                            <td style="color: #94a3b8;">FFT Spectral & Error Level Analysis</td>
                            <td><span class="status-pill status-ready">Phase 1 Ingestion</span></td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                            <td style="padding: 10px 4px; font-weight: 600; color: #22d3ee;">Video Deepfakes</td>
                            <td style="color: #cbd5e1;">Face-swap, Lip-sync, Re-enactment</td>
                            <td style="color: #94a3b8;">Temporal Flickering & Blink Biometrics</td>
                            <td><span class="status-pill status-ready">Phase 1 Ingestion</span></td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                            <td style="padding: 10px 4px; font-weight: 600; color: #22d3ee;">Voice Cloning</td>
                            <td style="color: #cbd5e1;">ElevenLabs, VALL-E, TTS</td>
                            <td style="color: #94a3b8;">Spectrogram Formant & Phase Disparity</td>
                            <td><span class="status-pill status-ready">Phase 1 Ingestion</span></td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                            <td style="padding: 10px 4px; font-weight: 600; color: #22d3ee;">Documents</td>
                            <td style="color: #cbd5e1;">Forged PDFs, Invoices, Contracts</td>
                            <td style="color: #94a3b8;">Font Glyphs, Copy-Move, Metadata Delta</td>
                            <td><span class="status-pill status-ready">Phase 1 Ingestion</span></td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 4px; font-weight: 600; color: #c084fc;">Cross-Modal XAI</td>
                            <td style="color: #cbd5e1;">Audio-Video Desynchronization</td>
                            <td style="color: #94a3b8;">Phoneme-Viseme Alignment & Grad-CAM</td>
                            <td><span class="status-pill status-coming-soon">Phase 2 Pipeline</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown("### 🛡️ System Integrity & Security")
        st.markdown(
            """
            <div class="cyber-card-purple">
                <div style="font-size: 0.9rem; font-weight: 600; color: #f8fafc; margin-bottom: 8px;">
                    Zero Fabricated Results Policy
                </div>
                <p style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.5; margin-bottom: 12px;">
                    DEEPFAKE X operates strictly according to Structured Forensic Evidence Handling principles. No placeholder synthetic probability scores are fabricated.
                </p>
                <div class="forensic-notice notice-phase" style="margin: 0; padding: 10px 14px;">
                    <div style="font-weight: 600; color: #22d3ee; font-size: 0.8rem;">CRYPTO-SEAL VERIFICATION</div>
                    <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 4px;">
                        All evidence ingested into DEEPFAKE X receives instantaneous SHA-256 cryptographic fingerprinting ensuring unbroken chain of custody.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

elif current_page == "Multimodal Investigation":
    page_header(
        title="Multimodal Forensic Investigation Center",
        subtitle="Ingest images, videos, and audio evidence simultaneously for coordinated cross-modal examination.",
        badge="MULTIMODAL INTELLIGENCE ACTIVE"
    )

    case_mgr = CaseManager.get_instance()
    rel_engine = ForensicReliabilityEngine.get_instance()
    correlator = EvidenceCorrelator.get_instance()
    pdf_gen = ForensicReportGenerator.get_instance()

    c_top1, c_top2 = st.columns([1.2, 1])
    with c_top1:
        st.markdown("#### 📁 Active Case Context")
        case_title = st.text_input("Case Title / Subject", value="Incident Case 2026-X", key="case_title_input")
        investigator_name = st.text_input("Lead Investigator", value="Senior Forensic Analyst", key="inv_name_input")
        investigation_notes = st.text_area("Investigation Notes / Brief", placeholder="Enter investigative context, source notes, or chain of custody origins...", key="inv_notes_input")

    with c_top2:
        st.markdown("#### 🛡️ Forensic Intake Guidelines")
        st.markdown(
            """
            <div class="cyber-card" style="font-size: 0.84rem; line-height: 1.5; color: #94a3b8;">
                <b style="color: #22d3ee;">Unified Cross-Modal Intake:</b><br>
                • Ingest multiple files across modalities (Images, Videos, Audio).<br>
                • Automatic media classification and SHA-256 fingerprinting.<br>
                • Sequential GPU execution on RTX 2050 to maintain memory bounds.<br>
                • Cross-modal correlation matrix with discrepancy flagging.
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("### 📥 Multimodal Evidence Ingestion (Batch Drag-and-Drop)")
    multi_files = st.file_uploader(
        "Upload any combination of images (JPG, PNG, WEBP), videos (MP4, MOV, AVI), and audio recordings (WAV, MP3, FLAC)",
        type=["jpg", "jpeg", "png", "webp", "mp4", "mov", "avi", "wav", "mp3", "flac"],
        accept_multiple_files=True,
        key="batch_multimodal_uploader"
    )

    if multi_files:
        st.success(f"✓ {len(multi_files)} media item(s) staged for intake.")
        
        # Categorize uploaded media
        st_images = []
        st_videos = []
        st_audios = []
        for mf in multi_files:
            fname = mf.name.lower()
            if any(fname.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                st_images.append(mf)
            elif any(fname.endswith(ext) for ext in [".mp4", ".mov", ".avi"]):
                st_videos.append(mf)
            elif any(fname.endswith(ext) for ext in [".wav", ".mp3", ".flac"]):
                st_audios.append(mf)

        st.caption(f"Identified Modalities: **{len(st_images)} Image(s)** | **{len(st_videos)} Video(s)** | **{len(st_audios)} Audio Sample(s)**")

        run_investigation_btn = st.button("🚀 Execute Unified Multimodal Investigation", type="primary", use_container_width=True)

        inv_session_key = f"active_investigation_{len(multi_files)}"
        if run_investigation_btn:
            prog = st.progress(0.0)
            status_box = st.empty()

            # 1. Initialize Case
            status_box.info("Initializing secure case container and SHA-256 fingerprinting...")
            active_case = case_mgr.create_case(title=case_title, investigator=investigator_name, notes=investigation_notes)
            
            # 2. Vaulting & Inventory
            inventory = []
            for mf in multi_files:
                b = mf.getvalue()
                h = case_mgr.store_evidence_file(b, mf.name, case_mgr.compute_sha256(b))
                sha = case_mgr.compute_sha256(b)
                modality = "Image" if mf in st_images else ("Video" if mf in st_videos else "Audio")
                inventory.append({
                    "filename": mf.name,
                    "modality": modality,
                    "file_size": f"{len(b)/(1024*1024):.2f} MB",
                    "sha256": sha
                })
            active_case["evidence_inventory"] = inventory
            prog.progress(0.2)

            # 3. Sequential Execution - Images
            img_detector = ImageForensicDetector.get_instance()
            for idx, img_f in enumerate(st_images):
                status_box.info(f"Analyzing image [{idx+1}/{len(st_images)}]: {img_f.name}...")
                pil_im = Image.open(img_f)
                im_res = img_detector.analyze_image(pil_im)
                im_res["filename"] = img_f.name
                im_res["sha256"] = case_mgr.compute_sha256(img_f.getvalue())
                active_case["individual_results"]["images"].append(im_res)
            prog.progress(0.5)

            # 4. Sequential Execution - Videos
            vid_pipeline = VideoForensicPipeline.get_instance()
            for idx, vid_f in enumerate(st_videos):
                status_box.info(f"Screening video [{idx+1}/{len(st_videos)}]: {vid_f.name}...")
                v_res = vid_pipeline.inspect_and_sample_video(vid_f.getvalue(), vid_f.name, num_frames=8)
                active_case["individual_results"]["videos"].append(v_res)
            prog.progress(0.7)

            # 5. Sequential Execution - Audio
            aud_detector = AudioForensicDetector.get_instance()
            for idx, aud_f in enumerate(st_audios):
                status_box.info(f"Evaluating audio [{idx+1}/{len(st_audios)}]: {aud_f.name}...")
                a_res = aud_detector.process_and_analyze_audio(aud_f.getvalue(), aud_f.name)
                active_case["individual_results"]["audios"].append(a_res)
            prog.progress(0.85)

            # 6. Cross-Modal Correlation & Reliability Assessment
            status_box.info("Computing cross-modal evidence correlation matrix...")
            corr_matrix = correlator.correlate_evidence(
                images=active_case["individual_results"]["images"],
                videos=active_case["individual_results"]["videos"],
                audios=active_case["individual_results"]["audios"]
            )
            active_case["correlation_analysis"] = corr_matrix

            rel_verdict = rel_engine.evaluate_investigation(
                image_results=active_case["individual_results"]["images"],
                video_results=active_case["individual_results"]["videos"],
                audio_results=active_case["individual_results"]["audios"],
                correlation_matrix=corr_matrix
            )
            active_case["reliability_assessment"] = rel_verdict

            # 7. Generate PDF Report
            status_box.info("Building formal forensic PDF document...")
            pdf_path = pdf_gen.generate_investigation_pdf(active_case)
            active_case["report_pdf_path"] = pdf_path

            # Save Case
            case_mgr.save_case(active_case)
            prog.progress(1.0)
            status_box.success("✓ Multimodal investigation execution complete!")
            st.session_state[inv_session_key] = active_case

        # Display Investigation Results if Available
        if inv_session_key in st.session_state:
            res_case = st.session_state[inv_session_key]
            rel_res = res_case.get("reliability_assessment", {})
            corr_res = res_case.get("correlation_analysis", {})

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 📋 Unified Investigation Dashboard")

            # High-level assessment callout
            verdict_cat = rel_res.get("verdict_category", "Unknown")
            is_threat = "manipulation" in verdict_cat.lower() or "conflicting" in verdict_cat.lower()
            v_color = "#ef4444" if "strong" in verdict_cat.lower() else ("#f59e0b" if is_threat else "#10b981")
            v_bg = "rgba(239, 68, 68, 0.12)" if "strong" in verdict_cat.lower() else ("rgba(245, 158, 11, 0.12)" if is_threat else "rgba(16, 185, 129, 0.12)")

            st.markdown(
                f"""
                <div class="cyber-card" style="border: 1px solid {v_color}; background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), {v_bg}); padding: 20px;">
                    <div style="font-size: 0.75rem; letter-spacing: 0.1em; color: #94a3b8; text-transform: uppercase;">
                        MULTIMODAL RELIABILITY SYNTHESIS (STRUCTURED FORENSIC EVALUATION)
                    </div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: {v_color}; margin: 6px 0 8px 0;">
                        {verdict_cat}
                    </div>
                    <div style="font-size: 0.9rem; color: #cbd5e1; line-height: 1.5; margin-bottom: 12px;">
                        <b>Evidentiary Strength:</b> {rel_res.get('evidence_strength')}<br>
                        <b>Forensic Rationale:</b> {rel_res.get('rationale')}
                    </div>
                    <div style="font-size: 0.75rem; color: #94a3b8; border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 8px;">
                        Investigation ID: <code style="color: #38bdf8;">{res_case.get('investigation_id')}</code> | Generated PDF Ready for Export
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # PDF Download Button
            pdf_file_path = res_case.get("report_pdf_path")
            if pdf_file_path and os.path.exists(pdf_file_path):
                with open(pdf_file_path, "rb") as pdf_data:
                    st.download_button(
                        label="📥 Download Official Forensic PDF Investigation Report",
                        data=pdf_data.read(),
                        file_name=os.path.basename(pdf_file_path),
                        mime="application/pdf",
                        type="primary"
                    )

            # Modality Tabs
            tab_ind, tab_corr, tab_inv = st.tabs([
                "🔬 Individual Detection Findings",
                "⚡ Cross-Modal Evidence Comparison",
                "🗃️ Evidence Custody Inventory"
            ])

            with tab_ind:
                indiv = res_case.get("individual_results", {})
                
                # Render Image Findings
                if indiv.get("images"):
                    st.markdown("##### 🖼️ Image Forensics Results")
                    for im in indiv["images"]:
                        col_a, col_b = st.columns([1, 2])
                        with col_a:
                            st.write(f"**{im.get('filename')}**")
                            st.caption(f"Dimensions: {im.get('dimensions')} | Device: {im.get('device')}")
                        with col_b:
                            st.write(f"Classification: **{im.get('classification')}** ({im.get('confidence_pct')}%)")
                            st.write(f"Synthetic: `{im.get('artificial_prob')}%` | Authentic: `{im.get('human_prob')}%`")
                            st.progress(float(im.get('artificial_prob', 0.0)) / 100.0)
                    st.markdown("---")

                # Render Video Findings
                if indiv.get("videos"):
                    st.markdown("##### 🎬 Video Forensics Results")
                    for vd in indiv["videos"]:
                        sum_v = vd.get("summary", {})
                        st.write(f"**{vd.get('filename')}** (Duration: {vd.get('video_metadata', {}).get('duration_seconds')}s)")
                        st.write(f"Flagged Frames: **{sum_v.get('synthetic_flagged_count')} / {sum_v.get('total_analyzed_frames')}** | Mean Synthetic: `{sum_v.get('mean_synthetic_score')}%` | Peak: `{sum_v.get('highest_synthetic_score')}%`")
                    st.markdown("---")

                # Render Audio Findings
                if indiv.get("audios"):
                    st.markdown("##### 🎙️ Audio Forensics Results")
                    for ad in indiv["audios"]:
                        st.write(f"**{ad.get('filename')}** (Duration: {ad.get('audio_metadata', {}).get('duration_seconds')}s)")
                        st.write(f"Classification: **{ad.get('classification')}** ({ad.get('confidence_pct')}%)")
                        st.write(f"Synthetic: `{ad.get('synthetic_score')}%` | Authentic: `{ad.get('authentic_score')}%`")
                        st.progress(float(ad.get('synthetic_score', 0.0)) / 100.0)

            with tab_corr:
                st.markdown("##### ⚡ Cross-Modal Pairwise Evidence Comparison")
                corrs = corr_res.get("correlations", [])
                if corrs:
                    for c in corrs:
                        sync_alert = c.get("sync_anomaly_flag", False)
                        disagree = c.get("detector_agreement") == "DISAGREEING_FINDINGS"
                        c_box_color = "rgba(239, 68, 68, 0.3)" if (sync_alert or disagree) else "rgba(56, 189, 248, 0.2)"
                        
                        st.markdown(
                            f"""
                            <div class="cyber-card" style="border: 1px solid {c_box_color}; padding: 12px; margin-bottom: 8px;">
                                <div style="display: flex; justify-content: space-between;">
                                    <b>{c.get('pair')}</b>
                                    <span style="font-size: 0.78rem; color: #22d3ee;">{c.get('relationship_type')}</span>
                                </div>
                                <div style="font-size: 0.85rem; color: #cbd5e1; margin-top: 4px;">
                                    {c.get('finding')}
                                </div>
                                <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">
                                    Status: <b>{c.get('detector_agreement')}</b> | {c.get('notes')}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No cross-modal pairs to correlate (requires multiple media files across different sensory domains).")

            with tab_inv:
                st.markdown("##### 🗃️ Cryptographically Sealed Custody Ledger")
                inv_list = res_case.get("evidence_inventory", [])
                if inv_list:
                    st.dataframe(pd.DataFrame(inv_list), use_container_width=True)

elif current_page == "Case Management":
    page_header(
        title="Case Management System & Evidence Archive",
        subtitle="Review, audit, reopen, and export historical multimodal forensics investigations.",
        badge="CASE REPOSITORY"
    )

    case_mgr = CaseManager.get_instance()
    all_cases = case_mgr.list_cases()

    st.markdown("### 📂 Registered Forensic Investigations")
    if all_cases:
        df_cases = pd.DataFrame(all_cases)
        st.dataframe(df_cases, use_container_width=True)

        selected_case_id = st.selectbox("Select Investigation ID to Inspect / Reopen", [c["investigation_id"] for c in all_cases])
        if selected_case_id:
            full_case = case_mgr.load_case(selected_case_id, record_reopen=True)
            if full_case:
                st.markdown(f"#### Investigation Overview: `{selected_case_id}`")
                st.write(f"**Title:** {full_case.get('title')}")
                st.write(f"**Investigator:** {full_case.get('investigator')}")
                st.write(f"**Created:** {full_case.get('created_at')}")
                st.write(f"**Status:** {full_case.get('status')}")
                st.write(f"**Overall Verdict:** {full_case.get('reliability_assessment', {}).get('verdict_category', 'N/A')}")
                
                # Audit chain verification badge
                audit_check = case_mgr.verify_audit_trail_integrity(full_case)
                if audit_check.get("valid"):
                    st.success(f"🔒 **Cryptographic Hash Chain Verified:** {audit_check.get('count')} tamper-evident events intact.")
                else:
                    st.error(f"⚠️ **Hash Chain Alert:** {audit_check.get('message')}")

                rep_path = full_case.get("report_pdf_path")
                if rep_path and os.path.exists(rep_path):
                    with open(rep_path, "rb") as f_pdf:
                        dl_clicked = st.download_button(
                            label=f"📥 Download Report ({selected_case_id})",
                            data=f_pdf.read(),
                            file_name=os.path.basename(rep_path),
                            mime="application/pdf",
                            key=f"dl_case_{selected_case_id}"
                        )
                        if dl_clicked:
                            case_mgr.log_report_exported(selected_case_id, os.path.basename(rep_path))
    else:
        st.info("No cases created yet. Execute a Multimodal Investigation to automatically generate forensic cases.")

elif current_page == "Settings":
    page_header(
        title="System Settings & Telemetry",
        subtitle="Manage hardware acceleration profiles, forensic thresholds, and pipeline limits.",
        badge="SYSTEM CONFIG"
    )

    st.markdown("### ⚙️ Engine Telemetry & Hardware Profile")
    st.markdown(
        """
        <div class="cyber-card">
            <table style="width: 100%; font-size: 0.88rem; color: #cbd5e1;">
                <tr><td style="padding: 6px;">GPU Target:</td><td><b>NVIDIA GeForce RTX 2050 (4 GB VRAM)</b></td></tr>
                <tr><td style="padding: 6px;">Image Backbone:</td><td><b>Swin Transformer (umm-maybe/AI-image-detector)</b></td></tr>
                <tr><td style="padding: 6px;">Video Screening:</td><td><b>OpenCV Uniform Frame Extraction (60s / 100MB bound)</b></td></tr>
                <tr><td style="padding: 6px;">Audio Backbone:</td><td><b>Wav2Vec 2.0 (MelodyMachine/Deepfake-audio-detection-V2)</b></td></tr>
                <tr><td style="padding: 6px;">Evidence Integrity:</td><td><b>SHA-256 Cryptographic Hash Chain & Manifests</b></td></tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True
    )

elif current_page == "Image Analysis":
    page_header(
        title="AI-Generated Image Forensics",
        subtitle="Detect synthetic generation traces from Stable Diffusion, Midjourney, DALL-E, and GAN architectures using deep neural classifiers.",
        badge="NEURAL PIPELINE ACTIVE"
    )

    c1, c2 = st.columns([1, 1.2])
    with c1:
        img_file = st.file_uploader("Upload Image to Inspect", type=["jpg", "jpeg", "png", "webp"], key="img_inspect")
        if img_file:
            pil_img = Image.open(img_file)
            st.image(pil_img, caption=f"Uploaded: {img_file.name}", use_container_width=True)
            meta = extract_forensic_metadata(img_file)
            st.markdown(
                f"""
                <div class="cyber-card">
                    <div style="font-weight: 700; color: #22d3ee; margin-bottom: 6px;">EVIDENCE METRICS</div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">Dimensions: <b>{pil_img.width} × {pil_img.height} px</b></div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">File Size: <b>{meta['File Size']}</b></div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">Format: <b>{pil_img.format or 'Unknown'}</b></div>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">SHA-256 Hash:</div>
                    <code style="word-break: break-all; font-size: 0.75rem; color: #38bdf8;">{meta['SHA-256 Hash']}</code>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("Upload an image file above to inspect metadata and perform neural forensic classification.")

    with c2:
        if img_file:
            st.markdown("### 🔬 Live Neural Forensic Inference")
            run_btn = st.button("🚀 Run AI Forensics Scan", type="primary", use_container_width=True)
            
            # Persist analysis in session state per file hash
            state_key = f"analysis_{meta['SHA-256 Hash']}"
            if run_btn:
                with st.spinner("Extracting latent representations & executing inference on GPU..."):
                    try:
                        detector = ImageForensicDetector.get_instance()
                        results = detector.analyze_image(pil_img)
                        st.session_state[state_key] = results
                    except Exception as err:
                        st.session_state[state_key] = {
                            "error": f"Failed to execute neural inference: {str(err)}",
                            "status": "INFERENCE_ERROR"
                        }

            if state_key in st.session_state:
                res = st.session_state[state_key]
                if "error" in res:
                    st.error(f"⚠️ {res['error']}")
                else:
                    is_ai = res["is_synthetic"]
                    art_val = float(res["artificial_prob"])
                    hum_val = float(res["human_prob"])
                    
                    # Normalization safeguard to ensure float representation between 0.0 and 1.0 for st.progress
                    art_frac = max(0.0, min(1.0, art_val / 100.0))
                    hum_frac = max(0.0, min(1.0, hum_val / 100.0))

                    st.markdown("#### 🔍 Forensic Inference Results")

                    # Primary Metrics Display using full-width card with no text truncation
                    pred_badge_color = "#ef4444" if is_ai else "#10b981"
                    pred_badge_bg = "rgba(239, 68, 68, 0.15)" if is_ai else "rgba(16, 185, 129, 0.15)"
                    pred_border = "rgba(239, 68, 68, 0.35)" if is_ai else "rgba(16, 185, 129, 0.35)"

                    st.markdown(
                        f"""
                        <div class="cyber-card" style="border: 1px solid {pred_border}; background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), {pred_badge_bg}); padding: 18px 22px; margin-bottom: 16px;">
                            <div style="font-size: 0.75rem; letter-spacing: 0.1em; color: #94a3b8; text-transform: uppercase; margin-bottom: 6px;">
                                PREDICTED CLASSIFICATION (UNCALIBRATED)
                            </div>
                            <div style="font-size: 1.6rem; font-weight: 800; color: {pred_badge_color}; line-height: 1.3; word-wrap: break-word; margin-bottom: 8px;">
                                {res['classification']}
                            </div>
                            <div style="font-size: 0.95rem; color: #cbd5e1;">
                                Model Score: <b style="color: #f8fafc; font-size: 1.15rem;">{res['confidence_pct']}%</b>
                                <span style="font-size: 0.78rem; color: #fbbf24; margin-left: 8px;">({res.get('calibration_status', 'Uncalibrated Softmax')})</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # Class Probabilities Breakdown using native Streamlit components
                    st.write(f"**Artificial / Synthetic Score:** `{art_val:.2f}%`")
                    st.progress(art_frac)

                    st.write(f"**Human / Authentic Score:** `{hum_val:.2f}%`")
                    st.progress(hum_frac)

                    st.caption(f"Total probability sum: `{art_val + hum_val:.2f}%` (Direct Softmax Distribution)")

                    # Uncertainty & Forensic Policy Warning
                    if not is_ai:
                        st.warning(
                            "⚠️ **Investigative Uncertainty Warning:** The model predicts authentic, "
                            "but this does not prove the image was camera-captured or free of manipulation. "
                            "Unseen generative models, post-processing filters, or compression artifacts can affect results."
                        )
                    else:
                        st.info(
                            "ℹ️ **Synthetic Artifact Detection:** High artificial score indicates feature representations "
                            "consistent with known diffusion/GAN generative patterns. Cross-validate with metadata & provenance."
                        )

                    # Hardware and Execution Details in structured columns
                    st.markdown("##### ⚙️ System Execution Telemetry")
                    t1, t2, t3, t4 = st.columns(4)
                    with t1:
                        st.caption("DEVICE")
                        st.write(f"**{res['device']}**")
                    with t2:
                        st.caption("ARCHITECTURE")
                        st.write(f"**{res.get('model_architecture', 'SwinTransformer')}**")
                    with t3:
                        st.caption("LATENCY")
                        st.write(f"**{res['inference_time_ms']} ms**")
                    with t4:
                        st.caption("VRAM FOOTPRINT")
                        st.write(f"**{res['vram_allocated_mb']} MB**")

                    st.caption(
                        "🔒 **Forensic Integrity Notice:** Probabilities reflect uncalibrated softmax activations "
                        "of `umm-maybe/AI-image-detector`. Results are intended for advisory forensic analysis."
                    )
            else:
                st.info("Click 'Run AI Forensics Scan' to perform neural forensic classification on this image.")
        else:
            coming_soon_card(
                module_name="Live Neural Forensic Pipeline",
                planned_pipeline=[
                    "Pretrained Swin Transformer Latent Classifier (umm-maybe/AI-image-detector).",
                    "Hardware acceleration via NVIDIA RTX 2050 Tensor Cores with automatic CPU fallback.",
                    "Uncalibrated raw Softmax prediction metrics.",
                    "Chain-of-Custody SHA-256 seal integrity matching.",
                    "Zero-fabrication Structured Forensic Evidence Handling."
                ],
                scheduled_phase="Phase 2 - Ready to Inspect"
            )

elif current_page == "Video Analysis":
    page_header(
        title="Video Deepfake & Frame Screening Forensics",
        subtitle="Frame-level neural synthetic media screening across temporal intervals on GPU tensor cores.",
        badge="NEURAL VIDEO SCREENING ACTIVE"
    )

    v1, v2 = st.columns([1, 1.2])
    with v1:
        vid_file = st.file_uploader("Upload Video File (MP4, MOV, AVI)", type=["mp4", "mov", "avi"], key="vid_inspect")
        if vid_file:
            vid_bytes = vid_file.getvalue()
            st.video(vid_bytes)
            meta = extract_forensic_metadata(vid_file)
            st.markdown(
                f"""
                <div class="cyber-card">
                    <div style="font-weight: 700; color: #22d3ee; margin-bottom: 6px;">STREAM ATTRIBUTES</div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">Container / Filename: <b>{vid_file.name}</b></div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">Stream Size: <b>{meta['File Size']}</b></div>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">SHA-256 Hash:</div>
                    <code style="word-break: break-all; font-size: 0.75rem; color: #38bdf8;">{meta['SHA-256 Hash']}</code>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("Upload a video clip (max 60s, 100MB) above to inspect stream container headers and execute frame-level forensics.")

    with v2:
        if vid_file:
            st.markdown("### 🔬 Live Video Forensics Screening")
            num_sample_frames = st.slider("Sampling Frame Density", min_value=4, max_value=24, value=12, step=2, help="Number of uniformly distributed frames to extract and screen across the video timeline.")
            run_vid_btn = st.button("🚀 Run Video Forensics Scan", type="primary", use_container_width=True)

            video_state_key = f"vid_analysis_{meta['SHA-256 Hash']}_{num_sample_frames}"
            if run_vid_btn:
                prog_bar = st.progress(0.0)
                status_text = st.empty()
                status_text.info("Initializing video stream and extracting timestamped frames...")

                try:
                    pipeline = VideoForensicPipeline.get_instance()
                    status_text.info("Running neural Swin Transformer inference on sampled frames on RTX 2050...")
                    prog_bar.progress(0.5)

                    scan_res = pipeline.inspect_and_sample_video(
                        video_bytes=vid_bytes,
                        filename=vid_file.name,
                        num_frames=num_sample_frames
                    )
                    st.session_state[video_state_key] = scan_res
                    prog_bar.progress(1.0)
                    status_text.empty()
                except Exception as ex:
                    st.session_state[video_state_key] = {
                        "error": f"Video analysis execution failed: {str(ex)}",
                        "status": "ERROR_EXCEPTION"
                    }
                    prog_bar.empty()
                    status_text.empty()

            if video_state_key in st.session_state:
                v_res = st.session_state[video_state_key]
                if "error" in v_res:
                    st.error(f"⚠️ {v_res['error']}")
                else:
                    v_meta = v_res.get("video_metadata", {})
                    v_summary = v_res.get("summary", {})
                    f_results = v_res.get("frame_results", [])
                    total_f = v_summary.get("total_analyzed_frames", 0)
                    syn_f = v_summary.get("synthetic_flagged_count", 0)
                    auth_f = v_summary.get("authentic_flagged_count", 0)
                    mean_score = v_summary.get("mean_synthetic_score", 0.0)
                    max_score = v_summary.get("highest_synthetic_score", 0.0)
                    peak_ts = v_summary.get("peak_timestamps", [])

                    # Summary Card
                    syn_alert = syn_f > 0
                    card_border = "rgba(239, 68, 68, 0.4)" if syn_alert else "rgba(16, 185, 129, 0.4)"
                    card_bg = "rgba(239, 68, 68, 0.12)" if syn_alert else "rgba(16, 185, 129, 0.12)"
                    summary_title = f"{syn_f} / {total_f} Frames Flagged Synthetic" if syn_alert else "All Sampled Frames Predict Authentic"

                    st.markdown(
                        f"""
                        <div class="cyber-card" style="border: 1px solid {card_border}; background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), {card_bg}); padding: 18px 22px; margin-bottom: 16px;">
                            <div style="font-size: 0.75rem; letter-spacing: 0.1em; color: #94a3b8; text-transform: uppercase; margin-bottom: 4px;">
                                FRAME SCREENING SUMMARY (UNCALIBRATED)
                            </div>
                            <div style="font-size: 1.5rem; font-weight: 800; color: {'#f87171' if syn_alert else '#34d399'}; margin-bottom: 8px;">
                                {summary_title}
                            </div>
                            <div style="font-size: 0.88rem; color: #cbd5e1; line-height: 1.5;">
                                Mean Synthetic Score: <b style="color: #f8fafc;">{mean_score}%</b> | Peak Synthetic Score: <b style="color: #f87171;">{max_score}%</b> at <code style="color: #38bdf8;">{', '.join(peak_ts) if peak_ts else 'N/A'}</code>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # KPI Metrics Row
                    sk1, sk2, sk3, sk4 = st.columns(4)
                    with sk1:
                        st.metric("Analyzed Frames", f"{total_f} frames")
                    with sk2:
                        st.metric("Flagged Synthetic", f"{syn_f} frames", delta="Flagged" if syn_f > 0 else "Clean", delta_color="inverse" if syn_f > 0 else "normal")
                    with sk3:
                        st.metric("Stream Duration", f"{v_meta.get('duration_seconds', 0.0)}s")
                    with sk4:
                        st.metric("Stream Resolution", f"{v_meta.get('resolution', 'N/A')}")

                    # Important Limitation & Uncertainty Warning
                    st.warning(
                        "⚠️ **Forensic Scope & Limitation Notice:** This module performs **frame-level synthetic artifact screening** using the Swin Transformer model. "
                        "It is **not** a dedicated face-swap, lip-sync, or temporal biometric detector. "
                        "The mean synthetic score represents an uncalibrated average of individual frame predictions and must not be interpreted as a calibrated whole-video fake probability."
                    )

                    # Interactive Timeline Chart
                    st.markdown("#### 📈 Frame-by-Frame Suspiciousness Timeline")
                    df_timeline = pd.DataFrame([
                        {
                            "Timestamp (s)": f["reported_timestamp_sec"],
                            "Formatted Time": f["formatted_timestamp"],
                            "Synthetic Score (%)": f["artificial_prob"],
                            "Authentic Score (%)": f["human_prob"],
                            "Classification": f["classification"],
                        }
                        for f in f_results
                    ])

                    fig = px.line(
                        df_timeline,
                        x="Timestamp (s)",
                        y="Synthetic Score (%)",
                        markers=True,
                        text="Formatted Time",
                        hover_data=["Classification", "Authentic Score (%)"],
                        labels={"Synthetic Score (%)": "Artificial Score (%)", "Timestamp (s)": "Timeline (seconds)"},
                    )
                    fig.add_hline(y=50, line_dash="dash", line_color="#ef4444", annotation_text="50% Synthetic Threshold", annotation_position="bottom right")
                    fig.update_traces(
                        line=dict(color="#38bdf8", width=3),
                        marker=dict(size=8, color=["#ef4444" if row["Synthetic Score (%)"] >= 50 else "#10b981" for _, row in df_timeline.iterrows()])
                    )
                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(15, 23, 42, 0.6)",
                        plot_bgcolor="rgba(15, 23, 42, 0.8)",
                        margin=dict(l=20, r=20, t=30, b=20),
                        height=280,
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Sampled Frame Thumbnails Grid
                    st.markdown("#### 🖼️ Extracted Frame Evidence Strip")
                    cols_per_row = 4
                    for row_idx in range(0, len(f_results), cols_per_row):
                        row_frames = f_results[row_idx:row_idx + cols_per_row]
                        cols = st.columns(len(row_frames))
                        for col, f_item in zip(cols, row_frames):
                            with col:
                                st.image(f_item["thumbnail"], caption=f"⏱️ {f_item['formatted_timestamp']}", use_container_width=True)
                                f_is_syn = f_item["is_synthetic"]
                                f_badge_color = "#f87171" if f_is_syn else "#34d399"
                                st.markdown(
                                    f"""
                                    <div style="font-size: 0.75rem; text-align: center; margin-top: -6px;">
                                        <b style="color: {f_badge_color};">{f_item['classification']}</b><br>
                                        <span style="color: #94a3b8;">Synthetic: {f_item['artificial_prob']}%</span>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                    # Telemetry footer
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.caption(
                        f"⚙️ **Execution Telemetry:** Device: **{v_summary.get('hardware_device', 'GPU')}** | "
                        f"Latency: **{v_summary.get('total_processing_latency_ms', 0)} ms** | "
                        f"FPS: **{v_meta.get('fps', 'N/A')}** | "
                        f"Total Stream Frames: **{v_meta.get('total_stream_frames', 'N/A')}** | "
                        f"Cryptographic Hash: `{v_res.get('sha256', '')}`"
                    )
        else:
            coming_soon_card(
                module_name="Live Video Forensics Screening",
                planned_pipeline=[
                    "Uniform timestamp frame extraction via OpenCV (MP4, MOV, AVI support).",
                    "Hardware accelerated frame inference using existing Swin Transformer on RTX 2050.",
                    "Frame-by-frame suspiciousness timeline visualization.",
                    "Evidence strip with extracted frame thumbnails and per-frame probability scores.",
                    "Structured forensic evidence handling and zero-fabrication reporting."
                ],
                scheduled_phase="Phase 3 - Ready to Inspect"
            )

elif current_page == "Audio Analysis":
    page_header(
        title="Synthetic Voice & Speech Forensics",
        subtitle="Detect neural text-to-speech (TTS), voice clones, and acoustic spoofing using Wav2Vec 2.0 sequence classifiers.",
        badge="NEURAL VOICE SCREENING ACTIVE"
    )

    a1, a2 = st.columns([1, 1.2])
    with a1:
        aud_file = st.file_uploader("Upload Audio Recording (WAV, MP3, FLAC)", type=["wav", "mp3", "flac"], key="aud_inspect")
        if aud_file:
            raw_audio_bytes = aud_file.getvalue()
            st.audio(raw_audio_bytes)
            meta = extract_forensic_metadata(aud_file)
            st.markdown(
                f"""
                <div class="cyber-card">
                    <div style="font-weight: 700; color: #22d3ee; margin-bottom: 6px;">AUDIO CONTAINER METRICS</div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">Container / Filename: <b>{aud_file.name}</b></div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">File Size: <b>{meta['File Size']}</b></div>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">SHA-256 Hash:</div>
                    <code style="word-break: break-all; font-size: 0.75rem; color: #38bdf8;">{meta['SHA-256 Hash']}</code>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("Upload an audio sample (.wav, .mp3, .flac) above to preview acoustic waveform and execute neural voice forensics.")

    with a2:
        if aud_file:
            st.markdown("### 🔬 Live Acoustic Voice Forensics")
            run_aud_btn = st.button("🚀 Run Voice Forensics Scan", type="primary", use_container_width=True)

            aud_state_key = f"aud_analysis_{meta['SHA-256 Hash']}"
            if run_aud_btn:
                with st.spinner("Decoding audio, computing spectrogram & running Wav2Vec2 inference on GPU..."):
                    try:
                        aud_detector = AudioForensicDetector.get_instance()
                        a_res = aud_detector.process_and_analyze_audio(
                            raw_bytes=raw_audio_bytes,
                            filename=aud_file.name
                        )
                        st.session_state[aud_state_key] = a_res
                    except Exception as err:
                        st.session_state[aud_state_key] = {
                            "error": f"Audio analysis execution failed: {str(err)}",
                            "status": "ERROR_EXCEPTION"
                        }

            if aud_state_key in st.session_state:
                res_aud = st.session_state[aud_state_key]
                if "error" in res_aud:
                    st.error(f"⚠️ {res_aud['error']}")
                else:
                    is_syn = res_aud["is_synthetic"]
                    syn_score = float(res_aud["synthetic_score"])
                    auth_score = float(res_aud["authentic_score"])

                    syn_frac = max(0.0, min(1.0, syn_score / 100.0))
                    auth_frac = max(0.0, min(1.0, auth_score / 100.0))

                    badge_color = "#ef4444" if is_syn else "#10b981"
                    badge_bg = "rgba(239, 68, 68, 0.15)" if is_syn else "rgba(16, 185, 129, 0.15)"
                    border_color = "rgba(239, 68, 68, 0.35)" if is_syn else "rgba(16, 185, 129, 0.35)"

                    # Forensic Classification Header
                    st.markdown(
                        f"""
                        <div class="cyber-card" style="border: 1px solid {border_color}; background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), {badge_bg}); padding: 18px 22px; margin-bottom: 16px;">
                            <div style="font-size: 0.75rem; letter-spacing: 0.1em; color: #94a3b8; text-transform: uppercase; margin-bottom: 6px;">
                                ACOUSTIC CLASSIFICATION (UNCALIBRATED)
                            </div>
                            <div style="font-size: 1.55rem; font-weight: 800; color: {badge_color}; line-height: 1.3; margin-bottom: 8px;">
                                {res_aud['classification']}
                            </div>
                            <div style="font-size: 0.92rem; color: #cbd5e1;">
                                Model Score: <b style="color: #f8fafc; font-size: 1.15rem;">{res_aud['confidence_pct']}%</b>
                                <span style="font-size: 0.78rem; color: #fbbf24; margin-left: 8px;">({res_aud.get('calibration_status', 'Uncalibrated Softmax')})</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # Empirical Benchmark Disclosure Callout
                    st.info(
                        "🔍 **Empirical Benchmark Disclosure:** Independent forensic evaluation indicates that while `umm-maybe/AI-image-detector` "
                        "and `MelodyMachine/Deepfake-audio-detection-V2` reliably detect legacy generative artifacts and acoustic formant synthesis, "
                        "the audio classifier exhibits **false negatives (0.0% synthetic score) on modern flow-matching neural voice clones (ElevenLabs)**. "
                        "Evaluated accuracy is vocoder-dependent. Detection results must be interpreted as advisory screening, not absolute proof."
                    )

                    # Score Progress Bars
                    st.write(f"**Synthetic / Cloned Voice Score:** `{syn_score:.2f}%`")
                    st.progress(syn_frac)

                    st.write(f"**Authentic Human Speech Score:** `{auth_score:.2f}%`")
                    st.progress(auth_frac)

                    st.caption(f"Total probability sum: `{syn_score + auth_score:.2f}%` (Direct Softmax Distribution)")

                    # Uncertainty & Limitations Warning
                    if not is_syn:
                        st.warning(
                            "⚠️ **Investigative Uncertainty Warning:** The model predicts authentic human speech, "
                            "but this does **not** prove the recording is genuine or unedited. Novel neural vocoders, "
                            "low bitrate telephony codecs, or background noise can affect classifier certainty."
                        )
                    else:
                        st.info(
                            "ℹ️ **Synthetic Speech Signature:** High synthetic probability indicates latent acoustic "
                            "representations matching known neural TTS / vocoder patterns. This does **not** identify "
                            "the speaker or pinpoint a specific person."
                        )

                    # Acoustic Signal Visualizations (Waveform & Spectrogram)
                    st.markdown("#### 📊 Acoustic Domain Analysis")
                    tab_wave, tab_spec = st.tabs(["🌊 Amplitude Waveform", "🌈 Audio Spectrogram (STFT)"])

                    with tab_wave:
                        wave_data = res_aud.get("waveform", {})
                        if wave_data and "time_axis" in wave_data:
                            fig_w = px.line(
                                x=wave_data["time_axis"],
                                y=wave_data["amplitude"],
                                labels={"x": "Time (seconds)", "y": "Normalized Amplitude"},
                            )
                            fig_w.update_traces(line=dict(color="#38bdf8", width=1.5))
                            fig_w.update_layout(
                                template="plotly_dark",
                                paper_bgcolor="rgba(15, 23, 42, 0.6)",
                                plot_bgcolor="rgba(15, 23, 42, 0.8)",
                                margin=dict(l=20, r=20, t=20, b=20),
                                height=220,
                            )
                            st.plotly_chart(fig_w, use_container_width=True)

                    with tab_spec:
                        spec_data = res_aud.get("spectrogram", {})
                        if spec_data and "power_db" in spec_data:
                            fig_s = go.Figure(
                                data=go.Heatmap(
                                    z=spec_data["power_db"],
                                    x=spec_data["times"],
                                    y=spec_data["frequencies"],
                                    colorscale="Magma",
                                    colorbar=dict(title="dB")
                                )
                            )
                            fig_s.update_layout(
                                template="plotly_dark",
                                paper_bgcolor="rgba(15, 23, 42, 0.6)",
                                plot_bgcolor="rgba(15, 23, 42, 0.8)",
                                xaxis_title="Time (seconds)",
                                yaxis_title="Frequency (Hz)",
                                margin=dict(l=20, r=20, t=20, b=20),
                                height=240,
                            )
                            st.plotly_chart(fig_s, use_container_width=True)

                    # Hardware & Telemetry Grid
                    st.markdown("##### ⚙️ System Execution Telemetry")
                    at1, at2, at3, at4 = st.columns(4)
                    meta_aud = res_aud.get("audio_metadata", {})
                    with at1:
                        st.caption("DEVICE")
                        st.write(f"**{res_aud['device']}**")
                    with at2:
                        st.caption("ARCHITECTURE")
                        st.write(f"**{res_aud.get('model_architecture', 'Wav2Vec2')}**")
                    with at3:
                        st.caption("LATENCY")
                        st.write(f"**{res_aud['inference_time_ms']} ms**")
                    with at4:
                        st.caption("VRAM FOOTPRINT")
                        st.write(f"**{res_aud['vram_allocated_mb']} MB**")

                    st.caption(
                        f"🔒 **Acoustic Container Telemetry:** Duration: **{meta_aud.get('duration_seconds', 0)}s** | "
                        f"Original Sample Rate: **{meta_aud.get('original_sample_rate_hz', 0)} Hz** | "
                        f"Target Resampled Rate: **{meta_aud.get('target_sample_rate_hz', 16000)} Hz** | "
                        f"Channels: **{meta_aud.get('channel_type', 'Mono')}** | "
                        f"RMS Energy: `{meta_aud.get('rms_energy', 0)}`"
                    )
        else:
            coming_soon_card(
                module_name="Live Voice Forensics Screening",
                planned_pipeline=[
                    "Pretrained Wav2Vec 2.0 sequence classifier (MelodyMachine/Deepfake-audio-detection-V2).",
                    "Acoustic downmixing & non-destructive 16 kHz polyphase resampling.",
                    "Time-frequency STFT Spectrogram & Amplitude Waveform generation via Scipy.",
                    "Dual uncalibrated softmax probability reporting (Synthetic vs. Authentic).",
                    "Zero-fabrication reporting adhering to Structured Forensic Evidence Handling without speaker-identity claims."
                ],
                scheduled_phase="Phase 4 - Ready to Inspect"
            )

elif current_page == "Document Analysis":
    page_header(
        title="Document Authenticity & Forgery Inspection",
        subtitle="Forensic validation of digital documents, forged invoices, contracts, and PDF structure alterations.",
        badge="PIPELINE STAGED"
    )

    d1, d2 = st.columns([1, 1.2])
    with d1:
        doc_file = st.file_uploader("Upload Document", type=["pdf", "docx", "txt"], key="doc_inspect")
        if doc_file:
            meta = extract_forensic_metadata(doc_file)
            st.markdown(
                f"""
                <div class="cyber-card">
                    <div style="font-weight: 700; color: #22d3ee; margin-bottom: 6px;">DOCUMENT INTEGRITY</div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">Name: <b>{meta['Filename']}</b></div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">Size: <b>{meta['File Size']}</b></div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">SHA-256: <code style="word-break: break-all;">{meta['SHA-256 Hash']}</code></div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("Upload a document to extract structural metadata and check revision history.")

    with d2:
        coming_soon_card(
            module_name="Document Forensics & Tamper Detection",
            planned_pipeline=[
                "Incremental PDF Update Analysis: Detect hidden or modified text blocks post-signing.",
                "Font & Glyph Homogeneity: Identify spliced character sets and altered numerical figures.",
                "Copy-Move & Forgery Detection: SIFT/ORB keypoint matching for duplicated signatures or seals.",
                "OCR Text Semantic Discrepancy: LLM-based hallucination and logic contradiction auditing."
            ],
            scheduled_phase="Phase 2"
        )

elif current_page == "Cross-Modal Verification":
    page_header(
        title="Cross-Modal Cohesion & Multimodal Verification",
        subtitle="Synchronized analysis across audio, video, text, and contextual metadata streams.",
        badge="PIPELINE STAGED"
    )

    coming_soon_card(
        module_name="Cross-Modal Multimodal Corroboration",
        planned_pipeline=[
            "Phoneme-to-Viseme Lip Synchronization: Cross-referencing audio speech with mouth movement dynamics.",
            "Visual-Text Alignment: Verifying whether document text matches referenced imagery without contextual contradiction.",
            "Environmental Lighting vs. Audio Reverb: Testing if acoustic room size matches visual spatial dimensions.",
            "Cross-Modal Confidence Fusion: Unified Bayesian authenticity scoring across all evidence channels."
        ],
        scheduled_phase="Phase 2"
    )

elif current_page == "Provenance Verification":
    page_header(
        title="C2PA Provenance & Cryptographic Content Credentials",
        subtitle="Inspect tamper-evident C2PA manifests, digital camera signatures, and public ledger provenance.",
        badge="PIPELINE STAGED"
    )

    st.markdown(
        """
        <div class="cyber-card">
            <h4 style="color: #22d3ee; margin-top: 0;">What is C2PA (Coalition for Content Provenance and Authenticity)?</h4>
            <p style="color: #94a3b8; font-size: 0.88rem; line-height: 1.6;">
                C2PA is an open technical standard allowing content creators and publishers to embed verifiable, tamper-evident metadata
                directly into digital assets. When an image or video is edited or generated by AI (such as Adobe Firefly, OpenAI DALL-E 3, or Google Imagen),
                a cryptographically signed manifest is attached.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    coming_soon_card(
        module_name="C2PA Manifest Parser & Public Key Ledger",
        planned_pipeline=[
            "JUMBF (JPEG Universal Metadata Box Format) extraction from container headers.",
            "X.509 Certificate Chain validation against trusted Root Certificate Authorities.",
            "Assertion Integrity Check: Verifying cryptographic hashes of original edits, tools, and parent assets.",
            "Tamper Indicator Flag: Warning when manifest hashes diverge from current file contents."
        ],
        scheduled_phase="Phase 2"
    )

elif current_page == "Forensic Reports":
    page_header(
        title="Forensic Audit Reports & Chain of Custody",
        subtitle="Export comprehensive, cryptographically signed PDF forensic reports suitable for court and security operations.",
        badge="REPORT ENGINE READY"
    )

    st.markdown(
        """
        <div class="forensic-notice notice-phase">
            <b>Audit Documentation Standard:</b> All generated reports include cryptographic hashes, ingest timestamps,
            examiner identity, hardware environment specifications, and module verdicts.
        </div>
        """,
        unsafe_allow_html=True
    )

    col_rep_left, col_rep_right = st.columns([1, 1.2])

    with col_rep_left:
        st.markdown("#### Case Information")
        case_id = st.text_input("Forensic Case ID", value="DFX-2026-001")
        examiner = st.text_input("Lead Examiner / Analyst", value="Forensics Officer #42")
        classification = st.selectbox("Classification Level", ["Confidential / Restricted", "Law Enforcement Only", "Public Verification", "Internal Security Audit"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Generate Phase 1 Audit Summary (JSON / CSV)", type="primary"):
            all_evidence = []
            for category, items in st.session_state.evidence_registry.items():
                for it in items:
                    it_copy = dict(it)
                    it_copy["Case ID"] = case_id
                    it_copy["Examiner"] = examiner
                    it_copy["Classification"] = classification
                    all_evidence.append(it_copy)

            if all_evidence:
                df = pd.DataFrame(all_evidence)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Evidence Custody Ledger (CSV)",
                    data=csv,
                    file_name=f"{case_id}_custody_ledger.csv",
                    mime="text/csv",
                )
                st.success("Audit ledger created successfully.")
            else:
                st.warning("No files ingested yet. Ingest media in the Upload Center first to generate an audit report.")

    with col_rep_right:
        coming_soon_card(
            module_name="Automated PDF Forensic Report Generation",
            planned_pipeline=[
                "High-resolution PDF generation via ReportLab / WeasyPrint.",
                "Embedded Grad-CAM visual heatmaps and spectral spectrograms.",
                "Cryptographic HMAC signature of report contents to prevent post-export tampering.",
                "Chain-of-custody tracking log adhering to NIST / ISO 27037 standards."
            ],
            scheduled_phase="Phase 2"
        )
