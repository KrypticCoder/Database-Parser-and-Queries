# Bradley Singer 997990414, Dimitar Vasilev 999307063

import psycopg2
import os
import sys

user = os.environ['USER']
letter_grades = {'letter': ('A', 'B', 'C', 'D', 'F'),
                 'sign': ('+', '-')}

letter_to_gp = {'A+': 4.0,
                'A': 4.0,
                'A-': 3.7,
                'B+': 3.3,
                'B': 3.0,
                'B-': 2.7,
                'C+': 2.3,
                'C': 2.0,
                'C-': 1.7,
                'D+': 1.3,
                'D': 1.0,
                'D-': 0.7,
                'F+': 0.3,
                'F': 0.0,
                'F-': 0.0}


def connect():
    conn = psycopg2.connect(database="fakeu", user=user)
    return conn


def threeA():
    con = connect()
    cursor = con.cursor()

    print('units   percent of students attempted')

    divisor = 0
    res_arr = []

    for unit in range(1, 21):
        qstr = '''select {0} as unit, count(*)::integer as numerator from (
                    select cs.term, cs.sid, sum(cs.units::float) as units_per_quarter from (
                        student natural join enroll natural join course
                    ) as cs
                    group by cs.term, cs.sid
                ) as final
                where units_per_quarter = {0};'''.format(unit)

        # print(qstr)

        cursor.execute(qstr)
        result = cursor.fetchall()
        res_numerator = result[0][1]
        # print('res_numerator',res_numerator,isinstance(res_numerator, int))
        if res_numerator is None:
            res_numerator = 0
        divisor += res_numerator
        # print('divisor', divisor, isinstance(divisor, int))
        res_arr.append(res_numerator)

    for i in range(1, 21):
        output_row = '{0:<10}{1:.3f}%'.format(i, (float(res_arr[i - 1] * 100) / float(divisor)))
        print(output_row)

    con.close()


def threeB():
    con = connect()
    cursor = con.cursor()

    print('units   GPA')

    res_arr = []

    for unit in range(1, 21):
        qstr = '''select {0} as unit, count(*)::integer as numerator, string_agg(final.unit_grade,'.') as all_grades_per_unit from (
                    select cs.term, cs.sid, sum(cs.units::float) as units_per_quarter, string_agg(cs.grade||'_'||cs.units::float,',') as unit_grade from (
                        student natural join enroll natural join course
                    ) as cs
                    group by cs.term, cs.sid
                ) as final
                where units_per_quarter = {0};'''.format(unit)

        cursor.execute(qstr)

        result = cursor.fetchall()
        all_grade_quarter = result[0][2]   # get the huge string of 'units,grade' joined by '.'

        gpa_quarter = -1.0
        total_units = -1.0
        gp_scale_quarter = []

        for quarter_grade in all_grade_quarter.split('.'):
            for course_grade in quarter_grade.split(','):
                gp = 0.0   # grade point (4.0, 3.7, etc)
                grade_unit = course_grade.split('_')

                if(len(grade_unit) > 0 and grade_unit[0] is not None):
                    grade = list(grade_unit[0])
                else:
                    grade = list('NG')

                    # if(grade_unit[1] is not None)
                if(len(grade_unit) > 1):
                    units = grade_unit[1]
                else:
                    units = 0.0

                # print(grade_unit[0] + ' : ' + grade_unit[1])
                # print(''.join(grade) + ' : ' + str(unit) )
                if(len(grade_unit) > 1 and len(grade) > 0 and units != 0):
                    if((grade[0] in letter_grades['letter'])):
                        if(len(grade) > 1):
                            if(grade[1] in letter_grades['sign']):
                                gp = letter_to_gp[''.join(grade[0:2])]
                        else:
                            gp = letter_to_gp[''.join(grade[0])]

                        # print( str(gp) + ' : ' + str(units) + ' = ' + str(gp * float(units)) )
                        total_units += float(units)
                        gp_scale_quarter.append(gp * float(units))

        if(total_units != -1.0):
            total_units = total_units + 1   # to account for the -1,0 delimiter
            gpa_quarter = (float(sum(gp_scale_quarter)) / total_units)

        if(gpa_quarter != -1.0):
            res_arr.append(gpa_quarter)

    for i in range(1, 21):
        output_row = '{0:<10}{1:.2f}'.format(i, res_arr[i - 1])
        print(output_row)

    con.close()


def threeC():
    con = connect()
    cursor = con.cursor()

    res_arr = []

    qstr = '''select instructors, string_agg(csm.grade||'_'||csm.units,',') as unit_grade from (
                select * from (
                    student natural join enroll natural join course natural join has
                ) as stuff
                where (grade = 'A+' or grade = 'A' or grade = 'A-' or grade = 'B+' or grade = 'B' or grade = 'B-' or grade = 'C+' or grade = 'C' or grade = 'C-' or grade = 'D+' or grade = 'D' or grade = 'D-' or grade = 'F') and grade != '' and units != ''
            ) as csm
            group by csm.instructors;'''

    cursor.execute(qstr)

    result = cursor.fetchall()

    for i in range(0, len(result)):
        if(len(result[i]) > 0 and result[i][0] is not None):
            inst = result[i][0]
        else:
            inst = 'Blank'

        if(len(result[i]) > 1 and result[i][1] is not None):
            # get the huge string of 'grade_units' joined by ','
            all_grade_inst = result[i][1]
        else:
            all_grade_inst = None

        gpa_inst = -1.0
        total_units = -1.0
        gp_scale_prof = []

        if(all_grade_inst is not None):
            for course_grade in all_grade_inst.split(','):
                gp = 0.0   # grade point (4.0, 3.7, etc)
                grade_unit = course_grade.split('_')

                if(len(grade_unit) > 0 and grade_unit[0] is not None):
                    grade = list(grade_unit[0])
                else:
                    grade = list('NG')

                if(len(grade_unit) > 1):
                    units = grade_unit[1]
                else:
                    units = 0.0

                if(len(grade_unit) > 1 and len(grade) > 0 and units != 0):
                    if((grade[0] in letter_grades['letter'])):
                        if(len(grade) > 1):
                            if(grade[1] in letter_grades['sign']):
                                gp = letter_to_gp[''.join(grade[0:2])]
                        else:
                            gp = letter_to_gp[''.join(grade[0])]

                        # print( str(gp) + ' : ' + str(units) + ' = ' + str(gp * float(units)) )
                        total_units += float(units)
                        gp_scale_prof.append(gp * float(units))

        # if( total_units != 0 ): # no valid grades for this instructor?
        if(total_units != -1.0 and total_units != 0):
            total_units = total_units + 1   # to account for the -1,0 delimiter
            gpa_inst = (float(sum(gp_scale_prof)) / total_units)

        if(gpa_inst != -1.0):
            res_arr.append((inst, gpa_inst))

    # Find max GPA instructors
    maxgpa = None

    for i in range(1, len(res_arr)):
        val = res_arr[i][1]
        if maxgpa is None or val > maxgpa:
            indices_max = [i]
            maxgpa = val
        elif val == maxgpa:
            indices_max.append(i)

    # Find min GPA instructors
    mingpa = None

    for i in range(1, len(res_arr)):
        val = res_arr[i][1]
        if mingpa is None or val < mingpa:
            indices_min = [i]
            mingpa = val
        elif val == mingpa:
            indices_min.append(i)

    print('Easiest instructor(s): ')
    for i in indices_max:
        output_row = '{0:<30}{1:.2f}'.format(res_arr[i][0], res_arr[i][1])
        print(output_row)

    print('')
    print('Hardest instructor(s): ')
    for i in indices_min:
        output_row = '{0:<30}{1:.2f}'.format(res_arr[i][0], res_arr[i][1])
        print(output_row)

    con.close()


def threeD():
    con = connect()
    cursor = con.cursor()

    qstr = '''select instructors, 'ABC' as subj, crse as course, array_agg(all_grades::varchar) as grades, array_agg(all_units::varchar) as units from (
                select r.instructors, r.term, r.subj, r.crse, r.all_grades, r.all_units from (
                    select final.instructors, final.term, final.subj, final.crse, array_agg(final.grade) as all_grades, array_agg(final.units) as all_units from (
                        select * from (
                            student natural join enroll natural join course natural join has
                        ) as valid_grades
                        where valid_grades.grade != '' and valid_grades.units != ''
                    ) as final
                    group by final.instructors, final.term, final.subj, final.crse
                    having final.instructors != ''
                ) as r
                where r.subj = 'ABC' and (r.crse >= 100 and r.crse < 200) and ('{P,NP}'::varchar[] && r.all_grades) and not ('{A+,A,A-,B+,B,B-,C+,C,C-,D+,D,D-,F}'::varchar[] && r.all_grades)
            ) as l
            group by instructors, crse;'''

    cursor.execute(qstr)
    p_np = cursor.fetchall()  # Instructors who taught courses with all P/NP grading

    qstr = '''select instructors, 'ABC' as subj, crse as course, array_agg(all_grades::varchar), array_agg(all_units::varchar) from (
                select r.instructors, r.term, r.subj, r.crse, r.all_grades, r.all_units from (
                    select final.instructors, final.term, final.subj, final.crse, array_agg(final.grade) as all_grades, array_agg(final.units) as all_units from (
                        select * from (
                            student natural join enroll natural join course natural join has
                        ) as valid_grades
                        where valid_grades.grade != '' and valid_grades.units != ''
                    ) as final
                    group by final.instructors, final.term, final.subj, final.crse
                    having final.instructors != ''
                ) as r
                where r.subj = 'ABC' and (r.crse >= 100 and r.crse < 200) and ('{A+,A,A-,B+,B,B-,C+,C,C-,D+,D,D-,F}'::varchar[] && r.all_grades)
            ) as l
            group by instructors, crse;'''

    cursor.execute(qstr)
    lg = cursor.fetchall()  # Instructors who taught courses with some letter grading

    res_arr_p = []  # P/NP results
    res_arr_l = []  # letter grade results

    # ************ P/NP (pass rate) calculations ***************

    for row_p_np in p_np:
        inst = row_p_np[0]
        crse = row_p_np[2]

        pass_units = 0.0
        total_units = 0.0

        # dictionary for clarity sake
        row = {'course': row_p_np[2], 'grades': row_p_np[3], 'units': row_p_np[4]}

        for i in range(0, len(row['grades'])):  # all array len the same
            row['grades'][i] = row['grades'][i].replace('{', '').replace('}', '')
            row['units'][i] = row['units'][i].replace('{', '').replace('}', '')

            if len(row['grades'][i]) < 3:   # single student in class
                if row['grades'][i] == 'P':
                    pass_units += float(row['units'][i])
                    # print('pass_units',pass_units)

                total_units += float(row['units'][i])
                # print('total_units',total_units)
            else:                           # multiple students in class
                class_grades = row['grades'][i].split(',')
                class_units = row['units'][i].split(',')
                for g in range(0, len(class_grades)):
                    if class_grades[g] == 'P':
                        pass_units += float(class_units[g])
                        # print('pass_units',pass_units)

                    total_units += float(class_units[g])
                    # print('total_units',total_units)

        res_arr_p.append((inst, 'ABC ' + str(crse), ((float(pass_units) * 100) / float(total_units))))

    # ************ Letter grade (GPA) calculations ***************

    for row_lg in lg:
        inst = row_lg[0]
        crse = row_lg[2]

        total_units = 0.0
        gp_scale_class = []

        # dictionary for clarity sake
        row = {'course': row_lg[2], 'grades': row_lg[3], 'units': row_lg[4]}

        for i in range(0, len(row['grades'])):  # all array len the same
            row['grades'][i] = row['grades'][i].replace('{', '').replace('}', '')
            row['units'][i] = row['units'][i].replace('{', '').replace('}', '')

            gp = 0.0

            # if inst == 'Dean, Daniel A.' and crse == 104:
            #     print('length of grades row: ' + str(len(row['grades'][i])))

            if len(row['grades'][i]) < 3:   # single student in class
                if len(row['grades'][i]) == 1:
                    if row['grades'][i] in letter_grades['letter']:
                        gp = letter_to_gp[row['grades'][i]]
                elif len(row['grades'][i]) == 4:
                    if list(row['grades'][i])[0] in letter_grades['letter'] and list(row['grades'][i])[1] in letter_grades['sign']:
                        gp = letter_to_gp[row['grades'][i]]

                total_units += float(row['units'][i])
                gp_scale_class.append(gp * float(row['units'][i]))

            else:                           # multiple students in class
                class_grades = row['grades'][i].split(',')
                class_units = row['units'][i].split(',')
                for g in range(0, len(class_grades)):
                    if len(class_grades[g]) == 1:
                        if class_grades[g] in letter_grades['letter']:
                            gp = letter_to_gp[class_grades[g]]
                    elif len(class_grades[g]) == 2:
                        if list(class_grades[g])[0] in letter_grades['letter'] and list(class_grades[g])[1] in letter_grades['sign']:
                            gp = letter_to_gp[class_grades[g]]

                    total_units += float(class_units[g])
                    gp_scale_class.append(gp * float(class_units[g]))

        res_arr_l.append((inst, 'ABC ' + str(crse), (float(sum(gp_scale_class)) / float(total_units))))

    # Find max pass rate instructors + course
    maxpass = None

    for i in range(1, len(res_arr_p)):
        val = res_arr_p[i][2]
        if maxpass is None or val > maxpass:
            indices_max_p = [i]
            maxpass = val
        elif val == maxpass:
            indices_max_p.append(i)

    # Find min pass rate instructors + course
    minpass = None

    for i in range(1, len(res_arr_p)):
        val = res_arr_p[i][2]
        if minpass is None or val < minpass:
            indices_min_p = [i]
            minpass = val
        elif val == minpass:
            indices_min_p.append(i)

    # Find max gpa instructors + course
    maxpass = None

    for i in range(1, len(res_arr_l)):
        val = res_arr_l[i][2]
        if maxpass is None or val > maxpass:
            indices_max_l = [i]
            maxpass = val
        elif val == maxpass:
            indices_max_l.append(i)

    # Find min gpa instructors + course
    minpass = None

    for i in range(1, len(res_arr_l)):
        val = res_arr_l[i][2]
        if minpass is None or val < minpass:
            indices_min_l = [i]
            minpass = val
        elif val == minpass:
            indices_min_l.append(i)

    # ******* Output result ***********

    # ******* P/NP result ***********
    print('----- P/NP Classes -----')
    print('{0:<30}{1:<15}{2}:'.format('Easiest instructor(s)', 'Class', 'Pass rate'))
    for i in indices_max_p:
        output_row = '{0:<30}{1:<15}{2:.2f}%'.format(res_arr_p[i][0], res_arr_p[i][1], res_arr_p[i][2])
        print(output_row)

    print('')
    print('{0:<30}{1:<15}{2}:'.format('Hardest instructor(s)', 'Class', 'Pass rate'))
    for i in indices_min_p:
        output_row = '{0:<30}{1:<15}{2:.2f}%'.format(res_arr_p[i][0], res_arr_p[i][1], res_arr_p[i][2])
        print(output_row)

    print('')
    print('')

    # ******* P/NP result ***********

    print('----- Letter Grade Classes -----')
    print('{0:<30}{1:<15}{2}:'.format('Easiest instructor(s)', 'Class', 'GPA'))
    for i in indices_max_l:
        output_row = '{0:<30}{1:<15}{2:.2f}'.format(res_arr_l[i][0], res_arr_l[i][1], res_arr_l[i][2])
        print(output_row)

    print('')
    print('{0:<30}{1:<15}{2}:'.format('Hardest instructor(s)', 'Class', 'GPA'))
    for i in indices_min_l:
        output_row = '{0:<30}{1:<15}{2:.2f}'.format(res_arr_l[i][0], res_arr_l[i][1], res_arr_l[i][2])
        print(output_row)

    con.close()


def threeE():

    print("These are the course IDs that conflict:")
    print('\n')

    all_pairings = []
    unique_pairs = dict()
    con = connect()
    cursor = con.cursor()
    qstr = '''
    select cid1, crse1, array_agg(distinct(cid2)) as cid2 , array_agg(distinct(crse2)) as crse2 from (
    select m1.cid as cid1, m2.cid as cid2, m1.term as term1, m2.term as term2, m1.subj as subj1, m2.subj as subj2, m1.crse as crse1, m2.crse as crse2, m1.starttime as starttime1, m2.starttime as starttime2, m1.endtime as endtime1, m2.endtime as endtime2 from
            (course natural join has
            ) m1
            ,
            (course natural join has
            )m2
    where m1.cid != m2.cid and
        m1.term = m2.term and
        m1.days = m2.days and
        m1.build = m2.build and
        m1.room = m2.room and
        (m1.crse != m2.crse or m1.subj != m2.subj) and
        ((m1.starttime < m2.endtime and m1.endtime > m2.starttime) or (m1.endtime > m2.starttime and m1.starttime < m2.endtime) or (m1.starttime = m2.starttime and m1.endtime = m2.endtime)) and
        (m1.days != '' and m1.starttime != '' and m1.endtime != '' and m1.build != '' and m1.room != '')
    ) as final
    group by cid1, term1, subj1, crse1
    ; '''

    cursor.execute(qstr)
    results = cursor.fetchall()

    for course_pair in results:
        for i in course_pair[2]:
            pair = []
            pair.append(course_pair[0])
            pair.append(i)
            all_pairings.append(tuple(sorted(pair)))

    for i in all_pairings:
        if i not in unique_pairs:
            unique_pairs[i] = True

    output = []

    for i in unique_pairs:
        output.append(i)

    output = sorted(output)

    count = 0
    for conflict in output:
        count += 1
        conflict = list(conflict)
        print('Course ' + str(conflict[0]) + ' conflicts with Course ' + str(conflict[1]))

    print('Number of conflicts: ' + str(count))

    threeE2(results)


def threeE2(results):

    all_pairings = []
    unique_pairs = dict()
    print('\n')
    print("These are all the courses that conflict:")
    print('\n')
    for course_pair in results:
        for i in course_pair[3]:
            pair = []
            pair.append(course_pair[1])
            pair.append(i)
            all_pairings.append(tuple(sorted(pair)))

    for i in all_pairings:
        if i not in unique_pairs:
            unique_pairs[i] = True

    output = []

    for i in unique_pairs:
        output.append(i)

    output = sorted(output)

    count = 0
    for conflict in output:
        count += 1
        conflict = list(conflict)
        print('Course ' + str(conflict[0]) + ' conflicts with Course ' + str(conflict[1]))

    print('Number of conflicts: ' + str(count))


def main():
    print('Please select the problem answer in the form \'3a\' from a-g')
    print('If you want to exit the program, type \'exit\'')
    while(1):
        prob_num = input('Problem: ')
        print('')

        if prob_num.lower() == '3a':
            threeA()
        elif prob_num.lower() == '3b':
            threeB()
        elif prob_num.lower() == '3c':
            threeC()
        elif prob_num.lower() == '3d':
            threeD()
        elif prob_num.lower() == '3e':
            threeE()
        elif prob_num.lower() == 'exit':
            sys.exit()
        else:
            print('Invalid problem number. Please choose 3a - 3g')
        print('')  # newline

if __name__ == '__main__':
    main()
