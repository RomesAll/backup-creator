from pathlib import Path
import sys
import fire
sys.path.insert(0, (str(Path(__file__).parent.parent.resolve())))
from presentation.cli.client import CliClient
import src.logging_conf

if __name__ == '__main__':
    fire.Fire(CliClient)