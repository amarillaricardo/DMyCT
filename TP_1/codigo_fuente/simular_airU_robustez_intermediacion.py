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

# Leer grafo
air = read_dir_graph_weighted(file_path)
print('Airport')
print('Es dirigido?:', nx.is_directed(air))
print('Es pesado?:', nx.is_weighted(air))
print('Es fuertemente conexo?:', nx.is_strongly_connected(air))
print('Es debilmente conexo?:', nx.is_weakly_connected(air))

# Componente gigante fuertemente conexa
airStronglyCC = sorted(nx.strongly_connected_components(air), key=len, reverse=True)
airStrongly = air.subgraph(airStronglyCC[0])
print('\nAirport componente gigante fuertemente conexa')
print('Es dirigido?:', nx.is_directed(airStrongly))
print('Es pesado?:', nx.is_weighted(airStrongly))
print('Es fuertemente conexo?:', nx.is_strongly_connected(airStrongly))

# Convertir a no dirigido y quitar pesos
airUndir = nx.DiGraph.to_undirected(airStrongly)
airU = airUndir.copy()
drop_weights(airU)
print('\nGrafo sin pesos (undirected)')
print('Es dirigido?:', nx.is_directed(airU))
print('Es pesado?:', nx.is_weighted(airU))
print('Es conectado?:', nx.is_connected(airU))

# -------------------------------
# Cálculo de intermediación
# -------------------------------
print("\n📊 Calculando centralidad de intermediación (esto puede tardar)...")
centralidad_airU = nx.betweenness_centrality(airU)

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

def simular_robustez(G_original, nodos_ordenados, dirigido=False):
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
print("\n🚀 Iniciando simulación de robustez usando intermediación...")
nodos = estrategia_tradicional(airU, centralidad_airU)

airU_ngn_bet, airU_eff_bet = simular_robustez(airU, nodos, dirigido=False)

# Guardar resultados
output_path = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(output_path, 'airU_intermediacion.pkl')

print(f"\n💾 Guardando resultados en '{output_file}'...")
with open(output_file, 'wb') as f:
    pickle.dump({'ngn': airU_ngn_bet, 'eff': airU_eff_bet}, f)

print("✅ Simulación completada: Aeropuertos - Intermediación")
