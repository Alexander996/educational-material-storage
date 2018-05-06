class CurrentDBConnection(object):
    db = None

    @classmethod
    def set_db_connection(cls, db):
        cls.db = db

    @classmethod
    def get_db_connection(cls):
        return cls.db
