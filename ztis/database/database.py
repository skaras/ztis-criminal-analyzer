from os.path import dirname, abspath
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, Company

MAIN_DIRECTORY = dirname(abspath(__file__))


class Database:
    DATABASE_FILE = 'criminals.db'

    engine = None
    session = None
    session_instance = None
    
    
    def __init__(self):
        self.engine = create_engine('sqlite:///%s/%s' % (MAIN_DIRECTORY, self.DATABASE_FILE), echo=True)
        self.session = sessionmaker(bind=self.engine)
        self.session.configure(bind=self.engine)
        self.session_instance = self.session()
    
    
    def create(self):
        Base.metadata.create_all(self.engine)
    
    
    def clear(self):
        con = self.engine.connect()
        
        trans = con.begin()
        for table in reversed(Base.metadata.sorted_tables):
            con.execute(table.delete())
        trans.commit()
    
    
    def destroy(self):
        Base.metadata.drop_all(self.engine)
    
    
    def save(self, obj):
        self.session_instance.add(obj)
        self.session_instance.commit()
    
    def save_all(self, obj_list):
        self.session_instance.add_all(obj_list)
        self.session_instance.commit()
    
    
    def get_session(self):
        return self.session_instance

"""
database = Database()
database.create()
database.destroy()
"""
