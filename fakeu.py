# Bradley Singer 997990414, Dimitar Vasilev 999307063

import os
import sys          # command line arguement (specify excel file to read at command line)
import psycopg2     # Operate on sql database
import csv          # needed to read csv files
import time

CUR_FILE = ''
MID = 0
user = os.environ['USER']
conn = psycopg2.connect(database="fakeu", user=user)
cursor = conn.cursor()

dbDict = {'Course': ('CID', 'TERM', 'SUBJ', 'CRSE', 'SEC', 'UNITSMIN', 'UNITSMAX'),
          'Student': ('SID', 'SURNAME', 'PREFNAME', 'EMAIL'),
          'Enroll': ('CID', 'TERM', 'SEAT', 'SID', 'LEVEL', 'UNITS', 'CLASS', 'MAJOR', 'GRADE', 'STATUS'),
          'Has': ('MID', 'CID', 'TERM', 'INSTRUCTORS', 'TYPE', 'DAYS', 'STARTTIME', 'ENDTIME', 'BUILD', 'ROOM')}

fileDict = {'Course': ("CID", "TERM", "SUBJ", "CRSE", "SEC", "UNITS"),
            'Meeting': ("INSTRUCTOR(S)", "TYPE", "DAYS", "TIME", "BUILD", "ROOM"),
            'Student': ("SEAT", "SID", "SURNAME", "PREFNAME", "LEVEL", "UNITS", "CLASS", "MAJOR", "GRADE", "STATUS", "EMAIL")}

key_loc = {'Course': [0, 1],
           'Student': [0],
           'Enroll': [0, 1, 3],
           'Has': [0, 1, 2]}

course_table_tuples = []
meeting_table_tuples = []
student_table_tuples = []

alldata = dict()
summerCourses = dict()

coursekeys = dict()
studentkeys = dict()
enrollkeys = dict()
haskeys = dict()

keys = {'Course': coursekeys, 'Student': studentkeys, 'Enroll': enrollkeys, 'Has': haskeys}


def initialize():
    """ create database tables """
    cursor.execute('''CREATE TABLE IF NOT EXISTS Course (
                        CID VARCHAR(50),
                        TERM VARCHAR(50),
                        SUBJ VARCHAR(50),
                        CRSE INTEGER,
                        SEC SMALLINT,
                        UNITSMIN INTEGER,
                        UNITSMAX INTEGER,
                        PRIMARY KEY (CID, TERM)
                );

                CREATE TABLE IF NOT EXISTS Student (
                        SID INTEGER PRIMARY KEY,
                        SURNAME VARCHAR(50),
                        PREFNAME VARCHAR(50),
                        EMAIL VARCHAR(50)
                );

                CREATE TABLE IF NOT EXISTS Enroll (
                        CID VARCHAR(50),
                        TERM VARCHAR(50),
                        SEAT SMALLINT,
                        SID INTEGER,
                        LEVEL VARCHAR(50),
                        UNITS VARCHAR(50),
                        CLASS VARCHAR(50),
                        MAJOR VARCHAR(50),
                        GRADE VARCHAR(10),
                        STATUS VARCHAR(50),
                        PRIMARY KEY (CID, TERM, SID)
               );

                CREATE TABLE IF NOT EXISTS Has (
                        MID INTEGER,
                        CID VARCHAR(50),
                        TERM VARCHAR(50),
                        INSTRUCTORS VARCHAR(30),
                        TYPE VARCHAR(50),
                        DAYS VARCHAR(50),
                        STARTTIME VARCHAR(50),
                        ENDTIME VARCHAR(50),
                        BUILD VARCHAR(50),
                        ROOM VARCHAR(5),
                        PRIMARY KEY (MID, CID, TERM)
                );

    ''')
    conn.commit()


def addValue(table, tup):
    """ add tuples to database
    """

    attributes = dbDict[table]
    query = '''INSERT INTO %s%s VALUES %s''' % (table, str(attributes).replace("'", ''), str(tup))

    # strips the string of attribute single quotes but leaves values single quotes
    query = query.replace('"', '')

    cursor.execute(query)
    conn.commit()


def checkKeys(table, tup):
    """ check that a tuple doesn't have a duplicate key
        and its key attributes are not null
    """
    check = 0
    global CUR_FILE
    tupkeys = ()
    quarter = CUR_FILE.split('_')[1]

    for i in key_loc[table]:
        tupkeys += (tup[i],)       # get the key attr from our tuple
        if tup[i] == '':           # if one of the key attr is null, return False
            return check
    if tupkeys in keys[table]:      # make sure we haven't added duplicate keys
        if table == 'Course':
            return 1
        if '3' in quarter and table == 'Course':
            newkey = ()
            for i in tupkeys:
                newkey += ((i + 'a'),)
            keys[table][newkey] = True
            check = 2
        else:
            check = 0
    else:
        keys[table][tupkeys] = True
        check = 1

    return check


def checkUnique(tup):
    """ returns True if tuple not in dictionary """
    if tup in alldata:
        return False
    else:
        alldata[tup] = 'true'
        return True


def createTuples():
    """ create tuples out of global arrays and
        prep for insertion into database
    """

    staredpair = ()
    conflictingCourse = False
    # if the tables are not empty
    if meeting_table_tuples and student_table_tuples and course_table_tuples:

        course = course_table_tuples[0]   # Course table should only have 1 value
        check = checkKeys('Course', course)

        # check if course tuple is unique in database and its keys are not null and its not a conflicting course
        if checkUnique(str(course)) and check == 1:
            addValue('Course', course)

        elif check == 2:                # if it is a conflicting course, create new key pair
            print('conflicting course')
            conflictingCourse = True
            diffcourse = ()
            staredpair = ((course[0] + 'a'), (course[1] + 'a'))          # cid, term with 'a' appended to each
            diffcourse += staredpair
            for x in range(2, len(course)):
                diffcourse += (course[x],)                              # subj, crse, sec, units
            addValue('Course', diffcourse)

        for meeting in meeting_table_tuples:

            has_tup = ()
            has_tup += (meeting[0],)                             # MID
            if conflictingCourse:
                has_tup += staredpair                           # cid*, term* from course if conflicting course
            else:
                has_tup += (course[0], course[1])
            for x in range(1, len(meeting)):                     # everything else from meeting that we missed
                has_tup += (meeting[x],)                        # instructor, type, days, starttime, endtime, build, room
            # check if has tuple is unique in database
            if checkUnique(str(has_tup)) and checkKeys('Has', has_tup):
                    addValue('Has', has_tup)

        for student in student_table_tuples:

            # Last tuple in student array will be empty because that is the line at which we call create_tuple()
            if student != ('',):
                student_tup = ()
                student_tup += (student[1], student[2], student[3], student[10])     # sid, surname, prefname, email

                # check if student tuple is unique in database
                if checkUnique(str(student_tup)) and checkKeys('Student', student_tup):
                    addValue('Student', student_tup)

                enroll_tup = ()
                if conflictingCourse:
                    enroll_tup += staredpair            # cid*, term* from course if conflicting course
                else:
                    enroll_tup += (course[0], course[1])
                enroll_tup += (student[0], student[1])   # seat, sid from student
                for x in range(4, len(student) - 1):     # everything else from student except email
                    enroll_tup += (student[x],)         # level, units, class, major, grade, status

                # check if enroll tuple is unique in database
                if checkUnique(str(enroll_tup)) and checkKeys('Enroll', enroll_tup):
                    addValue('Enroll', enroll_tup)

    del course_table_tuples[:]
    del meeting_table_tuples[:]
    del student_table_tuples[:]


def convertTime(time):
    """ conver time attribute to minutes """
    digit = time.split(' ')[0]
    day = time.split(' ')[1]
    hour = int(digit.split(':')[0])
    minn = int(digit.split(':')[1])
    if day == 'PM':
        if hour == 12:
            minutes = 60 * (12) + minn
        else:
            minutes = 60 * (hour + 12) + minn
    elif day == 'AM':
        if hour == 12:
            minutes = minn
        else:
            minutes = 60 * (hour) + minn

    return minutes


def parseAttr(attr):
    """ format each attribute of each row """
    attr = attr.replace('(', '')
    attr = attr.replace(')', '')
    attr = attr.strip('"')
    attr = attr.strip("'")
    attr = attr.replace("'", '')
    return attr


def readCSV(ifilepath):
    """ read in the file """

    # open the file
    csvfile = open(ifilepath)
    reader = csv.reader(csvfile)

    # initial conditions
    studentTableReached = False
    meetingTableReached = False
    courseTableReached = False
    row_count = -1
    emptyLineCount = 0
    reader = csv.reader(csvfile)
    global MID

    # read file line by line
    for row in reader:
        row_count += 1

        # First line in file is empty, skip
        if row_count == 0:
            continue

        insertRow = []
        newrow = tuple(';'.join(row).strip("'").split(';'))     # convert each line into tuple

        # For every 3 empty lines you come across, corresponding tuples should be created
        if newrow == ('',):
            courseTableReached = False
            meetingTableReached = False
            studentTableReached = False
            emptyLineCount += 1
            if emptyLineCount == 3:
                createTuples()
                emptyLineCount = 0

        # If course table reached, need to create unitsmin and unitsmax attributes for database
        if courseTableReached is True:

            attr_count = 0

            for attr in newrow:

                attr = parseAttr(attr)

                # units attribute is specified as range, create min and max
                if '.000' in attr:
                    attr = attr.replace('.000', '')
                    unitsMin = attr.split('-')[0].replace('"', '')
                    unitsMax = attr.split('-')[1].replace('"', '')
                    insertRow.append(unitsMin)
                    insertRow.append(unitsMax)

                # units attribute is single integer, copy twice
                elif attr_count == 5:
                    insertRow.append(attr)
                    insertRow.append(attr)

                # attribute is not unit
                else:
                    insertRow.append(attr)

                attr_count += 1

            insertTuple = tuple(insertRow)
            course_table_tuples.append(insertTuple)

        # meeting table has been reached
        if meetingTableReached is True:
            MID = MID + 1
            insertRow.append(" \'" + str(MID) + "\'")

            attr_count = 0
            for attr in newrow:
                attr = parseAttr(attr)

                # split time into 2 attributes
                if '-' in attr:
                    timeInterval = attr.split(' - ')
                    for i in range(len(timeInterval)):
                        time = convertTime(timeInterval[i])
                        insertRow.append(time)

                elif attr_count == 3:
                    insertRow.append(attr)
                    insertRow.append(attr)
                else:

                    insertRow.append(attr)

                attr_count += 1

            insertTuple = tuple(insertRow)
            meeting_table_tuples.append(insertTuple)

        # student table has been reached
        if studentTableReached is True:
            attr_count = 0
            for attr in newrow:
                attr = parseAttr(attr)
                if attr_count == 5 and attr == '':
                    attr = '-1'

                insertRow.append(attr)
                insertTuple = tuple(insertRow)
                attr_count += 1
            student_table_tuples.append(insertTuple)

        # set flags for eaech row
        if newrow == fileDict['Course']:
            courseTableReached = True

        elif newrow == fileDict['Meeting']:
            meetingTableReached = True

        elif newrow == fileDict['Student']:
            studentTableReached = True

    createTuples()


def destroy():
    """ for debugging purposes """
    cursor.execute('''DROP TABLE IF EXISTS Course; DROP TABLE IF EXISTS Meeting; DROP TABLE IF EXISTS Student; DROP TABLE IF EXISTS Enroll; DROP TABLE IF EXISTS Has''')
    conn.commit()


def main():
    global CUR_FILE
    destroy()
    initialize()

    print("inserting into database")
    tstart = time.time()

    if len(sys.argv) == 2:
        start_time = time.time()
        ifilepath = str(sys.argv[1])
        sys.stdout.write(ifilepath + ": ")
        readCSV('Grades/' + ifilepath)
        end_time = time.time()
        total_time = end_time - start_time
        print(total_time)

    else:
        for file in os.listdir('./Grades'):
            if file.endswith('.csv'):
                CUR_FILE = file
                start_time = time.time()
                sys.stdout.write(file + ": ")
                readCSV('Grades/' + file)
                end_time = time.time()
                total_time = end_time - start_time
                print(total_time)

    tend = time.time()
    total = tend - tstart
    print('')
    print('total time: ' + str(total))
    conn.close()

if __name__ == '__main__':
    main()
