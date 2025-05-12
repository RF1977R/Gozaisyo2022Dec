import streamlit as st
import gpxpy
import folium
from streamlit_folium import st_folium
from PIL import Image
import base64
import os

# --- 設定 ---
GPX_FILE = "static_data/yamap_2025-04-02.gpx"
PHOTO_FOLDER = "static_data/photos"

# --- ヘッダー ---
st.set_page_config(layout="wide")
st.title("登山ルートと写真マップ")

# --- GPX読み込み ---
with open(GPX_FILE, "r", encoding="utf-8") as f:
    gpx = gpxpy.parse(f)

# --- 緯度経度リスト抽出 ---
coords = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            coords.append((point.latitude, point.longitude))

center = coords[len(coords)//2] if coords else (35.0, 135.0)

# --- 地図生成 ---
m = folium.Map(location=center, zoom_start=13)
folium.PolyLine(coords, color='blue', weight=3).add_to(m)

# --- 写真マーカー配置 ---
if os.path.exists(PHOTO_FOLDER):
    photos = sorted(os.listdir(PHOTO_FOLDER))
    for i, photo in enumerate(photos):
        if not photo.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        try:
            with open(os.path.join(PHOTO_FOLDER, photo), "rb") as img_file:
                img_data = img_file.read()
                encoded = base64.b64encode(img_data).decode()
                html = f'<img src="data:image/jpeg;base64,{encoded}" width="300">'
                iframe = folium.IFrame(html, width=320, height=320)
                popup = folium.Popup(iframe, max_width=320)
                folium.Marker(
                    location=center,  # 写真のExif位置情報なしのため中央に仮配置
                    popup=popup,
                    icon=folium.Icon(color='orange', icon='camera', prefix='fa')
                ).add_to(m)
        except Exception as e:
            print(f"Error loading {photo}: {e}")

# --- 地図表示 ---
st_folium(m, width=1000)

# --- 写真一覧 ---
st.markdown("## 📸 写真ギャラリー")
cols = st.columns(3)
for i, photo in enumerate(photos):
    if photo.lower().endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(PHOTO_FOLDER, photo)
        img = Image.open(image_path)
        cols[i % 3].image(img, caption=photo, use_column_width=True)
