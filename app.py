"""
Streamlit Web Dashboard for Social Media Scraper Suite.
Supports:
1. Multi-Link Comment Scraper (Bebas input 1 atau banyak link TikTok, Instagram, X)
2. Profile & Timeline Scraper (Scrape postingan dari username)
"""
import asyncio
import io
import json
import pandas as pd
import streamlit as st

from core.storage import StorageManager
from scrapers.comment_scraper import CommentScraper, detect_platform_from_url
from scrapers.tiktok import TikTokScraper
from scrapers.instagram import InstagramScraper
from scrapers.twitter import TwitterScraper
from ui import render_sidebar, render_custom_styles, prepare_chart_dataframe, get_metric_summary

st.set_page_config(
    page_title="Scrapton - Multi-Platform Scraper",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_custom_styles()
platform, default_user, default_limit = render_sidebar()

# Title
st.markdown('<div class="main-title">🕸️ Scrapton Multi-Platform Scraper</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Scraper komentar berdasarkan link kustom atau ekstraksi konten profil (TikTok, IG, X)</div>', unsafe_allow_html=True)

# Main Navigation Mode
scrape_mode = st.radio(
    "📌 Pilih Mode Scraping:",
    options=["💬 Scrape Komentar dari Link Pilihan (Bebas Banyak Link)", "👤 Scrape Profil & Feed Akun"],
    horizontal=True
)

st.markdown("---")

# ==========================================
# MODE 1: MULTI-LINK COMMENT SCRAPER
# ==========================================
if "Scrape Komentar" in scrape_mode:
    st.subheader("💬 Multi-Link Comment Scraper")
    st.write("Masukkan satu atau beberapa link postingan/video (TikTok, Instagram Reels/Post, atau Tweet X). Setiap link dipisahkan oleh baris baru.")

    links_input = st.text_area(
        "🔗 Daftar Link URL Postingan (1 link per baris):",
        placeholder="https://www.tiktok.com/@tiktok/video/7708408003065580831\nhttps://www.instagram.com/p/C_abc123/\nhttps://x.com/elonmusk/status/1800000000000000000",
        height=140
    )

    col_opt1, col_opt2 = st.columns([1, 1])
    with col_opt1:
        comments_per_link = st.slider("🎯 Maksimal Komentar per Link", min_value=5, max_value=100, value=25, step=5)
    with col_opt2:
        st.info("💡 Scraper akan mengunjungi setiap link secara berurutan dan mengumpulkan semua komentar ke dalam 1 tabel yang sama.")

    btn_scrape_comments = st.button("🚀 Mulai Scrape Komentar", type="primary", use_container_width=True)

    if btn_scrape_comments:
        raw_urls = [line.strip() for line in links_input.strip().splitlines() if line.strip()]
        if not raw_urls:
            st.error("Silakan masukkan minimal 1 link postingan terlebih dahulu!")
        else:
            all_comments = []
            comment_scraper = CommentScraper()
            progress_bar = st.progress(0)
            status_text = st.empty()

            for idx, url in enumerate(raw_urls):
                platform_detected = detect_platform_from_url(url)
                plat_name = platform_detected.value.upper() if platform_detected else "UNKNOWN"
                status_text.write(f"⏳ ({idx + 1}/{len(raw_urls)}) Membaca komentar dari [{plat_name}]: `{url}`...")
                
                try:
                    result = asyncio.run(comment_scraper.scrape_comments_from_url(url, max_comments=comments_per_link))
                    all_comments.extend(result)
                except Exception as e:
                    st.warning(f"Gagal mengambil komentar dari {url}: {str(e)}")

                progress_bar.progress((idx + 1) / len(raw_urls))

            status_text.empty()
            progress_bar.empty()

            if all_comments:
                st.session_state["comment_results"] = all_comments
                st.success(f"🎉 Berhasil mengumpulkan total {len(all_comments)} komentar dari {len(raw_urls)} link!")
            else:
                st.warning("Tidak ada komentar yang berhasil diambil. Pastikan link valid atau platform tidak terkunci login wall.")

    # Show Comment Results
    if "comment_results" in st.session_state and st.session_state["comment_results"]:
        comments = st.session_state["comment_results"]
        st.markdown("### 📋 Hasil Scraping Komentar")

        storage = StorageManager()
        flat_comments = [c.model_dump(mode="json") for c in comments]
        df_comm = pd.DataFrame(flat_comments)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Komentar", len(df_comm))
        col2.metric("Total Link Terproses", df_comm["post_url"].nunique())
        col3.metric("Total Likes Komentar", int(df_comm["likes_count"].sum()) if "likes_count" in df_comm.columns else 0)

        # Reorder columns
        ordered_cols = ["platform", "author_username", "content", "likes_count", "reply_count", "post_url", "id"]
        avail_cols = [c for c in ordered_cols if c in df_comm.columns]
        df_comm = df_comm[avail_cols]

        st.dataframe(df_comm, use_container_width=True, height=400)

        col_d1, col_d2 = st.columns(2)
        csv_data = df_comm.to_csv(index=False).encode("utf-8")
        col_d1.download_button(
            label="📥 Unduh Komentar sebagai CSV",
            data=csv_data,
            file_name="scraped_comments.csv",
            mime="text/csv",
            use_container_width=True
        )

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_comm.to_excel(writer, index=False, sheet_name="Comments")
        col_d2.download_button(
            label="📊 Unduh Komentar sebagai Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name="scraped_comments.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# ==========================================
# MODE 2: PROFILE & FEED SCRAPER
# ==========================================
else:
    st.subheader(f"👤 Scrape Profil & Feed Akun ({platform.upper()})")
    
    col_u1, col_u2 = st.columns([2, 1])
    with col_u1:
        target_username = st.text_input("Target Username:", value=default_user, placeholder="misal: tiktok, cristiano, elonmusk").strip().lstrip("@")
    with col_u2:
        feed_limit = st.slider("Maksimal Postingan:", min_value=3, max_value=50, value=default_limit, step=1)

    btn_scrape_profile = st.button("🚀 Mulai Scrape Profil & Feed", type="primary", use_container_width=True)

    async def scrape_profile_flow(plat: str, user: str, limit: int):
        posts = []
        profile = None
        if plat == "tiktok":
            scraper = TikTokScraper()
            profile = await scraper.get_profile(user)
            async for post in scraper.get_user_posts(user, limit=limit):
                posts.append(post)
        elif plat == "instagram":
            scraper = InstagramScraper()
            profile = await scraper.get_profile(user)
            async for post in scraper.get_user_posts(user, limit=limit):
                posts.append(post)
        elif plat == "twitter":
            scraper = TwitterScraper()
            profile = await scraper.get_profile(user)
            async for post in scraper.get_user_posts(user, limit=limit):
                posts.append(post)
        return profile, posts

    if btn_scrape_profile:
        if not target_username:
            st.error("Silakan masukkan username target terlebih dahulu!")
        else:
            with st.spinner(f"Mengumpulkan konten dari @{target_username}..."):
                try:
                    profile, posts = asyncio.run(scrape_profile_flow(platform, target_username, feed_limit))
                    st.session_state["feed_posts"] = posts
                    st.session_state["feed_profile"] = profile
                    st.session_state["feed_user"] = target_username
                    st.session_state["feed_plat"] = platform
                    st.success(f"Berhasil mengumpulkan {len(posts)} konten dari @{target_username}!")
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat scraping: {str(e)}")

    if "feed_posts" in st.session_state and st.session_state["feed_posts"]:
        posts = st.session_state["feed_posts"]
        profile = st.session_state.get("feed_profile")
        user = st.session_state.get("feed_user")

        if profile:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Display Name", profile.display_name or f"@{profile.username}")
            col2.metric("Followers", f"{profile.followers_count:,}")
            col3.metric("Following", f"{profile.following_count:,}")
            col4.metric("Item Terkumpul", len(posts))

        storage = StorageManager()
        flattened = storage._flatten_items(posts)
        df = pd.DataFrame(flattened)

        st.dataframe(df, use_container_width=True, height=400)

        col_d1, col_d2 = st.columns(2)
        csv_data = df.to_csv(index=False).encode("utf-8")
        col_d1.download_button(
            label="📥 Unduh sebagai CSV",
            data=csv_data,
            file_name=f"{st.session_state['feed_plat']}_{user}.csv",
            mime="text/csv",
            use_container_width=True
        )

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Feed")
        col_d2.download_button(
            label="📊 Unduh sebagai Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name=f"{st.session_state['feed_plat']}_{user}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
