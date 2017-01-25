import os
import sys

import lindaparser

USERNAME = os.getenv("HHN_USERNAME")
PASSWORD = os.getenv("HHN_PASSWORD")

COL1_WIDTH = 65
COL2_WIDTH = 5
COL3_WIDTH = 5
ROW_LENGTH = COL1_WIDTH + COL2_WIDTH + COL3_WIDTH + 2


def format_float(f, decimals=None):
    if decimals is None:
        f = str(f)
    else:
        f = "{number:.{decimals}f}".format(number=f, decimals=decimals)
    
    return f.replace(".", ",")


def get_filtered_exams(exams, type):
    return [exam for exam in exams if exam["course_type"] == type]


def main():
    if not USERNAME:
        print("HHN_USERNAME not set")
        sys.exit(1)
    
    if not PASSWORD:
        print("HHN_PASSWORD not set")
        sys.exit(1)
    
    lindaparser.login(USERNAME, PASSWORD)
    
    current_exams = lindaparser.get_current_exams()
    current_exams.sort(key=lambda exam: exam["name"])
    
    exams_g = get_filtered_exams(current_exams, "G")
    exams_h = get_filtered_exams(current_exams, "H")
    
    print("Grundstudium:\n")
    print_average_grade(exams_g)
    
    print("\n\nHauptstudium:\n")
    print_average_grade(exams_h)

    print_total_ects(exams_g + exams_h)


def print_average_grade(exams):
    ects_total = 0
    ects_total_graded = 0
    grades_total = 0
    
    print_header()
    
    for exam in exams:
        if not exam["passed"]:
            continue
        
        if exam["grade"]:
            grade = format_float(exam["grade"])
        else:
            grade = "-"
        
        print("{} {} {}".format(
            exam["name"].ljust(COL1_WIDTH),
            format_float(exam["ects"]).ljust(COL2_WIDTH),
            grade.ljust(COL3_WIDTH)
        ))
        
        ects_total += exam["ects"]

        if exam["grade"]:
            ects_total_graded += exam["ects"]
            grades_total += exam["ects"] * exam["grade"]
    
    average = grades_total / ects_total_graded
    average = format_float(average, 2)

    ects_total = format_float(ects_total)
    grades_total = format_float(grades_total)
    
    print("{}\n{} {} {}".format(
        "-" * ROW_LENGTH,
        "Insgesamt".ljust(COL1_WIDTH),
        ects_total.ljust(COL2_WIDTH),
        grades_total.ljust(COL3_WIDTH)
    ))
    
    print("{} {} {}".format(
        "Durchschnitt".ljust(COL1_WIDTH),
        "".ljust(COL2_WIDTH),
        average.ljust(COL3_WIDTH)
    ))


def print_header():
    print("{} {} {}\n{}".format(
        "Veranstaltung".ljust(COL1_WIDTH),
        "ECTS".ljust(COL2_WIDTH),
        "Note".ljust(COL3_WIDTH),
        "-" * ROW_LENGTH
    ))


def print_total_ects(exams):
    ects = 0

    for exam in exams:
        ects += exam["ects"]

    print("\n\n{} {}".format(
        "ECTS Grundstudium und Hauptstudium".ljust(COL1_WIDTH),
        format_float(ects).ljust(COL2_WIDTH)
    ))


if __name__ == "__main__":
    main()
