"""
Dragon Judge 核心评分算法
情绪周期判断与龙头选股系统
"""
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MarketCycle(Enum):
    """市场情绪周期"""
    ICE_POINT = ("冰点", "ice_point", "❄️")      # 情绪极度低迷
    START = ("启动", "start", "🚀")              # 情绪开始回暖
    FERMENTATION = ("发酵", "fermentation", "🔥") # 情绪加速升温
    CLIMAX = ("高潮", "climax", "🌟")            # 情绪极度亢奋
    DIVERGENCE = ("分化/退潮", "divergence", "⚠️") # 情绪开始衰退
    
    def __init__(self, cn_name: str, en_name: str, emoji: str = "") -> None:
        self.cn_name = cn_name
        self.en_name = en_name
        self.emoji = emoji
    
    @classmethod
    def from_value(cls, value: Union[str, "MarketCycle"]) -> "MarketCycle":
        """
        从字符串值获取枚举
        
        Args:
            value: 市场周期值，可以是字符串或枚举
            
        Returns:
            MarketCycle 枚举值
            
        Raises:
            InvalidCycleError: 无法识别的市场周期
        """
        if isinstance(value, cls):
            return value
            
        for cycle in cls:
            if value in (cycle.value[0], cycle.value[1], cycle.cn_name, cycle.en_name):
                return cycle
        raise InvalidCycleError(f"Unknown market cycle: {value}")
    
    @property
    def display_name(self) -> str:
        """获取带表情的显示名称"""
        return f"{self.emoji} {self.cn_name}" if self.emoji else self.cn_name


@dataclass
class LeadingStock:
    """龙头股票数据"""
    code: str
    name: str
    limit_up_days: int  # 连板天数
    score: float = 0.0   # 综合评分
    
    # 五维评分
    height_score: float = 0.0      # 高度分
    competition_score: float = 0.0 # 竞争分
    sector_score: float = 0.0      # 板块分
    sentiment_score: float = 0.0   # 情绪分
    quality_score: float = 0.0     # 质量分
    
    # 扩展字段
    sector: Optional[str] = None           # 所属板块
    market_cap: Optional[float] = None     # 市值（亿元）
    turnover_rate: Optional[float] = None  # 换手率
    volume_ratio: Optional[float] = None   # 量比
    
    def __post_init__(self) -> None:
        """数据后处理验证"""
        if not self.code or not isinstance(self.code, str):
            raise ValidationError("股票代码必须是有效的字符串")
        if not self.name or not isinstance(self.name, str):
            raise ValidationError("股票名称必须是有效的字符串")
        if not isinstance(self.limit_up_days, int) or self.limit_up_days < 0:
            raise ValidationError("连板天数必须是非负整数")
    
    def to_dict(self, include_details: bool = False) -> Dict[str, Any]:
        """
        转换为字典
        
        Args:
            include_details: 是否包含扩展字段
            
        Returns:
            股票数据字典
        """
        result = {
            'code': self.code,
            'name': self.name,
            'limit_up_days': self.limit_up_days,
            'score': round(self.score, 2),
            'height_score': round(self.height_score, 2),
            'competition_score': round(self.competition_score, 2),
            'sector_score': round(self.sector_score, 2),
            'sentiment_score': round(self.sentiment_score, 2),
            'quality_score': round(self.quality_score, 2),
        }
        
        if include_details:
            result.update({
                'sector': self.sector,
                'market_cap': self.market_cap,
                'turnover_rate': self.turnover_rate,
                'volume_ratio': self.volume_ratio,
            })
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LeadingStock":
        """从字典创建实例"""
        return cls(
            code=data.get('code', ''),
            name=data.get('name', ''),
            limit_up_days=data.get('limit_up_days', 1),
            sector=data.get('sector'),
            market_cap=data.get('market_cap'),
            turnover_rate=data.get('turnover_rate'),
            volume_ratio=data.get('volume_ratio'),
        )


@dataclass
class MarketData:
    """市场数据结构"""
    date: str = ""
    limit_up_count: int = 0
    limit_down_count: int = 0
    total_stocks: int = 5000
    leading_stocks: List[Dict[str, Any]] = field(default_factory=list)
    sector_data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self) -> None:
        """验证数据有效性"""
        if not self.date:
            self.date = datetime.now().strftime('%Y-%m-%d')
        
        # 数值验证
        for field_name, value in [
            ('limit_up_count', self.limit_up_count),
            ('limit_down_count', self.limit_down_count),
        ]:
            if not isinstance(value, int) or value < 0:
                raise ValidationError(f"{field_name} 必须是非负整数")
        
        if not isinstance(self.total_stocks, int) or self.total_stocks <= 0:
            raise ValidationError("total_stocks 必须是正整数")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'date': self.date,
            'limit_up_count': self.limit_up_count,
            'limit_down_count': self.limit_down_count,
            'total_stocks': self.total_stocks,
            'leading_stocks': self.leading_stocks,
            'sector_data': self.sector_data,
        }


# ==================== 自定义异常 ====================

class DragonJudgeError(Exception):
    """Dragon Judge 基础异常"""
    
    def __init__(self, message: str, code: Optional[str] = None) -> None:
        self.message = message
        self.code = code or "DRAGON_JUDGE_ERROR"
        super().__init__(self.message)


class InvalidDataError(DragonJudgeError):
    """数据无效异常"""
    
    def __init__(self, message: str) -> None:
        super().__init__(message, code="INVALID_DATA")


class ValidationError(DragonJudgeError):
    """数据验证异常"""
    
    def __init__(self, message: str) -> None:
        super().__init__(message, code="VALIDATION_ERROR")


class InvalidCycleError(DragonJudgeError):
    """无效周期异常"""
    
    def __init__(self, message: str) -> None:
        super().__init__(message, code="INVALID_CYCLE")


class ConfigurationError(DragonJudgeError):
    """配置错误异常"""
    
    def __init__(self, message: str) -> None:
        super().__init__(message, code="CONFIG_ERROR")


# ==================== 核心评分类 ====================

class DragonJudge:
    """
    Dragon Judge - 龙判官
    A股情绪周期判断与龙头选股系统
    
    五维评分体系:
    1. 高度分 (40%): 连板高度，最高辨识度
    2. 竞争分 (30%): 同身位竞争强度
    3. 板块分 (20%): 板块效应和梯队完整性
    4. 情绪分 (5%): 市场情绪共振
    5. 质量分 (5%): 涨停质量（封板时间、换手率等）
    """
    
    # 情绪周期阈值
    DEFAULT_THRESHOLDS: Dict[str, float] = {
        'ice_point': 20.0,
        'start': 35.0,
        'fermentation': 50.0,
        'climax': 70.0,
        'divergence': 85.0
    }
    
    # 五维评分权重
    DEFAULT_WEIGHTS: Dict[str, float] = {
        'height': 0.40,      # 连板高度
        'competition': 0.30, # 竞争度
        'sector': 0.20,      # 板块效应
        'sentiment': 0.05,   # 市场情绪
        'quality': 0.05      # 涨停质量
    }
    
    # 评分参数配置
    SCORING_PARAMS: Dict[str, Any] = {
        'height_max_days': 5,           # 高度满分天数
        'competition_penalty': 20,      # 每增加一个竞争对手扣分
        'sector_base_score': 60,        # 板块基础分
        'sector_bonus_per_follower': 5, # 每个跟风股加分
        'quality_high_board_bonus': 20, # 连板质量加分
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化 Dragon Judge
        
        Args:
            config: 配置字典，可覆盖默认权重和阈值
                - weights: 评分权重 Dict[str, float]
                - thresholds: 周期阈值 Dict[str, float]
                - scoring_params: 评分参数 Dict[str, Any]
                
        Raises:
            ConfigurationError: 配置无效时抛出
        """
        self.config = config or {}
        self.weights = self.config.get('weights') or self.DEFAULT_WEIGHTS.copy()
        self.thresholds = self.config.get('thresholds') or self.DEFAULT_THRESHOLDS.copy()
        self.scoring_params = self.config.get('scoring_params') or self.SCORING_PARAMS.copy()
        
        # 验证配置
        self._validate_config()
        
        logger.info("Dragon Judge 初始化完成")
    
    def _validate_config(self) -> None:
        """
        验证配置有效性
        
        Raises:
            ConfigurationError: 配置无效时抛出
        """
        # 验证权重
        required_weights = ['height', 'competition', 'sector', 'sentiment', 'quality']
        for weight_key in required_weights:
            if weight_key not in self.weights:
                raise ConfigurationError(f"缺少权重配置: {weight_key}")
            if not isinstance(self.weights[weight_key], (int, float)):
                raise ConfigurationError(f"权重 {weight_key} 必须是数字")
            if not 0 <= self.weights[weight_key] <= 1:
                raise ConfigurationError(f"权重 {weight_key} 必须在 0-1 之间")
        
        # 验证权重总和
        total_weight = sum(self.weights.values())
        if not 0.99 <= total_weight <= 1.01:
            logger.warning(f"权重总和为 {total_weight}，建议调整为1.0")
        
        # 验证阈值
        threshold_order = ['ice_point', 'start', 'fermentation', 'climax', 'divergence']
        for i, threshold_key in enumerate(threshold_order):
            if threshold_key not in self.thresholds:
                raise ConfigurationError(f"缺少阈值配置: {threshold_key}")
            if i > 0:
                prev_key = threshold_order[i - 1]
                if self.thresholds[threshold_key] <= self.thresholds[prev_key]:
                    raise ConfigurationError(
                        f"阈值 {threshold_key} 必须大于 {prev_key}"
                    )
    
    def validate_market_data(self, market_data: Union[Dict[str, Any], MarketData]) -> MarketData:
        """
        验证市场数据有效性
        
        Args:
            market_data: 市场数据字典或 MarketData 对象
            
        Returns:
            验证后的 MarketData 对象
            
        Raises:
            InvalidDataError: 数据无效时抛出
            ValidationError: 验证失败时抛出
        """
        # 检查必需字段
        if isinstance(market_data, dict):
            required_fields = ['limit_up_count', 'limit_down_count']
            for field in required_fields:
                if field not in market_data:
                    raise InvalidDataError(f"缺少必要字段: {field}")
                value = market_data[field]
                if not isinstance(value, (int, float)):
                    raise InvalidDataError(f"{field} 必须是数字类型")
                if value < 0:
                    raise InvalidDataError(f"{field} 不能为负数")
        
        try:
            if isinstance(market_data, MarketData):
                return market_data
            elif isinstance(market_data, dict):
                return MarketData(
                    date=market_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                    limit_up_count=market_data.get('limit_up_count', 0),
                    limit_down_count=market_data.get('limit_down_count', 0),
                    total_stocks=market_data.get('total_stocks', 5000),
                    leading_stocks=market_data.get('leading_stocks', []),
                    sector_data=market_data.get('sector_data'),
                )
            else:
                raise InvalidDataError(f"不支持的数据类型: {type(market_data)}")
        except ValidationError:
            raise
        except Exception as e:
            raise InvalidDataError(f"数据验证失败: {str(e)}")
    
    def calculate_sentiment(self, market_data: Union[Dict[str, Any], MarketData]) -> float:
        """
        计算市场情绪分数 (0-100)
        
        算法说明:
        1. 基础分数基于涨跌停比例差值
        2. 考虑市场总体涨停率
        3. 连板股票数量加权
        4. 结果限制在 0-100 范围
        
        Args:
            market_data: 市场数据
        
        Returns:
            情绪分数 (0-100)
            
        Raises:
            InvalidDataError: 数据无效时抛出
        """
        data = self.validate_market_data(market_data)
        
        limit_up = data.limit_up_count
        limit_down = data.limit_down_count
        total = data.total_stocks
        
        # 计算涨跌停比例
        up_ratio = (limit_up / total) * 100
        down_ratio = (limit_down / total) * 100
        
        # 基础分数：50为中性，涨跌停差值影响情绪
        # 使用非线性映射，使极端值影响更明显
        sentiment_diff = up_ratio - down_ratio
        base_score = 50.0 + sentiment_diff * 2
        
        # 涨停率额外加分（涨停率>5%时开始加分）
        up_rate = limit_up / total
        if up_rate > 0.05:
            base_score += (up_rate - 0.05) * 200
        
        # 连板加分（只计算前5只）
        high_board_stocks = [
            s for s in data.leading_stocks 
            if s.get('limit_up_days', 1) >= 2
        ][:5]
        
        if high_board_stocks:
            high_board_bonus = sum(
                min(s.get('limit_up_days', 1) * 1.5, 8) 
                for s in high_board_stocks
            ) / len(high_board_stocks)
            base_score += high_board_bonus
        
        # 跌停惩罚（跌停数>涨停数10%时）
        if limit_down > 0 and limit_up > 0:
            if limit_down > limit_up * 0.1:
                penalty = (limit_down / max(limit_up, 1)) * 10
                base_score -= penalty
        
        # 限制在0-100范围
        return max(0.0, min(100.0, base_score))
    
    def detect_cycle(self, market_data: Union[Dict[str, Any], MarketData]) -> MarketCycle:
        """
        判断当前市场周期
        
        Args:
            market_data: 市场数据
        
        Returns:
            MarketCycle 枚举值
            
        Raises:
            InvalidDataError: 数据无效时抛出
        """
        sentiment = self.calculate_sentiment(market_data)
        
        if sentiment < self.thresholds['ice_point']:
            return MarketCycle.ICE_POINT
        elif sentiment < self.thresholds['start']:
            return MarketCycle.START
        elif sentiment < self.thresholds['fermentation']:
            return MarketCycle.FERMENTATION
        elif sentiment < self.thresholds['climax']:
            return MarketCycle.CLIMAX
        else:
            return MarketCycle.DIVERGENCE
    
    def select_leaders(
        self, 
        market_data: Union[Dict[str, Any], MarketData],
        top_n: Optional[int] = None
    ) -> List[LeadingStock]:
        """
        选择龙头股票
        
        Args:
            market_data: 市场数据
            top_n: 返回前N个龙头，None表示返回全部
        
        Returns:
            龙头股票列表，按综合评分排序
            
        Raises:
            InvalidDataError: 数据无效时抛出
        """
        data = self.validate_market_data(market_data)
        
        if not data.leading_stocks:
            logger.warning("没有提供龙头股票数据")
            return []
        
        leaders: List[LeadingStock] = []
        
        for stock_data in data.leading_stocks:
            try:
                if not isinstance(stock_data, dict):
                    logger.warning(f"无效的股票数据格式: {stock_data}")
                    continue
                
                leader = LeadingStock.from_dict(stock_data)
                
                # 计算五维评分
                self._calculate_five_dimensions(leader, data)
                
                # 计算综合评分
                leader.score = self._calculate_total_score(leader)
                
                leaders.append(leader)
                
            except (ValidationError, InvalidDataError) as e:
                logger.warning(f"股票数据验证失败: {e.message}")
                continue
        
        # 按综合评分排序
        leaders.sort(key=lambda x: x.score, reverse=True)
        
        if top_n:
            return leaders[:top_n]
        return leaders
    
    def _calculate_total_score(self, leader: LeadingStock) -> float:
        """
        计算综合评分
        
        Args:
            leader: 龙头股票对象
            
        Returns:
            综合评分
        """
        score = (
            leader.height_score * self.weights['height'] +
            leader.competition_score * self.weights['competition'] +
            leader.sector_score * self.weights['sector'] +
            leader.sentiment_score * self.weights['sentiment'] +
            leader.quality_score * self.weights['quality']
        )
        return min(100.0, max(0.0, score))
    
    def _calculate_five_dimensions(
        self, 
        leader: LeadingStock, 
        market_data: MarketData
    ) -> None:
        """
        计算五维评分
        
        Args:
            leader: 龙头股票对象
            market_data: 市场数据
        """
        params = self.scoring_params
        
        # 1. 高度分：基于连板天数，非线性增长
        # 公式: min((天数/满分天数)^1.5 * 100, 100)
        height_ratio = leader.limit_up_days / params['height_max_days']
        leader.height_score = min(pow(height_ratio, 1.5) * 100, 100.0)
        
        # 2. 竞争分：基于同身位股票数量
        same_height = sum(
            1 for s in market_data.leading_stocks 
            if s.get('limit_up_days', 0) == leader.limit_up_days
        )
        # 竞争分 = 100 - (同身位数量-1) * 扣分
        penalty = (same_height - 1) * params['competition_penalty']
        leader.competition_score = max(0.0, 100.0 - penalty)
        
        # 3. 板块分：基于板块效应
        leader.sector_score = self._calculate_sector_score(leader, market_data)
        
        # 4. 情绪分：与市场情绪相关
        # 情绪>70时加分，情绪<30时减分
        sentiment = self.calculate_sentiment(market_data)
        leader.sentiment_score = min(100.0, sentiment * 1.1)
        
        # 5. 质量分：涨停质量
        leader.quality_score = self._calculate_quality_score(leader)
    
    def _calculate_sector_score(
        self, 
        leader: LeadingStock, 
        market_data: MarketData
    ) -> float:
        """
        计算板块得分
        
        Args:
            leader: 龙头股票
            market_data: 市场数据
            
        Returns:
            板块得分
        """
        params = self.scoring_params
        base_score = float(params['sector_base_score'])
        
        # 如果有板块数据
        if market_data.sector_data and leader.sector:
            sector_info = market_data.sector_data.get(leader.sector, {})
            follower_count = sector_info.get('follower_count', 0)
            sector_limit_up_count = sector_info.get('limit_up_count', 0)
            
            # 跟风股加分
            bonus = min(follower_count * params['sector_bonus_per_follower'], 30)
            
            # 板块涨停数量加分
            if sector_limit_up_count >= 5:
                bonus += 10
            
            return min(100.0, base_score + bonus)
        
        return base_score
    
    def _calculate_quality_score(self, leader: LeadingStock) -> float:
        """
        计算涨停质量分
        
        Args:
            leader: 龙头股票
            
        Returns:
            质量得分
        """
        params = self.scoring_params
        base_score = 50.0
        
        # 连板质量加分
        if leader.limit_up_days >= 2:
            base_score += params['quality_high_board_bonus']
        
        # 换手率评估（如果有数据）
        if leader.turnover_rate is not None:
            # 理想换手率 5-15%
            if 5 <= leader.turnover_rate <= 15:
                base_score += 15
            elif leader.turnover_rate > 25:
                base_score -= 10  # 过高换手，可能有出货风险
        
        # 量比评估（如果有数据）
        if leader.volume_ratio is not None:
            # 量比>2表示放量
            if leader.volume_ratio >= 2:
                base_score += 10
        
        return min(100.0, base_score)
    
    def generate_report(
        self, 
        market_data: Union[Dict[str, Any], MarketData],
        include_details: bool = False
    ) -> Dict[str, Any]:
        """
        生成完整分析报告
        
        Args:
            market_data: 市场数据
            include_details: 是否包含详细数据
        
        Returns:
            报告字典
            
        Raises:
            InvalidDataError: 数据无效时抛出
        """
        data = self.validate_market_data(market_data)
        
        sentiment = self.calculate_sentiment(data)
        cycle = self.detect_cycle(data)
        leaders = self.select_leaders(data, top_n=10)
        
        report: Dict[str, Any] = {
            'date': data.date,
            'sentiment_score': round(sentiment, 2),
            'market_cycle': cycle.cn_name,
            'market_cycle_en': cycle.en_name,
            'market_cycle_display': cycle.display_name,
            'leading_stocks': [l.to_dict(include_details=include_details) for l in leaders],
            'strategy': self._generate_strategy(sentiment, cycle),
            'market_summary': {
                'limit_up_count': data.limit_up_count,
                'limit_down_count': data.limit_down_count,
                'total_stocks': data.total_stocks,
                'up_ratio': round(data.limit_up_count / data.total_stocks * 100, 2),
                'down_ratio': round(data.limit_down_count / data.total_stocks * 100, 2),
            },
            'generated_at': datetime.now().isoformat(),
        }
        
        # 添加风险等级
        report['risk_level'] = self._calculate_risk_level(sentiment, cycle)
        
        return report
    
    def _generate_strategy(self, sentiment: float, cycle: MarketCycle) -> str:
        """
        生成交易策略建议
        
        Args:
            sentiment: 情绪分数
            cycle: 市场周期
        
        Returns:
            策略建议文本
        """
        strategies: Dict[MarketCycle, str] = {
            MarketCycle.ICE_POINT: "空仓观望，等待冰点转折信号",
            MarketCycle.START: "轻仓试错，关注首板机会",
            MarketCycle.FERMENTATION: "半仓参与，聚焦主线龙头",
            MarketCycle.CLIMAX: "高潮减仓，只留核心龙头",
            MarketCycle.DIVERGENCE: "全面撤退，规避退潮风险"
        }
        
        base_strategy = strategies.get(cycle, "观望为主，等待明确信号")
        
        # 根据情绪分数添加额外建议
        if sentiment > 90:
            base_strategy += " ⚠️ 情绪过热，注意风险"
        elif sentiment < 10:
            base_strategy += " 💡 极度冰点，关注反转机会"
        elif 30 <= sentiment <= 45 and cycle == MarketCycle.START:
            base_strategy += " 📈 可能是启动初期，积极布局"
        
        return base_strategy
    
    def _calculate_risk_level(
        self, 
        sentiment: float, 
        cycle: MarketCycle
    ) -> Dict[str, Any]:
        """
        计算风险等级
        
        Args:
            sentiment: 情绪分数
            cycle: 市场周期
            
        Returns:
            风险等级信息
        """
        risk_levels = {
            MarketCycle.ICE_POINT: {"level": "低风险", "score": 1, "color": "🟢"},
            MarketCycle.START: {"level": "中低风险", "score": 2, "color": "🟢"},
            MarketCycle.FERMENTATION: {"level": "中等风险", "score": 3, "color": "🟡"},
            MarketCycle.CLIMAX: {"level": "高风险", "score": 4, "color": "🔴"},
            MarketCycle.DIVERGENCE: {"level": "极高风险", "score": 5, "color": "🔴"},
        }
        
        risk = risk_levels.get(cycle, {"level": "未知", "score": 0, "color": "⚪"}).copy()
        
        # 根据情绪分数调整
        if sentiment > 95:
            risk['warning'] = "情绪极度亢奋，随时可能回调"
        elif sentiment < 5:
            risk['warning'] = "情绪极度低迷，等待企稳信号"
        
        return risk
    
    def get_cycle_transition_probability(
        self, 
        current_cycle: MarketCycle,
        sentiment_trend: str = "flat"
    ) -> Dict[str, float]:
        """
        获取周期转换概率
        
        Args:
            current_cycle: 当前周期
            sentiment_trend: 情绪趋势 (up/down/flat)
            
        Returns:
            各周期转换概率
        """
        # 基于当前周期和趋势计算转换概率
        transitions: Dict[MarketCycle, Dict[str, Dict[str, float]]] = {
            MarketCycle.ICE_POINT: {
                "up": {MarketCycle.ICE_POINT: 0.3, MarketCycle.START: 0.7},
                "flat": {MarketCycle.ICE_POINT: 0.8, MarketCycle.START: 0.2},
                "down": {MarketCycle.ICE_POINT: 0.9, MarketCycle.START: 0.1},
            },
            MarketCycle.START: {
                "up": {MarketCycle.START: 0.4, MarketCycle.FERMENTATION: 0.6},
                "flat": {MarketCycle.START: 0.7, MarketCycle.FERMENTATION: 0.2, MarketCycle.ICE_POINT: 0.1},
                "down": {MarketCycle.START: 0.5, MarketCycle.ICE_POINT: 0.5},
            },
            MarketCycle.FERMENTATION: {
                "up": {MarketCycle.FERMENTATION: 0.5, MarketCycle.CLIMAX: 0.5},
                "flat": {MarketCycle.FERMENTATION: 0.8, MarketCycle.CLIMAX: 0.1, MarketCycle.DIVERGENCE: 0.1},
                "down": {MarketCycle.FERMENTATION: 0.4, MarketCycle.DIVERGENCE: 0.6},
            },
            MarketCycle.CLIMAX: {
                "up": {MarketCycle.CLIMAX: 0.6, MarketCycle.DIVERGENCE: 0.4},
                "flat": {MarketCycle.CLIMAX: 0.5, MarketCycle.DIVERGENCE: 0.5},
                "down": {MarketCycle.DIVERGENCE: 0.8, MarketCycle.CLIMAX: 0.2},
            },
            MarketCycle.DIVERGENCE: {
                "up": {MarketCycle.DIVERGENCE: 0.3, MarketCycle.FERMENTATION: 0.5, MarketCycle.START: 0.2},
                "flat": {MarketCycle.DIVERGENCE: 0.6, MarketCycle.ICE_POINT: 0.3, MarketCycle.FERMENTATION: 0.1},
                "down": {MarketCycle.DIVERGENCE: 0.4, MarketCycle.ICE_POINT: 0.6},
            },
        }
        
        return transitions.get(current_cycle, {}).get(sentiment_trend, {current_cycle: 1.0})
