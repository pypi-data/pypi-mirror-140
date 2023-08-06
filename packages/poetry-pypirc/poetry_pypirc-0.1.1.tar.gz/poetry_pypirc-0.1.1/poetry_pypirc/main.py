from configparser import ConfigParser
from pathlib import Path
import sys
import sh

PYPIRC_FILE = Path.home() / ".pypirc"


def main():
    parser = ConfigParser()
    filename = sys.argv[1] if len(sys.argv) > 1 else PYPIRC_FILE
    parser.read(filename)
    pypirc = parser._sections

    index_servers = (pypirc.get("distutils") or {}).get('index-servers') or ""
    index_servers = index_servers.split()
    if not index_servers:
        return

    for server in index_servers:
        print(server)
        server_config = pypirc.get(server) or {}
        if server_config.get("repository"):
            print(f"  Setting repositories.{server}.url")
            sh.poetry.config(
                f"repositories.{server}", server_config["repository"])

        if server_config.get("username") and server_config.get("password"):
            print(f"  Setting repositories.{server} auth")
            sh.poetry.config(
                f"http-basic.{index_servers}", server_config.get("username"), server_config.get("password"))


if __name__ == '__main__':
    main()
