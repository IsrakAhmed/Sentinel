import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler

def setup_logger():
    """Set up application logging"""
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Set up root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    console_handler.setFormatter(console_format)
    
    # Create file handler
    log_file = f"logs/sentinel_{time.strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s')
    file_handler.setFormatter(file_format)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Log startup message
    logger.info("Sentinel application starting")
    
    return logger