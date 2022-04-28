import logging


def get_logger(level: str):

    logger = logging.getLogger("suricata-misp")
    level_log = logging.getLevelName(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(level_log)

    return logger
