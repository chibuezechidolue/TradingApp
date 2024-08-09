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

    games_to_check=LEAGUE["num_of_weeks"] - MAX_AMOUNT_LENGTH

    game_play=PlayGame(driver=browser,market="o/u 2.5")
    # game_play.choose_market()

    user=LoginUser(driver=browser,username=os.environ.get("BETKING_USERNAME"),
                password=os.environ.get("BETKING_PASSWORD"))
    acc_bal=user.login()

    games_won=0
    total_amount_won=0
    for n in range(34):
        output=game_play.select_games_to_play()
        selected_games=output['selected_games']
        week_selected=output['week_selected']
        reduced_week_selected=reduce_week_selected(week_selected,by=0,league=LEAGUE["name"])        
        # print(selected_games)
        # acc_bal='4,000'
        acc_bal=game_play.place_the_bet(amount=50,test=os.environ.get('TEST'))
        output=pattern.check_result(games_selected=selected_games,latest_week=reduced_week_selected,acc_balance=acc_bal)
        result=output[0]
        possible_win=output[1]
        if result['outcome']=="WON":
            games_won+=1
            total_amount_won+=possible_win
            print(f"current_win_count: {games_won}")
            print(f"current total_money_won: {total_amount_won}")
    
    delete_cache(browser)
    time.sleep(5)
    terminate_driver_process(browser)

    print(f"Total Games Won: {games_won}")
    print(f"Total Money Won: {total_amount_won}")
    print(f"Net Profit: {total_amount_won-1700}")
    send_email(Email=os.environ.get("EMAIL_USERNAME"),
                Password=os.environ.get("EMAIL_PASSWORD"),
                Subject="SEASON FINISHED",
                Message=f"Total Games Won: {games_won}\nTotal Money Won: {total_amount_won}\nNet Profit: {total_amount_won-1700}"
                )
    

if __name__=="__main__":
     while True:
        # bot=mp.Process(target=start_bot,args=(count,),daemon=True)
        bot=MyCustomThread(target=play_bot,daemon=True)
        bot.start()
        bot.join()
        # bot.terminate()
        print('bot terminated')