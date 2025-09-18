import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os

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
        
        # Fill in email and continue
        await page.fill('input#username', USERNAME)
        await page.click('button#login-submit')
        await page.wait_for_selector('input#password', timeout=10000)
        
        # Fill in password and login
        await page.fill('input#password', PASSWORD)
        await page.click('button#login-submit')
        
        # Wait for navigation after login
        await page.wait_for_load_state('networkidle')
        
        # Navigate to the directory page
        await page.goto(DIRECTORY_URL)
        
        # Optional: wait for directory page to load
        await page.wait_for_load_state('networkidle')
        
        # Keep browser open for inspection
        await asyncio.sleep(10)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())