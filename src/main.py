from pathlib import Path
import fire, sys
from src.business.backup_creator import create_backup_worker_processes, BackUpCreator
from src.config import config
from src.data import MongoAdapter
from src.data.database import MongoManager

sys.path.insert(0, (str(Path(__file__).parent.parent.resolve())))

if __name__ == '__main__':
    create_backup_worker_processes('/home/roman/target')
    # repo = MongoAdapter(MongoManager(config.mongodb.url))
    # backup_creator: BackUpCreator = BackUpCreator(
    #     source=Path('/home/roman/target'),
    #     repository=repo,
    # )
    # for item in BackUpCreator.scan_folders(Path('/home/roman/target')):
    #     backup_creator.create(item)
    #

    # repo = MongoAdapter(mongo_manager.get_database())
    # BackUpCreator(
    #     source='/home/roman/target',
    #     repository=repo
    # ).create_backup()
    # # fire.Fire(CliClient)