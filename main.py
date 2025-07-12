import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(page_title="Prim + MST + DFS 시각화", layout="centered")
st.title("🛠️ Prim MST + DFS 순회 시각화")

# -----------------------------
# 노드 수와 입력 행렬
# -----------------------------
node_count = st.number_input("노드 수 입력", min_value=2, max_value=12, value=4)

symmetric_toggle = st.checkbox("🔁 양방향 간선 가중치 자동 대칭 처리", value=True)

default_matrix = [["" for _ in range(node_count)] for _ in range(node_count)]
df = pd.DataFrame(default_matrix, columns=[f"N{i}" for i in range(node_count)], index=[f"N{i}" for i in range(node_count)])
weight_matrix = st.data_editor(df, num_rows="fixed")

start_node = st.selectbox("🚩 DFS 시작 노드 선택", [f"N{i}" for i in range(node_count)])
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

# -----------------------------
# 시각화 함수
# -----------------------------
def draw_graph(graph, highlight_edges=None, title="그래프"):
    pos = nx.spring_layout(graph, seed=42)
    weights = nx.get_edge_attributes(graph, "weight")
    plt.figure(figsize=(6, 4))

    edge_colors = []
    for edge in graph.edges():
        if highlight_edges and (edge in highlight_edges or (edge[1], edge[0]) in highlight_edges):
            edge_colors.append("red")
        else:
            edge_colors.append("gray")

    nx.draw(graph, pos, with_labels=True, node_color="skyblue", edge_color=edge_colors, node_size=600, width=2)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=weights)
    st.pyplot(plt)

# -----------------------------
# 실행: Prim + DFS
# -----------------------------
matrix_values = weight_matrix.values.tolist()
if symmetric_toggle:
    matrix_values = make_symmetric_matrix(matrix_values)

G = parse_matrix(matrix_values, symmetric=symmetric_toggle)

st.markdown("### 🧩 전체 그래프")
if G.number_of_edges() == 0:
    st.warning("⚠️ 간선을 입력하세요.")
else:
    draw_graph(G, title="전체 그래프")
    st.write("노드 수:", G.number_of_nodes())
    st.write("간선 수:", G.number_of_edges())

if st.button("🚀 MST + DFS 순회 경로 실행"):
    if not nx.is_connected(G):
        st.warning("⚠️ 그래프가 연결되어 있어야 합니다.")
    else:
        st.subheader("✅ MST (Prim) + DFS 순회 경로")

        # Prim MST
        mst = nx.minimum_spanning_tree(G, algorithm="prim")
        draw_graph(mst, highlight_edges=mst.edges(), title="MST 결과")

        st.write("총 MST 가중치:", mst.size(weight="weight"))
        st.write("MST 간선 목록:", list(mst.edges(data=True)))

        # DFS 순회
        dfs_order = list(nx.dfs_preorder_nodes(mst, source=start_index))
        dfs_order.append(start_index)  # 순환 경로 만들기 (선택사항)
        path_str = " → ".join([f"N{n}" for n in dfs_order])
        st.markdown(f"**🔄 DFS 순회 경로**: {path_str}")
