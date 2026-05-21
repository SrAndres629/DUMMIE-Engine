"""Performance monitoring hook for DUMMIE daemon.

Tracks memory usage, component load times, and optimization metrics.
Reports to telemetry for continuous improvement.
"""
import logging
import os
import resource
import time
from typing import Any

from layers.l2_brain.metacognition.contracts import MetacognitiveFrame

logger = logging.getLogger("dummie.performance_monitor")

class PerformanceMonitorHook:
    """Monitors and reports performance metrics."""
    
    def __init__(self):
        self._start_time = time.time()
        self._request_count = 0
        self._total_latency = 0
        self._peak_memory_mb = 0
    
    async def run(self, frame: MetacognitiveFrame) -> MetacognitiveFrame:
        request_start = time.time()
        
        # Get current memory usage
        try:
            mem_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
            if mem_mb > self._peak_memory_mb:
                self._peak_memory_mb = mem_mb
        except Exception:
            mem_mb = 0
        
        self._request_count += 1
        
        # Get pruned context stats
        pruned = frame.telemetry.get("pruned_context", {})
        
        # Calculate latency
        latency = time.time() - request_start
        self._total_latency += latency
        avg_latency = self._total_latency / self._request_count
        
        # Build performance report
        perf_report = {
            "request_count": self._request_count,
            "current_latency_ms": round(latency * 1000, 2),
            "avg_latency_ms": round(avg_latency * 1000, 2),
            "current_memory_mb": round(mem_mb, 1),
            "peak_memory_mb": round(self._peak_memory_mb, 1),
            "uptime_seconds": round(time.time() - self._start_time, 1),
            "context_pruning": {
                "input_tokens": pruned.get("total_input_tokens", 0),
                "output_tokens": pruned.get("total_output_tokens", 0),
                "reduction_ratio": pruned.get("reduction_ratio", 0),
                "items_dropped": pruned.get("items_dropped", 0),
                "complexity": pruned.get("task_complexity", "unknown"),
            },
        }
        
        frame.telemetry["performance"] = perf_report
        
        # Log warnings
        if mem_mb > 2000:
            logger.warning(f"High memory usage: {mem_mb:.0f}MB")
        if latency > 1.0:
            logger.warning(f"High latency: {latency*1000:.0f}ms")
        
        return perf_report
    
    def get_status(self) -> dict:
        return {
            "request_count": self._request_count,
            "avg_latency_ms": round(self._total_latency / max(1, self._request_count) * 1000, 2),
            "peak_memory_mb": round(self._peak_memory_mb, 1),
            "uptime_seconds": round(time.time() - self._start_time, 1),
        }
