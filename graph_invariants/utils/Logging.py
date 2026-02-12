import os
import logging

def setup_logger(folder: str, filename: str = "!counter.log",
                 level: int = logging.INFO, to_console: bool = True) -> logging.Logger:
    """
    Create a simple logger that writes directly to <folder>/<filename>

    Args:
        folder (str): Directory where the log file will be created.
        filename (str): Log file name (default: 'counter.log').
        level (int): Logging level (default: logging.INFO).
        to_console (bool): If True, also print logs to stdout.

    Returns:
        logging.Logger: Configured logger instance.
    """
    os.makedirs(folder, exist_ok=True)  # ensure the folder exists
    log_path = os.path.join(folder, filename)

    logger = logging.getLogger("main_logger")
    logger.setLevel(level)

    # Avoid duplicate handlers if already configured
    if not logger.handlers:
        fmt = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s",
                                datefmt="%Y-%m-%d %H:%M:%S")

        # File handler → <folder>/<filename>
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setFormatter(fmt)
        fh.setLevel(level)
        logger.addHandler(fh)

        # Optional console handler
        if to_console:
            ch = logging.StreamHandler()
            ch.setFormatter(fmt)
            ch.setLevel(level)
            logger.addHandler(ch)

        logger.propagate = False
        logger.info(f"Logger initialized at {log_path}")

    return logger
