
import streamlit as st
import gpxpy
import folium
from streamlit_folium import st_folium
from PIL import Image
import base64
from io import BytesIO
from pathlib import Path
import exifread

# GPXファイルと写真ディレクトリのパス
GPX_FILE = "static_data/yamap_2022-12-03_07_21.gpx"
PHOTO_DIR = Path("static_data/photos")

# GitHub上の画像の公開URLのベースパス
GITHUB_BASE_URL = "https://raw.githubusercontent.com/RF1977R/GozaIsyo2022Dec/main/static_data/photos"

# GPXファイルの読み込み
with open(GPX_FILE, "r", encoding="utf-8") as f:
    gpx = gpxpy.parse(f)

# トラックポイントを取得
coords = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            coords.append((point.latitude, point.longitude))

def get_photo_location(photo_path):
    try:
        with open(photo_path, "rb") as f:
            tags = exifread.process_file(f)
        lat_ref = str(tags.get("GPS GPSLatitudeRef"))
        lon_ref = str(tags.get("GPS GPSLongitudeRef"))
        lat = tags.get("GPS GPSLatitude")
        lon = tags.get("GPS GPSLongitude")
        if not lat or not lon:
            return None
        def convert_to_degrees(value):
            d, m, s = value.values
            return float(d.num) / d.den + float(m.num) / m.den / 60 + float(s.num) / s.den / 3600
        lat_deg = convert_to_degrees(lat)
        lon_deg = convert_to_degrees(lon)
        if lat_ref == "S":
            lat_deg = -lat_deg
        if lon_ref == "W":
            lon_deg = -lon_deg
        return lat_deg, lon_deg
    except:
        return None

# 地図を作成（ルート中央を中心に）
#	center = coords[len(coords)//2]
#	m = folium.Map(location=center, zoom_start=15)
m = folium.Map(zoom_start=15)  # 中心点は一旦不要

# ルートをポリラインで追加
folium.PolyLine(coords, color='blue', weight=3).add_to(m)

# 地図の表示範囲をルート全体に自動調整
m.fit_bounds(coords)


# 写真付きマーカーを追加（Exif位置情報を使用）
for photo_path in sorted(PHOTO_DIR.glob("*.jpg")):
    location = get_photo_location(photo_path)
    if not location:
        continue
    img = Image.open(photo_path)
    thumbnail = img.copy()
    thumbnail.thumbnail((300, 300))
    buffer = BytesIO()
    thumbnail.save(buffer, format="JPEG")
    img_b64 = base64.b64encode(buffer.getvalue()).decode()
    image_url = f"{GITHUB_BASE_URL}/{photo_path.name}"
    img_html = f'<a href="{image_url}" target="_blank"><img src="data:image/jpeg;base64,{img_b64}" width="300"></a>'
    folium.Marker(location, popup=img_html, icon=folium.Icon(color='orange', icon='camera', prefix='fa')).add_to(m)

# Streamlitで表示
st.title("登山ルートと写真マップ")
st_folium(m, width=700, height=500)
