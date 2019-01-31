'''This module will check if a job is valid against a set of criteria'''

import logging


class Valid:
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('Valid')
        config = kwargs['config']
        try:
            self.unit_types = list()
            for unit_type in kwargs['unit_types']:
                if unit_type in config.get_valid_unit_types():
                    self.unit_types.append(unit_type)
                    self._logger.debug(f'Appended {unit_type} to allowed unit types')
                else:
                    self._logger.error(f'Someone has used wrong unit type {unit_type}')
        except KeyError as e:
            self._logger.error(f"Someone tried to use the wrong keyword {kwargs}")
            raise KeyError(e)

    def __str__(self):
        return f'''Valid criteria
Unit Types {self.unit_types}'''

    def check_validity(self, job):
        '''
        This checks to see if a jbo is valid
        :param job: this is a job class, it will be used to check the criteria
        :return: Boolean if it is valid or not.
        '''


if __name__ == '__main__':
    from config import Config

    default_config = Config('config')

    try:
        test_valid_class = Valid(config=default_config, unit_types='p')
        print(test_valid_class)
        test_valid_class1 = Valid(destination='lbbj')
    except KeyError as e:
        print("Test false as expected")
    else:
        print(test_valid_class)
