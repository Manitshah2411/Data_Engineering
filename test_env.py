def test_env():
    from src.config import (
        DB_USER, DB_NAME, DB_HOST, DB_PASSWORD, DB_PORT, DATABASE_URL
    )


    print("DB_USER :",DB_USER)
    print("DB_NAME :",DB_NAME)
    print("DB_HOST :",DB_HOST)
    print("DB_PASSWORD :",DB_PASSWORD)
    print("DB_PORT :",DB_PORT)
    print("URL :",DATABASE_URL)

if __name__ == "__main__":
    test_env()