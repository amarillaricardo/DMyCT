import pandas as pd
import networkx as nx
import numpy as np
import pickle
import os
from networkx.algorithms.efficiency_measures import global_efficiency

print("📡 Script iniciado: Facebook - Eigenvectores")

# -------------------------------
# Verificar archivo de entrada
# -------------------------------
file_path = 'facebook.txt'
if not os.path.isfile(file_path):
    raise FileNotFoundError(f"❌ El archivo '{file_path}' no se encontró.")
print("📁 Archivo encontrado.")

# -------------------------------
# Leer grafo no dirigido
# -------------------------------
print("📥 Cargando grafo...")
fb = nx.Graph()
array = np.loadtxt(file_path, dtype=int)
fb.add_edges_from(array)

print(f"Grafo cargado: {fb.number_of_nodes()} nodos, {fb.number_of_edges()} aristas.")
print(f"Es dirigido?: {nx.is_directed(fb)}")
print(f"Es conectado?: {nx.is_connected(fb)}")

# -------------------------------
# Calcular centralidad de eigenvectores
# -------------------------------
print("📊 Calculando centralidad de eigenvectores...")
try:
    centralidad_fb = nx.eigenvector_centrality(fb, max_iter=1000)
except nx.PowerIterationFailedConvergence:
    print("⚠️ Error: no convergió el cálculo de eigenvector. Reintentá con max_iter mayor.")
    exit()

# -------------------------------
# Funciones de simulación
# -------------------------------
def ng_n(G):
    giant = max(nx.connected_components(G), key=len)
    return len(giant) / G.number_of_nodes()

def estrategia_tradicional(G, centralidad_dict):
    return [n for n, _ in sorted(centralidad_dict.items(), key=lambda x: x[1], reverse=True)]

def simular_robustez(G_original, nodos_ordenados):
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
print("🚀 Iniciando simulación de robustez con eigenvectores...")
nodos = estrategia_tradicional(fb, centralidad_fb)
fb_ngn_eigen, fb_eff_eigen = simular_robustez(fb, nodos)

# -------------------------------
# Guardar resultados
# -------------------------------
output_path = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(output_path, 'fb_eigenvector.pkl')

print(f"💾 Guardando resultados en '{output_file}'...")
with open(output_file, 'wb') as f:
    pickle.dump({'ngn': fb_ngn_eigen, 'eff': fb_eff_eigen}, f)

print("✅ Simulación completada: Facebook - Eigenvectores")
