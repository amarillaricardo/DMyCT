import pandas as pd
import networkx as nx
import numpy as np
import pickle
import os
from networkx.algorithms.efficiency_measures import global_efficiency

print("📡 Script iniciado correctamente...")
print("Verificando existencia del archivo 'airport.txt'...")

# -------------------------------
# Leer grafo desde archivo
# -------------------------------
def read_dir_graph_weighted(filename):
    G = nx.DiGraph()
    array = np.loadtxt(filename, dtype=int)
    G.add_weighted_edges_from(array)
    return G

def drop_weights(G):
    for node, edges in nx.to_dict_of_dicts(G).items():
        for edge, attrs in edges.items():
            attrs.pop('weight', None)

file_path = 'airport.txt'
if not os.path.isfile(file_path):
    raise FileNotFoundError(f"❌ El archivo '{file_path}' no se encontró.")
print("📁 Archivo encontrado.")

print("📥 Cargando grafo dirigido con pesos...")
air = read_dir_graph_weighted(file_path)
print(f"Grafo cargado: {air.number_of_nodes()} nodos, {air.number_of_edges()} aristas.")

# Componente gigante fuertemente conexa
airStronglyCC = sorted(nx.strongly_connected_components(air), key=len, reverse=True)
airStrongly = air.subgraph(airStronglyCC[0])

# Convertir a no dirigido y sin pesos
airU = nx.DiGraph.to_undirected(airStrongly)
airU = airU.copy()
drop_weights(airU)

print(f"Grafo procesado: {airU.number_of_nodes()} nodos, {airU.number_of_edges()} aristas.")
print(f"Es conectado?: {nx.is_connected(airU)}")

# -------------------------------
# Cálculo de PageRank
# -------------------------------
print("\n📊 Calculando centralidad PageRank (grafo dirigido)...")
centralidad_air = nx.pagerank(airU, max_iter=1000)

# -------------------------------
# Funciones de simulación
# -------------------------------
def ng_n(G):
    if nx.is_directed(G):
        giant = max(nx.strongly_connected_components(G), key=len)
    else:
        giant = max(nx.connected_components(G), key=len)
    return len(giant) / G.number_of_nodes()

def estrategia_tradicional(G, centralidad_dict):
    return [n for n, _ in sorted(centralidad_dict.items(), key=lambda x: x[1], reverse=True)]

def simular_robustez(G_original, nodos_ordenados, dirigido=True):
    G = G_original.copy()
    fraccion_ngn = []
    eficiencias = []
    visitados = set()

    for i, nodo in enumerate(nodos_ordenados):
        if nodo in G and nodo not in visitados:
            G.remove_node(nodo)
            visitados.add(nodo)
        if G.number_of_nodes() == 0 or G.number_of_edges() == 0:
            fraccion_ngn.append(0)
            eficiencias.append(0)
            break
        fraccion_ngn.append(ng_n(G))
        eficiencias.append(global_efficiency(G))
        if i % 100 == 0:
            print(f"🧩 Iteración {i}/{len(nodos_ordenados)}")

    return fraccion_ngn, eficiencias

# -------------------------------
# Simulación
# -------------------------------
print("\n🚀 Iniciando simulación de robustez usando PageRank...")
nodos = estrategia_tradicional(airU, centralidad_air)

airU_ngn_pagerank, airU_eff_pagerank = simular_robustez(airU, nodos, dirigido=True)

# Guardar resultados
output_path = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(output_path, 'airU_pagerank.pkl')

print(f"\n💾 Guardando resultados en '{output_file}'...")
with open(output_file, 'wb') as f:
    pickle.dump({'ngn': airU_ngn_pagerank, 'eff': airU_eff_pagerank}, f)

print("✅ Simulación completada: Aeropuertos - PageRank")
