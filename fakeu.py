# Bradley Singer 997990414, Dimitar Vasilev 999307063

import os
import sys # command line arguement (specify excel file to read at command line)
import psycopg2 # Operate on sql database
import csv # needed to read csv files

fakeUDict = {'Course': ("CID", "TERM", "SUBJ", "CRSE", "SEC", "UNITS"), 
            'Meeting': ("INSTRUCTOR(S)", "TYPE", "DAYS", "TIME", "BUILD", "ROOM"),
            'Student': ("SEAT","SID","SURNAME", "PREFNAME", "LEVEL", "UNITS", "CLASS", "MAJOR", "GRADE", "STATUS", "EMAIL") }

all_tuples = []
idtable = []
set_tuples = []

def connect():
    # Connect to the PostgreSQL database.  Returns a database connection.
    return psycopg2.connect("dbname=fakeu")

def initialize():
    
    con = connect()
    cursor = con.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Course(
                        "CID" INTEGER NOT NULL PRIMARY KEY,
                        "TERM" INTEGER NOT NULL,
                        "SUBJ" VARCHAR(30) NOT NULL,
                        "CRSE" INTEGER NOT NULL,
                        "SEC" SMALLINT NOT NULL,
                        "UNITSMIN" INTEGER NOT NULL,
                        "UNITSMAX" INTEGER NOT NULL
                 );


    CREATE TABLE IF NOT EXISTS Meeting(
                        "INSTRUCTOR(S)" VARCHAR(30),            --"Last name, first name"
                        "TYPE" VARCHAR(20),
                        "DAYS" VARCHAR(20),                 --"At most, SMTWRFS"
                        "TIME" VARCHAR(30),                 
                        "BUILD" VARCHAR(30),
                        "ROOM" SMALLINT,
                        PRIMARY KEY ("INSTRUCTOR(S)", "ROOM")
                 );


    CREATE TABLE IF NOT EXISTS Student(
                        "SEAT" SMALLINT,
                        "SID" INTEGER,
                        "SURNAME" VARCHAR(20),
                        "PREFNAME" VARCHAR(20),
                        "LEVEL" VARCHAR(20),
                        "UNITS" SMALLINT,
                        "CLASS" VARCHAR(20),
                        "MAJOR" VARCHAR(20),
                        "GRADE" VARCHAR(2),
                        "STATUS" VARCHAR(20),
                        "EMAIL" VARCHAR(40) 
                 ); 

    ''')


    con.commit()
    con.close()


def get_attr(table):
    return fakeUDict[table]


def addValue(table, values):
    con = connect()
    cursor = con.cursor()
    inserts = ""
    attributes = get_attr(table)
    #print("asdfasdfasdf", str(attributes).replace("'", '"').replace("'", ""))
    #print("values", values)
    for tup in values:
        inserts += str(tup) + ','
    inserts = inserts.strip(',')
    # query_raw = 'INSERT INTO {}{} VALUES{}'.format(table, str(attributes).replace("'", '"'), inserts)
    query_raw2 = "INSERT INTO %s%s VALUES %s" % (table, str(attributes).replace("'", '"'), inserts)
    # strips the string of attribute single quotes but leaves values single quotes
    query = query_raw2.replace("'", "", (len(attributes) * 2))
    # print(query_raw)
    #print(query)
    # try:
    cursor.execute(query_raw2)
    con.commit()
    con.close()
    # except: 
    #     con.commit()
    #     con.close()
    #     return


def find_next(s, idx):
    #print len(idtable)
    for i in range(idx, len(idtable) - 1):
        next = idx + 1
        if (next < len(idtable) - 1 and idtable[i] == s):
            next = i
            return next



def addUnique(table, tuples_to_add):
    add_unique_tuples = []
    for tup in tuples_to_add:
        if tup not in set_tuples:
            add_unique_tuples.append(tup)
            set_tuples.append(tup)


    addValue(table, add_unique_tuples)


def parseResults():
    count = 0
    print("Adding values to db...")
    for val in idtable:
        #print("val", val)
        #print("count", count)
        
        if val == 0:
            count = count + 1
            continue
        elif val == 'c':
            nextAlpha = find_next('m', count)
            if(nextAlpha):
                tuples_to_add = all_tuples[count + 1:nextAlpha-1]
                addUnique('Course', tuples_to_add)

        elif val == 'm':
            nextAlpha = find_next('s', count)
            if(nextAlpha):
                #print('MnextAlpha', nextAlpha)
                #print(all_tuples[count:nextAlpha-1])
                tuples_to_add = all_tuples[count + 1:nextAlpha-1]
                addUnique('Meeting', tuples_to_add)
        elif val == 's':
            nextAlpha = find_next('c', count)
            if(nextAlpha):
                #print('SnextAlpha', nextAlpha)
                #print(all_tuples[count:nextAlpha-1])
                tuples_to_add = all_tuples[count + 1:nextAlpha-1]
                addUnique('Student', tuples_to_add)
        count = count + 1
    print("Finished adding values.")


def readCSV(ifilepath):
    try:
        count = 0
        courseTableReached = False
        csvfile = open(ifilepath)
        reader = csv.reader(csvfile)
        for row in reader:
            newrow = tuple(';'.join(row).strip("'").split(';'))
            row = []
            attr_count = 0
            for attr in newrow:
                attr = attr.replace('"','')

                if courseTableReached == True:
                    if '.000' in attr:
                        attr = attr.replace('.000', '')
                        units_min = attr.split('-')[0].replace('"', '')
                        units_max = attr.split('-')[1].replace('"', '')
                        row.append(units_min)
                        row.append(units_max)
                       
                    elif attr_count == 5:
                        row.append(attr)
                        row.append(attr)
                    else: 
                        row.append(attr)
                    attr_count += 1
                else:
                    row.append(attr)
            
            tup_row = tuple(row)
            all_tuples.append(tup_row)
            if tup_row == fakeUDict['Course']:
                #print('c')
                idtable.append('c')
            elif tup_row == fakeUDict['Meeting']:
                idtable.append('m')
                #print("m")
            elif tup_row == fakeUDict['Student']:
                idtable.append('s')
                #print('s')
            else: 
                idtable.append(0)

            if newrow == fakeUDict['Course']:
                courseTableReached = True
            elif newrow == fakeUDict['Meeting']:
                courseTableReached = False

            count += 1
        csvfile.close()
    except ValueError:
        sys.exit("Error: Invalid arguement passed. Should be a .csv file.")
    print(all_tuples)
    parseResults()
        
def deinitialize():
    con = connect()
    cursor = con.cursor()
    cursor.execute('''DROP TABLE IF EXISTS Course; DROP TABLE IF EXISTS Meeting; DROP TABLE IF EXISTS Student;''')
    con.commit()
    con.close()


def main():
    ifilepath = str(sys.argv[1])
    deinitialize()
    initialize()
    readCSV(ifilepath)

    #for each row in file:
    #addValue('Course', (2, 'fall', 'databases', 5, 4))
    

    # terminate()

if __name__ == '__main__': main()