# Bradley Singer 997990414, Dimitar Vasilev 999307063

import sys # command line arguement (specify excel file to read at command line)
import psycopg2 # Operate on sql database
import csv # needed to read csv files

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
                    	TERM INTEGER NOT NULL,
                    	SUBJ CHAR(3) NOT NULL,
                    	SEC SMALLINT NOT NULL,
                    	UNITS SMALLINT NOT NULL			--"1.000 - 5.000"
                 );


	CREATE TABLE IF NOT EXISTS Meeting(
						INSTRUCTOR VARCHAR(30),			--"Last name, first name"
						TYPE VARCHAR(20),
						DAY VARCHAR(7), 				--"At most, SMTWRFS"
						"TIME" TIME,					--"9:00 AM - 9:50 AM"
						BUILD CHAR(3),
						ROOM SMALLINT,
						PRIMARY KEY (INSTRUCTOR, ROOM)
                 );


	CREATE TABLE IF NOT EXISTS Student(
						SEAT SMALLINT,
						SID INTEGER PRIMARY KEY,
						SURNAME VARCHAR(20),
						PREFNAME VARCHAR(20),
						LEVEL CHAR(2),
						UNITS SMALLINT,
						CLASS CHAR(2),
						MAJOR CHAR(4),
						GRADE VARCHAR(2),
						STATUS CHAR(2),
						EMAIL VARCHAR(40) 
				 ); 

	''')

	con.commit()
	con.close()


def get_attr(table):
	return fakeUDict[table]


def addValue(table, values):
    con = connect()
    cursor = con.cursor()
    attributes = get_attr(table)
    
    query_raw = 'INSERT INTO {}{} VALUES{}'.format(table, attributes, values)
    # strips the string of attribute single quotes but leaves values single quotes
    query = query_raw.replace("'", "", (len(attributes) * 2))
    # print(query_raw)
    print(query)
    cursor.execute(query)
    con.commit()
    con.close()

def readCSV(ifilepath):
	# Get the filename + extension
	filenameFull = ifilepath.rsplit('/', 1)[1]
	# Get filename
	filename = filenameFull.split('.')[0]
	print filename

	count = 0

	with open(ifilepath, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
		for row in reader:
			if count = 5:
				break
			else:
				print(', '.join(row))
				count += 1

def main():
	ifilepath = str(sys.argv[1])

	initialize()
	readCSV(ifilepath)

 	#for each row in file:
 	#addValue('Course', (2, 'fall', 'databases', 5, 4))
	

 	# terminate()

if __name__ == '__main__': main()