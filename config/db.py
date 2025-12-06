# Your MySQL/Postgres connection (Singleton)

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            # Initialize connection here
        return cls._instance

    def get_connection(self):
        # Return the database connection
        pass

