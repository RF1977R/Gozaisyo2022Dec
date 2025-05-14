
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

def get_gps_coords(img_path):
    with open(img_path, 'rb') as f:
        tags = exifread.process_file(f)
    try:
        lat_ref = tags["GPS GPSLatitudeRef"].values
        lon_ref = tags["GPS GPSLongitudeRef"].values
        lat = tags["GPS GPSLatitude"].values
        lon = tags["GPS GPSLongitude"].values

        def dms_to_dd(dms, ref):
            d = float(dms[0].num) / dms[0].den
            m = float(dms[1].num) / dms[1].den
            s = float(dms[2].num) / dms[2].den
            dd = d + m / 60 + s / 3600
            if ref in ['S', 'W']:
                dd *= -1
            return dd

        return dms_to_dd(lat, lat_ref), dms_to_dd(lon, lon_ref)
    except:
        return None

# GPXファイルの読み込み
with open(GPX_FILE, "r", encoding="utf-8") as f:
    gpx = gpxpy.parse(f)

# トラックポイントを取得
coords = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            coords.append((point.latitude, point.longitude))

# 地図を作成（中央を中心に表示）
center = coords[len(coords)//2]
m = folium.Map(location=center, zoom_start=15)

# ルートをポリラインで追加
folium.PolyLine(coords, color='blue', weight=3).add_to(m)

# 写真付きマーカーを追加
for photo_path in sorted(PHOTO_DIR.glob("*.jpg")):
    gps = get_gps_coords(photo_path)
    if gps:
        img = Image.open(photo_path)
        img.thumbnail((300, 300))
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        img_b64 = base64.b64encode(buffer.getvalue()).decode()
        img_html = f'<img src="data:image/jpeg;base64,{img_b64}" width="300">'
        folium.Marker(gps, popup=img_html, icon=folium.Icon(color='orange', icon='camera', prefix='fa')).add_to(m)

# Streamlitで表示
st.title("登山ルートと写真マップ")
st_folium(m, width=700, height=500)
