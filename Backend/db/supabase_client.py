import supabase
from zope.interface import Interface, implementer
from db.database import Database


@implementer(Database)
class Supabase():
    def __init__(self, database_url, database_key):
        self.__database_client=self.__create_database(database_url, database_key)

    def __create_database(self, database_url, database_key):
        return supabase.create_client(database_url, database_key)

    def get_client(self):
        return self.__database_client