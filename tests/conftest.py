"""
Dragon Judge 测试配置
提供测试固件和共享配置
"""
import pytest
from src.scoring.dragon_judge import MarketData


@pytest.fixture
def sample_market_data():
    """提供样本市场数据"""
    return {
        'date': '2024-01-01',
        'limit_up_count': 50,
        'limit_down_count': 5,
        'total_stocks': 5000,
        'leading_stocks': [
            {'code': '000001', 'name': '平安银行', 'limit_up_days': 3},
            {'code': '000002', 'name': '万科A', 'limit_up_days': 2},
            {'code': '600519', 'name': '贵州茅台', 'limit_up_days': 1},
        ]
    }


@pytest.fixture
def sample_market_data_obj():
    """提供样本 MarketData 对象"""
    return MarketData(
        date='2024-01-01',
        limit_up_count=50,
        limit_down_count=5,
        total_stocks=5000,
        leading_stocks=[
            {'code': '000001', 'name': '平安银行', 'limit_up_days': 3},
            {'code': '000002', 'name': '万科A', 'limit_up_days': 2},
            {'code': '600519', 'name': '贵州茅台', 'limit_up_days': 1},
        ]
    )


@pytest.fixture
def empty_market_data():
    """提供空市场数据"""
    return {
        'date': '2024-01-01',
        'limit_up_count': 0,
        'limit_down_count': 0,
        'total_stocks': 5000,
        'leading_stocks': []
    }


@pytest.fixture
def ice_point_data():
    """冰点期市场数据"""
    return MarketData(
        date='2024-01-01',
        limit_up_count=10,
        limit_down_count=50,
        total_stocks=5000,
        leading_stocks=[]
    )


@pytest.fixture
def climax_data():
    """高潮期市场数据"""
    return MarketData(
        date='2024-01-01',
        limit_up_count=200,
        limit_down_count=0,
        total_stocks=5000,
        leading_stocks=[
            {'code': '000001', 'name': '龙头股1', 'limit_up_days': 6},
            {'code': '000002', 'name': '龙头股2', 'limit_up_days': 5},
            {'code': '000003', 'name': '龙头股3', 'limit_up_days': 4},
        ]
    )


@pytest.fixture
def custom_config():
    """提供自定义配置"""
    return {
        'weights': {
            'height': 0.40,
            'competition': 0.30,
            'sector': 0.20,
            'sentiment': 0.05,
            'quality': 0.05,
        },
        'thresholds': {
            'ice_point': 20.0,
            'start': 35.0,
            'fermentation': 50.0,
            'climax': 70.0,
            'divergence': 85.0
        }
    }
