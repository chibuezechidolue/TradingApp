import time
import os
from typing_extensions import final
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        StaleElementReferenceException, TimeoutException,
                                        NoSuchElementException)
from dotenv import load_dotenv
from tools import ( cancel_popup, game_selection_algorithm,clear_bet_slip,check_if_last_stake_has_played,
                   check_if_last_result_equal_input,confirm_outcome,send_email)
import datetime

load_dotenv()

class CheckPattern:
    """ To check if the the desired pattern of the desired market has occured. 
    It takes a driver instance as first argument """

    def __init__(self, driver: object,) -> None:
        self._VIRTUAL_BUTTON_LINK_TEXT = "VIRTUALS"
        self.browser = driver
        self.wait = WebDriverWait(driver=self.browser, timeout=10)

    def checkout_virtual(self, league: str):
        """ To enter the desired Virtual Game option(e.g. Bundesliga)"""
        try:
            virtual_button = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, self._VIRTUAL_BUTTON_LINK_TEXT)))
            virtual_button.click()
        except ElementClickInterceptedException:
            cancel_popup(self.browser)
            virtual_button = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, self._VIRTUAL_BUTTON_LINK_TEXT)))
            virtual_button.click()
        if league.lower() == "bundliga":
            css_selector = ".game-kings-bundliga.type-scheduled-league"
        virtual_choice_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        virtual_choice_button.click()


    def check_result(self,games_selected:list,latest_week: str,acc_balance:str=None):
        try:
            try:
                try:
                    standings_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="results-and-standings-button"]')))
                    # standings_button=self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"span.view-switch-icon")))
                    standings_button.click()
                except (TimeoutException,ElementClickInterceptedException):
                    standings_button=self.browser.find_element(By.CSS_SELECTOR, '[data-testid="results-and-standings-button"]')
                    standings_button.click()                
                try:
                    result_button = self.browser.find_elements(By.CSS_SELECTOR,'[data-testid="results-page-tab-standings"]')
                    result_button[1].click()

                except (TimeoutException,ElementClickInterceptedException):
                    result_button=self.browser.find_element(By.XPATH,"/html/body/app-root/app-wrapper/div/virtuals-league-wrapper/div/mobile-virtuals-soccer/mvs-virtual-league-page/div[2]/mvs-results-page/div[2]/div[2]")
                    result_button.click()
            except:
                self.browser.get("https://m.betking.com/virtual/league/kings-bundliga/results")
            time.sleep(5)
        
            game_weeks = self.browser.find_elements(By.CSS_SELECTOR, ".week-number")
            # checking if the last week played is latest_week before going ahead to save the page
            game_weeks = check_if_last_result_equal_input(self.browser, game_weeks=game_weeks,
                                                        week_to_check=latest_week,time_delay=30)
            
            home_team_names=self.browser.find_elements(By.CSS_SELECTOR,'[data-testid="results-home-team"]')[:9]
            for name in home_team_names:
                if games_selected.get(name.text)!=None:
                    parent_element=name.find_element(By.XPATH,'..')
                    ft_score = self.browser.execute_script(
                "return arguments[0].nextElementSibling.nextElementSibling;", parent_element)
                    games_selected[name.text]['ft_score']=ft_score.text
            output=confirm_outcome(games_selected_results=games_selected,games_played=len(games_selected))
            result=output[0]
            total_odds=output[1]
            potential_win=round(total_odds*50,2)
            games_selected['possible_win']=potential_win
            print(games_selected)
            if result=="WON":
                result={"outcome":result,"subject":f"You WON ₦{potential_win} this week","message":f"Betslip: {games_selected}"}
            else:
                result={"outcome":result,"subject":"You LOST this week.","message":f"Betslip: {games_selected}"}
        except Exception as error:
            print(f"an error occured when checking last result i want to use acc balance to check.This is the error: {error}")
            # if the result page fails, compare balances to tell the outcome
            if check_if_last_stake_has_played(browser=self.browser,week_to_check=latest_week,time_delay=30):
                time.sleep(10)  # TODO: Confirm the time to sleep before the balance reflects
                print("last staked has finnished playing")
                refresh_bal_button=self.browser.find_element(By.CSS_SELECTOR, '.user-balance-container .refresh-icon')
                refresh_bal_button.click()
                time.sleep(2)
                acc_balance_2=self.browser.find_element(By.CSS_SELECTOR, '.user-balance-container .amount').text
                print(f"Old acc bal {acc_balance}, New acc bal {acc_balance_2}")
                if float(acc_balance_2.replace(",","_"))>float(acc_balance.replace(',','_')):
                    result={"outcome":'WON',"subject":"You WON this week.","message":f"I used the acc bal to confirm ticket won. this is the error:\n{error}"}
                else:
                    result={"outcome":'LOST',"subject":"You LOST this week.","message":f"I used the acc bal to confirm ticket won. this is the error:\n{error}"}

        
        finally:
            print(result["subject"])
            if result['outcome']=="WON":
                send_email(Email=os.environ.get("EMAIL_USERNAME"),
                        Password=os.environ.get("EMAIL_PASSWORD"),
                        Subject=result["subject"],
                        Message=result["message"]
                        )
            cancel_result_page_button = self.browser.find_element(By.CSS_SELECTOR, "svg path")
            cancel_result_page_button.click()

        return [result,potential_win]




class PlayGame:
    """ To handle the Game Play like: choose_market, select_stake_option,
        place_the_bet. It takes a driver instance as first argument """

    def __init__(self, driver: object, market: str) -> None:
        self.market = market.lower()
        self.browser = driver
        self.wait = WebDriverWait(driver=self.browser, timeout=10)

    def choose_market(self):
        """ To select the market which was passed as a variable during initializing """
        self.browser.execute_script(f"window.scrollTo(0, 0);")
        try:
            # if check_if_current_week_islive(self.browser):
            #     time.sleep(40)
            three_goals_market = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="o/u-2.5-market"]')))
            three_goals_market.click()
        except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException):
            print('an exception occured')
            self.browser.execute_script(f"window.scrollTo(0, {three_goals_market.location['y']-200});")
            time.sleep(0.5)
            three_goals_market.click()


    def select_games_to_play(self):
        week_to_select = self.browser.find_elements(By.CSS_SELECTOR, '.week')[0]
        available_odds=self.browser.find_elements(By.CSS_SELECTOR, '[data-testid="match-odd-value"]')[:27]
        element_list=game_selection_algorithm(available_odds)
        selected_games={}
        for element in element_list:
            direct_parent_element=element.find_element(By.XPATH,'..')
            sibling = self.browser.execute_script("return arguments[0].previousElementSibling;", direct_parent_element)
            if sibling==None:
                selected_stake="over_2.5"
            else:
                selected_stake="under_2.5"
                
            # To click the selected element
            try:
                element.click()
            except ElementClickInterceptedException:
                self.browser.execute_script(f"window.scrollTo(0, {element.location['y']-200});")
                time.sleep(0.5)
                element.click()

            parent_element=element.find_element(By.XPATH,'../../../../..')
            teams = self.browser.execute_script(
                "return arguments[0].previousElementSibling;", parent_element)
            home_team_name=teams.find_element(By.CSS_SELECTOR, '[data-testid="match-home-team"]').text
            selected_games[home_team_name]={"selected_stake":selected_stake,"odd":float(element.text)}
        return {'week_selected':week_to_select.text,"selected_games":selected_games}


    def place_the_bet(self, amount: int, test: bool)->str:
        """ To bet the selected stake options each with the inputed amount"""
        # identify and click the betslip botton
        time.sleep(1)
        # betslip_button = self.wait.until(
        #     EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="nav-bar-betslip"]')))
        betslip_button=self.browser.find_element(By.CSS_SELECTOR,'[data-testid="nav-bar-betslip"]')
        betslip_button.click()
        # time.sleep(3)
        # identify and click the singles tab option
        try:

            # singles_button=self.browser.find_element(By.CSS_SELECTOR,'[data-testid="groupings-tab-singles"]')
            # singles_button.click()
            # identify, clear existing amount and input new amount
            # stake_input_box = self.browser.find_element(By.CSS_SELECTOR, '[data-testid="coupon-groupings-group-stake"]')
            stake_input_box = self.browser.find_element(By.CSS_SELECTOR, '[data-testid="coupon-totals-stake-amount-value"]')
            stake_input_box.clear()
            # time.sleep(1)
            stake_input_box.send_keys(amount)
            # scroll to the bottom of the page
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            if test:
                clear_bet_slip(self.browser)
            else:
                # identify and click the place bet button
                # place_bet_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[text="Place Bet"]')))
                place_bet_button=self.browser.find_element(By.CSS_SELECTOR, '[text="Place Bet"]')
                place_bet_button.click()
                # time.sleep(2)
                # identify and click the continue betting button
                try:
                    # continue_betting_button = self.wait.until(
                    #     EC.element_to_be_clickable((By.CSS_SELECTOR, '.bet-success-dialog-buttons .btn-text')))
                    continue_betting_button=self.browser.find_element(By.CSS_SELECTOR, '.bet-success-dialog-buttons .btn-text')
                    continue_betting_button.click()
                except (TimeoutException, NoSuchElementException):
                    # close_betslip_button = self.wait.until(
                    #     EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="coupon-close-icon"]')))
                    close_betslip_button=self.browser.find_element(By.CSS_SELECTOR, '[data-testid="coupon-close-icon"]')
                    close_betslip_button.click()
            try:
                acc_balance=self.browser.find_element(By.CSS_SELECTOR, '.user-balance-container .amount').text
                return acc_balance
            except (NoSuchElementException, TimeoutException):
                pass
        except:
            # close_betslip_button = self.wait.until(
            #     EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="coupon-close-icon"]')))
            close_betslip_button=self.browser.find_element(By.CSS_SELECTOR, '[data-testid="coupon-close-icon"]')
            close_betslip_button.click()
            close_betslip_button.click()



class LoginUser:
    """ To login a user with the relevant credentials.
      It takes a driver instance as first argument """

    def __init__(self, driver: object, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.browser = driver
        self.wait = WebDriverWait(driver=self.browser, timeout=10)

    def login(self):
        """ Login the user with the credentials from initialization and return the account balance of the user"""
        # login = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.text")))
        # login= self.browser.find_element(By.CSS_SELECTOR, "button.text")
        login= self.browser.find_element(By.CSS_SELECTOR, '.guest-header-content .text')
        try:
            login.click()
        except:
            try:
                cancel_popup(self.browser)
                login = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.text")))
                login.click()
            except:
                login= self.browser.find_element(By.CSS_SELECTOR, '.guest-header-content .text')
                login.click()
                
        username = self.browser.find_element(By.CSS_SELECTOR, '[placeholder="Username or Verified Mobile"]')
        password = self.browser.find_element(By.CSS_SELECTOR, '[placeholder="Password"]')
        # fill the username and password form with the inputed variable
        for char in self.username:
            # time.sleep(0.5)
            username.send_keys(char)
        for char in self.password:
            # time.sleep(0.5)
            password.send_keys(char)
        # time.sleep(1)
        login_button = self.browser.find_element(By.CSS_SELECTOR, '[text="Login"]')
        login_button.click()
        time.sleep(2)
        try:
            cancel_notification_option_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.kumulos-action-button-cancel")))
            # cancel_notification_option_button=self.browser.find_element(
            #     By.CSS_SELECTOR, "button.kumulos-action-button-cancel")
            cancel_notification_option_button.click()
        except (TimeoutException, NoSuchElementException):
            pass

        try:
            acc_balance=self.browser.find_element(By.CSS_SELECTOR, '.user-balance-container .amount').text
        except NoSuchElementException:
            acc_balance="210,000"
            pass
            # self.browser.refresh()
            # time.sleep(2)
            # acc_balance=self.browser.find_element(By.CSS_SELECTOR, '.user-balance-container .amount').text
            
        return acc_balance