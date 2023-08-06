from os import get_terminal_size
from pathlib import Path
from typing import Optional

import click
import uvicorn  # type:ignore

from . import __file__ as root_file
from . import __version__
from .utils.config import CONFIG_DIR, DEBUG, Config
from .utils.log import LOG_LEVEL, logger

COPYRIGHT = r"""<b><g>
  _    _ _ _     _          _____ _____  
 | |  | (_) |   (_)   /\   |  __ \_   _| 
 | |__| |_| |__  _   /  \  | |__) || |   
 |  __  | | '_ \| | / /\ \ |  ___/ | |   
 | |  | | | |_) | |/ ____ \| |    _| |_  
 |_|  |_|_|_.__/|_/_/    \_\_|   |_____| 
</g><e>
A program that implements easy-to-use APIs for a variety of commonly used sites
Repository: https://github.com/mixmoe/HibiAPI
</e></b>"""  # noqa:W291,W293


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "default": {
            "class": "hibiapi.utils.log.LoguruHandler",
        },
    },
    "loggers": {
        "uvicorn.error": {
            "handlers": ["default"],
            "level": LOG_LEVEL,
        },
        "uvicorn.access": {
            "handlers": ["default"],
            "level": LOG_LEVEL,
        },
    },
}

try:
    width, height = get_terminal_size()
except OSError:
    width, height = 0, 0


@click.command(name="HibiAPI")
@click.option(
    "--host",
    "-h",
    default=Config["server"]["host"].as_str(),
    help="listened server address",
    show_default=True,
)
@click.option(
    "--port",
    "-p",
    default=Config["server"]["port"].as_number(),
    help="listened server port",
    show_default=True,
)
@click.option(
    "--workers", "-w", default=1, help="amount of server workers", show_default=True
)
@click.option(
    "--reload",
    "-r",
    default=DEBUG,
    help="automatic reload while file changes",
    show_default=True,
    is_flag=True,
)
def main(host: str, port: int, workers: int, reload: bool):
    logger.warning(
        "\n".join(i.center(width) for i in COPYRIGHT.splitlines()),
    )
    logger.info(f"HibiAPI version: <g><b>{__version__}</b></g>")
    logger.info(
        "Server is running under <b>%s</b> mode!"
        % ("<r>debug</r>" if DEBUG else "<g>production</g>")
    )
    uvicorn.run(
        "hibiapi.app:app",
        host=host,
        port=port,
        debug=DEBUG,
        access_log=False,
        log_config=LOG_CONFIG,
        workers=workers,
        reload=reload,
        reload_dirs=[Path(root_file).parent, CONFIG_DIR],
        forwarded_allow_ips=Config["server"]["allowed-forward"].get(
            Optional[str]  # type:ignore
        ),
    )


if __name__ == "__main__":
    main()
