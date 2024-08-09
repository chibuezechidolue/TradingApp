from itertools import count
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (StaleElementReferenceException,NoSuchElementException,
                                        TimeoutException,ElementClickInterceptedException)
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv

import codecs
import time
import pygsheets 
import datetime
import threading
import os,psutil



def set_up_driver_instance():
    """ To create and return a webdriver object with disabled gpu and headless"""

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    # user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'

    chrome_options = webdriver.ChromeOptions()  # Google Chrome 
    # chrome_options = webdriver.EdgeOptions()      # Microsoft Edge 
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument('--log-level=3') # to stop printing error messages to the console 
    chrome_options.add_argument("start-maximized") # chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--disable-application-cache')
    chrome_options.add_argument('--disable-extensions')
    
    # prefs={'profile.default_content_setting_values': {'images': 2, 'javascript': 2}}
    # prefs = {"profile.managed_default_content_settings.images": 2, "profile.default_content_setting_values.javascript": 2}
    prefs = {'profile.default_content_setting_values': {'images': 2, "stylesheet":2,
                            'plugins': 2, 'popups': 2, 'geolocation': 2, 
                            'notifications': 2, 'auto_select_certificate': 2, 'fullscreen': 2, 
                            'mouselock': 2, 'mixed_script': 2, 'media_stream': 2, 
                            'media_stream_mic': 2, 'media_stream_camera': 2, 'protocol_handlers': 2, 
                            'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2, 
                            'push_messaging': 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop': 2, 
                            'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement': 2, 
                            'durable_storage': 2}}
    chrome_options.add_experimental_option('prefs', prefs)

    # chrome_options.add_argument("--disable-blink-features")
    # chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # chrome_options.add_argument('disable-infobars')


    #emulate a mobile device
    # mobile_emulation = { "deviceName": "Nexus 5" }
#     mobile_emulation = {
#    "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
#    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19",
#    "clientHints": {"platform": "Android", "mobile": True} }
#     chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

                    # To rotate the user agent in order to avoid detection
    # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    # driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
    # print(driver.execute_script("return navigator.userAgent;"))
    return webdriver.Chrome(options=chrome_options)   # Google Chrome
    # return webdriver.Edge(options=chrome_options)       # Microsoft Edge




def delete_cache(driver):
    driver.execute_cdp_cmd('Storage.clearDataForOrigin', {
    "origin": '*',
    "storageTypes": 'all',
    })
    # time.sleep(2)
    driver.delete_all_cookies()
    # time.sleep(2)
    driver.get('chrome://settings/clearBrowserData')  # Open your chrome settings.
    time.sleep(1)
    actions = ActionChains(driver) 
    actions.send_keys(Keys.TAB * 2 + Keys.DOWN * 4 + Keys.TAB * 7 + Keys.ENTER) # Google Chrome 
    # actions.send_keys(Keys.TAB * 2 + Keys.DOWN * 4 + Keys.TAB * 9 + Keys.ENTER) # Microsoft Edge  
    actions.perform()


def terminate_driver_process(browser):
    """Terminates the dirver instance and child processes associated with the driver instance."""
    process_name="chrome.exe"
    # process_name="msedge.exe"
    try:
        # To kill all process with the relating to the giver browser instance
        chrome_driver_id=browser.service.process.pid
        child_processes=psutil.Process(chrome_driver_id).children(recursive=True)
            # kill all chrome driver child processes
        # os.system(f"taskkill /F /PID {chrome_driver_id}")       #Window OS
        # os.system(f"taskkill {chrome_driver_id}")             #Linux OS
        browser.quit()
        for process in child_processes:
            if process.is_running():
                os.system(f"taskkill /F /PID {process.pid}")        #Window OS
                # os.system(f"kill {process.pid}")                  #Linux OS



        # os.system(f"taskkill /f /t /im {process_name}")   # Windows OS: to kill all process with the given process_name 
        
        # os.system(f"kilall {process_name}")   # Linux OS: to kill all process with the given process_name 

                            # OR

        # All OS: to kill all process with the given process_name
        # for process in psutil.process_iter():
        #     if process.name().lower() == process_name.lower():
        #         print(process.name())
        #         process.kill()

    except:
        pass


def cancel_popup(browser):
    """To cancel popup at the landing page"""
    wait=WebDriverWait(driver=browser,timeout=10)
    body=wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body")))
    body.click()
    cancel_body=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-testid="btn-close-header"]')))
    cancel_body.click()


def game_selection_algorithm(available_week_odds)->list: 
    element_list=[]
    for available_odds in available_week_odds:
        draw=100
        selected_home=None
        selected_draw=None
        selected_away=None
        n=0
        for _ in range(int(len(available_odds)/3)):
            current_row=available_odds[n:n+3]
            home=current_row[0]
            x=current_row[1]
            away=current_row[2]
            odd=abs(float(home.text)-float(away.text))
            if odd<draw:
                draw,selected_draw=odd,x
                selected_home,selected_away=home.text,away.text
            n+=3
        element_list.append(selected_draw)
    return element_list


def clear_bet_slip(browser):
    wait=WebDriverWait(driver=browser,timeout=10)
    browser.execute_script(f"window.scrollTo(0, 0);")
    time.sleep(1)
    try:
        try:
            clear_all_button= browser.find_element(By.CSS_SELECTOR,'.clear-all')
            clear_all_button.click()
        except (TimeoutException,NoSuchElementException):
            # betslip_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-testid="nav-bar-betslip"]')))
            # betslip_button=browser.find_element(By.CSS_SELECTOR,'[data-testid="nav-bar-betslip"]')
            # betslip_button.click()
            # time.sleep(1)
            pass
        try:
            # clear_all_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'.clear-all')))
            clear_all_button=browser.find_element(By.CSS_SELECTOR,'.clear-all')
            clear_all_button.click()
        except (TimeoutException,NoSuchElementException):
            pass
        except ElementClickInterceptedException:
            browser.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
            clear_all_button=browser.find_element(By.CSS_SELECTOR,'.clear-all')
            clear_all_button.click()
        # time.sleep(2)
        # close_betslip_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-testid="coupon-close-icon"]')))
        try:
            close_betslip_button=browser.find_element(By.CSS_SELECTOR,'[data-testid="coupon-close-icon"]')
            close_betslip_button.click()
        except:
            continue_betting_button=browser.find_element(By.CSS_SELECTOR,'[data-testid="coupon-continue-betting"]')
            continue_betting_button.click  
        time.sleep(1)
    except:
        pass


import smtplib
from email.mime.multipart import MIMEMultipart               #
from email.mime.text import MIMEText                         # Necessary imports inorder to attach a file(page)
from email.mime.base import MIMEBase                         #
from email import encoders                                   #
def send_email(Email:str,Password:str,Message:str,Subject:str,File_path:list=[]):
    """To send an email attached with the screenshoot(s) of a page(specifically the result page)"""
    msg=MIMEMultipart()
    msg['From'] = Email
    msg['To'] = Email
    msg['Subject'] = Subject
    body = Message
    msg.attach(MIMEText(body, 'plain'))

    for n in range(len(File_path)):
        with open(File_path[n], "rb") as attachment:
            p = MIMEBase('application', 'octet-stream')
            p.set_payload((attachment).read()) 
            encoders.encode_base64(p) 
            p.add_header('Content-Disposition', f"attachment; filename= {File_path[n].split('/')[-1]}")
            msg.attach(p)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com') as connection:
            connection.login(user=Email, password=Password)
            connection.sendmail(from_addr=Email,
                                to_addrs = Email,
                                msg = msg.as_string()
                                )
    except:
        pass


def check_if_last_stake_has_played(browser:object,week_to_check:str,time_delay:float):
    week_to_select = browser.find_elements(By.CSS_SELECTOR, '.week')
    print(week_to_select[0].text,week_to_check)
    while week_to_select[0].text==week_to_check:
        time.sleep(time_delay)
        week_to_select[:] = browser.find_elements(By.CSS_SELECTOR, '.week')
    print(week_to_select[0].text,week_to_check)    
    return True


def reload_result_page(browser):
    """ To cancel and reload result page inorder to reflect new changes to the result"""
    wait=WebDriverWait(driver=browser,timeout=10)

    try:
        betslip_button=browser.find_element(By.CSS_SELECTOR,'[data-testid="nav-bar-betslip"]')
        betslip_button.click()
        time.sleep(0.5)
        close_betslip_button=browser.find_element(By.CSS_SELECTOR,'[data-testid="coupon-close-icon"]')
        close_betslip_button.click()
        time.sleep(0.5)

    except:

        # cancel_result_page_button=browser.find_element(By.CSS_SELECTOR,"svg path")
        cancel_result_page_button=browser.find_element(By.CSS_SELECTOR,"svg path")
        cancel_result_page_button.click()
        time.sleep(0.5)
        # standings_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"span.view-switch-icon")))
        standings_button=browser.find_element(By.CSS_SELECTOR,"span.view-switch-icon")
        standings_button.click()
        time.sleep(0.5)
        result_button = browser.find_elements(By.CSS_SELECTOR,'[data-testid="results-page-tab-standings"]')
        # result_button=browser.find_element(By.XPATH,"/html/body/app-root/app-wrapper/div/virtuals-league-wrapper/mobile-virtuals-soccer/mvs-virtual-league-page/div[2]/mvs-results-page/div[2]/div[2]")
        result_button[1].click()
        time.sleep(1)


def check_if_last_result_equal_input(browser:object,game_weeks:list,week_to_check:str,time_delay:float)->list:   #updated game weeks
    """ To check if the current last result is the same with the week_to_check 
    input variable, then return an updated game_weeks """
   
    if week_to_check=="Week 0":
        return game_weeks
    last_result_week=game_weeks[0].text
    print(last_result_week,week_to_check)
    while last_result_week!=week_to_check:
        #print(last_result_week,week_to_check)
        time.sleep(time_delay)
        reload_result_page(browser)
        time.sleep(2)
        for _ in range(3):
            game_weeks[:]=browser.find_elements(By.CSS_SELECTOR,".week-number")
            if game_weeks!=[]:
                break
            reload_result_page(browser)
            time.sleep(2)
        last_result_week=game_weeks[0].text
    print(last_result_week,week_to_check)
    return game_weeks


def reduce_week_selected(week_selected:str,by:int,league:str)->str:
    """To reduce the week which the staking options has been selected while waiting for last staked result"""
    if league=="bundliga":
        last_week="34"
    else:
        last_week="38"
    var_list=week_selected.split(" ") # To split the string(Week_selected)
    num=str(int(var_list[1])-by)      # Convert number part to int, then reduce by(-by), then covert back to str()
    if len(num)==1 and num=='0':
        output=var_list[0]+" "+last_week    # To change the output back to 34(which is the last week for bundesliga) Since week 1 - by = 0  
    else:
        output=var_list[0]+" "+num
    return output

# def confirm_outcome(games_selected_results:dict,games_played:int):
#     games_won=0
#     total_odds=1
#     for k,v in games_selected_results.items():
#         ft_score=v['ft_score']
#         ft_home_score=int(ft_score[0])
#         ft_away_score=int(ft_score[4])
#         total_goals=ft_away_score+ft_home_score
#         total_odds*=v["odd"]
#         if v["selected_stake"]=='over_2.5' and total_goals>=3:
#             games_won+=1
#         elif v["selected_stake"]=='under_2.5'and total_goals<3:
#             games_won+=1
#     if games_won==games_played:
#         result='WON'
#     else:
#         result="LOST"

#     return [result,round(total_odds,2)]


def confirm_outcome(games_selected_results:dict,games_played:int):
    games_won=0
    total_odds=1
    for k,v in games_selected_results.items():
        ft_score=v['ft_score']
        ft_home_score=int(ft_score[0])
        ft_away_score=int(ft_score[4])
        total_goals=ft_away_score+ft_home_score
        total_odds*=v["odd"]
        if ft_home_score==ft_away_score:
            result='WON'
        else:
            result="LOST"

    return [result,round(total_odds,2)]


class MyCustomThread(threading.Thread):
    # def __init__(self, group: None = None, target: Callable[..., object] | None = None, name: str | None = None, args: codecs.Iterable[codecs.Any] = ..., kwargs: threading.Mapping[str, codecs.Any] | None = None, *, daemon: bool | None = None) -> None:
    #     super().__init__(group, target, name, args, kwargs, daemon=daemon)
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None,daemon=bool):
        threading.Thread.__init__(self, group, target, name, args, kwargs,daemon=daemon)
        self._return = None

    def run(self):
        self.error = None
        if self._target is not None:
            try:
                self._return = self._target(*self._args, **self._kwargs)
            except BaseException as e:
                self.error=e

    # def check_error(self):
    #     if self.exc:
    #         raise self.exc
        
    def join(self, *args):
        threading.Thread.join(self, *args)
        return self._return

