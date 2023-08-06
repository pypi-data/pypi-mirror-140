"""Persistence

:date: Mar 7, 2021
:author: Aldo Diaz, Marcelo Sureda

Persistence is the component responsible for objects and configuration storage
and retrieval.
"""

from os import environ, mkdir, path
from vcdextension.libraries import constants
from vcdextension.libraries.logger import Logger
from yaml import safe_load
import pickledb


class Persistence:
    """
    Persistence Class
    This is the component responsible for objects and configuration storage
    and retrieval. Is a Pythonic implementation of the Singleton pattern.
    """

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Persistence, cls).__new__(cls)
            # Initialization code
            cls.__instance.__config = cls.__load_config()
            cls.__instance.__db = cls.__init_db()
        return cls.__instance

    @classmethod
    def __load_config(cls):
        """
        Load configuration from file

        :return: Dict object with configuration keys
        """
        log = Logger()
        config = None
        try:
            config_file = constants.DEFAULT_CONFIG_FILE
            if constants.ENV_VAR_CONFIG_FILE in environ:
                config_file = environ[constants.ENV_VAR_CONFIG_FILE]
            with open(config_file, 'r') as f:
                config = safe_load(f)
        except Exception as e:
            log.error(f"<<{type(e).__qualname__}>>: {e}")
        return config

    def get_config(self):
        """
        Returns the configuration object.

        :return: Dict object with configuration keys
        """
        return self.__config

    @classmethod
    def __init_db(cls):
        """
        Returns database object.

        :return: PickleDB object
        """
        try:
            database_file = cls.__instance.__config['vcdextension']['db_file']
        except KeyError:
            database_file = constants.DEFAULT_DB_FILE
        database_dir = path.dirname(database_file)
        if not path.isdir(database_dir):
            mkdir(database_dir)
        return pickledb.load(database_file, auto_dump=False)

    def save(self, key, value):
        """
        Save key with value to the database.

        :param str key: Element key
        :param value: Object value
        :return: True if key successfully added to database
        """
        return self.__db.set(key, value)

    def load(self, key):
        """
        Returns the corresponding value for the key

        :param str key: Object key
        :return: False if key error
        """
        return self.__db.get(key)

    def remove(self, key):
        """
        Deletes the key from the database

        :param str key: Object key
        :return: False if key error, True if success
        """
        return self.__db.rem(key)

    def save_db_file(self):
        """
        Save database file to disk

        :return: True if database successfully saved
        """
        return self.__db.dump()

    def reload_db_file(self):
        """
        Load database file from disk

        :return: True if database successfully loaded
        """
        return self.__db.load(self.__db.loco, False)
