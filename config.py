from pathlib import Path

class Config:
    """
    This is the configuration reader for the program
    We need this to be able to be overridden via command line in the future
    """
    def __init__(self, config_file):
        path = Path(config_file)
        if path.is_file():
            with open(config_file,'r') as data:
                    lines = data.readlines()
            for line in lines:
                [key,value] = line.strip().split('=')
                if key.strip() == "url":
                    self.url = value
                elif key.strip() == "access key":
                    self.access_key = value
                elif key.strip() == "default icao":
                    self.icao = value
        else:
            raise IOError("File {} does not exist or is not a regular file".format(config_file))
        if self.url == None or self.access_key == None or self.icao == None:
            raise ValueError("Config file missing essential element")

    def get_url(self):
        return self.url

    def get_access_key(self):
        return self.access_key

    def get_icao(self):
        return self.icao
