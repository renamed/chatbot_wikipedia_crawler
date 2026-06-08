from datetime import datetime
import logging
from logging.handlers import MemoryHandler
import os



def setup_logging() -> logging.Logger:
    """Configures logging to output to both console and a timestamped file."""

    logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
    logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

    current_date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    log_filename = f"run_{current_date}.log"

    os.makedirs("logs", exist_ok=True)
    log_path = os.path.join("logs", log_filename)

    logger = logging.getLogger("chatbot_wikipedia_crawler")
    logger.setLevel(logging.INFO)

    log_format = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # File Handler
    file_handler = logging.FileHandler(
        log_path, 
        encoding ="utf-8",
        delay = True
    )

    buffered_handler = MemoryHandler(
        capacity=100,
        flushLevel=logging.INFO,
        target=file_handler
    )
    buffered_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_format)
    logger.addHandler(buffered_handler)

    return logger