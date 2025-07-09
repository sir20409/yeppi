import streamlit as st
import geocoder
import pytz
from datetime import datetime
from pysolar.solar import get_altitude, get_azimuth
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium
import math

st.title("🌳 햇빛 회피 경로 시뮬레이터")

# 1. 사용자 위치 & 현재 시간 (한국시간)
g = geocoder.ip('me')
lat, lon = (g.latlng if g.latlng else (37.5665, 126.9780))
kst = pytz.timezone("Asia/Seoul")
now_naive = datetime.now()  # naive datetime
now = kst.localize(now_naive)  # timezone-aware
dt_utc = now.astimezone(pytz.utc)

# 2. 출발지, 도착지 입력 (위도,경도)
orig = st.text_input("출발지 (lat,lon)", f"{lat:.5f},{lon:.5f}")
dest = st.text_input("도착지 (lat,lon)", f"{lat+0.01:.5f},{lon+0.01:.5f}")

try:
    lat1, lon1 = map(float, orig.split(","))
    lat2, lon2 = map(float, dest.split(","))
except Exception as e:
    st.error("위도, 경도 입력 형식이 잘못되었습니다. 예: 37.5665,126.9780")
    st.stop()

# 3. 도로망 bbox 기준 불러오기 (north, south, east, west 순서)
north = max(lat1, lat2) + 0.005
south = min(lat1, lat2) - 0.005
east = max(lon1, lon2) + 0.005
west = min(lon1, lon2) - 0.005

G = ox.graph_from_bbox(north, south, east, west, network_type='walk')

# 4. 태양 고도 및 방위각 계산 (사용자 현재 위치 기준)
alt = get_altitude(lat, lon, dt_utc)
azi = get_azimuth(lat, lon, dt_utc)

# 5. 엣지 비용 함수 (길이 + 그림자 효과)
def edge_sun_cost(u, v, data):
    length = data.get('length', 1)
    if alt <= 0:
        return length  # 태양 안 뜨면 그냥 길이 비용
    # tan(alt)가 0이면 너무 커질 수 있으니 최소값 처리
    tan_alt = math.tan(math.radians(alt))
    if tan_alt < 0.01:
        tan_alt = 0.01
    shadow_cost = length / tan_alt
    return length + shadow_cost

# 6. 엣지별 비용 설정
edge_weights = {}
for u, v, key, data in G.edges(keys=True, data=True):
    edge_weights[(u, v, key)] = edge_sun_cost(u, v, data)
nx.set_edge_attributes(G, edge_weights, 'weight')

# 7. 출발지, 도착지에 가장 가까운 노드 찾기
orig_node = ox.distance.nearest_nodes(G, lon1, lat1)
dest_node = ox.distance.nearest_nodes(G, lon2, lat2)

# 8. 최단 경로 계산 (가중치 'weight' 기준)
try:
    route = nx.shortest_path(G, orig_node, dest_node, weight='weight')
except nx.NetworkXNoPath:
    st.error("출발지와 도착지 사이에 경로를 찾을 수 없습니다.")
    st.stop()

# 9. 지도 생성 및 경로 표시
m = folium.Map(location=[lat, lon], zoom_start=15)
folium.Marker([lat1, lon1], tooltip="출발").add_to(m)
folium.Marker([lat2, lon2], tooltip="도착").add_to(m)

route_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]
folium.PolyLine(route_coords, color='green', weight=5, tooltip="그림자 우선 경로").add_to(m)

st.write(f"🌥️ 태양 고도: {alt:.1f}°, 방위각: {azi:.1f}°")
st_folium(m, width=700, height=500)

