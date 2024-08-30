import sys,os
# inorder to use absolute path in importing  set_up_driver_instance
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from dotenv import load_dotenv
from tools import set_up_driver_instance  
import imaplib, email, os
import datetime,time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


load_dotenv()
 
 
    

SINCE_DATE="21-Jul-2024"
# SINCE_DATE="14-Jun-2024
# EXCLUDE_DATE="13 Jun 2024"" 
EXCLUDE_DATE="13 Jul 2024"
imap_url = 'imap.gmail.com'
 
# Function to get email content part i.e its body part
def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)
 
# Function to search for a key value pair 
def search(key, value, con):
    # using only SINCE or BEFORE to filter 
    result, data = con.search(None, key, '"{}"'.format(value))
    # using both SINCE and BEFORE to filter
    # result, data = con.search(None,'(SINCE "24-Jun-2024" BEFORE "26-Jun-2024")' )
    
    # result, data = con.search(None,'(SINCE "17-Apr-2024"  )' )
    # result, data = con.search(None,f'(SINCE {SINCE_DATE}  )' )
    # result, data = con.search(None,"ALL" )  #not sure about the all


    return data
 
# Function to get the list of emails under this label
def get_emails(result_bytes):
    msgs = [] # all the email data are pushed inside an array
    count=0
    for num in result_bytes[0].split():
        typ, data = con.fetch(num, '(RFC822)')

        # create a dictionary so as to sort with date since gmail does not support con.sort()
        msg_object={}
        msg_object_copy={}
        msg=email.message_from_bytes(data[0][1])
        msg_date=""
        for val in msg['Date'].split(' '):
            if(len(val)==1):
                val="0"+val
            # to pad the single date with 0
            msg_date=msg_date+val+" "
        msg_date=msg_date[:-13]
        msg_object['date']= datetime.datetime.strptime(msg_date,"%a, %d %b %Y %H:%M:%S")
    # to convert string to date time object for sorting the list
        msg_object['msg']=msg
        msg_object_copy=msg_object.copy()
        msgs.append(msg_object_copy)
        count+=1
        if count==80:
            break
    # msgs.sort(reverse=True,key=lambda r:r['date'])
    msgs.sort(reverse=False,key=lambda r:r['date'])
    return msgs


# this is done to make SSL connection with GMAIL
con = imaplib.IMAP4_SSL(imap_url) 
 
# logging the user in
response=con.login(os.environ.get("EMAIL_USERNAME"), os.environ.get("EMAIL_PASSWORD")) 
print(response) 
# calling function to check for email under this label
result=con.select('FullSeason') 
print(result)
 
 # fetching emails from this user "tu**h*****1@gmail.com"
# msgs = get_emails(search('FROM', os.environ.get("EMAIL_USERNAME"), con))

msgs = get_emails(search('SINCE', SINCE_DATE, con))
# msgs=get_emails('ALL')
print(len(msgs))

# for since and before option
# msgs=msgs[:19]  #
# print(len(msgs))  #

def check_result(ft_scores:list,ht_scores:list,curr_profit:int,curr_sec:int):
    count=0
    count2=0
    score="3 - 0"
    # ht_scores=ht_scores
    # if score in ht_scores or score[::-1] in ht_scores:
    #     count=ht_scores.count(score)
    #     count2=ht_scores.count(score[::-1])
    #     print(f"{score} came {count}, {score[::-1]} came {count2}. TOTAL={count+count2}")
    #     return True
    # else:
    #     return False

    profit=curr_profit
    level=1
    weekly_stake=180*level
    weekly_pot_profit=80*level
    ht_scores=ht_scores[curr_sec-1:]
    for n in range(len(ht_scores)):
        current_week=(n+curr_sec)//9 if (n+curr_sec)%9 == 0 else ((n+curr_sec)//9)+1
        ht_home=int(ht_scores[n][0])
        ht_away=int(ht_scores[n][4])
        ft_home=int(ft_scores[n][0])
        ft_away=int(ft_scores[n][4])
        # print(f"{ft_home} - {ft_away}")
        if ft_home>ft_away and ht_home==ht_away :
            count+=1
            profit+=weekly_pot_profit
        elif ft_home<ft_away and ht_home==ht_away:
            count2+=1
            profit+=weekly_pot_profit

        if profit > (current_week*weekly_stake):
            print(current_week)
            print(f"This SEASON Profit ={profit - (current_week*weekly_stake)}")
            return [True,f"total_profit={profit} - total_staked_amount = {(current_week*weekly_stake)}",f"X/1 came {count}, X/2 came {count2}. TOTAL={count+count2}",profit]
            # break
    print(current_week)
    print(f"curr_profit={profit}, curr_staked= {(current_week*weekly_stake)}")
    return [False,f"X/1 came {count}, X/2 came {count2}. TOTAL={count+count2}",profit]
    # print(f"X/1 came {count}, X/2 came {count2}. TOTAL={count+count2}")

def read_saved_pages():
    browser=set_up_driver_instance()
    path='C:/Users/Stanley Chidolue/TradingAPP/CompileData/saved_pages'
    result_pages=[f"{path}/one_to_ten_page.html",f"{path}/eleven_to_twenty_page.html",
                  f"{path}/twentyone_to_thirty_page.html",f"{path}/thirtyone_to_thirtyfour_page.html",]
    ht_scores=[]
    ft_scores=[]
    week_to_save=[10,20,30,34,40]
    sections=[1,91,181,271]
    curr_profit=0
    for n in range(4):
        # browser.set_network_conditions(offline=True, latency=2, throughput=500 * 1024)
        browser.get(result_pages[n])
        # browser.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="results-page-tab-standings"]')))
        # time.sleep(5)
        # browser.execute_script("window.stop();")
        current_ht_scores=browser.find_elements(By.CSS_SELECTOR, ".score.ht")[:week_to_save[n]*9]
        current_ft_scores=browser.find_elements(By.CSS_SELECTOR, ".score.ft")[:week_to_save[n]*9]
        for i in range(len(current_ft_scores)):
            current_ht_scores[i]=current_ht_scores[i].text
            current_ft_scores[i]=current_ft_scores[i].text
        if n==3:
            start=6
            print(f"this is the len of ft_scores BEFORE adding 36 scores: {len(ft_scores)}")
        else:
            start=0
        ht_scores.extend(current_ht_scores[::-1][start*9:])
        ft_scores.extend(current_ft_scores[::-1][start*9:])
    
        outcome=check_result(ft_scores=ft_scores,ht_scores=ht_scores,curr_profit=curr_profit,curr_sec=sections[n])
        curr_profit=outcome[-1]
        if outcome[0]:
            print(outcome[1])
            browser.quit()
            break
    if not outcome[0]:
        print('Failed!!!')
        print(outcome[1])


for msg in msgs:
    my_msg=msg['msg']
    print(my_msg['date'])
    download_folder="./saved_pages"
    try:
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
    except:
        pass










        # print(part.get_content_type())
        # if my_msg['date'][5:16]!=EXCLUDE_DATE:
        #     if part.get_content_type()=="text/plain":
        #         content=part.get_payload()

    #             # new_content=content
    #             # print(new_content)
    #             try:
    #                 new_content=content.replace(" ","")[17:]
    #                 exec(new_content)
    #             except SyntaxError:
    #                 try:
    #                     new_content=content.replace(" ","")[22:]
    #                     exec(new_content)
    #                 except Exception as e:
    #                     print(f"this is the exec() error: {e} ")