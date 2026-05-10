use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct IntentAudit {
    pub intent_type: String,
    pub target: String,
    pub risk_score: f32,
}

/// Escudo de DUMMIE Engine (L3)
/// Valida la conformidad de intenciones de L2 antes de su propagación.
#[pyfunction]
fn audit_intent(intent_json: String) -> PyResult<String> {
    let audit: IntentAudit = serde_json::from_str(&intent_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;

    // Lógica de Veto (Spec 31 - Blast Radius)
    let is_safe = if audit.intent_type == "delete_root" {
        false
    } else {
        audit.risk_score < 0.8
    };

    let response = serde_json::json!({
        "authorized": is_safe,
        "shield_note": if is_safe { "CONFIRM_L3" } else { "VETO_L3_RISK_OVERFLOW" }
    });

    Ok(response.to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn shield(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(audit_intent, m)?)?;
    Ok(())
}
