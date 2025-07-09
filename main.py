import streamlit as st
import geocoder, pytz
from datetime import datetime
from pysolar.solar import get_altitude, get_azimuth
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium
import math

st.title("🌳 햇빛 회피 경로 시뮬레이터")

# 사용자 위치 & 시간
g = geocoder.ip('me')
lat, lon = (g.latlng if g.latlng else (37.5665,126.9780))
kst = pytz.timezone("Asia/Seoul")
now = datetime.now(kst)
dt_utc = now.astimezone(pytz.utc)

# 출발 · 도착 입력
orig = st.text_input("출발지 (lat,lon)", f"{lat:.5f},{lon:.5f}")
dest = st.text_input("도착지 (lat,lon)", f"{lat+0.01:.5f},{lon+0.01:.5f}")
lat1, lon1 = map(float, orig.split(","))
lat2, lon2 = map(float, dest.split(","))

# 도로망 로딩
G = ox.graph_from_bbox(min(lat1,lat2)-0.005, max(lat1,lat2)+0.005,
                       min(lon1,lon2)-0.005, max(lon1,lon2)+0.005, network_type='walk')

# 태양 고도/방위각 계산
alt = get_altitude(lat, lon, dt_utc)
azi = get_azimuth(lat, lon, dt_utc)

# 비용 함수: 그림자가 많을수록 낮은 비용
def edge_sun_cost(u, v, data):
    mid_lat = (G.nodes[u]['y']+G.nodes[v]['y'])/2
    mid_lon = (G.nodes[u]['x']+G.nodes[v]['x'])/2
    if alt <= 0:
        return data.get('length',1)
    shadow = data.get('length',1)/math.tan(math.radians(alt))
    return data.get('length',1) + shadow

nx.set_edge_attributes(G, {edge: edge_sun_cost(*edge, data) for edge, data in G.edges.items()}, 'weight')

# 최단경로 (그림자 비용 기준) 계산
orig_node = ox.distance.nearest_nodes(G, lon1, lat1)
dest_node = ox.distance.nearest_nodes(G, lon2, lat2)
route = nx.shortest_path(G, orig_node, dest_node, weight='weight')

# 지도 시각화
m = folium.Map(location=[lat, lon], zoom_start=15)
folium.Marker([lat1, lon1], tooltip="출발").add_to(m)
folium.Marker([lat2, lon2], tooltip="도착").add_to(m)
coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]
folium.PolyLine(coords, color="green", weight=5, tooltip="그림자 우선 경로").add_to(m)
st.write(f"🌥️ 태양 고도: {alt:.1f}°, 방위각: {azi:.1f}°")
st_folium(m, width=700, height=500)
