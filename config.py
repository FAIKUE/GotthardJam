import yaml


class Config:
    """Helper Class to get values out of yaml config files."""
    def __init__(self, path):
        self.path = path

    def get_value(self, key):
        with open(self.path, "r") as yaml_file:
            config = yaml.safe_load(yaml_file)
            return config[key]