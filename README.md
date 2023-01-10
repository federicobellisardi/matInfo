# matInfo

## Usage:

~/desktop/phd/tutorato/matInfo/script$ python report_correction.py -c ../config/conf.json -sf -df -w -ms

## Configuration file Template:
{\
  "relazione_n" : "I",\
  "matInfo" : "*/home/fede/desktop/phd/tutorato/MatInfo/AA_2022_2023*",

  "username" : "mail address",\
  "pwd" : "pass generated for application"\
}

## Options
- create students folder -> sf
- marks dataframe creation -> df
- send warning mail to missing students -> w
- send mail to students with marks  -> ms

## Structure
Read all files downloaded from mails' attachment and create folder for each student that send the report. 
Check if there are students that didn't send the report and create a list of them. Send an email to those people to push for sending it.
Create a dataframe with all the students and an empty column to be filled with marks and finally send to each student an email with the corresponding grade.