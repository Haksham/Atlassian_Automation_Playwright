import asyncio
import os

from dotenv import load_dotenv
import pandas as pd
from playwright.async_api import async_playwright

load_dotenv()

LOGIN_URL = os.getenv("ATLASSIAN_URL")
DIRECTORY_URL = os.getenv("ATLASSIAN_DIRECTORY_URL")
USERNAME = os.getenv("ATLASSIAN_USERNAME")
PASSWORD = os.getenv("ATLASSIAN_PASSWORD")

# Read email IDs and group names from Excel sheet named "User.xlsx"
excel_path = os.path.join(os.path.dirname(__file__), "Data/User.xlsx")
df = pd.read_excel(excel_path)
email_list = df['Mail Id'].dropna().tolist()  # Assumes column name is 'Mail Id'
group_list = df['Group'].dropna().tolist()    # Assumes column name is 'Group'


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Go to Atlassian login page
        await page.goto(LOGIN_URL)

        # Step 1: Enter email and click continue
        await page.fill('input#username-uid1', USERNAME)
        await page.click('button#login-submit')
        await page.wait_for_selector('input#password', timeout=10000)

        # Step 2: Enter password and click log in
        await page.fill('input#password', PASSWORD)
        await page.click('button#login-submit')
        await page.wait_for_load_state('networkidle')

        # Step 3: Click on 'Directory' inside div[role="list"]
        await page.wait_for_selector('div[role="list"] >> text=Directory', timeout=10000)
        await page.click('div[role="list"] >> text=Directory')
        await page.wait_for_load_state('networkidle')

        # Step 4: Click on 'Users' inside div[role="list"]
        await page.wait_for_selector('div[role="list"] >> text=Users', timeout=10000)
        await page.click('div[role="list"] >> text=Users')
        await page.wait_for_load_state('networkidle')

        for email, group in zip(email_list, group_list):
            # Step 5: Click on 'invite users' button
            await page.wait_for_selector('button:has-text("invite users")', timeout=10000)
            await page.click('button:has-text("invite users")')
            await page.wait_for_selector('input#invite-users-email-input', timeout=10000)

            # Step 6: Enter email IDs and group names from Excel sheet
            await page.fill('input#invite-users-email-input', email)
            await page.fill('input#group-membership-input', str(group))
            await page.press('input#group-membership-input', 'Enter')
            await page.click('button[data-testid="invite-submit-button"]')
            await page.wait_for_selector('input#invite-users-email-input', state='hidden', timeout=10000)
            await page.reload()
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)  # Pause for demo; adjust as needed 

        # Keep browser open for inspection
        await asyncio.sleep(3)
        await browser.close()

# only 4 id per batch

if __name__ == "__main__":
    asyncio.run(run())