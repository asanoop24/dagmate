import os

from dagger.core import Dagger
from dagger.utils import load_yaml

config_dir = os.environ["CONFDIR"]
# config_file = "./conf/config.yml"

config = {}
for f in os.listdir(config_dir):
    config = load_yaml(os.path.join(config_dir, f))

_dagger = Dagger(config=config)
_dagger.activate()
