from typing import List, Any, Callable

try:
    from layers.l2_brain.domain.dtos import HypothesisBundle, Hypothesis
except ModuleNotFoundError:
    from domain.dtos import HypothesisBundle, Hypothesis

class CounterfactualService:
    """
    Motor de Inferencias Contrafactuales (do-calculus).
    Evalúa escenarios 'what-if' (do(a)) simulando el impacto de una acción
    antes de ejecutarla.
    """
    
    @staticmethod
    def evaluate_intervention(
        action_a: Any,
        context_x: Any,
        utility_function: Callable[[Any, Any], float],
        cost_lambda: float = 0.1,
        cost_function: Callable[[Any], float] = lambda a: 1.0
    ) -> float:
        """
        Evalúa E[U | do(a), x] - lambda * C(a)
        """
        expected_utility = utility_function(action_a, context_x)
        cost = cost_function(action_a)
        
        return expected_utility - (cost_lambda * cost)
        
    @staticmethod
    def select_optimal_action(
        actions: List[Any],
        context_x: Any,
        utility_function: Callable[[Any, Any], float],
        cost_lambda: float = 0.1
    ) -> Any:
        """
        Selecciona a* = argmax E[U | do(a), x] - lambda * C(a)
        """
        if not actions:
            return None
            
        best_action = None
        best_score = float('-inf')
        
        for action in actions:
            score = CounterfactualService.evaluate_intervention(
                action, context_x, utility_function, cost_lambda
            )
            if score > best_score:
                best_score = score
                best_action = action
                
        return best_action
