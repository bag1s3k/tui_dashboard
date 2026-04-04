import logging
from rich.logging import RichHandler

def logging_setup():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="[dark_red]{name}[/] {message}",
        datefmt="%H:%M:%S",
        style="{"
    )

    handler = RichHandler(
        level=logging.DEBUG,
        rich_tracebacks=True,
        omit_repeated_times=False,
        markup=True
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)