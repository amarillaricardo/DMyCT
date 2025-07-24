import pandas as pd
import networkx as nx
import numpy as np
import pickle
import os
from networkx.algorithms.efficiency_measures import global_efficiency

print("📡 Script iniciado: Facebook - Intermediación")

file_path = 'facebook.txt'
if not os.path.isfile(file_path):
    raise FileNotFoundError(f"❌ El archivo '{file_path}' no se encontró.")
print("📁 Archivo encontrado.")

# Leer grafo no dirigido
fb = nx.Graph()
array = np.loadtxt(file_path, dtype=int)
fb.add_edges_from(array)

print(f"Grafo cargado: {fb.number_of_nodes()} nodos, {fb.number_of_edges()} aristas.")

print("📊 Calculando centralidad de intermediación...")
centralidad_fb = nx.betweenness_centrality(fb)

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

print("🚀 Iniciando simulación de robustez...")
nodos = estrategia_tradicional(fb, centralidad_fb)
fb_ngn, fb_eff = simular_robustez(fb, nodos)

output_path = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(output_path, 'fb_intermediacion.pkl')

print(f"💾 Guardando en: {output_file}")
with open(output_file, 'wb') as f:
    pickle.dump({'ngn': fb_ngn, 'eff': fb_eff}, f)

print("✅ Simulación completada: Facebook - Intermediación")
