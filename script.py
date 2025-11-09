import sys
import time
import getpass
from datetime import datetime
from pathlib import Path
import configparser
import os
import re

playwright_option = 1

# print("select an option\n1. playwright standard [recommended]\n2. playwright w/ stealth\n3. playwright w/ stealth and custom config (experimental)")
# playwright_option = int(input())
# if(playwright_option < 1 or playwright_option > 3):
#     sys.exit(1)





#try importing playwright
try:
    from playwright.sync_api import sync_playwright, Page, expect
    if(playwright_option == 2 or playwright_option == 3):
        from playwright_stealth import stealth_sync, StealthConfig
except ImportError:
    print("Error: Playwright not installed.")
    print("run:")
    print("1. pip install playwright")
    print("2. playwright install")
    sys.exit(1)










def simple_safety_check(page, SAFETY_CHECKS):
    # checking if environment is safe
    print("*******************************************")
    print("checking 'navigator.webdriver' flag...")
    flag_value = page.evaluate("navigator.webdriver")
    # print(f"'navigator.webdriver' flag value is: {flag_value}")
    # print(f"'safety check' is: {SAFETY_CHECKS}")
    print("*******************************************\n")

    if(flag_value) == True and (SAFETY_CHECKS) == True:
        print("flag is true. ensuring safety and exiting. set safety_checks to false to circumvent this\n")
        sys.exit(1)
    elif(flag_value) == True and (SAFETY_CHECKS) == False:
        print("!!!YOU ARE RUNNING THIS SCRIPT WITH THE MOST OBVIOUS BOT FLAG. DO IT ON YOUR OWN RISK!!!\n")
        return
    else:
        print("flag is false. moving on...\n")
        return










def website_safety_check(page, SAFETY_CHECKS, HEADLESS_MODE):
    print('type n to skip these checks. YOU SHOULD ALWAYS CHECK THIS WEBSITES RESULTS')
    choice = input()
    if(choice != 'n'):
        # goto botcheck websites(s)
        print('go fullscreen with chromium, then press enter\nALWAYS CHECK THIS WEBSITES RESULTS')
        input()
        website1 = "https://bot.sannysoft.com/"
        page.goto(website1)
        print('all good ?')
        input()
        if(HEADLESS_MODE) == True:
            save_page_html(page, website1, "bot_sannysoft")
        print('moving on ...')

        website2 = "https://abrahamjuliot.github.io/creepjs/"   
        page.goto(website2)
        print('all good ?')
        input()
        if(HEADLESS_MODE) == True:
            save_page_html(page, website1, "bot_sannysoft")
        print('moving on ...')

        # website3 = "https://www.google.com/recaptcha/api2/demo"
        # page.goto(website3)
        # page.locator("#id_della_checkbox").check()        
        # print('all good ?')
        # if(HEADLESS_MODE) == True:
        #     save_page_html(page, website1, "bot_sannysoft")
        # input()

        print('are you sure you want to continue?')
        input()
    return










def instagram_navigation(page, USERNAME):
    page.goto("https://www.instagram.com/accounts/login/")

    # cookies
    print("clicking cookie banner (if present)...")
    try:
        
        page.get_by_role("button", name="Decline optional cookies").click(timeout=1000)
        print("cookie banner accepted.")
    except Exception:
        try:
            page.get_by_role("button", name="Allow all cookies").click(timeout=500)
            print("cookie banner alternative accepted.")
        except Exception:
            print("cookie banner not found or already accepted. moving on...")



    try:
        
        print("filling user's credentials ...")
        page.get_by_role("button", name="Login").click(timeout=500)
        page.fill('input[name="username"]', USERNAME)
        print("press enter after logging in")
        input()
    except:
        print('already logged in?')


    page.goto(f"https://www.instagram.com/{USERNAME}/")

    print("you should be seeing your profile page. starting the script")

    scroll_selector = config_read_object('div')

    print("opening FOLLOWING list ...")
    page.click('a[href$="/following/"]')
    page.wait_for_selector('div[role="dialog"]')

    print("scrolling the list ...")
    # 1. find pop-up dialog and waiting for it to open
    dialog_locator = page.locator('div[role="dialog"]')
    try:
        # waiting up to 5 secs
        dialog_locator.wait_for(state="visible", timeout=5000)
    except Exception:
        print("⛔ Error: pop-up (div[role='dialog']) did not open.")
        return # exit if not found

    # 2. search the scrollable element

    popup_locator = dialog_locator.locator(scroll_selector)
    
    # 3. check if found
    if popup_locator.count() == 0:
        print(f"⛔ Error: scroll selector'{scroll_selector}' not found.")
        print("     please, update the CSS selector in the config file (should be something like '_aano').")
        return # exit if not found

    # 4. now it can scroll
    last_height = 0
    while True:
        # .evaluate()
        popup_locator.evaluate('el => el.scrollTop = el.scrollHeight')
        
        time.sleep(0.4) 
        
        new_height = popup_locator.evaluate('el => el.scrollHeight')
        if new_height == last_height:
            print("Scrolling terminato.")
            break
        last_height = new_height

    print("saving the list ...")
    following_list = page.evaluate("""
        () => {
            const names = [];
            document.querySelectorAll('div[role="dialog"] a[href^="/"][role="link"] span[dir="auto"]').forEach(el => {
                names.push(el.textContent.trim());
            });
            return names;
        }
    """)
    page.get_by_role("button", name="Close").click()

    print('done')



    print("opening FOLLOWERS list ...")
    page.click('a[href$="/followers/"]')
    page.wait_for_selector('div[role="dialog"]')

    print("scrolling the list ...")
    # 1. find pop-up dialog and waiting for it to open
    dialog_locator = page.locator('div[role="dialog"]')
    try:
        # waiting up to 5 secs
        dialog_locator.wait_for(state="visible", timeout=5000)
    except Exception:
        print("⛔ Error: pop-up (div[role='dialog']) did not open.")
        return # exit if not found

    # 2. search the scrollable element

    popup_locator = dialog_locator.locator(scroll_selector)
    
    # 3. check if found
    if popup_locator.count() == 0:
        print(f"⛔ Error: scroll selector'{scroll_selector}' not found.")
        print("     please, update the CSS selector in the config file (should be something like '_aano').")
        return # exit if not found

    # 4. now it can scroll
    last_height = 0
    while True:
        # .evaluate()
        popup_locator.evaluate('el => el.scrollTop = el.scrollHeight')
        
        time.sleep(0.4) 
        
        new_height = popup_locator.evaluate('el => el.scrollHeight')
        if new_height == last_height:
            print("Scrolling terminato.")
            break
        last_height = new_height

    print("saving the list ...")
    followers_list = page.evaluate("""
        () => {
            const names = [];
            document.querySelectorAll('div[role="dialog"] a[href^="/"][role="link"] span[dir="auto"]').forEach(el => {
                names.push(el.textContent.trim());
            });
            return names;
        }
    """)
    page.get_by_role("button", name="Close").click()

    save_results(following_list, followers_list)











def config_read():
    # try reading config
    config = configparser.ConfigParser()

    if not Path('config.ini').exists():
        print("Error: 'config.ini' not found.")
        sys.exit(1)

    config.read('config.ini')

    try:
        # load settings
        SETTINGS = config['settings']
        HEADLESS_MODE = SETTINGS.getboolean('headless')
        SAFETY_CHECKS = SETTINGS.getboolean('safety_checks')
        OUTPUT = Path(SETTINGS.get('output', 'output'))
        # if (OUTPUT) == '':
        OUTPUT = Path(__file__).resolve().parent


        # load credentials
        PROFILE = config['profile']
        USERNAME = PROFILE.get('username')
        #PASSWORD = PROFILE.get('password')
        return HEADLESS_MODE, SAFETY_CHECKS, OUTPUT, USERNAME


    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)










def config_read_object(name):
    # try reading config
    config = configparser.ConfigParser()

    if not Path('config.ini').exists():
        print("Error: 'config.ini' not found.")
        sys.exit(1)

    config.read('config.ini')

    try:
        # load
        MISC = config['misc']
        config_object = MISC.get(name)
        return config_object


    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)









def _save_txt_file(percorso_cartella, nome_file, lista_dati):
    percorso_file = percorso_cartella / f"{nome_file}.txt"
    
    file_content = "\n".join(lista_dati)
    
    try:
        percorso_file.write_text(file_content, encoding="utf-8")
        print(f"✅ file saved in: {nome_file}.txt ({len(lista_dati)} users)")
    except Exception as e:
        print(f"❌ error {nome_file}: {e}")

def save_results(following_list, followers_list):
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_dir = Path(__file__).resolve().parent
    folder_path = base_dir / timestamp
    
    folder_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n--- saving in: {folder_path} ---")

    following_set = set(following_list)
    followers_set = set(followers_list)

    sobs = following_set - followers_set
    
    fans = followers_set - following_set

    _save_txt_file(folder_path, "following", following_list)
    _save_txt_file(folder_path, "followers", followers_list)
    _save_txt_file(folder_path, "sobs", list(sobs))
    _save_txt_file(folder_path, "fans", list(fans))

    print("\n--- results chart ---")
    print(f"👤 following: {len(following_set)}")
    print(f"👥 followers: {len(followers_set)}")
    print(f"❌ SOBS: {len(sobs)}")
    print(f"💚 fans: {len(fans)}")
    
    return












def run_scrape(HEADLESS_MODE, SAFETY_CHECKS, OUTPUT, USERNAME, playwright_option):
    # "stealth" profile folder
    profile_dir = OUTPUT / "my_chrome_profile"
    os.makedirs(profile_dir, exist_ok=True)

    print("*******************************************")
    print("instagramSOBS script. started")
    print("*******************************************\n")
    
    
    print(f"using the profile folder: {profile_dir}\n")

    with sync_playwright() as p:
        
        browser = None  # Initialize browser variable
        context = None  # Initialize context variable

        if(playwright_option == 1):
            #creating "stealth" chromium instance            
            context = p.chromium.launch_persistent_context(
                profile_dir,
                headless=HEADLESS_MODE,
                executable_path="/usr/bin/chromium",
                
                # "stealth" arguments
                args=[
                    '--window-size=1920,1080',
                    '--disable-plugins',
                    '--disable-blink-features=AutomationControlled',
                    '--no-first-run',
                    '--no-service-autorun',
                    '--password-store=basic',
                ]
            )



            page = context.pages[0]
            page.set_viewport_size({"width": 1920, "height": 1020})
        else:
            #creating "stealth" chromium instance            
            browser = p.chromium.launch(
                headless=HEADLESS_MODE,
                executable_path="/usr/bin/chromium",
                args=[
                    '--window-size=1920,1020', 
                ]
            )

            LINUX_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"

            context = browser.new_context(
                viewport={'width': 1920, 'height': 1020},
                device_scale_factor=1,
                user_agent=LINUX_USER_AGENT
            )

            #custom stealth
            config = StealthConfig(
                renderer = "AMD",
            )  
            if(playwright_option == 3):
                stealth_sync(context, config)
            else:
                stealth_sync(context)

            page = context.new_page()

        # injecting JS for spoofing webdriver
        #page.add_init_script("delete navigator.__proto__.webdriver;")
        page.add_init_script("navigator.webdriver = false")
        
        #first sc
        simple_safety_check(page, SAFETY_CHECKS)

        #second sc
        website_safety_check(page, SAFETY_CHECKS, HEADLESS_MODE)
        

        print("surfing in progress...")

        # goto instagram page
        instagram_navigation(page, USERNAME)
        


        print("script complete. closing browser.")
        if context:
            context.close()
        if browser:
            browser.close()










def save_page_html(page, url_to_fetch, output_file):
    try:
            page.goto(url_to_fetch, wait_until="networkidle")
            
            html_content = page.content()
            
            output_path = Path(__file__).resolve().parent / output_file
            output_path.write_text(html_content, encoding="utf-8")
            
            print(f"\n✅ website results saved in: {output_path}")

    except Exception as e:
        print(f"❌ error: {e}")
    
    # finally:
    #     browser.close()
        
        








if __name__ == "__main__":
    HEADLESS_MODE, SAFETY_CHECKS, OUTPUT, USERNAME = config_read()

    print(f"HEADLESS_MODE = ", HEADLESS_MODE)
    print(f"SAFETY_CHECKS =", SAFETY_CHECKS)
    print(f"OUTPUT = ", OUTPUT)
    print(f"USERNAME = ", USERNAME)

    run_scrape(HEADLESS_MODE, SAFETY_CHECKS, OUTPUT, USERNAME, playwright_option)

