import optparse
import uvicorn

from configs.local import local_config
from configs.prod import prod_config
from configs.stage import stage_config
from src import create_fastapi_app


CONFIG_LOOKUP = {
    "local": local_config,
    "stage": stage_config,
    "prod": prod_config,
}


def config_settings(options):
    config = CONFIG_LOOKUP[options.config]
    config.update({"run_migrations": True if options.migrate in ["true", "True"] else False})
    return config


parser = optparse.OptionParser()
parser.add_option("--config", default="local", help="which config to load")
parser.add_option("--migrate", default=True, help="migrate models to db on startup")
options, args = parser.parse_args()

settings = config_settings(options)

app = create_fastapi_app(settings)

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings["host"], port=settings["port"], workers=settings["worker_count"])
