"""
Dragon Judge - A股情绪龙头分析系统

核心模块导出
"""

from .dragon_judge import (
    DragonJudge,
    MarketCycle,
    LeadingStock,
    MarketData,
    DragonJudgeError,
    InvalidDataError,
    ValidationError,
    InvalidCycleError,
    ConfigurationError,
)

__version__ = "2.0.0"
__author__ = "Dragon Judge Team"

__all__ = [
    "DragonJudge",
    "MarketCycle",
    "LeadingStock",
    "MarketData",
    "DragonJudgeError",
    "InvalidDataError",
    "ValidationError",
    "InvalidCycleError",
    "ConfigurationError",
]
