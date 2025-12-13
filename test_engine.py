from src.db_engine import get_engine
from sqlalchemy import text

def test_engine():
    print("Creating Engine...")
    
    engine = get_engine(echo=False) # engine object assigned 
    print("Engine created successfully!!!\n")
    
    print("Testing connection...")
    with engine.connect() as conn: # with as is used bcoz it closes the connection automatically after use preventing leaking
        result = conn.execute(text("SELECT 1")) # Text is used so that the script is readable by the sqlalchemy
        print("Connection successful!!! Result :", result.scalar()) # scalar is used to get the single row from single row 
        # query, it is used only in testing not in real world
        print()
    print("Testing done!!!")    
    
if __name__ == "__main__":
    test_engine()    