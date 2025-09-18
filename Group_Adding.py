import asyncio
import os

from dotenv import load_dotenv
import pandas as pd
from playwright.async_api import async_playwright

# Load environment variables from .env file
load_dotenv()

# Retrieve Atlassian credentials and URLs from environment variables
LOGIN_URL = os.getenv("ATLASSIAN_URL")
USERNAME = os.getenv("ATLASSIAN_USERNAME")
PASSWORD = os.getenv("ATLASSIAN_PASSWORD")

# Read group names from Excel sheet named "Group.xlsx"
excel_path = os.path.join(os.path.dirname(__file__), "Data/Group.xlsx")
df = pd.read_excel(excel_path)
group_list = df['Group'].dropna().tolist()  # Extract non-empty group names

async def run():
    """
    Automates the process of creating groups in Atlassian organization,
    using group names from an Excel sheet. Navigates through the admin portal and submits group creation forms.
    """
    async with async_playwright() as p:
        # Launch Chromium browser in non-headless mode for inspection
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Step 1: Navigate to Atlassian login page
        await page.goto(LOGIN_URL)

        # Step 2: Enter username/email and proceed
        await page.fill('input#username-uid1', USERNAME)
        await page.click('button#login-submit')
        await page.wait_for_selector('input#password', timeout=10000)

        # Step 3: Enter password and log in
        await page.fill('input#password', PASSWORD)
        await page.click('button#login-submit')
        await page.wait_for_load_state('networkidle')

        # Step 4: Navigate to 'Directory' section in the sidebar
        await page.wait_for_selector('div[role="list"] >> text=Directory', timeout=10000)
        await page.click('div[role="list"] >> text=Directory')
        await page.wait_for_load_state('networkidle')

        # Step 5: Iterate through each group name and create the group
        for group in group_list:
            # Navigate to 'Groups' section in the sidebar
            await page.wait_for_selector('div[role="list"] >> text=Groups', timeout=10000)
            await page.click('div[role="list"] >> text=Groups')
            await page.wait_for_load_state('networkidle')

            # Click on 'Create group' button
            await page.wait_for_selector('button:has-text("Create group")', timeout=10000)
            await page.click('button:has-text("Create group")')
            await page.wait_for_selector('input[name="groupName"]', timeout=10000)

            # Fill in group name and description from Excel sheet
            await page.fill('input[name="groupName"]', group)
            await page.fill('textarea[name="groupDescription"]', f"This is: {group}")

            # Submit the group creation form
            await page.click('button[data-testid="test-create-group-modal-button"]')
            await asyncio.sleep(1)  # Short pause to allow processing

        # Keep browser open for inspection before closing
        await asyncio.sleep(4)
        await browser.close()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(run())