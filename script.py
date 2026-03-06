import sys
import time
import random
import getpass
import select
from datetime import datetime
from pathlib import Path
import configparser
import os
import re
import inquirer

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

            print('are you sure you want to continue?')
            input()
    return


def scrape_list(page, list_type, scroll_selector, USERNAME, SCROLL_DURATION):
    """
    scrapes either the 'following' or 'followers' list with human-like delays.
    """

    print(f"--- opening {list_type.upper()} list ---")
    page.click(f'a[href$="/{list_type}/"]')

    print("waiting for dialog...")
    dialog_locator = page.locator('div[role="dialog"]')
    try:
        dialog_locator.wait_for(state="visible", timeout=5000)
    except Exception:
        print(f"⛔ error: {list_type} pop-up did not open.")
        try:
            page.goto(f"https://www.instagram.com/{page.url.split('/')[3]}/")
        except Exception:
            instagram_navigation(page, USERNAME, SCROLL_DURATION, scroll_selector)
        return []

    print("locating scroll area...")
    popup_locator = dialog_locator.locator(scroll_selector)

    # Dynamic print based on the config setting
    print(f"blindly scrolling the list for up to {SCROLL_DURATION} seconds...")

    # Calculate center coordinates once to use for the virtual mouse
    try:
        center_x = page.evaluate("window.innerWidth") / 2
        center_y = page.evaluate("window.innerHeight") / 2
        page.mouse.move(center_x, center_y)
    except Exception as e:
        print(f"⛔ error moving mouse to center: {e}")

    start_time = time.time()
    scroll_count = 0

    # Loop until SCROLL_DURATION seconds have passed
    while time.time() - start_time < SCROLL_DURATION:
        try:
            # Still good to keep this fallback just in case IG actually loads it
            if popup_locator.get_by_text("Suggested for you", exact=True).is_visible(timeout=100):
                print("\n'suggested for you' text found. stopping scroll.")
                break
        except Exception:
            pass

        # --- BLIND VIRTUAL MOUSE SCROLL ---
        try:
            # Randomize the scroll delta slightly so it's not exactly the same every time
            scroll_delta = random.randint(450, 650)
            page.mouse.wheel(0, scroll_delta)
        except Exception as e:
            print(f"  (virtual mouse scroll failed: {e})")

        scroll_count += 1

        # Occasional "deep breath" break every 5-7 scrolls
        if scroll_count % random.randint(5, 7) == 0:
            long_pause = random.uniform(3.5, 6.2)
            time.sleep(long_pause)
        else:
            # Standard human-like reaction delay between scrolls
            time.sleep(random.uniform(0.6, 1.2))

        # --- TIMER & MANUAL INTERRUPT ---
        remaining = SCROLL_DURATION - int(time.time() - start_time)
        print(f"   scrolling... {remaining}s left. press Enter to stop early.", end="\r")

        # Listen for the Enter key to break the loop early
        if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
            input()
            print("\nmanual stop triggered.")
            break

    print("\nscrolling phase complete.")

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
    final_list = scraped_list

    # Close the dialog with a slight delay
    time.sleep(random.uniform(1.0, 2.0))
    page.get_by_role("button", name="Close").click()
    print(f"--- finished {list_type.upper()} list ---")

    return final_list


def instagram_navigation(page, USERNAME, SCROLL_DURATION, SCROLL_SELECTOR):
    page.goto("https://www.instagram.com/accounts/login/")

    # cookies
    print("clicking cookie banner (if present)...")
    try:
        page.get_by_role("button", name="Decline optional cookies").click(timeout=500)
        print("cookie banner accepted.")
    except Exception:
        try:
            page.get_by_role("button", name="Allow all cookies").click(timeout=100)
            print("cookie banner alternative accepted.")
        except Exception:
            print("cookie banner not found or already accepted. moving on...")

    try:
        print("filling user's credentials ...")
        page.get_by_role("button", name="Login").click(timeout=100)
        page.fill('input[name="username"]', USERNAME)
        print("press enter after logging in")
        input()
    except:
        print('already logged in?')

    page.goto(f"https://www.instagram.com/{USERNAME}/")

    print("you should be seeing your profile page. starting the script")

    # Pass the variables down to the scraping function
    following_list = scrape_list(page, "following", SCROLL_SELECTOR, USERNAME, SCROLL_DURATION)
    followers_list = scrape_list(page, "followers", SCROLL_SELECTOR, USERNAME, SCROLL_DURATION)

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

        # Pull the new scroll_duration setting, defaulting to 60 if it's missing
        SCROLL_DURATION = SETTINGS.getint('scroll_duration', fallback=60)

        # if (OUTPUT) == '':
        OUTPUT = Path(__file__).resolve().parent

        # load credentials
        PROFILE = config['profile']
        USERNAME = PROFILE.get('username')

        # load misc elements right here to save an I/O read
        MISC = config['misc']
        SCROLL_SELECTOR = MISC.get('div')

        return HEADLESS_MODE, SAFETY_CHECKS, OUTPUT, USERNAME, SCROLL_DURATION, SCROLL_SELECTOR

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

def _append_txt_file(folder_path, file_name, data):
    #only one line per function call
    percorso_file = folder_path / f"{file_name}.txt"

    try:
        with open(percorso_file, 'a', encoding="utf-8") as f:
            f.write("\n" + data)

        print(f"✅ data appended to: {file_name}.txt")
    except Exception as e:
        print(f"❌ error appending {file_name}: {e}")


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

    print("\n--- results chart ---")
    print(f"👤 following: {len(following_set)}")
    print(f"👥 followers: {len(followers_set)}")
    print(f"❌ SOBS: {len(sobs)}")
    print(f"💚 fans: {len(fans)}")


    choice = input("do you mind saving this ? y/n\n")
    if(choice != 'n'):
        _save_txt_file(folder_path, "following", following_list)
        _save_txt_file(folder_path, "followers", followers_list)
        _save_txt_file(folder_path, "sobs", list(sobs))
        _save_txt_file(folder_path, "fans", list(fans))
        _append_txt_file(base_dir, "list", timestamp)

        choice = input("do you mind adding the latest diff? [this will let you see who unfollowed you during this time]\ny/n\n")
        if(choice != 'n'):
            list_selector(base_dir, timestamp)

    return


def run_scrape(HEADLESS_MODE, SAFETY_CHECKS, OUTPUT, USERNAME, SCROLL_DURATION, SCROLL_SELECTOR, playwright_option):
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
        instagram_navigation(page, USERNAME, SCROLL_DURATION, SCROLL_SELECTOR)

        print("script complete. closing browser.")
        if context:
            context.close()
        if browser:
            browser.close()


def list_selector(dir, folder_name):
    list_file_path = dir / "list.txt"

    try:
        with open(list_file_path, 'r') as f:
            lines = [line for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"Error: {list_file_path} not found.")
        sys.exit(1)

    if len(lines) == 0:
        print(f"{list_file_path} is empty")
        sys.exit(1)

    num_options = len(lines)
    dynamic_list = ["latest dump"]
    file_options = [f"{i+1}. {lines[i].strip()}" for i in range(num_options-1)] # KEEP IN MIND: -1 FOR REMOVING THE LATEST ITEM
    dynamic_list.extend(file_options)
    dynamic_list.append("exit")

    questions = [
        inquirer.List(
            'choice',
            message="Select an option:",
            choices=dynamic_list,
        )
    ]

    answers = inquirer.prompt(questions)

    if not answers:
        print("\nSelection cancelled.")
        sys.exit(0)

    answer = answers['choice']

    print(f"You selected: {answer}")

    if(answer == "latest dump"):
        answer = dynamic_list[-2]

    diff_dump(dir, answer, folder_name)


def diff_dump(dir, prev_folder_name, folder_name):
    prev_folder_name = prev_folder_name[3:].strip()
    prev_folder_path = dir / prev_folder_name
    folder_path = dir / folder_name

    # Load previous and current followers
    with open(prev_folder_path / "followers.txt", "r", encoding="utf-8") as f:
        prevfollowers = f.read().splitlines()

    with open(folder_path / "followers.txt", "r", encoding="utf-8") as f:
        actualfollowers = f.read().splitlines()

    # Load current following to verify if they still exist and you still follow them
    with open(folder_path / "following.txt", "r", encoding="utf-8") as f:
        actualfollowing = f.read().splitlines()

    # Find everyone who disappeared from the followers list
    missing_followers = set(prevfollowers) - set(actualfollowers)

    # TRUE SOBS: They disappeared from followers, BUT you are still following them
    # This automatically filters out deleted accounts and mutual unfollows
    true_unfollowers = missing_followers.intersection(set(actualfollowing))

    print(f"People who actively unfollowed you (SOBS): {true_unfollowers}")

    diff_path = dir / "diffs"
    diff_path.mkdir(parents=True, exist_ok=True)

    # Save the clean diff
    _save_txt_file(diff_path, f"diff_{folder_name}", list(true_unfollowers))

    # Call the display function we added previously
    display_latest_diff(dir)


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

def display_latest_diff(dir):
    diff_path = dir / "diffs"

    if not diff_path.exists() or not diff_path.is_dir():
        print("\n⛔ no 'diffs' folder found.")
        return

    # Get all text files in the diffs directory
    diff_files = list(diff_path.glob("diff_*.txt"))

    if not diff_files:
        print("\n⛔ no diff files found.")
        return

    # Sort files by name (which includes the timestamp) to get the latest
    latest_file = sorted(diff_files)[-1]

    print(f"\n📄 --- LATEST DIFF: {latest_file.name} ---")
    try:
        with open(latest_file, "r", encoding="utf-8") as f:
            contents = f.read().strip()
            if contents:
                print(contents)
            else:
                print("(no unfollowers in this diff - you are all good!)")
    except Exception as e:
        print(f"❌ error reading diff file: {e}")
    print("------------------------------------------\n")


if __name__ == "__main__":
    # Unpack the newly extracted SCROLL_SELECTOR alongside the rest
    HEADLESS_MODE, SAFETY_CHECKS, OUTPUT, USERNAME, SCROLL_DURATION, SCROLL_SELECTOR = config_read()

    print(f"HEADLESS_MODE = ", HEADLESS_MODE)
    print(f"SAFETY_CHECKS =", SAFETY_CHECKS)
    print(f"OUTPUT = ", OUTPUT)
    print(f"USERNAME = ", USERNAME)
    print(f"SCROLL_DURATION = ", SCROLL_DURATION)
    print(f"SCROLL_SELECTOR = ", SCROLL_SELECTOR)

    # Pass it down the chain
    run_scrape(HEADLESS_MODE, SAFETY_CHECKS, OUTPUT, USERNAME, SCROLL_DURATION, SCROLL_SELECTOR, playwright_option)
