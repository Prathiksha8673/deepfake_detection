import os
import streamlit as st

def load_custom_css():
    """Load high-tech cybersecurity CSS theme."""
    css_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "css", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_sidebar():
    """Render unified navigation sidebar."""
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 10px 0 16px 0;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="cyber-pulse"></span>
                    <span style="font-weight: 800; font-size: 1.35rem; color: #22d3ee; letter-spacing: 0.08em;">DEEPFAKE X</span>
                </div>
                <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 4px;">
                    Forensics & Authenticity
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("<p style='font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.12em; color: #64748b; font-weight: 700;'>FORENSIC MODULES</p>", unsafe_allow_html=True)
        
        menu_items = [
            ("📡 Overview Dashboard", "Overview"),
            ("🔍 Multimodal Investigation", "Multimodal Investigation"),
            ("⚡ Evidence Correlation", "Cross-Modal Verification"),
            ("📁 Case Management", "Case Management"),
            ("🖼️ Image Forensics", "Image Analysis"),
            ("🎬 Video Forensics", "Video Analysis"),
            ("🎙️ Audio Forensics", "Audio Analysis"),
            ("📄 Document Forensics", "Document Analysis"),
            ("📑 Forensic Reports", "Forensic Reports"),
            ("⚙️ System Settings", "Settings"),
        ]

        if "current_page" not in st.session_state:
            st.session_state.current_page = "Overview"

        for label, page_key in menu_items:
            is_active = (st.session_state.current_page == page_key)
            button_style = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{page_key}", use_container_width=True, type=button_style):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("---")
        st.markdown(
            """
            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 8px; padding: 12px; margin-top: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.75rem; color: #94a3b8;">SYSTEM ENGINE</span>
                    <span class="status-pill status-ready">Phase 1</span>
                </div>
                <div style="font-size: 0.72rem; color: #64748b; margin-top: 6px; font-family: monospace;">
                    Python 3.11.18 | Streamlit 1.67<br>
                    Hardware: RTX 2050 (Ready)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return st.session_state.current_page
