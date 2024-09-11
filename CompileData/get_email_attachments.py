import sys,os
# inorder to use absolute path in importing  set_up_driver_instance
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from dotenv import load_dotenv
from tools import set_up_driver_instance  
from compiling_tools import (print_both,read_saved_pages,get_emails,search)
import imaplib


load_dotenv()




SINCE_DATE="19-Apr-2024" #27
# SINCE_DATE="14-Jun-2024
# EXCLUDE_DATE="06 Jun 2024"" 
EXCLUDE_DATE="18 Apr 2024"
imap_url = 'imap.gmail.com'
 

 

# this is done to make SSL connection with GMAIL
con = imaplib.IMAP4_SSL(imap_url) 
 
# logging the user in
response=con.login(os.environ.get("EMAIL_USERNAME"), os.environ.get("EMAIL_PASSWORD")) 
print_both(response) 
# calling function to check for email under this label
result=con.select('FullSeason') 
print_both(result)

 
 # fetching emails from this user "tu**h*****1@gmail.com"
# msgs = get_emails(search('FROM', os.environ.get("EMAIL_USERNAME"), con))

msgs = get_emails(con,search('SINCE', SINCE_DATE, con))
# msgs=get_emails('ALL')
print_both(len(msgs))

# for since and before option
# msgs=msgs[:19]  #
# print_both(len(msgs))  #




for msg in msgs:
    my_msg=msg['msg']
    print_both(my_msg['date'])
    download_folder="./saved_pages"
    try:
        if my_msg['date'][5:16]!=EXCLUDE_DATE:
            for part in my_msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue

                filename = part.get_filename()
                att_path = os.path.join(download_folder, filename)

                with open(att_path,'wb') as html_file:
                    html_file.write(part.get_payload(decode=True))

            read_saved_pages()
    except Exception as error:
        print_both(f'this is the error: {error}')
        pass



