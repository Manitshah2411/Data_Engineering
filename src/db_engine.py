from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from src.config import DATABASE_URL

def get_engine(echo: bool = False):
    """
    This method creates an engine object of sqlalchemy 
    
    Params:
    echo (bool) -> This is for logger like it will print all the SQL statements.
    Here default is False for clean output, and only True for testing.
    
    Returns:
    It returns a sqlalchemy.engine.Engine : A database that is ready to connect
    """
    
    url = make_url(DATABASE_URL) # It converts the DATABASE_URL into an object that is usable by the sqlalchemy
    
    
    engine = create_engine(
        url, # The url which is converted
        
        pool_size=5,
    # pool_size: its the maximum connection the engine can make, you can't just set numbers massive bcoz more the
    # pool size more the chances to crash and slowing down the system. It's like waiters being ready to serve the customers
    # once they serve, they are ready to serve again.
    
        max_overflow=10,
    # These are the temporary waiters who are ready to serve but are not as skilled as the full time waiters and 
    # they are only called when the fulltime waiters are not free.
    # They are sent back once they serve
    
        echo=echo # Default is true so no logging until set True
    )
    
    return engine


        