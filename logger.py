import logging
from logging import Formatter, StreamHandler


class ColoredFormatter(Formatter):
    def format(self, record):
        message = record.getMessage()
        mapping = {
            'INFO': (36, "[*] "),  # cyan
            'WARNING': (33, "[-] "),  # yellow
            'ERROR': (31, "[!] "),  # red
            'SUCCESS': (32, "[+] ")  # green
        }

        # Default to white
        color, prefix = mapping.get(record.levelname, (37, ""))
        return f"\033[{color}m{prefix}{message}\033[0m"


log = logging.getLogger(__name__)
handler = StreamHandler()
formatter = ColoredFormatter()
handler.setFormatter(formatter)
log.addHandler(handler)

# Add success level
logging.SUCCESS = 25
logging.addLevelName(logging.SUCCESS, 'SUCCESS')
setattr(log, 'success', lambda message, *args: log._log(logging.SUCCESS, message, args))

log.setLevel(logging.INFO)
