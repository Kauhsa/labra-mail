# encoding: utf-8

import csv
import json
import pyzmail
import sys

EMAIL_REPLACES = {

}


def find_email(student_name, students_data):
    if student_name in EMAIL_REPLACES:
        return EMAIL_REPLACES[student_name]

    for student in students_data:
        user = student["user"]
        full_name = user["forename"] + " " + user["surename"]
        if full_name == student_name:
            return user["email"]

    raise Exception('Email for student %s not found!' % student_name)


def compose_message(grading):
    return "%s\n\nArvosana: %s" % (grading[22], grading[24])


def compose_mail(grading, recv_email):
    return pyzmail.compose_mail(
        text=(compose_message(grading), 'utf-8'),
        sender='test@helsinki.fi',
        recipients=[(grading[0], recv_email)],
        subject='Javalabra 2014-3: Arvosanasi',
        default_charset='utf8',
    )


def compose_mails(grading_data, students_data):
    for grading in grading_data:
        if not grading[0]:
            continue
        recv_email = find_email(grading[0], students_data)
        yield compose_mail(grading, recv_email)

if __name__ == '__main__':
    grading_csv_path = 'grading.csv'
    students_json_path = 'students.json'

    with open(grading_csv_path, 'r') as grading_csv_file, open(students_json_path, 'r') as students_json_file:
        grading_data = zip(*csv.reader(grading_csv_file))[1:]
        students_data = json.load(students_json_file)

    for a in compose_mails(grading_data, students_data):
        print a
        print
