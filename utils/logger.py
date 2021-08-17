import logging


class Logger:
    def __init__(self, level=logging.INFO) -> None:
        self.logger = logging.getLogger("suricata-misp")
        self.level = level
        self.formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.ch = logging.StreamHandler()
        self.ch.setLevel(level)
        self.ch.setFormatter(self.formatter)
        self.logger.addHandler(self.ch)

    def log(self, message, level=logging.INFO):
        self.logger.log(level, message)
