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

        # Step 4: Click on 'Groups' inside div[role="list"]
        await page.wait_for_selector('div[role="list"] >> text=Groups', timeout=10000)
        await page.click('div[role="list"] >> text=Groups')
        await page.wait_for_load_state('networkidle')

        # Step 5: Extract org-id from the current URL
        current_url = page.url
        match = re.search(r'/o/([a-f0-9\-]+)/groups', current_url)
        org_id = match.group(1) if match else None

        if org_id:
            api_url = f"https://admin.atlassian.com/gateway/api/adminhub/um/org/{org_id}/groups?count=20&start-index=1"
            response = await page.request.get(api_url)
            groups_json = await response.json()
            
            # Extract only id, name, description for each group
            filtered_groups = [
                {
                    "id": group.get("id"),
                    "name": group.get("name"),
                    "description": group.get("description")
                }
                for group in groups_json.get("groups", [])
            ]
            
            # Save to Groups_Result.json
            with open("Outputs/Groups_Result.json", "w") as f:
                json.dump(filtered_groups, f, indent=2)
            print("Saved filtered groups to Groups_Result.json")
        else:
            print("Could not extract org-id from URL.")

        
        # Keep browser open for inspection
        await asyncio.sleep(4)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())