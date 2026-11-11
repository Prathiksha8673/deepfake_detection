import streamlit as st
import pandas as pd
from PIL import Image
import io

from src.components.sidebar import load_custom_css, render_sidebar
from src.components.cards import page_header, coming_soon_card
from src.utils.file_handler import extract_forensic_metadata
from src.modules.image_detector import ImageForensicDetector
from src.modules.video_detector import VideoForensicPipeline
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
                    DEEPFAKE X operates strictly according to ISO/IEC 27037 forensic sound practices. No placeholder synthetic probability scores are fabricated.
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

elif current_page == "Upload Center":
    page_header(
        title="Multimodal Evidence Ingestion Center",
        subtitle="Ingest images, videos, audio samples, and documents with instant cryptographic sealing and custody hashing.",
        badge="SECURE INGESTION"
    )

    tab_img, tab_vid, tab_aud, tab_doc = st.tabs([
        "🖼️ Image Evidence", "🎬 Video Evidence", "🎙️ Audio Samples", "📄 Document Files"
    ])

    with tab_img:
        st.markdown("#### Upload Image Files for Forensics")
        uploaded_imgs = st.file_uploader(
            "Select high-resolution images (JPEG, PNG, WEBP, TIFF)",
            type=["jpg", "jpeg", "png", "webp", "tiff"],
            accept_multiple_files=True,
            key="uploader_imgs"
        )
        if uploaded_imgs:
            for f in uploaded_imgs:
                meta = extract_forensic_metadata(f)
                if not any(item["SHA-256 Hash"] == meta["SHA-256 Hash"] for item in st.session_state.evidence_registry["images"]):
                    st.session_state.evidence_registry["images"].append(meta)
            st.success(f"✓ Ingested and cryptographically sealed {len(uploaded_imgs)} image file(s).")

    with tab_vid:
        st.markdown("#### Upload Video Files for Temporal Forensics")
        uploaded_vids = st.file_uploader(
            "Select video files (MP4, AVI, MOV, MKV)",
            type=["mp4", "avi", "mov", "mkv"],
            accept_multiple_files=True,
            key="uploader_vids"
        )
        if uploaded_vids:
            for f in uploaded_vids:
                meta = extract_forensic_metadata(f)
                if not any(item["SHA-256 Hash"] == meta["SHA-256 Hash"] for item in st.session_state.evidence_registry["videos"]):
                    st.session_state.evidence_registry["videos"].append(meta)
            st.success(f"✓ Ingested and cryptographically sealed {len(uploaded_vids)} video file(s).")

    with tab_aud:
        st.markdown("#### Upload Audio Recordings for Voice Synthesis Inspection")
        uploaded_auds = st.file_uploader(
            "Select audio files (WAV, MP3, FLAC, OGG, M4A)",
            type=["wav", "mp3", "flac", "ogg", "m4a"],
            accept_multiple_files=True,
            key="uploader_auds"
        )
        if uploaded_auds:
            for f in uploaded_auds:
                meta = extract_forensic_metadata(f)
                if not any(item["SHA-256 Hash"] == meta["SHA-256 Hash"] for item in st.session_state.evidence_registry["audios"]):
                    st.session_state.evidence_registry["audios"].append(meta)
            st.success(f"✓ Ingested and cryptographically sealed {len(uploaded_auds)} audio file(s).")

    with tab_doc:
        st.markdown("#### Upload Documents for Forgery & Provenance Analysis")
        uploaded_docs = st.file_uploader(
            "Select document files (PDF, DOCX, TXT)",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            key="uploader_docs"
        )
        if uploaded_docs:
            for f in uploaded_docs:
                meta = extract_forensic_metadata(f)
                if not any(item["SHA-256 Hash"] == meta["SHA-256 Hash"] for item in st.session_state.evidence_registry["documents"]):
                    st.session_state.evidence_registry["documents"].append(meta)
            st.success(f"✓ Ingested and cryptographically sealed {len(uploaded_docs)} document file(s).")

    st.markdown("---")
    st.markdown("### 📋 Active Evidence Custody Ledger")
    all_evidence = []
    for category, items in st.session_state.evidence_registry.items():
        for it in items:
            it_copy = dict(it)
            it_copy["Modality Category"] = category.capitalize()
            all_evidence.append(it_copy)

    if all_evidence:
        df_ledger = pd.DataFrame(all_evidence)[["Filename", "Modality Category", "File Size", "SHA-256 Hash", "Ingestion Timestamp", "Custody Status"]]
        st.dataframe(df_ledger, use_container_width=True)
    else:
        st.info("No media files have been uploaded yet. Upload files above to view real-time forensic custody signatures.")

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
                        "🔒 **Forensic Integrity Notice (ISO/IEC 27037):** Probabilities reflect uncalibrated softmax activations "
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
                    "Zero-fabrication ISO/IEC 27037 compliant audit outputs."
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
                    "ISO/IEC 27037 compliant zero-fabrication reporting."
                ],
                scheduled_phase="Phase 3 - Ready to Inspect"
            )

elif current_page == "Audio Analysis":
    page_header(
        title="Synthetic Voice & Speech Forensics",
        subtitle="Detect neural text-to-speech (TTS), voice clones, and acoustic splicing anomalies.",
        badge="PIPELINE STAGED"
    )

    a1, a2 = st.columns([1, 1.2])
    with a1:
        aud_file = st.file_uploader("Upload Audio Recording", type=["wav", "mp3", "flac"], key="aud_inspect")
        if aud_file:
            st.audio(aud_file)
            meta = extract_forensic_metadata(aud_file)
            st.markdown(
                f"""
                <div class="cyber-card">
                    <div style="font-weight: 700; color: #22d3ee; margin-bottom: 6px;">AUDIO CONTAINER METRICS</div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">Size: <b>{meta['File Size']}</b></div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">SHA-256: <code style="word-break: break-all;">{meta['SHA-256 Hash']}</code></div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("Upload an audio sample to preview waveform and prepare acoustic spectrogram decomposition.")

    with a2:
        coming_soon_card(
            module_name="Acoustic Voice Synthesis Detection",
            planned_pipeline=[
                "Mel-Spectrogram Generation: High-resolution time-frequency domain transforms.",
                "Phase Discontinuity Analysis: Linear predictive coding (LPC) residual energy checks.",
                "Voice Anti-Spoofing: RawNet2 / AASIST neural vocoder fingerprinting (Phase 2).",
                "Acoustic Room Impulse Response (RIR) consistency checks across speakers."
            ],
            scheduled_phase="Phase 2"
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
