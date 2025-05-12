import streamlit as st
import folium
from folium import IFrame
import base64
import gpxpy
from streamlit_folium import st_folium

# --- 定数設定 ---
GPX_FILE = "static_data/yamap_2022-12-03_07_21.gpx"
PHOTO_DIR = Path("static_data/photos")

# --- GPXファイルの読み込み ---
with open(GPX_FILE, "r", encoding="utf-8") as f:
    gpx = gpxpy.parse(f)

coords = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            coords.append((point.latitude, point.longitude))

# 中心座標（全体の中間点）
center = coords[len(coords) // 2]

# --- 地図の生成とルート描画 ---
m = folium.Map(location=center, tiles="OpenStreetMap")
folium.PolyLine(coords, color="blue", weight=3).add_to(m)

# --- 写真表示マーカー追加 ---
photos = sorted(PHOTO_DIR.glob("*.jpg")) + sorted(PHOTO_DIR.glob("*.jpeg"))
for i, photo in enumerate(photos):
    # 座標のインデックスを写真の数に合わせて間引く
    if i >= len(coords): break
    latlon = coords[i]

    # Base64エンコード
    with open(photo, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    html = f'<img src="data:image/jpeg;base64,{encoded}" width="200">'
    iframe = IFrame(html, width=210, height=210)
    popup = folium.Popup(iframe, max_width=2650)
    folium.Marker(latlon, popup=popup, icon=folium.Icon(color="orange", icon="camera")).add_to(m)

# --- 表示エリアを全体にフィットさせる ---
m.fit_bounds([coords[0], coords[-1]])

# --- Streamlit 表示 ---
st.title("登山ルートと写真マップ")
st_data = st_folium(m, width=1000, height=700)
