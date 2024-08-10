from selenium.webdriver.common.by import By
from tools import (set_up_driver_instance,delete_cache,terminate_driver_process,reduce_week_selected,
                   send_email,MyCustomThread)
from brain import CheckPattern, LoginUser,PlayGame
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        StaleElementReferenceException, TimeoutException,
                                        NoSuchElementException)
from dotenv import load_dotenv
import multiprocessing as mp
import time,os,math

def play_bot():
    LEAGUE={"name":"bundliga","num_of_weeks":34}
    LOOP_LENGTH=math.ceil(LEAGUE["num_of_weeks"]/4)+1
    # LOOP_LENGTH=4
    game_result={}
    print(" \nStarting a NEW SEASON\n ")
    try:
        for n in range(LOOP_LENGTH):  # 9 being the number of 4 weeks in 34 weeks 
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

            time.sleep(5)
            # game_play.choose_market()
            if n==LOOP_LENGTH-1:
                week_to_check=34 if int(reduced_week_selected[5:])-2 == 0 else int(reduced_week_selected[5:])-2
                current_result=pattern.check_result(length="last 4",games_selected=selected_games,latest_week=f"Week {week_to_check}") 
                game_result.update(current_result)
                print(f"Final game_result: {game_result}")
                break
            elif n != 0:
                current_result=pattern.check_result(length="last 4",games_selected=selected_games,latest_week=reduced_week_selected) 
                game_result.update(current_result)
                if n==LOOP_LENGTH-2:
                    play_length=2
                else:
                    play_length=4

                # print(f"this is game_result: {game_result}")
            else:
                browser=pattern.check_result(length="new season")
                play_length=4
            game_play=PlayGame(driver=browser,market="o/u 2.5")
            output=game_play.select_games_to_play(length=play_length)
            selected_games=output['selected_games']
            last_available_week=output['last_available_week']
            reduced_week_selected=reduce_week_selected(last_available_week,by=0,league=LEAGUE["name"])  
            # print(f"this is selected_games: {selected_games}")
            delete_cache(browser)
            time.sleep(5)
            terminate_driver_process(browser)

            # modifies time to sleep in respect to end of season
            if n==LOOP_LENGTH-2:
                time_to_sleep=3*60
            else:
                time_to_sleep=9*60
            print(f"i am waiting for {time_to_sleep}secs")
            time.sleep(time_to_sleep)

        summarized_result={}
        for k,v in game_result.items():
            try:
                current_score=v["ft_score"]
                if summarized_result.get(current_score)!=None:
                    summarized_result[current_score]+=1
                else:
                    summarized_result[current_score]=1
            except KeyError:
                # game_result.pop(k)
                # del game_result[k]
                pass

        pattern_list=["1 - 0","0 - 1","1 - 1","2 - 1","1 - 2","2 - 2"]
        pattern_scores={}
        for score in pattern_list:
            pattern_scores[score]=summarized_result.get(score)
        print(f"Summarized Result: {summarized_result}")
        print(f"PATTERN SCORES: {pattern_scores}")
        send_email(Email=os.environ.get("EMAIL_USERNAME"),
                    Password=os.environ.get("EMAIL_PASSWORD"),
                    Subject="SEASON FINISHED",
                    Message=f"PATTERN SCORES: {pattern_scores}\nSummarized Result: {summarized_result}\nFull Result: {game_result}"
                    )
    except Exception as error:
        print(f"An error occured this SEASON. The Error: {error}")
        pass
    

if __name__=="__main__":
    while True:
        if os.environ.get("OPERATING_SYSTEM")=="windows":
            os.system(f"taskkill /f /t /im chrome.exe")  # Windows OS: to kill all process with the given process_name 
        elif os.environ.get("OPERATING_SYSTEM")=="linux":
            os.system(f"killall chrome")   # Linux OS: to kill all process with the given process_name
        play_bot()
        # bot=mp.Process(target=play_bot,daemon=True)
        bot=MyCustomThread(target=play_bot,daemon=True)
        bot.start()
        bot.join()
        if bot.error:
            print(bot.error)
        # bot.terminate()
        print('bot terminated')