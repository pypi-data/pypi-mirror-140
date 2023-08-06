from .read import read_config
from .write import write_config

conf_dict = read_config()
conf_path = conf_dict['conf_path']
