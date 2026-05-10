import pytest
from layers.l2_brain.domain.counterfactual_service import CounterfactualService

def test_evaluate_intervention():
    # Contexto: memoria llena.
    # Acción A: borrar cache (Utilidad esperada: 10, costo: 2)
    # Acción B: reiniciar db (Utilidad esperada: 12, costo: 100)
    
    def utility(action, context):
        if action == "clear_cache": return 10.0
        if action == "restart_db": return 12.0
        return 0.0
        
    def cost(action):
        if action == "clear_cache": return 2.0
        if action == "restart_db": return 100.0
        return 1.0

    score_a = CounterfactualService.evaluate_intervention("clear_cache", {}, utility, cost_lambda=0.1, cost_function=cost)
    score_b = CounterfactualService.evaluate_intervention("restart_db", {}, utility, cost_lambda=0.1, cost_function=cost)
    
    # score_a = 10 - 0.1*2 = 9.8
    # score_b = 12 - 0.1*100 = 2.0
    assert score_a > score_b

def test_select_optimal_action():
    actions = ["clear_cache", "restart_db"]
    
    def utility(a, x): return 10.0 if a == "clear_cache" else 12.0
    
    # Mismo test, usando select_optimal_action
    # Necesitamos empaquetar cost_function dentro de utility (forma simplificada) o pasar el lambda.
    # El test prueba select_optimal_action asumiendo cost por defecto (1.0).
    
    # score clear_cache: 10 - 0.1(1) = 9.9
    # score restart_db: 12 - 0.1(1) = 11.9
    best = CounterfactualService.select_optimal_action(actions, {}, utility, cost_lambda=0.1)
    assert best == "restart_db"
