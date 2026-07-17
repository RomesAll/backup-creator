from pathlib import Path
import fire, sys
sys.path.insert(0, (str(Path(__file__).parent.parent.resolve())))
from src.presentation.cli.client import CliClient
import logging_conf

if __name__ == '__main__':
    fire.Fire(CliClient)