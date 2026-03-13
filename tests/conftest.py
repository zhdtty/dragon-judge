"""
Dragon Judge 测试套件
"""
import pytest
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 全局 fixtures
@pytest.fixture
def sample_market_data():
    """示例市场数据"""
    return {
        "date": "2026-03-14",
        "limit_up_count": 45,
        "limit_down_count": 8,
        "total_stocks": 5000,
        "leading_stocks": [
            {"code": "000001", "name": "平安银行", "limit_up_days": 3},
            {"code": "000002", "name": "万科A", "limit_up_days": 2},
        ]
    }

@pytest.fixture
def sample_sector_data():
    """示例板块数据"""
    return {
        "hot_sectors": [
            {"name": "人工智能", "change_pct": 5.2, "lead_stock": "603000"},
            {"name": "新能源", "change_pct": 3.8, "lead_stock": "002594"},
        ]
    }
