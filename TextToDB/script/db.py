import psycopg2
# TODO: Consider whether postgresql is really necessary or if we can manage with sqlite

### BEGIN DATABASE DEF ###

class DB():
    def __init__(self,
                 schema_path: str,
                 cfg_path: str,
                 db_path: str,
                 ):
        
        self.schema_path = schema_path

        with open(schema_path) as _f:
            self.schema = _f.read()

        self.connection = psycopg2.connect(
            # TODO: Use cfg file to load this information
            # Should include an example file only
            # Consider how to safely store password info
            database = "charterdb"
        )
        # Set autocommit to True to allow creating DB
        self.connection.autocommit = True

        self.cursor = self.connection.cursor()

        print("Finished initialising database")

    def create_database(self):
        print("Creating tables from schema " + str(self.schema_path))
        self.cursor.execute(self.schema)
        print("Schema query executed successfully")
        

    def clear_database(self):
        print("Dropping and recreating public schema")
        query = """--sql
        DROP SCHEMA public CASCADE;
        CREATE SCHEMA public;
        GRANT ALL ON SCHEMA public TO postgres;
        GRANT ALL ON SCHEMA public TO public;
        COMMENT ON SCHEMA public IS 'standard public schema';
        """
        self.cursor.execute(query)
        print("Schema public successfully re-created")
    
### END DATABASE DEF ###

### BEGIN CHARTERTEXT CLASS DEF ###
### Move this out of the main.py file ###

