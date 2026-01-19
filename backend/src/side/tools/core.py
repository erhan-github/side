"""
Core utilities and singletons for Side tools.

This module provides shared state and utility functions used across all tools.
Single source of truth for auto-intelligence, database, and market analyzer.
"""

from side.intel.auto_intelligence import AutoIntelligence
from side.intel.market import MarketAnalyzer
from side.storage.simple_db import SimplifiedDatabase

# Global singletons - initialized lazily
_auto_intel: AutoIntelligence | None = None
_database: SimplifiedDatabase | None = None
_market: MarketAnalyzer | None = None


def get_auto_intel() -> AutoIntelligence:
    """Get or create auto-intelligence singleton."""
    global _auto_intel
    if _auto_intel is None:
        _auto_intel = AutoIntelligence()
    return _auto_intel


def get_database() -> SimplifiedDatabase:
    """Get or create database singleton."""
    global _database
    if _database is None:
        _database = SimplifiedDatabase()
    return _database


def get_market() -> MarketAnalyzer:
    """Get or create market analyzer singleton."""
    global _market
    if _market is None:
        _market = MarketAnalyzer()
    return _market
