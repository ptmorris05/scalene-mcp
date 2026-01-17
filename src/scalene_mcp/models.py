"""Pydantic models for Scalene profiling data.

These models provide type-safe interfaces to Scalene's JSON output
and our own analysis results.
"""

from __future__ import annotations

from typing import Any

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
    cpu_samples: list[float] = Field(default_factory=list)

    # GPU metrics
    gpu_percent: float = Field(0.0, ge=0, le=100)

    # Memory metrics
    memory_peak_mb: float = Field(0.0, ge=0)
    memory_average_mb: float = Field(0.0, ge=0)
    memory_alloc_mb: float = Field(0.0, ge=0)
    memory_alloc_count: int = Field(0, ge=0)
    memory_samples: list[list[float]] = Field(default_factory=list)

    # Utilization
    cpu_utilization: float = Field(0.0, ge=0, le=1)
    core_utilization: float = Field(0.0, ge=0)

    # Loop info
    loop_start: int | None = None
    loop_end: int | None = None

    @property
    def total_cpu_percent(self) -> float:
        """Total CPU percentage across all categories."""
        return self.cpu_percent_python + self.cpu_percent_c + self.cpu_percent_system


class MemoryLeak(BaseModel):
    """Memory leak detection result from Scalene.
    
    Mirrors Scalene's LeakInfo structure exactly.
    """

    model_config = ConfigDict(frozen=True)

    filename: str
    lineno: int
    line: str
    likelihood: float = Field(..., ge=0, le=1, description="Leak probability (0-1)")
    velocity_mb_s: float = Field(..., ge=0, description="Leak rate in MB/s")


class ProfileResultSummary(BaseModel):
    """Response from profile tool."""

    profile_id: str
    success: bool = True

    # Quick stats
    elapsed_time_sec: float
    max_memory_mb: float
    files_profiled: int

    # Top issues (preview)
    top_cpu_lines: list[dict[str, Any]] = Field(default_factory=list)
    top_memory_lines: list[dict[str, Any]] = Field(default_factory=list)
    leak_count: int = 0

    # Text summary for LLM
    summary_text: str

    # Next steps
    suggested_actions: list[str] = Field(default_factory=list)
