import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# -----------------------------
# UI 구성
# -----------------------------
st.title("Prim vs Kruskal 최소 신장 트리 시각화")

node_count = st.number_input("노드 수 입력 (2 이상)", min_value=2, max_value=20, value=4, step=1)

st.markdown("#### 간선 가중치 행렬 입력")
st.caption("🔁 위쪽 삼각형만 입력하세요 (i < j). 아래쪽은 무시됩니다. "
           "빈 칸은 간선 없음, 숫자 0도 유효한 가중치입니다. 간선은 양방향이고 동일 가중치입니다.")

# 기본 빈 행렬 생성
default_matrix = [["" for _ in range(node_count)] for _ in range(node_count)]
df = pd.DataFrame(default_matrix, columns=[f"N{i}" for i in range(node_count)], index=[f"N{i}" for i in range(node_count)])
weight_matrix = st.data_editor(df, num_rows="fixed")

# -----------------------------
# 입력 처리 및 그래프 생성
# -----------------------------
def parse_matrix(matrix):
    G = nx.Graph()
    for i in range(len(matrix)):
        G.add_node(i)
        for j in range(i + 1, len(matrix)):
            val = matrix[i][j]
            if val == "" or val is None:
                continue  # 간선 없음
            try:
                weight = float(val)
                G.add_edge(i, j, weight=weight)  # 양방향, 동일 가중치
            except ValueError:
                continue
    return G

G = parse_matrix(weight_matrix.values.tolist())

# -----------------------------
# 알고리즘 구현
# -----------------------------
def run_prim(graph):
    return nx.minimum_spanning_tree(graph, algorithm="prim")

def run_kruskal(graph):
    return nx.minimum_spanning_tree(graph, algorithm="kruskal")

def draw_graph(graph, title="그래프"):
    pos = nx.spring_layout(graph, seed=42)
    weights = nx.get_edge_attributes(graph, 'weight')
    plt.figure(figsize=(6, 4))
    nx.draw(graph, pos, with_labels=True, node_color="skyblue", edge_color="gray", node_size=600)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=weights)
    st.pyplot(plt)

# -----------------------------
# 실행 버튼 및 결과 출력
# -----------------------------
if st.button("Prim & Kruskal 알고리즘 실행"):
    if G.number_of_edges() == 0:
        st.warning("⚠️ 그래프에 유효한 간선이 없습니다.")
    else:
        st.subheader("🔷 Prim 알고리즘 결과")
        prim_mst = run_prim(G)
        draw_graph(prim_mst, title="Prim MST")
        prim_weight = prim_mst.size(weight="weight")
        st.write("총 가중치:", prim_weight)
        st.write("간선 목록:", list(prim_mst.edges(data=True)))

        st.subheader("🔶 Kruskal 알고리즘 결과")
        kruskal_mst = run_kruskal(G)
        draw_graph(kruskal_mst, title="Kruskal MST")
        kruskal_weight = kruskal_mst.size(weight="weight")
        st.write("총 가중치:", kruskal_weight)
        st.write("간선 목록:", list(kruskal_mst.edges(data=True)))
