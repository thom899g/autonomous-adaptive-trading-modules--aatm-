"""
Configuration for Autonomous Adaptive Trading Modules (AATM)
Centralized configuration with type-safe settings and environment variable management
"""
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TradingMode(Enum):
    """Trading operation modes"""
    BACKTEST = "backtest"
    PAPER_TRADING = "paper"
    LIVE_TRADING = "live"
    SIMULATION = "simulation"

class AssetClass(Enum):
    """Supported asset classes"""
    CRYPTO = "crypto"
    STOCKS = "stocks"
    FOREX = "forex"
    FUTURES = "futures"

@dataclass
class MarketConfig:
    """Market-specific configuration"""
    exchange: str = "binance"
    symbol: str = "BTC/USDT"
    timeframe: str = "1h"
    asset_class: AssetClass = AssetClass.CRYPTO
    max_historical_candles: int = 1000
    realtime_update_interval: int = 60  # seconds

@dataclass
class StrategyConfig:
    """Strategy evolution configuration"""
    initial_population_size: int = 10
    evolution_interval_hours: int = 24
    performance_window_days: int = 30
    mutation_rate: float = 0.1
    crossover_rate: float = 0.7
    elitism_count: int = 2
    max_strategy_complexity: int = 50

@dataclass
class RiskConfig:
    """Risk management configuration"""
    max_position_size_pct: float = 2.0
    max_portfolio_risk_pct: float = 5.0
    stop_loss_pct: float = 2.0
    take_profit_pct: float = 4.0
    max_daily_loss_pct: float = 3.0
    max_concurrent_trades: int = 5

@dataclass
class FirebaseConfig:
    """Firebase configuration for state management"""
    project_id: str = field(default_factory=lambda: os.getenv("FIREBASE_PROJECT_ID", ""))
    credentials_path: str = field(default_factory=lambda: os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase_credentials.json"))
    collection_strategies: str = "aatm_strategies"
    collection_performance: str = "aatm_performance"
    collection_market_state: str = "aatm_market_state"
    collection_trade_logs: str = "aatm_trade_logs"

@dataclass
class AATMConfig:
    """Main AATM configuration container"""
    # Core settings
    trading_mode: TradingMode = TradingMode.PAPER_TRADING
    module_name: str = "aatm_v1"
    log_level: str = "INFO"
    
    # Sub-configurations
    market: MarketConfig = field(default_factory=MarketConfig)
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    firebase: FirebaseConfig = field(default_factory=FirebaseConfig)
    
    # Feature flags
    enable_auto_evolution: bool = True
    enable_telegram_alerts: bool = True
    enable_performance_tracking: bool = True
    enable_market_regime_detection: bool = True
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.firebase.project_id:
            logging.error("Firebase project ID not configured")
            return False
            
        if self.risk.max_position_size_pct > 10:
            logging.warning("Position size exceeds recommended maximum")
            
        return True

# Global configuration instance
config = AATMConfig()

# Configure logging
def setup_logging(level: str = "INFO"):
    """Configure logging with consistent format"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger('ccxt').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

# Initialize logging
logger = setup_logging(config.log_level)