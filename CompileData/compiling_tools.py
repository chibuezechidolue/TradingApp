import sys,os
# inorder to use absolute path in importing  set_up_driver_instance
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from tools import set_up_driver_instance  
import email
import datetime,time
from selenium.webdriver.common.by import By




def print_both(*args):
    """To print on the terminal as well as an output file"""
    with open('output.txt','at') as file:
        to_print = ' '.join([str(arg) for arg in args])
        print(to_print)
        print(to_print, file=file)
        # file.write(to_print)
  

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
def get_emails(con,result_bytes):
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
        if count==10:
            break
    # msgs.sort(reverse=True,key=lambda r:r['date'])
    msgs.sort(reverse=False,key=lambda r:r['date'])
    return msgs



def check_result(ft_scores:list,ht_scores:list,curr_profit:int,curr_sec:int,counts:list,curr_stake,week_ref:list,market:str):
    count=counts[0]
    count2=counts[1]
    # market="3 - 0"
    # ht_scores=ht_scores
    # if score in ht_scores or score[::-1] in ht_scores:
    #     count=ht_scores.count(score)
    #     count2=ht_scores.count(score[::-1])
    #     print_both(f"{score} came {count}, {score[::-1]} came {count2}. TOTAL={count+count2}")
    #     return True
    # else:
    #     return False

    profit=curr_profit
    FIXED_MIN_PROFIT=90
    # FIXED_MIN_PROFIT=20
    level=1
    weekly_stake=week_ref[0]
    total_stake=curr_stake
    weekly_pot_profit=week_ref[1]
    ht_scoress=ht_scores[curr_sec-1:]
    ft_scoress=ft_scores[curr_sec-1:]
    print_both(weekly_stake)
    for i in range(len(ht_scoress)//9):
        start_index=i*9
        end_index=start_index+9
        ht_scores=ht_scoress[start_index:end_index]
        ft_scores=ft_scoress[start_index:end_index]
        per_week=0
        for n in range(len(ht_scores)):
            # current_week=(n+curr_sec)//9 if (n+curr_sec)%9 == 0 else ((n+curr_sec)//9)+1
            current_week=((i+1)*n+curr_sec)//9 if ((i+1)*n+curr_sec)%9 == 0 else (((i+1)*n+curr_sec)//9)+1

            ht_home=int(ht_scores[n][0])
            ht_away=int(ht_scores[n][4])
            ft_home=int(ft_scores[n][0])
            ft_away=int(ft_scores[n][4])

            if market=="X/X":
                if ft_home==ft_away and ht_home==ht_away:
                    count+=1
                    per_week+=1
                    profit+=weekly_pot_profit
            
            elif market=="X/12":
                # print_both(f"{ft_home} - {ft_away}")
                if ft_home>ft_away and ht_home==ht_away:
                    count+=1
                    per_week+=1
                    profit+=weekly_pot_profit
                elif ft_home<ft_away and ht_home==ht_away:
                    count2+=1
                    per_week+=1
                    profit+=weekly_pot_profit
            total_stake+=weekly_stake

        # profit+=per_week*weekly_pot_profit
    
        # if profit > total_stake:
        if (profit - total_stake) >= 40:
            # print_both(current_week)
            print_both(f"This SEASON Profit ={profit - total_stake}")
            print_both(f'OUTCOME came {per_week} in week {current_week}')
            return [True,f"total_profit={profit} - total_staked_amount = {total_stake}",f"X/1 came {count}, X/2 came {count2}. TOTAL={count+count2}",[weekly_stake,weekly_pot_profit],total_stake,[count,count2],profit]
            # break
        print_both(f'OUTCOME came {per_week} in week {current_week}')
        loss=total_stake - profit
        print_both(f"loss{total_stake,profit} =={loss}. loss_range={money_range(amount=loss)}")
        if market=="X/12": weekly_stake=((loss+FIXED_MIN_PROFIT)/9)*2; weekly_pot_profit=weekly_stake*4.5
        elif market=="X/X": weekly_stake=((loss+FIXED_MIN_PROFIT)/6); weekly_pot_profit=(weekly_stake)*5
        print_both(weekly_stake,weekly_pot_profit)
    print_both(current_week)
    print_both(f"curr_profit={profit}, curr_staked= {total_stake}")
    return [False,f"X/1 came {count}, X/2 came {count2}. TOTAL={count+count2}",[weekly_stake,weekly_pot_profit],total_stake,[count,count2],profit]
    # print_both(f"X/1 came {count}, X/2 came {count2}. TOTAL={count+count2}")


def money_range(amount):
    length=len(str(round(abs(amount))))
    if length==7:
        output=f"{str(amount)[0]} million"
    elif length==6:
        output=f"{str(amount)[0]} hundred thousand"
    elif length==5:
        output=f"{str(amount)[:2]} thousand"
    elif length==4:
        output=f"{str(amount)[0]} thousand"
    elif length==3:
        output=f"{str(amount)[0]} hundred"
    else:
        output=str(round(abs(amount)))

    return output


def read_saved_pages():
    # market="X/12"
    market="X/X"
    browser=set_up_driver_instance()
    path='C:/Users/Stanley Chidolue/TradingAPP/CompileData/saved_pages'
    result_pages=[f"{path}/one_to_ten_page.html",f"{path}/eleven_to_twenty_page.html",
                  f"{path}/twentyone_to_thirty_page.html",f"{path}/thirtyone_to_thirtyfour_page.html",]
    ht_scores=[]
    ft_scores=[]
    week_to_save=[10,20,30,34,40]
    sections=[1,91,181,271]
    curr_profit=0
    counts=[0,0]
    curr_stake=0
    level=1
    # weekly_stake=10*2*level
    if market=="X/12": weekly_pot_profit=90*level; weekly_stake=10*2*level
    elif market=="X/X": weekly_pot_profit=50*level; weekly_stake=10*level
    week_ref=[weekly_stake,weekly_pot_profit]
    for n in range(4):
        # browser.set_network_conditions(offline=True, latency=2, throughput=500 * 1024)
        browser.get(result_pages[n])
        # browser.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="results-page-tab-standings"]')))
        time.sleep(5)
        # browser.execute_script("window.stop();")
        current_ht_scores=browser.find_elements(By.CSS_SELECTOR, ".score.ht")[:week_to_save[n]*9]
        current_ft_scores=browser.find_elements(By.CSS_SELECTOR, ".score.ft")[:week_to_save[n]*9]
        for i in range(len(current_ft_scores)):
            current_ht_scores[i]=current_ht_scores[i].text
            current_ft_scores[i]=current_ft_scores[i].text
        if n==3:
            start=6
            print_both(f"this is the len of ft_scores BEFORE adding 36 scores: {len(ft_scores)}")
        else:
            start=0
        ht_scores.extend(current_ht_scores[::-1][start*9:])
        ft_scores.extend(current_ft_scores[::-1][start*9:])
    
        outcome=check_result(ft_scores=ft_scores,ht_scores=ht_scores,curr_profit=curr_profit,curr_sec=sections[n],
                             counts=counts,curr_stake=curr_stake,week_ref=week_ref,market=market)
        curr_profit=outcome[-1]
        counts=outcome[-2]
        curr_stake=outcome[-3]
        week_ref=outcome[2]
        if outcome[0]:
            print_both(outcome[1])
            browser.quit()
            break
    if not outcome[0]:
        print_both('Failed!!!')
        print_both(outcome[1])