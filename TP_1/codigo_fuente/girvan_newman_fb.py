"""Script para ejecutar Girvan-Newman sobre un grafo y guardar la mejor partición + evolución en CSV (sin gráfico)."""
import pickle
import numpy as np
import networkx as nx
import os
import datetime

print("Script iniciado correctamente...")
print("Verificando existencia del archivo 'facebook.txt'...")

# -------------------------------
# Leer grafo desde archivo
# -------------------------------
def read_graph(filename):
    G = nx.Graph()
    array = np.loadtxt(filename, dtype=int)
    G.add_edges_from(array)
    return G

file_path = 'facebook.txt'
if not os.path.isfile(file_path):
    raise FileNotFoundError(f"El archivo '{file_path}' no se encontró.")
print("Archivo encontrado.")

print("Cargando grafo...")
G_fb = read_graph(file_path)
print(f"Grafo cargado: {G_fb.number_of_nodes()} nodos, {G_fb.number_of_edges()} aristas.")

# -------------------------------
# Inicializar archivo CSV
# -------------------------------
csv_file = "modularidad_por_iteracion_fb.csv"
with open(csv_file, "w") as f:
    f.write("iteracion,comunidades,modularidad\n")

# -------------------------------
# Ejecutar Girvan-Newman
# -------------------------------
print("Ejecutando algoritmo Girvan-Newman...")
modulos = nx.community.girvan_newman(G_fb)

mod_max = -999
com_max = None
mejor_iter = 0

# -------------------------------
# Bucle principal
# -------------------------------
for step, communities in enumerate(modulos, start=1):
    print(f"Iteración {step}: calculando modularidad...")
    n_modularidad = nx.community.modularity(G_fb, communities)
    n_comunidades = len(communities)

    print(f"Modularidad = {n_modularidad:.4f} | Comunidades: {n_comunidades}")

    # Guardar evolución en CSV
    with open(csv_file, "a") as f:
        f.write(f"{step},{n_comunidades},{n_modularidad:.6f}\n")

    # Guardar mejor partición
    if n_modularidad > mod_max:
        mod_max = n_modularidad
        com_max = tuple(sorted(c) for c in communities)
        mejor_iter = step

        fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"best_partition_fb_{fecha}.pkl"
        with open(filename, "wb") as f:
            pickle.dump({
                "iter": mejor_iter,
                "modularity": mod_max,
                "partition": com_max
            }, f)
        print(f"Partición guardada: iteración {step}, modularidad = {mod_max:.4f}")

# -------------------------------
# Fin del proceso
# -------------------------------
print("\nProceso completado.")
print(f"Mejor partición en la iteración {mejor_iter} con modularidad: {mod_max:.4f}")
print(f"Número de comunidades: {len(com_max)}")
print(f"Histórico guardado en: {csv_file}")
