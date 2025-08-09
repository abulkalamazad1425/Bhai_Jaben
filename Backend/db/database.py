from zope.interface import Interface, implementer
import supabase

class Database(Interface):
    def create_database(self, database_url, database_key):
        pass
    def get_client(self):
        pass