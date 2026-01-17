"""Pydantic models for Scalene profiling data.

These models provide type-safe interfaces to Scalene's JSON output
and our own analysis results.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Raw Scalene Data Models (mirror Scalene's JSON schema)
# ============================================================================


class LineMetrics(BaseModel):
    """Profiling metrics for a single line of code."""

    model_config = ConfigDict(frozen=True)

    lineno: int = Field(..., description="Line number")
    line: str = Field(..., description="Source code")

    # CPU metrics
    cpu_percent_python: float = Field(0.0, ge=0, le=100)
    cpu_percent_c: float = Field(0.0, ge=0, le=100)
    cpu_percent_system: float = Field(0.0, ge=0, le=100)
    cpu_samples: List[float] = Field(default_factory=list)

    # GPU metrics
    gpu_percent: float = Field(0.0, ge=0, le=100)

    # Memory metrics
    memory_peak_mb: float = Field(0.0, ge=0)
    memory_average_mb: float = Field(0.0, ge=0)
    memory_alloc_mb: float = Field(0.0, ge=0)
    memory_alloc_count: int = Field(0, ge=0)
    memory_samples: List[List[float]] = Field(default_factory=list)

    # Utilization
    cpu_utilization: float = Field(0.0, ge=0, le=1)
    core_utilization: float = Field(0.0, ge=0)

    # Loop info
    loop_start: Optional[int] = None
    loop_end: Optional[int] = None

    @property
    def total_cpu_percent(self) -> float:
        """Total CPU percentage."""
        return self.cpu_percent_python + self.cpu_percent_c + self.cpu_percent_system

    @property
    def is_hotspot(self) -> bool:
        """Is this line a performance hotspot?"""
        return self.total_cpu_percent > 5.0 or self.memory_peak_mb > 100.0


class MemoryLeak(BaseModel):
    """Memory leak detection result."""

    model_config = ConfigDict(frozen=True)

    filename: str
    lineno: int
    line: str
    likelihood: float = Field(..., ge=0, le=1, description="Leak probability")
    velocity_mb_s: float = Field(..., ge=0, description="Leak rate in MB/s")

    @property
    def severity(self) -> Literal["low", "medium", "high", "critical"]:
        """Severity classification."""
        if self.likelihood > 0.8:
            return "critical"
        elif self.likelihood > 0.6:
            return "high"
        elif self.likelihood > 0.4:
            return "medium"
        return "low"


class ProfileResultSummary(BaseModel):
    """Response from profile tool."""

    profile_id: str
    success: bool = True

    # Quick stats
    elapsed_time_sec: float
    max_memory_mb: float
    files_profiled: int

    # Top issues (preview)
    top_cpu_lines: List[Dict[str, Any]] = Field(default_factory=list)
    top_memory_lines: List[Dict[str, Any]] = Field(default_factory=list)
    leak_count: int = 0

    # Text summary for LLM
    summary_text: str

    # Next steps
    suggested_actions: List[str] = Field(default_factory=list)
