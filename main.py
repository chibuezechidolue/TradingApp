from selenium.webdriver.common.by import By
from tools import (set_up_driver_instance,delete_cache,terminate_driver_process,reduce_week_selected,
                   send_email,MyCustomThread)
from brain import CheckPattern, LoginUser,PlayGame
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        StaleElementReferenceException, TimeoutException,
                                        NoSuchElementException)
from dotenv import load_dotenv
import time,os

def play_bot():
    MAX_AMOUNT_LENGTH=14
    LEAGUE={"name":"bundliga","num_of_weeks":34}
    game_result={}
    print(" \nStarting a NEW SEASON\n ")
    for n in range(9):  # 9 being the number of 4 weeks in 34 weeks 
        browser=set_up_driver_instance()       # driver instance without User Interface (--headless)
        print(f"checking week {n*4+1} to week {n*4+4}")
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

        games_to_check=LEAGUE["num_of_weeks"] - MAX_AMOUNT_LENGTH
        time.sleep(5)

        game_play=PlayGame(driver=browser,market="o/u 2.5")
        # game_play.choose_market()
        if n != 0:
            current_result=pattern.check_result(games_selected=selected_games,latest_week=reduced_week_selected,acc_balance=acc_bal)  #NOTE: change the output of check rsult
            game_result.update(current_result)
            print(f"this is gamse_result: {game_result}")
        
        output=game_play.select_games_to_play()
        selected_games=output['selected_games']
        last_available_week=output['last_available_week']
        reduced_week_selected=reduce_week_selected(last_available_week,by=0,league=LEAGUE["name"])        
        # print(selected_games)
        acc_bal='4,000'
        print(f"this is selected_games: {selected_games}")
        delete_cache(browser)
        time.sleep(5)
        terminate_driver_process(browser)

        time_to_sleep=9*60
        print(f"i am waiting for {time_to_sleep}secs")
        time.sleep(time_to_sleep)

    summarized_result={}
    for k,v in game_result.items():
        if summarized_result.get(v["ft_score"])!=None:
            summarized_result[v["ft_score"]]+=1
        else:
            summarized_result[v["ft_score"]]=1
    print(summarized_result)
    send_email(Email=os.environ.get("EMAIL_USERNAME"),
                Password=os.environ.get("EMAIL_PASSWORD"),
                Subject="SEASON FINISHED",
                Message=f"Summarized Result: {summarized_result}\nFull Result: {game_result}"
                )
    

if __name__=="__main__":
    # while True:
    os.system(f"taskkill /f /t /im chrome.exe")
    play_bot()
    # bot=mp.Process(target=start_bot,args=(count,),daemon=True)
    # bot=MyCustomThread(target=play_bot,daemon=True)
    # bot.start()
    # bot.join()
    # if bot.error:
    #     print(bot.error)
    # # bot.terminate()
    # print('bot terminated')