<<<<<<< HEAD
# fakeu
Homework 4 for ECS165a Databases
# Authors
Bradley Singer 997990414  
Dimitar Vasilev 999307063
=======
# Homework 4

Special Note: Our program parses through all files in 1-2 minutes on our local machine 
but it takes 15 - 20 minutes to run on CSIF. I've already rewritten my parser program twice 
to get it working fast and I don't know how to make it run any faster at this point. 


You are designing a database for a university called FakeU. As a trial you have been
provided grade data from courses for departments ABC and DEF. The grade data is from
Summer of 1989 until Summer of 2012. The data provided is in CSV format, and is only
as complete as could be made possible. There may be errors, omissions or redundant data
in the files. FakeU like UC Davis is on a quarter system, however they have recently
transitioned to a single summer quarter instead of two summer sessions. This has
corrupted some of their summer data as all summer session classes have now been
grouped into a single summer quarter term. Each course has a course ID (CID), a term it
was offered (TERM), a subject (SUBJ), a course number (CRSE), a section (SEC), and
number of units (UNITS). Within a course there listings of meetings, the instructor of the
meeting (INSTRUCTOR(S)), meeting type (TYPE), day of meeting (DAYS), time of
meeting (TIME), meeting building (BUILD), and meeting room (ROOM) are also listed.
For each student that takes the course there is a student seat (SEAT), a student ID (SID),
the student’s surname (SURNAME), the student’s preferred name (PREFNAME), the
student’s (LEVEL), the number of units the student is receiving (UNITS), the student’s
class standing (CLASS), the student’s major (MAJOR), the grade the student received in
the course (GRADE), the student’s registration status (STATUS), and the student’s email
address (EMAIL).

## Contributors

Name | Student ID 
--- | --- | ---
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
--- | --- | ---
Python | 3
Postgres| 9.6
>>>>>>> e5997c5... Changed formatting. Added README. Removed extraneous files
