Feature: Interfaz Command Canvas (DE-V2-L6-26)
  Criterios de Aceptación Ejecutables para el Despliegue en Webview de IDE.

  Scenario: Render Command Canvas inside VS Code Webview
    Given a VS Code extension host
    When the Command Canvas is loaded as a Webview
    Then it must initialize the "PostMessageBridge"
    And it must successfully handshake with the L1 Nervous system via ACP
    And the Performance Metric: webview_render_latency < 50ms
    And the Performance Metric: bridge_echo_latency < 5ms

  Scenario: Real-time context update in Sidecar
    Given a cursor move event in the IDE editor
    When the Semantic Bridge (L4) emits a context update
    Then the Command Canvas must highlight the active LST node visually
    And the Performance Metric: visual_sync_latency < 100ms
