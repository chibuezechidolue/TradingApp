from dotenv import load_dotenv
import imaplib, email, os
import datetime

load_dotenv()
 
#  Sat, 10 Aug 2024 17:18:23
    

SINCE_DATE="10-Aug-2024"
# SINCE_DATE="14-Jun-2024
# EXCLUDE_DATE="13 Jun 2024"" 
EXCLUDE_DATE="09 Aug 2024"
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
        msg_date=msg_date[:25]
        msg_object['date']= datetime.datetime.strptime(msg_date,"%a, %d %b %Y %H:%M:%S")
    # to convert string to date time object for sorting the list
        msg_object['msg']=msg
        msg_object_copy=msg_object.copy()
        msgs.append(msg_object_copy)
        # count+=1
        # if count==16:
        #     break
    # msgs.sort(reverse=True,key=lambda r:r['date'])
    msgs.sort(reverse=False,key=lambda r:r['date'])
    return msgs


# this is done to make SSL connection with GMAIL
con = imaplib.IMAP4_SSL(imap_url) 
 
# logging the user in
response=con.login(os.environ.get("EMAIL_USERNAME"), os.environ.get("EMAIL_PASSWORD")) 
print(response) 
# calling function to check for email under this label
result=con.select('INBOX') 
print(result)
 
 # fetching emails from this user "tu**h*****1@gmail.com"
# msgs = get_emails(search('FROM', os.environ.get("EMAIL_USERNAME"), con))

msgs = get_emails(search('SINCE', SINCE_DATE, con))
print(len(msgs))

# for since and before option
# msgs=msgs[:19]  #
# print(len(msgs))  #




none_values=[]
for msg in msgs:
    my_msg=msg['msg']
    # print(my_msg['date'])
    for part in my_msg.walk():
        # print(part.get_content_type())
        if my_msg['date'][5:16]!=EXCLUDE_DATE:
            if part.get_content_type()=="text/plain":
                content=part.get_payload()

                # try:
                #     t=content.split("\n")[0]
                #     current_result=eval(t[16:])
                #     for k,v in current_result.items():
                #         if k in none_values:
                #             if v == None:
                #                 print("You lost")
                #             else:
                #                 none_values.remove(k)
                #                 # print("You won")
                #         if v==None:
                #             # print(k)
                #             none_values.append(k)
                #     print(current_result)
                # except Exception as error:
                #     print(f"an error occured. this is the error {error}")
                #     pass

                # print(content)
                try:
                    t=content.split("Full Result: ")
                    current_result=eval(t[1])
                    draw_count=0
                    is_draw=False
                    length=0
                    for k,v in current_result.items():
                        if v['avg_diff']==0.020000000000000018:
                            length+=1
                            ft_score=v["ft_score"]
                            if int(ft_score[0])==int(ft_score[4]):
                            # if ft_score == "1 - 1":
                            # if int(ft_score[0])+int(ft_score[4])==1:
                            # if int(ft_score[0])+int(ft_score[4])==1 or ft_score == "1 - 1":
                            # if ft_score == "0 - 1" or ft_score == "1 - 1":
                            # if int(ft_score[0])>int(ft_score[4]):
                                draw_count+=1
                                print("Yessssssss")
                                # print(k,v["ft_score"])
                    if draw_count>0:
                        is_draw=True
                    # else:
                        # print(my_msg['date'])
                    print(f"{is_draw},{draw_count} in {length}")
                except Exception as error:
                    print(f"an error occured. this is the error {error}")
                    pass

