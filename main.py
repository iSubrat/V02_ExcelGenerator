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
    df = pd.DataFrame(columns=['ID', 'Date', 'Time', 'Meeting ID', 'Tutor Name', 'Session Type', 'Student First Name',
                                'Student Middle Name', 'Student Last Name', 'Parent First Name', 'Parent Last Name',
                                'Grade', 'Class Status', 'Comments', 'Start Time', 'Duration (Hrs)', 'Amount', 'Subject',
                                'Topic', 'Status of last Assigned Homework', 'Homework Assigned', 'Test Conducted',
                                'Test Score', 'Country', 'Meeting Link'])
    cnx = mysql.connector.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )
    cursor = cnx.cursor()
    print('Connection Established')
    query = ("SELECT * FROM teacher_date ORDER BY Id DESC LIMIT 10000")
    cursor.execute(query)
    for i in cursor:
        df.loc[len(df.index)] = i
    for i in range(len(df)):
        end_time = df.at[i, 'Time']
        start_time = df.at[i, 'Start Time']
        duration = end_time - start_time
        df.at[i, 'Duration (Hrs)'] = duration
    df = df.replace({'': ''}, regex=True)
    df.to_excel("Meeting Data.xlsx", index=False)
    current_timestamp = datetime.datetime.now().strftime("%I_%M%p on %B %d, %Y")
    print('Excel File Generated')
    cursor.close()
    cnx.close()
    session = ftplib.FTP(ftp_host, ftp_user, ftp_password)
    session.cwd(ftp_path)
    
    if datetime.datetime.now() <= datetime.datetime(2024, 4, 5): # Year, Month, Day
        with open("Meeting Data.xlsx", 'rb') as file:
            session.storbinary('STOR Meeting Data.xlsx', file)

    with open("Meeting Data.xlsx", 'rb') as file:
        session.storbinary(f'STOR Backup_Meeting_Data_{current_timestamp}.xlsx', file)
    session.quit()
    print('Excel File uploaded to the Server.')
except Exception as e:
    print(e)
