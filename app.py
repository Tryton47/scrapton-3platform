"""
Streamlit Web Dashboard for Social Media Scraper Suite.
Modular entrypoint connecting scrapers, live UI, and data exports.
"""
import asyncio
import io
import json
import pandas as pd
import streamlit as st

from core.storage import StorageManager
from scrapers.instagram import InstagramScraper
from scrapers.tiktok import TikTokScraper
from scrapers.twitter import TwitterScraper
from ui import render_sidebar, render_custom_styles, prepare_chart_dataframe, get_metric_summary

st.set_page_config(
    page_title="Scrapton - Multi-Platform Scraper",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_custom_styles()
platform, username, limit = render_sidebar()

# Main Title
st.markdown('<div class="main-title">🕸️ Scrapton Multi-Platform Scraper</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Ekstraksi data profil, konten, dan metrik interaksi (TikTok, Instagram, X) secara visual</div>', unsafe_allow_html=True)

start_button = st.button("🚀 Mulai Scraping Sekarang", type="primary", use_container_width=True)

async def scrape_target(platform: str, username: str, limit: int):
    posts = []
    profile = None
    if platform == "tiktok":
        scraper = TikTokScraper()
        profile = await scraper.get_profile(username)
        async for post in scraper.get_user_posts(username, limit=limit):
            posts.append(post)
    elif platform == "instagram":
        scraper = InstagramScraper()
        profile = await scraper.get_profile(username)
        async for post in scraper.get_user_posts(username, limit=limit):
            posts.append(post)
    elif platform == "twitter":
        scraper = TwitterScraper()
        profile = await scraper.get_profile(username)
        async for post in scraper.get_user_posts(username, limit=limit):
            posts.append(post)
    return profile, posts

if start_button:
    if not username:
        st.error("Silakan masukkan username target terlebih dahulu di sidebar!")
    else:
        with st.spinner(f"Sedang mengumpulkan data dari {platform.upper()} untuk @{username}..."):
            try:
                profile, posts = asyncio.run(scrape_target(platform, username, limit))
                st.session_state["last_profile"] = profile
                st.session_state["last_posts"] = posts
                st.session_state["last_platform"] = platform
                st.session_state["last_username"] = username
                st.success(f"Berhasil mengumpulkan {len(posts)} item dari @{username}!")
            except Exception as e:
                st.error(f"Terjadi kesalahan saat scraping: {str(e)}")

# Display Scraped Results
if "last_posts" in st.session_state and st.session_state["last_posts"]:
    posts = st.session_state["last_posts"]
    profile = st.session_state.get("last_profile")
    user = st.session_state.get("last_username")

    st.markdown("---")

    if profile:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Display Name", profile.display_name or f"@{profile.username}")
        col2.metric("Followers", f"{profile.followers_count:,}")
        col3.metric("Following", f"{profile.following_count:,}")
        col4.metric("Item Terkumpul", len(posts))

    storage = StorageManager()
    flattened = storage._flatten_items(posts)
    df = pd.DataFrame(flattened)

    desired_cols = [
        "id", "author_username", "content", "metrics_likes",
        "metrics_comments", "metrics_views", "metrics_shares", "url"
    ]
    existing_cols = [c for c in desired_cols if c in df.columns]
    other_cols = [c for c in df.columns if c not in desired_cols]
    df = df[existing_cols + other_cols]

    tab_table, tab_chart, tab_json = st.tabs(["📋 Tabel Data Interaktif", "📈 Grafik Metrik", "🔍 Raw JSON"])

    with tab_table:
        st.dataframe(df, use_container_width=True, height=400)

        col_d1, col_d2 = st.columns(2)
        csv_data = df.to_csv(index=False).encode("utf-8")
        col_d1.download_button(
            label="📥 Unduh sebagai CSV",
            data=csv_data,
            file_name=f"{st.session_state['last_platform']}_{user}.csv",
            mime="text/csv",
            use_container_width=True
        )

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="ScrapedData")
        col_d2.download_button(
            label="📊 Unduh sebagai Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name=f"{st.session_state['last_platform']}_{user}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with tab_chart:
        chart_df = prepare_chart_dataframe(df)
        if chart_df is not None:
            st.subheader("Distribusi Views & Likes per Konten")
            st.bar_chart(chart_df)
            summary = get_metric_summary(df)
            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("Total Likes", f"{summary['total_likes']:,}")
            col_s2.metric("Total Comments", f"{summary['total_comments']:,}")
            col_s3.metric("Total Views", f"{summary['total_views']:,}")
        else:
            st.info("Metrik chart tidak lengkap pada postingan yang diambil.")

    with tab_json:
        raw_json = json.dumps([p.model_dump(mode="json") for p in posts], indent=2, ensure_ascii=False)
        st.json(raw_json)
