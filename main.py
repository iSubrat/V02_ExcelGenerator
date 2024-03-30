import os
import mysql.connector
import pandas as pd
import ftplib
import datetime

# Retrieve secrets from GitHub
db_host = os.environ['DB_HOST']
db_port = os.environ['DB_PORT']
db_name = os.environ['DB_NAME']
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']
ftp_host = os.environ['FTP_HOST']
ftp_user = os.environ['FTP_USER']
ftp_password = os.environ['FTP_PASSWORD']
ftp_path = os.environ['FTP_PATH']

try:
    print('Script Running...')
    # Updated to match the new schema
    df = pd.DataFrame(columns=['ID', 'Tutor Name', 'End Date', 'Session Type', 'Student First Name',
                               'Student Middle Name', 'Student Last Name', 'Parent First Name', 'Parent Second Name',
                               'Grade', 'Class Status', 'Comments', 'Start Time', 'End Time', 'Duration (Hrs)',
                               'Meeting ID', 'Amount', 'Subject', 'Topic', 'Homework Status', 'Homework Assigned',
                               'Test Conducted', 'Test Score', 'Country', 'Meeting Link', 'Created At'])
    cnx = mysql.connector.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )
    cursor = cnx.cursor()
    print('Connection Established')
    query = ("SELECT id, tutor_name, end_date, session_type, student_first, student_mid, student_last, parent_first, parent_sec, grade, class_status, comments, start_time, end_time, duration, meeting_id, amount, subject, topic, homework_status, homework_assigned, test_conducted, test_score, country, meeting_link, created_at FROM tutor_sessions ORDER BY id DESC LIMIT 10000")
    cursor.execute(query)
    for row in cursor:
        # Update the DataFrame row directly with the fetched data
        df.loc[len(df.index)] = row

    # Replace any unwanted characters
    df = df.replace({'': ''}, regex=True)
    
    # Convert 'Start Time' and 'End Time' to datetime, and recalculate 'Duration (Hrs)'
    df['Start Time'] = pd.to_datetime(df['Start Time'], format='%H:%M:%S')
    df['End Time'] = pd.to_datetime(df['End Time'], format='%H:%M:%S')
    df['Duration (Hrs)'] = (df['End Time'] - df['Start Time']).dt.seconds / 3600

    # Export to Excel
    df.to_excel("Meeting Data.xlsx", index=False)
    current_timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    print('Excel File Generated')

    cursor.close()
    cnx.close()

    session = ftplib.FTP(ftp_host, ftp_user, ftp_password)
    session.cwd(ftp_path)

    with open("Meeting Data.xlsx", 'rb') as file:
        session.storbinary('STOR Meeting_Data_' + current_timestamp + '.xlsx', file)
    
    session.quit()
    print('Excel File uploaded to the Server.')
except Exception as e:
    print(e)
