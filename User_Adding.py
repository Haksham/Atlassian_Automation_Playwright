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

# Read email IDs and group names from Excel sheet named "User.xlsx"
excel_path = os.path.join(os.path.dirname(__file__), "Data/User.xlsx")
df = pd.read_excel(excel_path)
email_list = df['Mail Id'].dropna().tolist()  # Extract non-empty email IDs
group_list = df['Group'].dropna().tolist()    # Extract non-empty group names

async def run():
    """
    Automates the process of inviting users to Atlassian organization and assigning them to groups,
    using data from an Excel sheet. Navigates through the admin portal and submits invitations.
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

        # Step 5: Navigate to 'Users' section in the sidebar
        await page.wait_for_selector('div[role="list"] >> text=Users', timeout=10000)
        await page.click('div[role="list"] >> text=Users')
        await page.wait_for_load_state('networkidle')

        # Step 6: Click on 'invite users' button
        await page.wait_for_selector('button:has-text("invite users")', timeout=10000)
        await page.click('button:has-text("invite users")')
        await page.wait_for_selector('input#invite-users-email-input', timeout=10000)

        # Step 7: Iterate through email and group pairs and fill the invitation form
        for email, group in zip(email_list, group_list):
            # Enter email address
            await page.fill('input#invite-users-email-input', email)
            # Enter group name and confirm selection
            await page.fill('input#group-membership-input', str(group))
            await page.press('input#group-membership-input', 'Enter')

        # Step 8: Submit the invitation form
        await page.click('button[data-testid="invite-submit-button"]')     

        # Keep browser open for inspection before closing
        await asyncio.sleep(5)
        await browser.close()

# Note: Only 4 IDs can be invited per batch due to Atlassian limitations.

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(run())