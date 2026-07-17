from pathlib import Path
import fire, sys
sys.path.insert(0, (str(Path(__file__).parent.parent.resolve())))
print(sys.path)
from src.presentation.cli.client import CliClient

if __name__ == '__main__':
    fire.Fire(CliClient)