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

# Read group names from Excel sheet named "Group.xlsx"
excel_path = os.path.join(os.path.dirname(__file__), "Group.xlsx")
df = pd.read_excel(excel_path)
group_list = df['Group'].dropna().tolist()  # Assumes column name is 'Group'

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
        
        for group in group_list:
            # Step 4: Click on 'Groups' inside div[role="list"]
            await page.wait_for_selector('div[role="list"] >> text=Groups', timeout=10000)
            await page.click('div[role="list"] >> text=Groups')
            await page.wait_for_load_state('networkidle')
            
            # Step 5: Click on 'Create group' button
            await page.wait_for_selector('button:has-text("Create group")', timeout=10000)
            await page.click('button:has-text("Create group")')
            await page.wait_for_selector('input[name="groupName"]', timeout=10000)
            
            # Step 6: Enter group names from Excel sheet
        
            await page.fill('input[name="groupName"]', group)
            await page.fill('textarea[name="groupDescription"]', f"This is: {group}")

            # Add logic to submit/create if needed, e.g.:
            await page.click('button[data-testid="test-create-group-modal-button"]')
            await asyncio.sleep(1)  # Pause for demo; adjust as needed
        
        # Keep browser open for inspection
        await asyncio.sleep(4)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())