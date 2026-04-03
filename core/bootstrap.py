def initialize() -> None:
    """
    Initialization steps:
     1. Set rich tracebacks
     2. Set logging
    """
    from rich.traceback import install
    install()

    from utils.log import logging_setup
    logging_setup()