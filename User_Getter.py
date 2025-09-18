import asyncio
import os
import json
import re

from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

LOGIN_URL = os.getenv("ATLASSIAN_URL")
DIRECTORY_URL = os.getenv("ATLASSIAN_DIRECTORY_URL")
USERNAME = os.getenv("ATLASSIAN_USERNAME")
PASSWORD = os.getenv("ATLASSIAN_PASSWORD")

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

        # Step 5: Extract org-id from the current URL
        current_url = page.url
        match = re.search(r'/o/([a-f0-9\-]+)/users', current_url)
        org_id = match.group(1) if match else None

        if org_id:
            api_url = f"https://admin.atlassian.com/gateway/api/admin/v2/orgs/{org_id}/directories/-/users"
            response = await page.request.get(api_url)
            User_json = await response.json()

            # Filter required fields
            filtered_users = []
            for user in User_json.get("data", []):
                filtered_users.append({
                    "id": user.get("accountId"),
                    "name": user.get("name"),
                    "email": user.get("email"),
                    "status": user.get("status"),
                    "accountStatus": user.get("accountStatus")
                })

            # Save to JSON file
            with open("Outputs/Users_Result.json", "w") as f:
                json.dump(filtered_users, f, indent=2)
   
        # Keep browser open for inspection
        await asyncio.sleep(4)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())