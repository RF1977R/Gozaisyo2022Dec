import streamlit as st
import gpxpy
import folium
from streamlit_folium import st_folium
from PIL import Image
import base64
from io import BytesIO
from pathlib import Path
import exifread  # ローカルにインストールされていればOK

# データパス
GPX_FILE = "static_data/yamap_2022-12-03_07_21.gpx"
PHOTO_DIR = Path("static_data/photos")
GITHUB_BASE_URL = "https://raw.githubusercontent.com/RF1977R/Gozaosyo2022Dec/main/static_data/photos"

# GPX読み込み
with open(GPX_FILE, "r", encoding="utf-8") as f:
    gpx = gpxpy.parse(f)

# ルート座標抽出
coords = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            coords.append((point.latitude, point.longitude))

# 地図初期化
center = coords[len(coords)//2]
m = folium.Map(location=center, zoom_start=15)
folium.PolyLine(coords, color='blue', weight=3).add_to(m)

# EXIF → 座標変換関数
def dms_to_decimal(dms):
    return float(dms.values[0].num) / float(dms.values[0].den) + \
           float(dms.values[1].num) / float(dms.values[1].den) / 60 + \
           float(dms.values[2].num) / float(dms.values[2].den) / 3600

# 写真マーカー表示
for photo_path in sorted(PHOTO_DIR.glob("*.jpg")):
    with open(photo_path, "rb") as f:
        tags = exifread.process_file(f)

    lat_tag = tags.get("GPS GPSLatitude")
    lon_tag = tags.get("GPS GPSLongitude")
    if not lat_tag or not lon_tag:
        continue

    lat = dms_to_decimal(lat_tag)
    lon = dms_to_decimal(lon_tag)

    img = Image.open(photo_path)
    thumbnail = img.copy()
    thumbnail.thumbnail((300, 300))
    buffer = BytesIO()
    thumbnail.save(buffer, format="JPEG")
    img_b64 = base64.b64encode(buffer.getvalue()).decode()
    image_url = f"{GITHUB_BASE_URL}/{photo_path.name}"
    img_html = f'<a href="{image_url}" target="_blank"><img src="data:image/jpeg;base64,{img_b64}" width="300"></a>'

    folium.Marker([lat, lon], popup=img_html, icon=folium.Icon(color='orange', icon='camera', prefix='fa')).add_to(m)

# Streamlit表示
st.title("登山ルートと写真マップ")
st_folium(m, width=700, height=500)
