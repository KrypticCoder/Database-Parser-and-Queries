# DataBase Parser Program & Queries

The following is an assignment for ECS 165A databases course at UC Davis. The specifications are included in 'Homework04.pdf'. In essence, the goal is to insert all of the data in the Grades folder into a local database using Postgres and then run specific queries on the data. 

## Contributors

Name | Student ID 
--- | ---
Bradley Singer | 997990414
Dimitar Vasilev | 999307063

## Installation
1. All testing files should be in a folder called 'Grades' and should follow the format '2012_Q3.csv'
3. Make sure you have postresql installed on your computer and the server is running. For instructions on setting up postgres, visit [https://sites.google.com/site/ecs165afall2013/discussion-sections/postgres-setup]
4. start the server using `start_postgres`
5. Open postresql by typing either `psql` or `psql postgres` depending on the default database on your system
6. Create a database with the name 'fakeu' with the following command: `CREATE DATABASE fakeu;`
7. Exit postgres with '\q'

## Usage
* To run the program, execute `python3 fakeu.py` in the same directory where the Grades folder is located. This should insert the data file by file from the Grades folder into the database 'fakeu'.
* To run the specified queries, make sure the database is filled up, and run `python3 queries.py` from the same folder as 'fakeu.py'. Follow the instructions outputted

## Requirements

Program | Version 
--- | ---
Python | 3
Postgres| 9.6
