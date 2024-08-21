from selenium.webdriver.common.by import By
from tools import (set_up_driver_instance,delete_cache,terminate_driver_process,reduce_week_selected,
                   send_email,MyCustomThread)
from brain import CheckPattern, LoginUser,PlayGame
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        StaleElementReferenceException, TimeoutException,
                                        NoSuchElementException)
from dotenv import load_dotenv
import time,os
load_dotenv()

def play_bot():
    MAX_AMOUNT_LENGTH=14
    LEAGUE={"name":"bundliga","num_of_weeks":34}
    browser=set_up_driver_instance()       # driver instance without User Interface (--headless)
    print(" \nStarting a NEW SEASON\n ")
    try:
        browser.get("https://m.betking.com/")
    except:
        pass

    try:
        pattern=CheckPattern(browser)
        pattern.checkout_virtual(league=LEAGUE["name"])
    except:
        try:
            browser.get("https://m.betking.com/virtual/league/kings-bundliga")  
        except:
            delete_cache(browser)
            time.sleep(5)
            terminate_driver_process(browser)
            # browser.quit()
            browser=set_up_driver_instance()       # driver instance without User Interface (--headless)
            browser.get("http://m.betking.com/virtual/league/kings-bundliga")

    time.sleep(3)
    # browser=pattern.check_result(length='new season')

    game_play=PlayGame(driver=browser,market="o/u 2.5")

    user=LoginUser(driver=browser,username=os.environ.get("BETKING_USERNAME"),
                password=os.environ.get("BETKING_PASSWORD"))
    acc_bal=user.login()


    total_amount_won=0
    # amount_list=[50,50,50,50,50,50,50,100,100,100,100,120,150,170,190,215,240,275,320,370,420,480,
    #             550,625,720,830,935,1080,1230,1410,1605,1830,2090,2390]
    amount_list=[100, 100, 100, 100, 100, 100, 100, 200, 200, 200, 200, 240, 300, 340, 380, 430, 480, 550, 640, 740]
    for n in range(34):
        output=game_play.select_games_to_play(amount=amount_list[n])
        selected_games=output['selected_games']
        week_selected=output['week_selected']
        acc_bal=output['acc_bal']
        potential_win=output['potential_win']
        reduced_week_selected=reduce_week_selected(week_selected,by=0,league=LEAGUE["name"])        
        # acc_bal='4,000'
        output=pattern.check_result(games_selected=selected_games,latest_week=reduced_week_selected,acc_balance=acc_bal)
        result=output
        if result['outcome']=="WON":
            total_amount_won=potential_win
            break
    
    delete_cache(browser)
    time.sleep(5)
    terminate_driver_process(browser)
    total_funds_staked=sum(amount_list[:n+1])
    send_email(Email=os.environ.get("EMAIL_USERNAME"),
                Password=os.environ.get("EMAIL_PASSWORD"),
                Subject="SEASON FINISHED",
                Message=f"Total Money Staked: {total_funds_staked}\nTotal Money Won: {total_amount_won}\nNet Profit: {float(total_amount_won.strip('₦').replace(',','')) - total_funds_staked}"
                )
    

if __name__=="__main__":
    #  while True:
    if os.environ.get("OPERATING_SYSTEM")=="windows":
        os.system(f"taskkill /f /t /im chrome.exe")  # Windows OS: to kill all process with the given process_name 
    elif os.environ.get("OPERATING_SYSTEM")=="linux":
        os.system(f"killall chrome")   # Linux OS: to kill all process with the given process_name
    play_bot()
        # bot=mp.Process(target=start_bot,args=(count,),daemon=True)
        # bot=MyCustomThread(target=play_bot,daemon=True)
        # bot.start()
        # bot.join()
        # if bot.error:
        #     print(bot.error)
        # # bot.terminate()
        # print('bot terminated')