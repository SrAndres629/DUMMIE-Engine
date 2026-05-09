from .pattern_miner_v2 import PatternMinerV2

class PatternMiner(PatternMinerV2):
    """
    Wrapper de compatibilidad estricto apuntando a PatternMinerV2.
    Esto previene romper contratos existentes con L3/L5 o SelfWorktreeOrchestrator.
    """
    pass
