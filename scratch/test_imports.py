import sys
import os

# Simular la ejecución desde la raíz
sys.path.append(os.getcwd())

try:
    from layers.l2_brain.metacognition.pipeline import MetacognitivePipeline
    print("Import exitoso con prefijo")
except ImportError as e:
    print(f"Error con prefijo: {e}")

try:
    from metacognition.pipeline import MetacognitivePipeline
    print("Import exitoso sin prefijo")
except ImportError as e:
    print(f"Error sin prefijo: {e}")
