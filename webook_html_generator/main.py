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

    generator = Generator(config)
    scheduler = BlockingScheduler(daemon=True)

    minutes = int(config.scheduler_interval_in_min)
    seconds = int(config.scheduler_interval_in_sec)
    start_date = '2022-03-14 09:55:00'
    scheduler.add_job(generator.handler, 'interval', minutes=minutes,
                      seconds=seconds, start_date=start_date)
    scheduler.start()



