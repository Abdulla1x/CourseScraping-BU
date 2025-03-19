from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig
from pydantic import SecretStr
import os
import asyncio
import getpass
from dotenv import load_dotenv
load_dotenv()

username = input("Enter your username: ")
password = getpass.getpass("Enter your password: ")
api_key = os.getenv("GEMINI_API_KEY")

task = f"""
    ### Step 1: Navigate to Website
    Open "https://cudportal.cud.ac.ae/student/login.asp" in a web browser.
    ### Step 2: Enter Credentials
    Enter the following credentials:
    - Username: {username}
    - Password: {password}
    ### Step 3: Login
    Click the "Login" button.
    ### Step 4: Access Courses
    Click on the "Course Offerings" tab.
    ### Step 5: Filter Courses
    Filter the courses by selecting the "Show Filter" option.
    Select SEAST from the division dropdown
    Click the "Apply Filter" button.
    ### Step 6: Obtain Courses
    Retrieve the list of courses in json.
"""

# Initialize the model
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(os.getenv('GEMINI_API_KEY')))
browser = Browser()
async def main():
    agent = Agent(
        task=task,
        llm=llm,
    )
    await agent.run()
    input("Press Enter to continue...")
    await browser.close()

asyncio.run(main())