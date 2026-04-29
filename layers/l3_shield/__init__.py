try:
    from .topological_auditor import TopologicalAuditor
    from .budget_auditor import BudgetAuditor
    from .compliance_auditor import ComplianceAuditor
except ImportError:
    from topological_auditor import TopologicalAuditor
    from budget_auditor import BudgetAuditor
    from compliance_auditor import ComplianceAuditor
