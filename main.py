# shadow_simulator.py
import streamlit as st
from datetime import datetime
import pytz
from pysolar.solar import get_altitude, get_azimuth
import folium
from streamlit_folium import st_folium
import math

st.title("태양 위치 & 그림자 시뮬레이터")

# 사용자 입력
latitude = st.number_input("위도 (예: 37.5665)", value=37.5665)
longitude = st.number_input("경도 (예: 126.9780)", value=126.9780)
date_input = st.date_input("날짜", datetime.now().date())
time_input = st.time_input("시간", datetime.now().time())
building_height = st.number_input("건물 높이 (미터)", value=10.0)

# 시각 계산
local_tz = pytz.timezone("Asia/Seoul")
dt_local = local_tz.localize(datetime.combine(date_input, time_input))
dt_utc = dt_local.astimezone(pytz.utc)

# 태양 고도 및 방위각 계산
altitude = get_altitude(latitude, longitude, dt_utc)
azimuth = get_azimuth(latitude, longitude, dt_utc)

st.write(f"🌞 태양 고도: {altitude:.2f}°")
st.write(f"🧭 태양 방위각: {azimuth:.2f}°")

# 그림자 길이 및 방향 계산
if altitude > 0:
    shadow_length = building_height / math.tan(math.radians(altitude))
    st.write(f"🕶️ 그림자 길이: {shadow_length:.2f} 미터")

    # 위도/경도 기준 그림자 위치 계산 (단순화)
    def offset_coordinates(lat, lon, distance_m, azimuth_deg):
        # 거리(m)와 방위각을 위도, 경도로 변환
        delta_lat = distance_m * math.cos(math.radians(azimuth_deg)) / 111_000
        delta_lon = distance_m * math.sin(math.radians(azimuth_deg)) / (111_000 * math.cos(math.radians(lat)))
        return lat + delta_lat, lon + delta_lon

    shadow_lat, shadow_lon = offset_coordinates(latitude, longitude, shadow_length, azimuth + 180)  # 반대 방향

    # 지도 생성 및 마커
    m = folium.Map(location=[latitude, longitude], zoom_start=18)
    folium.Marker([latitude, longitude], tooltip="건물 위치").add_to(m)
    folium.PolyLine(locations=[[latitude, longitude], [shadow_lat, shadow_lon]],
                    color="gray", weight=4, tooltip="그림자").add_to(m)
    st_folium(m, width=700, height=500)
else:
    st.warning("태양이 지평선 아래에 있습니다. (고도 음수)")

