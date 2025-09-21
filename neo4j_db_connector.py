from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

class Neo4jConnection:

    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
            self.__driver.verify_connectivity() # Проверка соединения при инициализации
        except Exception as e:
            print(f"Failed to create the driver: {e}")
            # ИЗМЕНЕНО: Пробрасываем исключение наверх
            raise e

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, db=None):
        if self.__driver is None:
            raise Exception("Driver not initialized!")
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query))
        except ServiceUnavailable as e:
            print(f"Query failed due to DB connection issue: {e}")
            # ИЗМЕНЕНО: Пробрасываем исключение, чтобы Streamlit мог его поймать
            raise e
        except Exception as e:
            print(f"Query failed: {e}")
            # ИЗМЕНЕНО: Пробрасываем исключение
            raise e
        finally:
            if session is not None:
                session.close()
        return response