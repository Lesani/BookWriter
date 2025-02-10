# utils.py

import logging
from colorama import init, Fore, Style

# Initialize Colorama
init(autoreset=True)

def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format=f"{Fore.GREEN}%(asctime)s{Style.RESET_ALL} - %(name)s - %(levelname)s - %(message)s"
    )
