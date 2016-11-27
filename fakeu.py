# Bradley Singer 997990414, Dimitar Vasilev 999307063

import os
import sys # command line arguement (specify excel file to read at command line)
import psycopg2 # Operate on sql database
import csv # needed to read csv files

dbDict = {'Course': ('CID', 'TERM', 'SUBJ', 'CRSE', 'SEC', 'UNITSMIN', 'UNITSMAX'), 
            'Meeting': ('INSTRUCTORS', 'TYPE', 'DAYS', 'TIME', 'BUILD', 'ROOM'),
            'Student': ('SEAT','SID','SURNAME', 'PREFNAME', 'LEVEL', 'UNITS', 'CLASS', 'MAJOR', 'GRADE', 'STATUS', 'EMAIL') }

fileDict = {'Course': ("CID", "TERM", "SUBJ", "CRSE", "SEC", "UNITS"), 
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
                        CID INTEGER PRIMARY KEY,
                        TERM INTEGER,
                        SUBJ VARCHAR(50),
                        CRSE INTEGER,
                        SEC SMALLINT,
                        UNITSMIN INTEGER,
                        UNITSMAX INTEGER
                 );


    CREATE TABLE IF NOT EXISTS Meeting(
                        INSTRUCTORS VARCHAR(30),            --Last name, first name
                        TYPE VARCHAR(50),
                        DAYS VARCHAR(50),                 --At most, SMTWRFS
                        TIME VARCHAR(50),                 
                        BUILD VARCHAR(50),
                        ROOM VARCHAR(5)
                        --PRIMARY KEY (INSTRUCTORS, ROOM)
                 );


    CREATE TABLE IF NOT EXISTS Student(
                        SEAT SMALLINT,
                        SID INTEGER,
                        SURNAME VARCHAR(50),
                        PREFNAME VARCHAR(50),
                        LEVEL VARCHAR(50),
                        UNITS SMALLINT,
                        CLASS VARCHAR(50),
                        MAJOR VARCHAR(50),
                        GRADE VARCHAR(10),
                        STATUS VARCHAR(50),
                        EMAIL VARCHAR(50) 
                 ); 

    ''')


    con.commit()
    con.close()


def get_attr(table):
    return dbDict[table]


def addValue(table, values):
    con = connect()
    cursor = con.cursor()
    inserts = ""
    attributes = get_attr(table)
    #print("asdfasdfasdf", str(attributes).replace("'", '"').replace("'", ""))
    #print("values", values)
    for tup in values:
        print('Tuple: ', tup)
        if str(tup).find('"') > 0:
            begin_dq_index = 0
            end_dq_index = 0
            tup_str = str(tup)
            print('Got here!!!!!!!!!!!!!!')
            # while begin_dq_index < (len(tup_str) - 1):
            begin_dq_index = tup_str.find('"', begin_dq_index)
            end_dq_index = tup_str.find('"', begin_dq_index)
            apos_index = tup_str.find("'", begin_dq_index, end_dq_index)
            tup_list = list(tup_str)
            tup_list[apos_index] = "''"
            tup = ''.join(tup_list)
            print('########################################' + tup)

            begin_dq_index = end_dq_index + 1
        inserts += str(tup) + ','
    inserts = inserts.strip(',')
    # query_raw = 'INSERT INTO {}{} VALUES{}'.format(table, str(attributes).replace("'", '"'), inserts)
    query = '''INSERT INTO %s%s VALUES %s''' % (table, str(attributes).replace("'", ''), inserts)
    # strips the string of attribute single quotes but leaves values single quotes

    query = query.replace('"', '')

    # print(query)

    #print(query)
    # try:
    cursor.execute(query)
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

def check_if_same(count, alpha):
    if count == alpha:
        return True

def parseResults():
    count = 0
    print("Adding values to db...")
    for val in idtable:
        #print("val", val)
        #print("count", count)
        check = False
        if val == 0 or val == 'e':
            count += 1
            continue
        elif val == 'c' or val == 'm' or val == 's':
            # print("count", count)
            nextAlpha = find_next('e', count)
            # print("nextAlpha", nextAlpha)
            if nextAlpha:
                check = check_if_same(count + 1, nextAlpha)
                if check:
                    # print("check is true")
                    count = nextAlpha
                    continue
                else:
                    tuples_to_add = all_tuples[count + 1: nextAlpha]
                    if val == 'c':
                        addUnique('Course', tuples_to_add)
                    elif val == 'm':
                        addUnique('Meeting', tuples_to_add)
                    elif val == 's':
                        addUnique('Student', tuples_to_add)
                    count += 1
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

            if newrow == fileDict['Meeting'] or newrow == fileDict['Student']:
                courseTableReached = False

            for attr in newrow:
                attr = attr.replace('"','')
                attr = attr.replace('(', '')
                attr = attr.replace(')', '')

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

            if tup_row == fileDict['Course']:
                #print('c')
                idtable.append('c')
            elif tup_row == dbDict['Meeting']:
                idtable.append('m')
                #print("m")
            elif tup_row == fileDict['Student']:
                idtable.append('s')
                #print('s')
            elif tup_row == ('',):
                idtable.append('e')

            else: 
                idtable.append(0)

            if newrow == fileDict['Course']:
                courseTableReached = True

            count += 1
        csvfile.close()
    except ValueError:
        sys.exit("Error: Invalid arguement passed. Should be a .csv file.")
    # print(all_tuples)
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