from dotenv import load_dotenv
from compiling_tools import (print_both,get_emails,search)

import imaplib, os

load_dotenv()
 


def check_ht_ft(ht_score,ft_score):
    ht_home=int(ht_score[0])
    ht_away=int(ht_score[4])
    ft_home=int(ft_score[0])
    ft_away=int(ft_score[4])
    result=None
    
    if ft_home==ft_away and (ht_home>ht_away or ht_home<ht_away):
        result="2/X"
    # if ht_home==ht_away and (ft_home>ft_away or ft_home<ft_away):
    #     result="X/2"
    # if ht_home==ht_away and ft_home==ft_away:
    #     result="X/X"
    # if ft_home==ft_away:
    #     result="X"
    # if ht_home==ht_away:
    #     result="X"
    # if ht_home==ht_away and ft_home>ft_away:
    #     result="X/1"

    # if ht_home==ht_away and ft_home<ft_away:
    #     result="X/2"
    # if ft_home==ft_away and ht_home<ht_away:
    #     result="2/X"
    # if (ht_home<ht_away and ft_home>ft_away) or (ht_home>ht_away and ft_home<ft_away) :
    #     result="2/X"
    
    return result


def check_content(content,type:str):
    if type=="ft":
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
                        break
                # if length==12:
                #     break
                        # print(k,v["ft_score"])
            if draw_count>0:
                is_draw=True
            else:
                print(my_msg['date'])
            print(f"{is_draw},{draw_count} in {length}")
        except Exception as error:
            print(f"an error occured. this is the error {error}")
            pass
    elif type=="ht":
        try:
            t=content.split("Full Result: ")
            current_result=eval(t[1])
            draw_count=0
            is_draw=False
            length=0
            score_odds={"1 - 0": 5.43,"0 - 1": 5.41,"2 - 0": 14.5,"0 - 2": 14.5,"2 - 1": 17.1,"1 - 2": 16.7,}
            score_odds={"1/X":16.7,"2/X":16.6,"X/1":8.11,"X/2":8.05,"X/X":5.36,"1/1":4.43,"2/2":4.38}
            # score_list=[50,50,50,50,100,100,150,150,250,250,350,400]
            score_list=[16.66,16.66,33.33,50,66.66,100,150,233.33,350,533.33,800,1200]
            # score_list=[25,25,25,25,25,25,50,50,50,75,75,75]
            profit=0
            for k,v in current_result.items():
                # if v['avg_diff']==0.020000000000000018:
                if v['avg_diff']:
                    length+=1
                    ht_score=v.get("ht_score")
                    ft_score=v.get("ft_score")
                    # if int(ht_score[0])>0 and int(ht_score[4])>0:
                    # if score_odds.get(ht_score)!=None:
                    #     if score_odds.get(ht_score)<6: 
                    #         profit+=score_odds.get(ht_score)*20
                    #     else:
                    #         profit+=score_odds.get(ht_score)*5
                        # print(f"You WON: {score_odds.get(ht_score)*10}")
                    # else:
                    #     profit-=80
                        # print(f"You LOST: {80}")
                    # if ht_score == "0 - 0":
                    # if ht_score == "2 - 1" or ht_score == "1 - 2":
                    if ft_score == "1 - 2" or ft_score == "2 - 1"  :
                    # if (int(ht_score[0])>int(ht_score[4]) and int(ft_score[0])<int(ft_score[4])) or (int(ht_score[0])<int(ht_score[4]) and int(ft_score[0])>int(ft_score[4])):
                        # profit+=score_odds.get(ht_score)*score_list[length-1]
                        # draw_count+=1
                        # break
                    # result=check_ht_ft(ht_score=ht_score,ft_score=ft_score)
                    # if result != None:
                    # if result != None:
                    #     profit+=9*score_list[length-1]
                        draw_count+=1
                        # print(ht_score,ft_score,result)
                        # print(9,score_list[length-1])
                        # break
                    
                    
                # if length==30:
                #     break
            # print(profit - sum(score_list[:length])*3)

            if draw_count>0:
                is_draw=True
            # else:
            #     print(my_msg['date'])
            print(f"{is_draw},{draw_count} in {length}")
        except Exception as error:
            print(f"an error occured. this is the error {error}")
            pass



#  Sat, 10 Aug 2024 17:18:23


SINCE_DATE="1-Sep-2024"           # SINCE_DATE="14-Jun-2024        
EXCLUDE_DATE="18 Aug 2024"         # EXCLUDE_DATE="13 Jun 2024""
imap_url = 'imap.gmail.com'

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

msgs = get_emails(con,search('SINCE', SINCE_DATE, con))
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

                # check_content(content=content,type="ft")
                check_content(content=content,type="ht")

