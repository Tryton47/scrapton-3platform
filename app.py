"""
Scrapton: Apify-Style Actor Console for Social Media Comment Scraping.
Focused developer interface for batch comment extraction from TikTok, Instagram, and X.
"""
import asyncio
import io
import time
from datetime import datetime
import pandas as pd
import streamlit as st

from scrapers.comment_scraper import CommentScraper, detect_platform_from_url
from utils.comment_analyzer import analyze_comment

# ── Page Configuration ───────────────────────────────────────────────
st.set_page_config(
    page_title="Scrapton Actor Console",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS: High-Density Apify / Zinc Developer Tool Styling ────────────
st.markdown("""
<style>
    /* Reset Streamlit chrome */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        padding: 1.25rem 2rem 3rem 2rem;
        max-width: 1200px;
    }
    [data-testid="collapsedControl"] {display: none;}

    /* Typography & Core Palette */
    * {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    code, kbd, samp, pre {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace !important;
    }

    /* Actor Header Banner */
    .actor-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 20px;
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 8px;
        margin-bottom: 18px;
    }
    .actor-title-row {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .actor-icon {
        width: 36px;
        height: 36px;
        background: #27272a;
        border: 1px solid #3f3f46;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }
    .actor-name {
        font-size: 18px;
        font-weight: 700;
        color: #f4f4f5;
        letter-spacing: -0.3px;
        margin: 0;
    }
    .actor-namespace {
        color: #71717a;
        font-weight: 400;
        margin-right: 2px;
    }
    .version-tag {
        font-size: 11px;
        padding: 2px 7px;
        border-radius: 4px;
        background: #27272a;
        color: #a1a1aa;
        border: 1px solid #3f3f46;
        font-family: monospace;
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 4px;
        background: rgba(16, 185, 129, 0.12);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }

    /* Terminal Console Box */
    .terminal-box {
        background: #09090b;
        border: 1px solid #27272a;
        border-radius: 6px;
        padding: 14px 16px;
        font-family: monospace;
        font-size: 12.5px;
        line-height: 1.6;
        color: #d4d4d8;
        max-height: 280px;
        overflow-y: auto;
    }
    .terminal-time {
        color: #71717a;
    }
    .terminal-tag {
        color: #10b981;
        font-weight: 600;
    }
    .terminal-url {
        color: #38bdf8;
    }

    /* High Density Metric Cards */
    [data-testid="stMetric"] {
        background: #18181b !important;
        border: 1px solid #27272a !important;
        border-radius: 6px !important;
        padding: 12px 16px !important;
    }
    [data-testid="stMetric"] label {
        color: #a1a1aa !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #fafafa !important;
        font-family: monospace;
    }

    /* Action Buttons */
    div.stButton > button[kind="primary"] {
        background: #10b981 !important;
        color: #09090b !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 10px 20px !important;
        transition: background 0.15s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        background: #059669 !important;
    }

    div.stDownloadButton > button {
        background: #18181b !important;
        color: #e4e4e7 !important;
        border: 1px solid #3f3f46 !important;
        border-radius: 6px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }
    div.stDownloadButton > button:hover {
        background: #27272a !important;
        border-color: #52525b !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #27272a;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        font-size: 13px;
        font-weight: 600;
        color: #a1a1aa;
        border-radius: 6px 6px 0 0;
    }
    .stTabs [aria-selected="true"] {
        color: #10b981 !important;
        border-bottom: 2px solid #10b981 !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Actor Header ─────────────────────────────────────────────────────
st.markdown("""
<div class="actor-header">
    <div class="actor-title-row">
        <div class="actor-icon">🕷️</div>
        <div>
            <h1 class="actor-name"><span class="actor-namespace">scrapton/</span>social-comment-scraper</h1>
            <div style="display:flex; gap:8px; margin-top:4px; align-items:center;">
                <span class="version-tag">v2.2.0</span>
                <span style="font-size:12px; color:#71717a;">Multi-link comment extractor for TikTok, Instagram, and X</span>
            </div>
        </div>
    </div>
    <div>
        <span class="status-badge">● System Ready</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Session State Initialization ─────────────────────────────────────
if "url_input_data" not in st.session_state:
    st.session_state["url_input_data"] = pd.DataFrame([
        {
            "URL": "https://www.tiktok.com/@tiktok/video/7708408003065580831",
            "Platform": "TikTok",
            "Label": "sample-tiktok",
        },
        {
            "URL": "https://www.instagram.com/p/DF123456789/",
            "Platform": "Instagram",
            "Label": "sample-ig",
        },
    ])

if "run_logs" not in st.session_state:
    st.session_state["run_logs"] = [
        f"[{datetime.now().strftime('%H:%M:%S')}] System initialized. Actor ready for execution."
    ]

if "dataset_results" not in st.session_state:
    st.session_state["dataset_results"] = []

# ── Main Tabs ────────────────────────────────────────────────────────
tab_input, tab_console, tab_storage = st.tabs([
    "📥 1. Input Configuration",
    "🖥️ 2. Execution Console",
    "📊 3. Storage Dataset",
])

# ── Tab 1: Input Configuration ───────────────────────────────────────
with tab_input:
    st.caption("Konfigurasi target URL dan parameter scraping. Input mendukung multi-link sekaligus.")

    col_grid, col_config = st.columns([3, 1], gap="medium")

    with col_grid:
        st.markdown("**Start URLs (Tabel Input Target)**")
        edited_df = st.data_editor(
            st.session_state["url_input_data"],
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "URL": st.column_config.TextColumn(
                    "Post / Video URL",
                    help="Paste URL postingan TikTok, Instagram Reels, atau Tweet",
                    required=True,
                ),
                "Platform": st.column_config.SelectboxColumn(
                    "Platform (Auto/Manual)",
                    options=["Auto-Detect", "TikTok", "Instagram", "Twitter / X"],
                    default="Auto-Detect",
                    width="small",
                ),
                "Label": st.column_config.TextColumn(
                    "Label / Tag",
                    help="Identifier opsional untuk pengelompokan output",
                    width="small",
                ),
            },
            key="actor_url_editor",
        )

    with col_config:
        st.markdown("**Run Options**")
        max_comments_per_url = st.number_input(
            "Max Comments / URL",
            min_value=5,
            max_value=300,
            value=25,
            step=5,
            help="Batas maksimum komentar yang diambil per link",
        )
        include_analysis = st.checkbox(
            "Auto Sentiment & Spam Analysis",
            value=True,
            help="Tambahkan kolom analisis sentimen dan indikator spam",
        )
        st.markdown("---")
        run_actor_button = st.button("🚀 Start Actor Run", type="primary", use_container_width=True)

# ── Execution Logic ──────────────────────────────────────────────────
async def execute_scraping_job(urls: list[str], max_limit: int, analyze: bool):
    scraper = CommentScraper()
    extracted_items = []
    log_stream = st.session_state["run_logs"]

    progress_bar = st.progress(0, text="Menginisialisasi browser engine...")

    for i, url in enumerate(urls, 1):
        plat = detect_platform_from_url(url)
        plat_name = plat.value.upper() if plat else "UNKNOWN"
        now_str = datetime.now().strftime("%H:%M:%S")

        msg = f"[{now_str}] [{i}/{len(urls)}] Scraping {plat_name}: {url[:60]}"
        log_stream.append(msg)

        try:
            batch = await scraper.scrape_comments_from_url(url, max_comments=max_limit)
            for item in batch:
                dumped = item.model_dump(mode="json")
                if analyze:
                    dumped = analyze_comment(dumped)
                extracted_items.append(dumped)

            success_msg = f"[{now_str}] ✓ Berhasil mengambil {len(batch)} komentar dari {plat_name}"
            log_stream.append(success_msg)
        except Exception as exc:
            err_msg = f"[{now_str}] ✗ Error pada {url[:45]}: {str(exc)}"
            log_stream.append(err_msg)

        progress_bar.progress(i / len(urls), text=f"Progress: {i}/{len(urls)} URLs selesai")

    progress_bar.empty()
    st.session_state["dataset_results"] = extracted_items
    st.session_state["run_logs"].append(
        f"[{datetime.now().strftime('%H:%M:%S')}] Job selesai. Total {len(extracted_items)} record berhasil disimpan ke Dataset."
    )

if run_actor_button:
    valid_urls = [
        str(row["URL"]).strip()
        for _, row in edited_df.iterrows()
        if isinstance(row.get("URL"), str) and str(row.get("URL")).strip().startswith("http")
    ]

    if not valid_urls:
        st.error("Masukkan minimal 1 URL valid di tabel input (diawali http/https).")
    else:
        st.toast(f"Memulai scraping untuk {len(valid_urls)} link...", icon="⚙️")
        asyncio.run(execute_scraping_job(valid_urls, max_comments_per_url, include_analysis))
        st.toast("Scraping selesai! Buka tab Storage Dataset untuk melihat hasil.", icon="✅")

# ── Tab 2: Execution Console ─────────────────────────────────────────
with tab_console:
    st.markdown("**Live Run Logs (Console Output)**")
    log_content = "<br>".join([
        f'<span class="terminal-time">{l.split("]")[0]}]</span> {l.split("]", 1)[-1]}'
        for l in st.session_state["run_logs"]
    ])
    st.markdown(f'<div class="terminal-box">{log_content}</div>', unsafe_allow_html=True)
    if st.button("Clear Logs", use_container_width=False):
        st.session_state["run_logs"] = [f"[{datetime.now().strftime('%H:%M:%S')}] Logs reset by user."]
        st.rerun()

# ── Tab 3: Storage Dataset ───────────────────────────────────────────
with tab_storage:
    data_list = st.session_state.get("dataset_results", [])

    if not data_list:
        st.info("Dataset masih kosong. Jalankan scraping pada tab 'Input Configuration' terlebih dahulu.")
    else:
        df_result = pd.DataFrame(data_list)

        # Dataset Metrics Summary
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Records", f"{len(df_result):,}")
        m2.metric("Target URLs", df_result["post_url"].nunique() if "post_url" in df_result.columns else 0)
        likes_total = int(df_result["likes_count"].sum()) if "likes_count" in df_result.columns else 0
        m3.metric("Total Likes", f"{likes_total:,}")
        plat_count = df_result["platform"].nunique() if "platform" in df_result.columns else 0
        m4.metric("Platforms", plat_count)

        st.markdown("---")

        # Filters row
        f_col1, f_col2 = st.columns([2, 1])
        with f_col1:
            search_query = st.text_input("Filter berdasarkan teks komentar / username", placeholder="Cari keyword...")
        with f_col2:
            platforms_list = ["Semua"] + list(df_result["platform"].unique()) if "platform" in df_result.columns else ["Semua"]
            selected_plat = st.selectbox("Filter Platform", options=platforms_list)

        filtered_df = df_result.copy()
        if selected_plat != "Semua" and "platform" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["platform"] == selected_plat]
        if search_query:
            q = search_query.lower()
            mask = filtered_df["content"].astype(str).str.lower().str.contains(q) | \
                   filtered_df["author_username"].astype(str).str.lower().str.contains(q)
            filtered_df = filtered_df[mask]

        # Table Display
        display_cols = [c for c in [
            "platform", "author_username", "content", "sentiment",
            "likes_count", "reply_count", "is_spam", "post_url"
        ] if c in filtered_df.columns]

        st.dataframe(
            filtered_df[display_cols],
            use_container_width=True,
            height=420,
            column_config={
                "platform": st.column_config.TextColumn("Platform", width="small"),
                "author_username": st.column_config.TextColumn("Author", width="medium"),
                "content": st.column_config.TextColumn("Comment Text", width="large"),
                "sentiment": st.column_config.TextColumn("Sentiment", width="small"),
                "likes_count": st.column_config.NumberColumn("Likes", format="%d", width="small"),
                "reply_count": st.column_config.NumberColumn("Replies", format="%d", width="small"),
                "is_spam": st.column_config.CheckboxColumn("Spam?", width="small"),
                "post_url": st.column_config.LinkColumn("Source URL", width="medium"),
            },
        )

        # Export Actions
        st.markdown("**Export Dataset**")
        exp1, exp2, exp3 = st.columns(3)

        csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
        exp1.download_button(
            "📥 Download CSV",
            data=csv_bytes,
            file_name="dataset_comments.csv",
            mime="text/csv",
            use_container_width=True,
        )

        excel_buf = io.BytesIO()
        with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
            filtered_df.to_excel(writer, index=False, sheet_name="Comments")
        exp2.download_button(
            "📊 Download Excel (.xlsx)",
            data=excel_buf.getvalue(),
            file_name="dataset_comments.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

        json_bytes = filtered_df.to_json(orient="records", indent=2, force_ascii=False).encode("utf-8")
        exp3.download_button(
            "📋 Download JSON",
            data=json_bytes,
            file_name="dataset_comments.json",
            mime="application/json",
            use_container_width=True,
        )
