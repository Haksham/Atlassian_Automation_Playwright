import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

LOGIN_URL = os.getenv("ATLASSIAN_URL")
DIRECTORY_URL = os.getenv("ATLASSIAN_DIRECTORY_URL")
USERNAME = os.getenv("ATLASSIAN_USERNAME")
PASSWORD = os.getenv("ATLASSIAN_PASSWORD")

# Read email IDs from Excel sheet named "users.xlsx"
excel_path = os.path.join(os.path.dirname(__file__), "User.xlsx")
df = pd.read_excel(excel_path)
email_list = df['Mail Id'].dropna().tolist()  # Assumes column name is 'Mail Id'

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
        
        # Step 5: Click on 'invite users' button
        await page.wait_for_selector('button:has-text("invite users")', timeout=10000)
        await page.click('button:has-text("invite users")')
        await page.wait_for_selector('input#invite-users-email', timeout=10000)
        
        # Step 6: Enter email IDs from Excel sheet
        for email in email_list:
            await page.fill('input#invite-users-email', email)
            # Add logic to submit/invite if needed, e.g.:
            # await page.click('button:has-text("Send invitation")')
            await asyncio.sleep(1)  # Pause for demo; adjust as needed
        
        # Keep browser open for inspection
        await asyncio.sleep(10)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())