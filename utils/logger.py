"""
Logging Configuration

This module provides centralized logging for the web automation framework.
Implements dual logging (console + file) with proper formatting.

Author: Senior SDET
Date: 2026-01-02
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from config.settings import settings


class Logger:
    """
    Centralized logger for the framework.
    
    Provides dual logging:
    - Console: INFO level with colored output
    - File: DEBUG level with detailed information
    """
    
    _instance: Optional[logging.Logger] = None
    
    @classmethod
    def get_logger(cls, name: str = "framework") -> logging.Logger:
        """
        Get or create logger instance.
        
        Args:
            name: Logger name (default: "framework")
            
        Returns:
            Configured logger instance
            
        Example:
            >>> logger = Logger.get_logger(__name__)
            >>> logger.info("Test started")
        """
        if cls._instance is None:
            cls._instance = cls._setup_logger(name)
        return cls._instance
    
    @classmethod
    def _setup_logger(cls, name: str) -> logging.Logger:
        """
        Set up logger with console and file handlers.
        
        Args:
            name: Logger name
            
        Returns:
            Configured logger
        """
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        logger.handlers.clear()
        
        # Console handler (INFO level)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            fmt='%(asctime)s [%(levelname)8s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # File handler (DEBUG level)
        log_dir = Path(settings.LOGS_DIR)
        log_dir.mkdir(exist_ok=True)
        
        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"test_run_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            fmt='%(asctime)s [%(levelname)8s] [%(filename)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        logger.info(f"Logger initialized. Log file: {log_file}")
        
        return logger
    
    @classmethod
    def cleanup_old_logs(cls, keep_count: int = 5) -> None:
        """
        Clean up old log files, keeping only the most recent ones.
        
        Args:
            keep_count: Number of recent log files to keep (default: 5)
            
        Example:
            >>> Logger.cleanup_old_logs(keep_count=5)
        """
        log_dir = Path(settings.LOGS_DIR)
        if not log_dir.exists():
            return
        
        # Get all log files sorted by modification time
        log_files = sorted(
            log_dir.glob("test_run_*.log"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        # Delete old log files
        for old_log in log_files[keep_count:]:
            try:
                old_log.unlink()
                print(f"Deleted old log file: {old_log.name}")
            except Exception as e:
                print(f"Failed to delete {old_log.name}: {e}")


# Export logger instance
logger = Logger.get_logger()
