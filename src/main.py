from pathlib import Path
import sys
import fire
sys.path.insert(0, (str(Path(__file__).parent.parent.resolve())))
from presentation.cli.client import CliClient
if __name__ == '__main__':
    fire.Fire(CliClient)