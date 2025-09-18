import asyncio
import os
import json
import re

from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables from .env file
load_dotenv()

# Retrieve Atlassian credentials and URLs from environment variables
LOGIN_URL = os.getenv("ATLASSIAN_URL")
USERNAME = os.getenv("ATLASSIAN_USERNAME")
PASSWORD = os.getenv("ATLASSIAN_PASSWORD")

async def run():
    """
    Automates login to Atlassian admin portal, navigates to Users section,
    fetches user details and their group memberships, and saves the results to a JSON file.
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

        # Step 6: Extract organization ID from the current URL using regex
        current_url = page.url
        match = re.search(r'/o/([a-f0-9\-]+)/users', current_url)
        org_id = match.group(1) if match else None

        if org_id:
            # Construct API URL to fetch users for the organization
            api_url = f"https://admin.atlassian.com/gateway/api/admin/v2/orgs/{org_id}/directories/-/users?limit=100"
            response = await page.request.get(api_url)
            User_json = await response.json()

            filtered_users = []

            # Iterate through each user and fetch their group memberships
            for user in User_json.get("data", []):
                user_gp = []

                # Construct API URL to fetch groups for the user
                user_group_url = (
                    f"https://admin.atlassian.com/gateway/api/admin/v2/orgs/{org_id}/directories/-/groups?accountIds={user.get('accountId')}"
                )
                group_response = await page.request.get(user_group_url)
                group_json = await group_response.json()
                
                # Collect group names for the user
                for group in group_json.get("data", []):
                    user_gp.append(group.get("name"))

                # Append filtered user info to the list
                filtered_users.append({
                    "Id": user.get("accountId"),
                    "Name": user.get("name"),
                    "Email": user.get("email"),
                    "Status": user.get("status"),
                    "Last Seen": user.get("addedToOrg"),
                    "Groups": user_gp
                })

            # Save filtered user data to JSON file
            with open("Outputs/Users_Result.json", "w") as f:
                json.dump(filtered_users, f, indent=2)
   
        # Keep browser open for inspection before closing
        await asyncio.sleep(4)
        await browser.close()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(run())