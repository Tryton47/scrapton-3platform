"""
Visual header and sidebar layout components for Streamlit.
"""
import streamlit as st
from .session_helper import get_session_status

def render_sidebar():
    """Renders user controls, platform selection, and session indicator in sidebar."""
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/bot.png", width=70)
        st.title("Scrapton Controls")
        st.markdown("---")

        platform_choice = st.selectbox(
            "🎯 Pilih Platform",
            options=["TikTok", "Instagram", "X (Twitter)"],
            index=0
        )
        platform_map = {
            "TikTok": "tiktok",
            "Instagram": "instagram",
            "X (Twitter)": "twitter"
        }
        selected_platform = platform_map[platform_choice]

        username_input = st.text_input(
            "👤 Target Username",
            placeholder="misal: tiktok, cristiano, elonmusk",
            help="Masukkan username tanpa tanda @"
        ).strip().lstrip("@")

        limit_input = st.slider(
            "📊 Jumlah Konten / Limit",
            min_value=3,
            max_value=50,
            value=10,
            step=1
        )

        st.markdown("---")
        st.subheader("🔑 Status Sesi Akun")

        session_status = get_session_status()
        col_ig, col_tt, col_tw = st.columns(3)
        col_tt.metric("TikTok", "Aktif" if session_status["tiktok"] else "Kosong")
        col_ig.metric("IG", "Aktif" if session_status["instagram"] else "Kosong")
        col_tw.metric("X", "Aktif" if session_status["twitter"] else "Kosong")

        st.caption("Tip: Login sesi via CLI interaktif jika akun terkena login wall.")

    return selected_platform, username_input, limit_input

def render_custom_styles():
    """Inject modern CSS styling into Streamlit view."""
    st.markdown("""
    <style>
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1E88E5;
            margin-bottom: 0px;
        }
        .sub-title {
            font-size: 1.0rem;
            color: #757575;
            margin-bottom: 25px;
        }
        .metric-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            border-left: 5px solid #1E88E5;
        }
    </style>
    """, unsafe_allow_html=True)
