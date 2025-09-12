import logging
import logging.handlers
import json
import datetime


def format_json(record):
    """Format log record as simplified JSON string"""
    log_entry = {
        "time": datetime.datetime.fromtimestamp(record.created).isoformat(),
        "logger": record.name,
        "level": record.levelname,
        "message": record.getMessage(),
        "line": record.lineno,
    }
    if record.exc_info:
        log_entry["exception"] = logging._defaultFormatter.formatException(
            record.exc_info
        )
    return json.dumps(log_entry)


def initialize_logger(log_destination='application.log', logger_name='application_log', console=False, backup_count=1, log_size_mb=2):
    
    logger = logging.getLogger(logger_name)
    if logger.hasHandlers():
        return logger
    
    """Setup logging with simplified JSON format and file rotation"""
    formatter = logging.Formatter()
    formatter.format = format_json

    file_handler = logging.handlers.RotatingFileHandler(
        f"./logs/{log_destination}",
        maxBytes=log_size_mb * 1024 * 1024,
        backupCount=backup_count
    )
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    if console:
      console_handler = logging.StreamHandler()
      console_handler.setFormatter(formatter)
      logger.addHandler(console_handler)

    return logger
