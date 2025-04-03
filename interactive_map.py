import streamlit as st
import folium
import rasterio
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from streamlit_folium import st_folium
from folium.plugins import FastMarkerCluster

# 📌 โหลด NDVI โดยอ่านเฉพาะบางส่วน (ถ้าจำเป็น)
def read_ndvi(file_path):
    with rasterio.open(file_path) as src:
        window = rasterio.windows.Window(0, 0, min(500, src.width), min(500, src.height))  # อ่านเฉพาะ 500x500 pixel
        ndvi = src.read(1, window=window)
        ndvi[ndvi == src.nodata] = np.nan  # กำหนดค่า nodata เป็น NaN
        bounds = src.bounds  # ขอบเขตพิกัด
    return ndvi, bounds

# 📍 โหลดไฟล์ NDVI
ndvi_path = r"D:\Year_2025\CodePy\interactive map\CBD_corn_20250320_NDVI.tif" # เปลี่ยนเป็น path ไฟล์ของคุณ
ndvi, bounds = read_ndvi(ndvi_path)

# 🗺️ คำนวณพิกัดศูนย์กลางแผนที่
center_lat = (bounds.top + bounds.bottom) / 2
center_lon = (bounds.left + bounds.right) / 2

# 🔹 สร้างแผนที่ Folium
m = folium.Map(location=[center_lat, center_lon], zoom_start=10, tiles="OpenStreetMap")

# 📌 Overlay NDVI บนแผนที่
folium.raster_layers.ImageOverlay(
    image=ndvi,
    bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
    colormap=lambda x: (x, 1-x, 0),  # สีเขียว-แดง
    opacity=0.6,
).add_to(m)

# 📍 ข้อมูลตัวอย่างจุดสุ่ม NDVI
sample_points = [
    {"lat": center_lat + 0.01, "lon": center_lon + 0.01, "ndvi": 0.4},
    {"lat": center_lat - 0.01, "lon": center_lon - 0.01, "ndvi": 0.6},
    {"lat": center_lat, "lon": center_lon, "ndvi": 0.75},
]

# ✅ ใช้ FastMarkerCluster เพื่อให้โหลดเร็ว
FastMarkerCluster([(p["lat"], p["lon"]) for p in sample_points]).add_to(m)

# 🌍 แสดงแผนที่ใน Streamlit
st.title("📌 NDVI Interactive Map")
st_folium(m, width=700, height=500, key="map")

# 📊 กราฟ NDVI
st.subheader("📊 กราฟสรุป NDVI")

# ✅ แปลงข้อมูลเป็น DataFrame
df = pd.DataFrame(sample_points)

# 🔹 Scatter plot NDVI vs ค่าอื่นๆ
fig_scatter = go.Figure(data=[go.Scatter(x=df["lat"], y=df["ndvi"], mode="markers", marker=dict(color="green"))])
fig_scatter.update_layout(title="Scatter NDVI by Location", xaxis_title="Latitude", yaxis_title="NDVI")
st.plotly_chart(fig_scatter, use_container_width=True)

# 📌 เลือกจุดแสดง NDVI แบบเจาะจง
st.subheader("🔍 เลือกจุดเพื่อดูค่า NDVI")
selected_point = st.selectbox("เลือกจุด:", df.index)
selected_data = df.iloc[selected_point]

# 🔹 แสดงค่า NDVI ของจุดที่เลือก
fig_bar = go.Figure(go.Bar(x=["NDVI"], y=[selected_data["ndvi"]], marker_color="green"))
fig_bar.update_layout(title=f"ค่า NDVI ของจุดที่เลือก: {selected_data['ndvi']:.2f}")
st.plotly_chart(fig_bar, use_container_width=True)
