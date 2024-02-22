#!/usr/bin/env python3
# this module is a middleware for pydantic. 
# It creates all the classes for a set of existing tables, read from a sqllite database.
# The database is read and the tables are created as pydantic models.
# The models are then used to create a FastAPI application.
# The application is then run as a uvicorn server.
# The server is then run on a specified port.
import sqlite3
import sys
from pydantic import BaseModel

# This function reads the database and returns a list of tables.
def read_db():
    conn = sqlite3.connect('/home/ben/dbschema/lite1l.sqlite')
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    conn.close()
    return tables

# This function reads the database and returns a list of columns for a given table.
def read_columns(table):
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    c.execute(f"PRAGMA table_info({table})")
    columns = c.fetchall()
    conn.close()
    return columns

# This function takes a list and creates the pydantic model.
def create_model(table, columns):
    model = f"class {table}(BaseModel):\n"
    for column in columns:
        model += f"    {column[1]}: {column[2]}\n"
    return model

if __name__ == "__main__":
    tables = read_db()
    for table in tables:
        columns = read_columns(table[0])
        model = create_model(table[0], columns)
        print(model)
        exec(model)

print(f"Hello World")
