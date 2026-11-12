import streamlit as st

def page_header(title: str, subtitle: str, badge: str = "PHASE 1 READY"):
    """Standardized cybersecurity header across all views."""
    badge_class = "status-ready" if "READY" in badge else "status-coming-soon"
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                <h1 style="margin: 0; font-size: 2.1rem;">{title}</h1>
                <span class="status-pill {badge_class}">{badge}</span>
            </div>
            <p style="color: #94a3b8; font-size: 0.95rem; margin-top: 6px; margin-bottom: 0;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def coming_soon_card(module_name: str, planned_pipeline: list, scheduled_phase: str = "Phase 2"):
    """Placeholder card indicating upcoming AI model pipelines."""
    pipeline_bullets = "".join([f"<li style='margin-bottom: 6px; color: #cbd5e1;'>{item}</li>" for item in planned_pipeline])
    st.markdown(
        f"""
        <div class="cyber-card-purple" style="margin-top: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h3 style="margin: 0; color: #c084fc; font-size: 1.15rem;">🔬 {module_name} Engine Pipeline</h3>
                <span class="status-pill status-coming-soon">Scheduled: {scheduled_phase}</span>
            </div>
            <p style="color: #94a3b8; font-size: 0.88rem; margin-bottom: 14px;">
                AI models and inference weights will be integrated in subsequent phases. No fabricated synthetic predictions are displayed.
            </p>
            <div style="font-size: 0.85rem; font-weight: 600; color: #a855f7; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;">
                Planned Inspection Methodology:
            </div>
            <ul style="padding-left: 20px; font-size: 0.88rem; margin-bottom: 0;">
                {pipeline_bullets}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
