import sys


sys.path.append("../EVAtool")


def test_config():
    from evatool.utils.config import Config

    config = Config(configfile="/home/xiegy/github/EVAtool/refs/reference_config.json")
    print(config.config)


test_config()
