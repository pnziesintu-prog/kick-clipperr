import streamlit as st
import subprocess
import os
import glob

st.set_page_config(page_title="Kick VOD Clipper for TikTok", page_icon="🎬", layout="centered")

st.title("🎬 Kick VOD Clipper (9:16 for TikTok)")
st.write("Paste a Kick.com VOD link below to automatically download and crop it into a mobile-friendly 9:16 clip.")

vod_url = st.text_input("🔗 Enter Kick VOD URL:")

start_time = st.text_input("⏱️ Start Time (e.g., 00:12:30):", "00:00:00")
duration = st.slider("🎞️ Clip Duration (seconds):", min_value=10, max_value=60, value=30)

if st.button("🚀 Generate TikTok Clip", type="primary"):
    if not vod_url:
        st.warning("Please enter a valid Kick URL.")
    else:
        with st.status("Downloading and processing video...", expanded=True) as status:
            st.write("📥 Downloading video from Kick...")
            
            # Clean up old files
            for f in glob.glob("output_clip.mp4") + glob.glob("downloaded_vod.*"):
                try:
                    os.remove(f)
                except:
                    pass

            # Download using yt-dlp
            download_cmd = [
                "yt-dlp",
                "-f", "best[ext=mp4]/best",
                "-o", "downloaded_vod.%(ext)s",
                vod_url
            ]
            
            result = subprocess.run(download_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                status.update(label="❌ Download failed!", state="error")
                st.error(result.stderr)
            else:
                st.write("✂️ Cutting and cropping to 9:16 vertical format...")
                
                # Find the downloaded file
                downloaded_files = glob.glob("downloaded_vod.*")
                if not downloaded_files:
                    status.update(label="❌ Error finding downloaded file.", state="error")
                    st.stop()
                
                input_file = downloaded_files[0]
                
                # FFmpeg command to crop center to 9:16 and trim duration
                # vf crop filter: h:w:x:y -> crops the center of a horizontal video into vertical 9:16
                ffmpeg_cmd = [
                    "ffmpeg", "-y",
                    "-ss", start_time,
                    "-i", input_file,
                    "-t", str(duration),
                    "-vf", "crop=in_h*9/16:in_h:(in_w-in_h*9/16)/2:0",
                    "-c:v", "libx264", "-preset", "fast",
                    "-c:a", "aac",
                    "output_clip.mp4"
                ]
                
                ffmpeg_result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                
                if ffmpeg_result.returncode != 0:
                    status.update(label="❌ FFmpeg processing failed!", state="error")
                    st.error(ffmpeg_result.stderr)
                else:
                    status.update(label="✨ Clip ready for TikTok!", state="complete")
                    st.success("Success! Download your 9:16 clip below:")

        if os.path.exists("output_clip.mp4"):
            st.video("output_clip.mp4")
            with open("output_clip.mp4", "rb") as file:
                st.download_button(
                    label="📥 Download TikTok Clip",
                    data=file,
                    file_name="kick_tiktok_clip.mp4",
                    mime="video/mp4"
                )
