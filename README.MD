# MySQLdump File To Analytical Report using Docker
This docker file runs a python code -v 3.8 to download a table from the web, then process it to generate an excel file with 4 sheets. 

## The program generates an analytical report with 4 sheets as follows:
- Weekly_Stats <= Weekly statistics
- Yearly_Stats <= year-over-year statistics comparison
- Summary_Yearly_Stats <= summary table for the yearly stats table
- Summary_Weekly_Stats <= summary table for the weekly stats table

## Files
- Dockerfile
- requirements.txt
- financial_data_analysis.py
- readme.txt
- Analytics_Report <= sample generated report


## Instructions
Please follow below example code to get the intended output from the program.

Example:
- To build the container
Save the files (Dockerfile, requirements.txt, financial_data_analysis.py) in one directory and run the following inside the same directory

	$ docker build --tag ryan/mysqldump-docker:1 .

- To run the container and save the output file to Downloads directory on your host machine
After building the image, you need to run it while mounting one of your directories on your host machine to the directory where the generated report is saved on. If the file runs without error, you should see the file in the mounted folder. Make sure you have write permission for the selected directory path.
	
	$ docker run -it -v ~/Downloads:/usr/src/app/output ryan/sql_mysqldump-docker:1

- Compress and save the container image:
You can save the built image and run it somewhere else directly from a compressed .tar.gz file.

	$ docker save ryan/python-docker:1 | gzip > isaac_docker_mysqldump.tar.gz

- Unzip and load isaac_docker_mysqldump.tar.gz
To load this file in a Linux environment, make sure you have docker installed and run the following in the same directory

	$ docker load < isaac_docker_mysqldump.tar.gz

### Codes to load mysqldump file in a ubuntu Linux environment
Before running MySQL, you need to make sure that you have mysql-server installed on your machine. In a command line interface, in a ubuntu environment, you can use following codes or read the documentation page https://ubuntu.com/server/docs/databases-mysql:

	$ sudo apt-get install mysql-server
	$ sudo systemctl start mysql <= to start the service if it does not start automatically
	$ /usr/bin/mysql -u root -p <= to access mysql and start coding
	$> CREATE DATABASE customers_data;
	$> USE customers_data;
	$> SOURCE data_example.sql; <= mysqldump file that you want to load, from the same directory


 Following code was used in MySQL to generate the table that was used in python

	$> CREATE TABLE joined AS
	     (SELECT a.*, b.segment
      		FROM fact_date_customer_campaign a
        	       JOIN dim_customer b
        	            ON a.customer_id = b.customer_id
      		WHERE b.segment = 'Segment A'
      		  AND a.date < '2018-09-23');

	$> SELECT * FROM joined LIMIT 5; <= to look at the first 5 rows


To connect to the table from any place using a docker container with a python program, the data in the joined table has to be exported and I chose to host it on Google Drive to access it using a public URL in python to retrieve the data. To export the table, you may use the command line or export it directly from MySQL. You have to check for the best parameters to set based on the data and the characters or encoding used. Example codes are provided below:
	
	$ /usr/bin/mysql --user=user --password -h <localhost> --execute "SELECT * FROM customers_data.joined;" > '//<your full directory path>//cust_data.csv'
	$> select * from joined
		into outfile '//<your full directory path>//cust_data.csv'
	  	    fields optionally enclosed by '"'
	    	    terminated by ',' 
			escaped by '\' 
			lines terminated by '\n';	
		
I had challenges in running MySQL environment to export the new table inside docker due to its size, so I exported it using DataGrip, then uploaded it to the cloud to read it in python. The URL link for the data could change as it is hosted on Google drive. If you receive an error related to downloading the data and the URL, you may need to contact me to update the link inside the '.py' python file.
Depending on your settings and MySQL version, you might face some errors in exporting to your file path. you will likely come across "MySQL server is running with the --secure-file-priv option so it cannot execute this statement"  error, you may read more about it on https://stackoverflow.com/questions/32737478/how-should-i-tackle-secure-file-priv-in-mysql

After loading the table in python, financial_data_analysis.py processes the table to generate the desired analytical report. ***SendGrid API is used to send the report as an attachment to an email. The API is removed for public publishing but can be replaced if you create a new API. refer to their website for more details "https://docs.sendgrid.com/for-developers/sending-email/api-getting-started"***


contact email: isaac-ca@outlook.com
