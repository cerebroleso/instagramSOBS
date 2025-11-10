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
        time.sleep(3)
        return
    else:
        print("flag is false. moving on...\n")
        return










def website_safety_check(page, SAFETY_CHECKS, HEADLESS_MODE):
    print("ALWAYS CHECK THIS WEBSITES RESULTS")
    if(SAFETY_CHECKS == False):
        print('type n to skip these checks. YOU SHOULD ALWAYS CHECK THIS')
        choice = input()
        if(choice != 'n'):
            # goto botcheck websites(s)
            print('go fullscreen with chromium, then press enter\n')
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






















def scrape_list(page, list_type, scroll_selector):
    """
    scrapes either the 'following' or 'followers' list,
    stops scrolling when "Suggested for you" is seen,
    and excludes the last 30 results.
    """
    
    print(f"--- opening {list_type.upper()} list ---")
    page.click(f'a[href$="/{list_type}/"]')
    
    print("waiting for dialog...")
    dialog_locator = page.locator('div[role="dialog"]')
    try:
        dialog_locator.wait_for(state="visible", timeout=5000)
    except Exception:
        print(f"⛔ error: {list_type} pop-up did not open.")
        # try to go back to the profile page to prevent a crash on the next run
        try:
            page.goto(f"https://www.instagram.com/{page.url.split('/')[3]}/") 
        except Exception:
            pass # if it fails, just return
        return [] # return an empty list on error

    print("locating scroll area...")
    popup_locator = dialog_locator.locator(scroll_selector)
    
    if popup_locator.count() == 0:
        print(f"⛔ error: scroll selector '{scroll_selector}' not found.")
        print("     please, update the CSS selector in the config file (should be something like '_aano').")
        page.get_by_role("button", name="Close").click()
        return [] # Return an empty list on error

    print("scrolling the list...")
    last_height = 0
    while True:
        try:
            is_suggested_visible = popup_locator.get_by_text("Suggested for you", exact=True).is_visible(timeout=100)
            if is_suggested_visible:
                print("'suggested for you' text found. stopping scroll.")
                break # stop scrolling
        except Exception:
            # not visible or not found, which is good. continue scrolling.
            pass 
        
        # scroll down
        popup_locator.evaluate('el => el.scrollTop = el.scrollHeight')
        time.sleep(0.4) 
        
        # check if we've reached the end
        new_height = popup_locator.evaluate('el => el.scrollHeight')
        if new_height == last_height:
            print("scrolling complete (reached the end).")
            break
        last_height = new_height

    print("saving the list...")
    scraped_list = page.evaluate("""
        () => {
            const names = [];
            document.querySelectorAll('div[role="dialog"] a[href^="/"][role="link"] span[dir="auto"]').forEach(el => {
                names.push(el.textContent.trim());
            });
            return names;
        }
    """)
    
    print(f"captured {len(scraped_list)} raw profiles.")

    final_list = []
    if len(scraped_list) > 30:
        print("excluding the last 30 (as they are likely suggestions).")
        final_list = scraped_list[:-30] # this gets all items EXCEPT the last 30
    else:
        print("list is 30 or fewer profiles, not trimming.")
        final_list = scraped_list
    
    print(f"final list size: {len(final_list)}")
    
    # Close the dialog
    page.get_by_role("button", name="Close").click()
    print(f"--- finished {list_type.upper()} list ---")
    
    return final_list

















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

    following_list = scrape_list(page, "following", scroll_selector)
    
    followers_list = scrape_list(page, "followers", scroll_selector)
    
    print("Done scraping both lists.")
    
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









def _save_txt_file(folder_path, file_name, data):
    percorso_file = folder_path / f"{file_name}.txt"
    
    file_content = "\n".join(data)
    
    try:
        percorso_file.write_text(file_content, encoding="utf-8")
        print(f"✅ file saved in: {file_name}.txt ({len(data)} users)")
    except Exception as e:
        print(f"❌ error {file_name}: {e}")

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

    print("do you mind adding the latest diff? [this will lets you see who unfollowed you during this time]\n")
    prev_folder_path = input("name of the folder where followers.txt is located\n")

    prevfollowers = open(f"{prev_folder_path}/followers.txt","r")
    actualfollowers = open(f"{folder_path}/followers.txt","r")
    prevfollowers = prevfollowers.readlines()
    actualfollowers = actualfollowers.readlines()
    print(prevfollowers)
    print(actualfollowers)
    DF = [ x for x in prevfollowers if x not in actualfollowers ]
    print(DF)

    diff_path = base_dir / "diffs"
    diff_path.mkdir(parents=True, exist_ok=True)
    open(f"{diff_path}/diff_{timestamp}.txt", 'x')
    _save_txt_file(diff_path, f"diff_{timestamp}", DF)
    
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
        #input()

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

