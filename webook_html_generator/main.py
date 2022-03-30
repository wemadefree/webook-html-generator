from dotenv import load_dotenv
from pathlib import Path
from webook_html_generator.config import Config
from webook_html_generator.generator import Generator
from apscheduler.schedulers.background import BlockingScheduler


def load_config() -> Config:
    dotenv_path = Path('../.env')
    load_dotenv(dotenv_path=dotenv_path)
    return Config()


if __name__ == '__main__':
    config: Config = load_config()
    if not config:
        raise ValueError("Cannot generate config file")
        exit(1)

    html_generator = Generator(config)
    scheduler = BlockingScheduler(daemon=True)
    scheduler.add_job(html_generator.make_templates, 'interval', seconds=int(config.scheduler_interval), start_date='2022-03-14 09:55:00')
    scheduler.start()



