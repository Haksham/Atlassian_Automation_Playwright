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
    Automates login to Atlassian admin portal, navigates to Groups section,
    fetches group details and their members, and saves the results to a JSON file.
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

        # Step 5: Navigate to 'Groups' section in the sidebar
        await page.wait_for_selector('div[role="list"] >> text=Groups', timeout=10000)
        await page.click('div[role="list"] >> text=Groups')
        await page.wait_for_load_state('networkidle')

        # Step 6: Extract organization ID from the current URL using regex
        current_url = page.url
        match = re.search(r'/o/([a-f0-9\-]+)/groups', current_url)
        org_id = match.group(1) if match else None

        if org_id:
            # Construct API URL to fetch groups for the organization
            api_url = f"https://admin.atlassian.com/gateway/api/adminhub/um/org/{org_id}/groups"
            response = await page.request.get(api_url)
            groups_json = await response.json()

            filtered_groups = []
            
            # Iterate through each group and fetch their members
            for group in groups_json.get("groups", []):
                group_members = []

                # Construct API URL to fetch members for the group
                group_member_url = f"https://admin.atlassian.com/gateway/api/adminhub/um/org/{org_id}/groups/{group.get('id')}/members"
                member_response = await page.request.get(group_member_url)
                member_json = await member_response.json()

                # Collect display names of group members
                for member in member_json.get("users", []):
                    group_members.append(member.get("displayName"))

                # Append filtered group info to the list
                filtered_groups.append({
                    "Id": group.get("id"),
                    "Name": group.get("name"),
                    "Description": group.get("description"),
                    "Members": group_members
                })
            
            # Save filtered groups data to JSON file
            with open("Outputs/Groups_Result.json", "w") as f:
                json.dump(filtered_groups, f, indent=2)
            print("Saved filtered groups to Groups_Result.json")
        else:
            print("Could not extract org-id from URL.")

        # Keep browser open for inspection before closing
        await asyncio.sleep(4)
        await browser.close()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(run())