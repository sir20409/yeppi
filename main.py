import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from networkx.algorithms.approximation import traveling_salesman_problem

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(page_title="그래프 알고리즘 시각화", layout="centered")
st.title("📊 그래프 알고리즘 시각화 도구")

# -----------------------------
# 입력: 노드 수 및 가중치 행렬
# -----------------------------
node_count = st.number_input("노드 수 입력", min_value=2, max_value=12, value=4)

symmetric_toggle = st.checkbox("🔁 양방향 간선 가중치 자동 대칭 처리", value=True)

if symmetric_toggle:
    st.caption("상삼각형만 입력하세요 (i < j). 간선은 양방향이며 자동으로 대칭 처리됩니다.")
else:
    st.caption("모든 셀을 직접 입력하세요. 간선은 양방향이지만 가중치는 별도로 설정됩니다.")

default_matrix = [["" for _ in range(node_count)] for _ in range(node_count)]
df = pd.DataFrame(default_matrix, columns=[f"N{i}" for i in range(node_count)], index=[f"N{i}" for i in range(node_count)])
weight_matrix = st.data_editor(df, num_rows="fixed")

# -----------------------------
# 알고리즘 선택
# -----------------------------
st.markdown("### 📌 알고리즘 선택")
algorithm = st.selectbox(
    "사용할 알고리즘을 선택하세요:",
    [
        "🛠️ 확장형 연결 방식 (Prim)",
        "🪢 묶음 연결 방식 (Kruskal)",
        "🧭 모든 노드 순회 (TSP)"
    ]
)

if "TSP" in algorithm:
    start_node = st.selectbox("🚩 시작 노드를 선택하세요", [f"N{i}" for i in range(node_count)])
    start_index = int(start_node[1:])

# -----------------------------
# 그래프 생성 함수
# -----------------------------
def make_symmetric_matrix(matrix):
    n = len(matrix)
    for i in range(n):
        for j in range(i + 1, n):
            matrix[j][i] = matrix[i][j]
    return matrix

def parse_matrix(matrix, symmetric=True):
    G = nx.Graph()
    n = len(matrix)
    for i in range(n):
        G.add_node(i)
        for j in range(n):
            if i == j:
                continue
            val = matrix[i][j]
            if val == "" or val is None:
                continue
            try:
                weight = float(val)
                if symmetric and G.has_edge(j, i):
                    continue
                G.add_edge(i, j, weight=weight)
            except ValueError:
                continue
    return G

matrix_values = weight_matrix.values.tolist()
if symmetric_toggle:
    matrix_values = make_symmetric_matrix(matrix_values)

G = parse_matrix(matrix_values, symmetric=symmetric_toggle)

# -----------------------------
# 시각화 함수 (에러 수정 포함)
# -----------------------------
def draw_graph(graph, highlight_edges=None, title="그래프"):
    pos = nx.spring_layout(graph, seed=42)
    weights = nx.get_edge_attributes(graph, "weight")
    plt.figure(figsize=(6, 4))

    edge_colors = []
    for edge in graph.edges():
        if highlight_edges is not None and (edge in highlight_edges or (edge[1], edge[0]) in highlight_edges):
            edge_colors.append("red")
        else:
            edge_colors.append("gray")

    nx.draw(graph, pos, with_labels=True, node_color="skyblue", edge_color=edge_colors, node_size=600, width=2)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=weights)
    st.pyplot(plt)

# -----------------------------
# 전체 그래프 출력
# -----------------------------
st.markdown("### 🧩 전체 입력 그래프")
if G.number_of_edges() == 0:
    st.info("간선을 추가하면 전체 그래프가 여기에 표시됩니다.")
else:
    draw_graph(G, title="전체 그래프")
    st.write("노드 수:", G.number_of_nodes())
    st.write("간선 수:", G.number_of_edges())
    st.write("간선 목록:", list(G.edges(data=True)))

# -----------------------------
# 알고리즘 실행
# -----------------------------
if st.button("🚀 알고리즘 실행"):
    if G.number_of_edges() == 0:
        st.warning("⚠️ 간선이 없습니다.")
    else:
        if "Prim" in algorithm:
            st.subheader("🛠️ 확장형 연결 방식 (Prim)")
            mst = nx.minimum_spanning_tree(G, algorithm="prim")
            draw_graph(mst, highlight_edges=mst.edges())
            st.write("총 가중치:", mst.size(weight="weight"))
            st.write("연결된 간선:", list(mst.edges(data=True)))

        elif "Kruskal" in algorithm:
            st.subheader("🪢 묶음 연결 방식 (Kruskal)")
            mst = nx.minimum_spanning_tree(G, algorithm="kruskal")
            draw_graph(mst, highlight_edges=mst.edges())
            st.write("총 가중치:", mst.size(weight="weight"))
            st.write("연결된 간선:", list(mst.edges(data=True)))

        elif "TSP" in algorithm:
            st.subheader("🧭 모든 노드 순회 (TSP)")
            try:
                path = traveling_salesman_problem(G, cycle=True, weight="weight", nodes=[start_index])
                tsp_edges = list(zip(path[:-1], path[1:]))
                total_cost = sum(G[u][v]['weight'] for u, v in tsp_edges)
                st.write("방문 순서:", " → ".join([f"N{n}" for n in path]))
                st.write("총 거리:", total_cost)
                draw_graph(G, highlight_edges=tsp_edges)
            except Exception as e:
                st.error(f"TSP 계산 중 오류 발생: {e}")
