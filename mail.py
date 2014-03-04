# encoding: utf-8

import csv
import getpass
import json
import pyzmail
import sys

EMAIL_REPLACES = {
}


def find_email(student_name, students_data):
    # for testing purposes, if you want all mails sent to same address
    # return 'foo@helsinki.fi'

    if student_name in EMAIL_REPLACES:
        return EMAIL_REPLACES[student_name]

    for student in students_data:
        user = student["user"]
        full_name = user["forename"] + " " + user["surename"]
        if full_name == student_name:
            return user["email"]

    raise Exception('Email for student "%s" not found!' % student_name)


def compose_message(grading):
    return "%s\n\nArvosana: %s" % (grading[22], grading[24])


def compose_mail(grading, recv_email):
    return pyzmail.compose_mail(
        text=(compose_message(grading), 'utf-8'),
        sender=(u'Javalabra', 'javalabra-noreply@cs.helsinki.fi'),
        recipients=[(grading[0], recv_email)],
        subject='Javalabra 2014-3: Arvosanasi',
        default_charset='utf-8',
    )


def compose_mails(grading_data, students_data):
    for grading in grading_data:
        if not grading[0]:
            continue
        recv_email = find_email(grading[0], students_data)
        yield compose_mail(grading, recv_email)


def actually_mail(mails):
    print 'Actually sending emails...'

    smtp_host = 'smtp.helsinki.fi'
    smtp_port = 587
    smtp_mode = 'tls'
    smtp_login = raw_input('SMTP Username: ')
    smtp_password = getpass.getpass('SMTP Password: ')

    for payload, mail_from, rcpt_to, msg_id in mails:
        ret = pyzmail.send_mail2(payload, mail_from, rcpt_to, smtp_host,
                                 smtp_port=smtp_port, smtp_mode=smtp_mode,
                                 smtp_login=smtp_login, smtp_password=smtp_password)

        if ret:
            print 'Failed recipients'
            for recipient, (code, msg) in ret.iteritems():
                print 'code=%d recipient=%s error=%s' % (code, recipient, msg)
            break
        else:
            print 'Sent mail to recipients %s' % rcpt_to


if __name__ == '__main__':
    grading_csv_path = 'grading.csv'
    students_json_path = 'students.json'

    with open(grading_csv_path, 'r') as grading_csv_file, open(students_json_path, 'r') as students_json_file:
        grading_data = zip(*csv.reader(grading_csv_file))[1:]
        students_data = json.load(students_json_file)

    mails = list(compose_mails(grading_data, students_data))[9:10]

    for payload, mail_from, rcpt_to, msg_id in mails:
        print payload
        print 'Sender:', mail_from
        print 'Receivers:', rcpt_to
        print
        print '---'
        print

    if len(sys.argv) > 1 and sys.argv[1] == '--run':
        confirmation = raw_input('Enter "Y" if you REALLY want to send all emails: ')
        if confirmation == 'Y':
            actually_mail(mails)
        else:
            print 'Aborted.'
