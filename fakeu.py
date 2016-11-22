# Bradley Singer 997990414, Dimitri Vasilev

import psycopg2

fakeUDict = {'Course': ('CID', 'TERM', 'SUBJ', 'SEC', 'UNITS'), 
			'Meeting': ('INSTRUCTOR', 'TYPE', 'DAY', 'TIME', 'BUILD', 'ROOM'),
			'Student': ('SID', 'SEAT', 'SURNAME', 'PREFNAME', 'LEVEL', 'UNITS', 'CLASS', 'MAJOR', 'GRADE', 'STATUS', 'EMAIL') }

def connect():
    # Connect to the PostgreSQL database.  Returns a database connection.
    return psycopg2.connect("dbname=fakeu")

def initialize():

	con = connect()
	cursor = con.cursor()
	cursor.execute('''
	CREATE TABLE IF NOT EXISTS Course(
						CID INTEGER NOT NULL PRIMARY KEY,
                    	TERM VARCHAR(6) NOT NULL, -- Winter, Spring, Summer, Fall
                    	SUBJ VARCHAR(20) NOT NULL,
                    	SEC SMALLINT NOT NULL,
                    	UNITS SMALLINT NOT NULL
                 );


	CREATE TABLE IF NOT EXISTS Meeting(
						INSTRUCTOR VARCHAR(20) NOT NULL,
						TYPE VARCHAR(20) NOT NULL,
						DAY VARCHAR(9) NOT NULL,
						"TIME" TIME NOT NULL,
						BUILD VARCHAR(20) NOT NULL,
						ROOM SMALLINT NOT NULL,
						PRIMARY KEY (INSTRUCTOR, ROOM)
                 );


	CREATE TABLE IF NOT EXISTS Student(
						SID INTEGER NOT NULL PRIMARY KEY,
						SEAT SMALLINT NOT NULL,
						SURNAME VARCHAR(20) NOT NULL,
						PREFNAME VARCHAR(20) NOT NULL,
						LEVEL SMALLINT NOT NULL,
						UNITS SMALLINT NOT NULL,
						CLASS VARCHAR(20) NOT NULL,
						MAJOR VARCHAR(20) NOT NULL,
						GRADE SMALLINT NOT NULL,
						STATUS VARCHAR(20) NOT NULL,
						EMAIL VARCHAR(40) NOT NULL
				 ); 

	''')

	con.commit()
	con.close()


def get_attr(table):
	return fakeUDict[table]


def addValues(table, values):
    con = connect()
    cursor = con.cursor()
    attributes = get_attr(table)
    
    query_raw = 'INSERT INTO {}{} VALUES{}'.format(table, attributes, values)
    query = query_raw.replace("'", "", (len(attributes) * 2))
    # print(query_raw)
    # print(query)
    cursor.execute(query)
    con.commit()
    con.close()


def main():
 	initialize()
 	#readfile
 	#for each row in file:
 	addValues('Course', (1, 'fall', 'databases', 5, 4))
	

 	# terminate()

if __name__ == '__main__': main()