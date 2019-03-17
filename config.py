from pathlib import Path
import configparser


class Config:
    """
    This is the configuration reader for the program
    We need this to be able to be overridden via command line in the future
    """
    # TODO this class should be the single source of truth for default data. Alter this to change data after __init__
    def __init__(self, config_file):
        path = Path(config_file)
        if path.is_file():
            config = configparser.ConfigParser()
            config.read_file(open(path))
            self.url = config['SERVER']['url']
            self.access_key = config['SERVER']['accesskey']
            self.icao = config['DEFAULTS']['icao']
            self.icao_destination = config['DEFAULTS']['icao_destination']
            self.valid_unit_types = config['VALIDITY']['unit_types']
        else:
            raise IOError("File {} does not exist or is not a regular file".format(config_file))
        if not self.url or not self.access_key or not self.icao:
            raise ValueError("Config file missing essential element")

    def get_url(self):
        return self.url

    def get_access_key(self):
        return self.access_key

    def get_icao(self):
        return self.icao

    def get_icao_destination(self):
        return self.icao_destination

    def get_valid_unit_types(self):
        return self.valid_unit_types
