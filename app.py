import streamlit as st
import pandas as pd
from PIL import Image
import io

from src.components.sidebar import load_custom_css, render_sidebar
from src.components.cards import page_header, coming_soon_card
from src.utils.file_handler import extract_forensic_metadata

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
        subtitle="Detect synthetic generation traces from Stable Diffusion, Midjourney, DALL-E, and GAN architectures.",
        badge="PIPELINE STAGED"
    )

    c1, c2 = st.columns([1, 1.2])
    with c1:
        img_file = st.file_uploader("Upload Image to Inspect", type=["jpg", "jpeg", "png", "webp"], key="img_inspect")
        if img_file:
            st.image(img_file, caption=f"Uploaded: {img_file.name}", use_container_width=True)
            meta = extract_forensic_metadata(img_file)
            st.markdown(
                f"""
                <div class="cyber-card">
                    <div style="font-weight: 700; color: #22d3ee; margin-bottom: 6px;">EVIDENCE METRICS</div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">Resolution / Size: <b>{meta['File Size']}</b></div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">SHA-256: <code style="word-break: break-all;">{meta['SHA-256 Hash']}</code></div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("Upload an image file above to inspect metadata and prepare forensic feature extraction.")

    with c2:
        coming_soon_card(
            module_name="Image Forensics & Artifact Detection",
            planned_pipeline=[
                "Spatial Domain Analysis: PRNU (Photo-Response Non-Uniformity) sensor noise fingerprinting.",
                "Frequency Domain Analysis: 2D Fast Fourier Transform (FFT) high-frequency grid artifact detection.",
                "Compression Forensics: Error Level Analysis (ELA) for localized resaving and splice detection.",
                "Deep Feature Classification: EfficientNet / ConvNeXt synthetic boundary detection (Phase 2).",
                "Explainable Heatmaps: Grad-CAM synthetic localization layers."
            ],
            scheduled_phase="Phase 2"
        )

elif current_page == "Video Analysis":
    page_header(
        title="Video Deepfake & Face-Swap Forensics",
        subtitle="Analyze temporal continuity, facial boundary warps, gaze consistency, and lip-sync synchronization.",
        badge="PIPELINE STAGED"
    )

    v1, v2 = st.columns([1, 1.2])
    with v1:
        vid_file = st.file_uploader("Upload Video File", type=["mp4", "mov", "avi"], key="vid_inspect")
        if vid_file:
            st.video(vid_file)
            meta = extract_forensic_metadata(vid_file)
            st.markdown(
                f"""
                <div class="cyber-card">
                    <div style="font-weight: 700; color: #22d3ee; margin-bottom: 6px;">STREAM ATTRIBUTES</div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">Size: <b>{meta['File Size']}</b></div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">SHA-256: <code style="word-break: break-all;">{meta['SHA-256 Hash']}</code></div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("Upload a video clip to inspect stream container headers and prepare frame sampling.")

    with v2:
        coming_soon_card(
            module_name="Video Deepfake Analysis",
            planned_pipeline=[
                "Frame Decomposition & Face ROI Tracking: Haar/RetinaFace bounding-box alignment.",
                "Biometric Consistency: Eye blink frequency and biological pulse (remote photoplethysmography / rPPG).",
                "Temporal Coherence: Inter-frame optical flow disparity to expose face-swap edge seams.",
                "Neural Spatiotemporal Models: 3D CNN / Video Transformer inference (Phase 2)."
            ],
            scheduled_phase="Phase 2"
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
