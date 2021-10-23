
#------------------------------------#
# Importing libraries
#------------------------------------#
import pandas as pd
import numpy as np
import datetime
import xlsxwriter

#------------------------------------#
# loading the data
# This data was uploaded into the cloud to easily access it remotely
#------------------------------------#
url= "https://drive.google.com/file/d/1Q5YnZ1ZyGPZ5hBVNny5efZPjeD9iYHZV/view?usp=sharing"
path = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]
joined = pd.read_csv(path,                   
                  header=0, 
                  sep=',')

#--------------------------------------------#
# Creating temp tables to extract statistics
#--------------------------------------------#
# drop segment column since all the records belong to Segment A now
joined.drop(['segment','customer_id','campaign_id'], axis=1, inplace=True)

# change type to datetime to extract week numbers and years
joined['date'] = pd.to_datetime(joined['date'])
joined.sort_values('date',inplace=True)

temp=[]
for date in joined['date']:
    if date.year == 2017:
        temp.append(f'Week {int(date.strftime("%U"))} {date.year}')
    elif date.year == 2018:
        temp.append(f'Week {int(date.strftime("%W"))} {date.year}')
joined['week&year'] = temp

# Create Gross Revenue column
joined['Gross Revenue'] = joined['cost'] + joined['datacost'] + joined['revenue']

# Create an aggregate average and sum table since all the stats requested are on date level not clients' level
# Move date index to a column to use it splitting the years                    
df_average= joined.groupby('week&year', sort= False).mean().copy().reset_index()
df_sum= joined.groupby('week&year', sort= False).sum().copy().reset_index()

# Create Margin percentage for each week of the year ( = net/gross)
df_average['Margin %'] = df_average['revenue'] / df_average['Gross Revenue']*100
df_sum['Margin %'] = df_sum['revenue'] / df_sum['Gross Revenue']*100                 

#--------------------------------------------#
# Process tables and prepare the statistics
#--------------------------------------------#

# Create a new table to hold the needed statistics for all periods
df= pd.DataFrame()
# Create the year and week columns
df= df_average[['week&year']].copy()
# Total Gross Revenue for each week of the year  [cost + datacost + revenue ]
df['Total Gross Revenue'] = df_sum['Gross Revenue']

# Daily Average Gross Revenue for each week of the year
df['Daily AVG Gross Revenue'] = df_average['Gross Revenue'].copy()

# Total Net Revenue for each week of the year. Net Revenue is calculated as [ = revenue ]
df['Total Net Revenue'] = df_sum['revenue'].copy()

# Daily Average Net Revenue for each week of the year
df['Daily AVG Net Revenue'] = df_average['revenue'].copy()

# Margin percentage for each week of the year ( = net/gross). Margin is calculated as [ = net revenue / (cost + datacost + revenue) ]
df['Margin%'] = df_sum['Margin %'].copy()*100

# Period-over-Period growth percentage for net and gross for each week of the year (e.g. Week 4 2018 vs. Week 3 2018). Growth calculation is [ = (current period - comparison period) / comparison period ]

for i in range(1, len(df)):
    df.loc[i, 'Weekly Net Revenue Growth %'] = (df.loc[i, 'Total Net Revenue'] - df.loc[i-1, 'Total Net Revenue']) / df.loc[i-1, 'Total Net Revenue']*100
    df.loc[i, 'Weekly Net Gross Growth %'] = (df.loc[i, 'Total Gross Revenue'] - df.loc[i-1, 'Total Gross Revenue']) / df.loc[i-1, 'Total Gross Revenue']*100

df= df.style.set_precision(0)

#--------------------------------------------#
# Prepare year to year stats                    
#--------------------------------------------#                     

# Create a new table for year-over-year comparison
#only data up until September 23rd 2017 is used
temp_2017 = joined[(joined['date'] <= '23-09-2017') & (joined['date'] >= '01-01-2017')]
temp_2018 = joined[(joined['date'] <= '23-09-2018') & (joined['date'] >= '01-01-2018')]

# Split the table to 2017 and 2018 tables, aggregate them to weekly data
df_sum2017= temp_2017.groupby('week&year', sort= False).sum().copy().reset_index()
df_sum2018= temp_2018.groupby('week&year', sort= False).sum().copy().reset_index()

# Rename columns and add 2018 columns to 2017's side by side
# Calculating Margin % column
df_sum2017['Margin %'] = df_sum2017['revenue']/df_sum2017['Gross Revenue']*100
df_sum2018['Margin %'] = df_sum2018['revenue']/df_sum2018['Gross Revenue']*100

df_sum2017.columns = [f'2017 {column}' for column in df_sum2017.columns]

yearly_df= df_sum2017

for i in range(0,len(df_sum2017)):
    for column in df_sum2018.columns:
        yearly_df[f'2018 {column}']= df_sum2018[column]

# Year-over-Year growth percentage for each week of the year, for net and gross (e.g. Week 21 2018 vs Week 21 2017).
for i in range(1, len(yearly_df)):
    yearly_df.loc[i, 'Yearly Net Revenue Growth %'] = (yearly_df.loc[i, '2018 revenue'] - yearly_df.loc[i, '2017 revenue']) / yearly_df.loc[i, '2017 revenue'] *100
    yearly_df.loc[i, 'Yearly Net Gross Growth %'] = (yearly_df.loc[i, '2018 Gross Revenue'] - yearly_df.loc[i, '2017 Gross Revenue']) / yearly_df.loc[i, '2017 Gross Revenue'] *100

yearly_df= yearly_df.style.set_precision(0)                    

summary1 = yearly_df.data.describe()
summary2 = df.data.describe()                    
#--------------------------------------------#
# Save and export statistics to an Excel file                    
#--------------------------------------------#            


# Create a Pandas Excel writer using XlsxWriter as the engine
writer = pd.ExcelWriter('/usr/src/app/output/Analytics_Report.xlsx', engine='xlsxwriter')

# Write each dataframe to a different sheet as per the requirements
df.to_excel(writer, sheet_name='Weekly_Stats')
yearly_df.to_excel(writer, sheet_name='Yearly_Stats')
summary1.to_excel(writer, sheet_name='Summary_Yearly_Stats')
summary2.to_excel(writer, sheet_name='Summary_Weekly_Stats')                    

# Close the Excel writer and save the Excel file
writer.save()

print('docker container ran successfully and statistics were saved in current directory or the mounted directory as "Analytics_Report.xlsx')


#--------------------------------------------#
# Send email attachment                    
#--------------------------------------------#  


# https://github.com/sendgrid/sendgrid-python

import base64
import os
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName,
    FileType, Disposition, ContentId)
from sendgrid import SendGridAPIClient

message = Mail(
    from_email='isaac-ca@outlook.com',
    to_emails='isaac-ca@outlook.com',
    subject='Sending with Twilio SendGrid API',
    html_content='<strong>Python, test API</strong>')
file_path = 'example.pdf'
with open('/usr/src/app/output/Analytics_Report.xlsx', 'rb') as f:
    data = f.read()
    f.close()
encoded = base64.b64encode(data).decode()
attachment = Attachment()
attachment.file_content = FileContent(encoded)
attachment.file_name = FileName('Analytics_Report.xlsx')
attachment.file_type = FileType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
attachment.disposition = Disposition('attachment')
attachment.content_id = ContentId('Example Content ID')
message.attachment = attachment
try:
    sendgrid_client = SendGridAPIClient(os.environ.get("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"))
    response = sendgrid_client.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print("Sorry we couldn't send an email with an attached report now! Don't worry, this can be resolved with few code adjustments", "for your reference, this is the error message:" , e.body)
