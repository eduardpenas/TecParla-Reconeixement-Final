import matplotlib.pyplot as plt
import numpy as np
import os
import re

# --- CONFIGURACIÓN ESTÉTICA ---
plt.style.use('ggplot')
COLORS = ['#E24A33', '#348ABD', '#988ED5', '#777777', '#FBC15E', '#8EBA42', '#FFB5B8']

def plot_confusion_matrix():
    """Genera el mapa de calor de la matriz de confusión final"""
    # Datos copiados de tu ejecución final (Deep Learning 96.75%)
    # Filas: Real (a, e, i, o, u)
    # Columnas: Predicho (a, e, i, o, u)
    cm = np.array([
        [386, 1, 0, 12, 1],
        [0, 397, 2, 0, 1],
        [0, 3, 394, 1, 2],
        [9, 1, 0, 371, 19],
        [0, 0, 0, 13, 387]
    ])
    classes = ['a', 'e', 'i', 'o', 'u']

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    
    # Etiquetas
    ax.set_xticks(np.arange(len(classes)))
    ax.set_yticks(np.arange(len(classes)))
    ax.set_xticklabels(classes, fontsize=12)
    ax.set_yticklabels(classes, fontsize=12)
    ax.set_ylabel('Vocal Real', fontsize=14, fontweight='bold')
    ax.set_xlabel('Predicción del Sistema', fontsize=14, fontweight='bold')
    ax.set_title('Matriz de Confusión Final (MLP)', fontsize=16)

    # Escribir los valores dentro de los cuadros
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            val = cm[i, j]
            color = "white" if val > thresh else "black"
            # Resaltar la diagonal
            weight = 'bold' if i == j else 'normal'
            ax.text(j, i, format(val, 'd'),
                    ha="center", va="center",
                    color=color, fontsize=12, fontweight=weight)

    plt.tight_layout()
    plt.savefig('grafica_matriz_confusion.png', dpi=300)
    print(">>> Generada: grafica_matriz_confusion.png")

def plot_model_comparison():
    """Comparativa de barras entre los 3 sistemas"""
    modelos = ['Euclídeo', 'GMM (8 Gauss)', 'Deep Learning (MLP)']
    exactitud = [83.0, 95.85, 96.75] # Tus resultados
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    barras = ax.bar(modelos, exactitud, color=['#95a5a6', '#3498db', '#e74c3c'], width=0.6)
    
    # Línea de meta (100%)
    ax.axhline(y=100, color='gray', linestyle='--', alpha=0.5)
    
    # Etiquetas y título
    ax.set_ylabel('Exactitud (%)', fontsize=12)
    ax.set_title('Evolución del Rendimiento del Sistema Ramsés', fontsize=16)
    ax.set_ylim(80, 100) # Zoom entre 80% y 100% para que se vea la diferencia
    
    # Poner el valor encima de cada barra
    for rect in barras:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., height + 0.2,
                f'{height}%',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig('grafica_comparativa_modelos.png', dpi=300)
    print(">>> Generada: grafica_comparativa_modelos.png")

def plot_training_curve(log_file='entrenamiento.log'):
    """Intenta leer el log y pintar la curva. Si no existe, avisa."""
    epochs, losses, accs = [], [], []
    
    if not os.path.exists(log_file):
        print(f"AVISO: No encuentro '{log_file}'. Saltando gráfica de aprendizaje.")
        print("   (Para generarla: bash ramses/todo.sh > entrenamiento.log)")
        return

    with open(log_file, 'r') as f:
        for line in f:
            # Regex para buscar "Epo X: Loss=Y | Acc=Z%"
            m = re.search(r"Epo (\d+): Loss=([\d.]+) \| Acc=([\d.]+)%", line)
            if m:
                epochs.append(int(m.group(1)))
                losses.append(float(m.group(2)))
                accs.append(float(m.group(3)))
    
    if not epochs:
        print("AVISO: El log está vacío o no tiene el formato esperado.")
        return

    # Gráfica de doble eje
    fig, ax1 = plt.subplots(figsize=(10, 6))

    color = 'tab:red'
    ax1.set_xlabel('Épocas de Entrenamiento')
    ax1.set_ylabel('Loss (Error)', color=color, fontweight='bold')
    ax1.plot(epochs, losses, color=color, linewidth=2, label='Training Loss')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx() 
    color = 'tab:blue'
    ax2.set_ylabel('Accuracy (Exactitud %)', color=color, fontweight='bold')
    ax2.plot(epochs, accs, color=color, linewidth=2, linestyle='--', label='Val Accuracy')
    ax2.tick_params(axis='y', labelcolor=color)
    
    # Marcar el máximo
    max_acc = max(accs)
    best_epoch = epochs[accs.index(max_acc)]
    plt.title(f'Curva de Aprendizaje (Mejor: {max_acc}% en época {best_epoch})')
    
    plt.tight_layout()
    plt.savefig('grafica_curva_aprendizaje.png', dpi=300)
    print(f">>> Generada: grafica_curva_aprendizaje.png (Max: {max_acc}%)")

if __name__ == "__main__":
    print("--- Generando Gráficas Finales ---")
    plot_confusion_matrix()
    plot_model_comparison()
    plot_training_curve() # Busca 'entrenamiento.log' automáticamente