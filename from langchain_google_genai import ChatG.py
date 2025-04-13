from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig, Controller
from pydantic import SecretStr, BaseModel
from typing import List
import os
import asyncio
import getpass
from dotenv import load_dotenv
import pandas as pd
from playwright.async_api import BrowserContext

load_dotenv()

username = input("Enter your username: ")
password = getpass.getpass("Enter your password: ")
api_key = os.getenv("GEMINI_API_KEY")

class CPage(BaseModel):
    total_pages: int

class Course(BaseModel):
    course_code: str
    course_name: str
    credits: int
    instructor: List[str]
    room: str
    days: str
    start_time: str
    end_time: str
    max_enroll: str
    total_enroll: str

class Courses(BaseModel):
    courses: List[Course]

controller = Controller(output_model=Courses)

starting_task = f"""
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
    ### Step 6: Wait till the site loads
    Wait until the site fully loads
"""

def get_iter_task(page_num: int) -> str:
    return f"""
    #Step 7: go to desired page
    Go to page {page_num}
    #Step 8: obtain info
    Only Obtain the following information for each course (Make sure its in JSON format):
    - Course Code
    - Course Name
    - Credits
    - Instructor
    - Room
    - Days
    - Start Time
    - End Time
    - Max Enroll
    - Total Enroll
    ### Step 7: Return Courses
    Return the obtained information."""

async def click_next_page(page, current_page):
    next_button = await page.query_selector(f"text='{current_page + 1}'")
    if next_button:
        await next_button.click()
        await page.wait_for_timeout(1500)
        return True
    return False

def save_to_file(data, pagenum,  filename="test.csv"):
    courses_data = []
    for course in data:
        course_dict = {
            "Course Code": course.course_code,
            "Course Name": course.course_name,
            "Credits": course.credits,
            "Instructor": ", ".join(course.instructor),
            "Room": course.room,
            "Days": course.days,
            "Start Time": course.start_time,
            "End Time": course.end_time,
            "Max Enroll": course.max_enroll,
            "Total Enroll": course.total_enroll
        }
        courses_data.append(course_dict)

    df = pd.DataFrame(courses_data)
    # Write header only for the first page
    df.to_csv(filename, mode='a', index=False, header=not os.path.exists(filename))
    print(f"Page {pagenum} data saved to {filename}")

# Initialize the model
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', 
                             api_key=SecretStr(os.getenv('GEMINI_API_KEY')),
                             temperature=0.0)
browser = Browser()

async def main():
    current_page = 1

    try:
        async with await browser.new_context() as context:
            # First agent to get total pages
            agent = Agent(
                task=starting_task,
                llm=llm,
                browser_context=context,
                use_vision=False,
                controller=controller
            )  
            await agent.run()

            pageobj = await context.get_current_page()
            url = pageobj.url
            visited_urls = set()
            # Process each page
            while True:
                if click_next_page(url, current_page) and url not in visited_urls: # Makes sure there is a next page and it hasn't been visited before
                    try:
                        next_agent = Agent(
                            task=get_iter_task(current_page),
                            llm=llm,
                            browser_context=context,
                            use_vision=False,
                            controller=controller,
                            max_actions_per_step=20
                        )

                        pageobj = await context.get_current_page()
                        url = pageobj.url
                        visited_urls.add(url)

                        results = await next_agent.run()
                        data = results.final_result()
                        if data:
                            parsed = Courses.model_validate_json(data)
                            save_to_file(parsed.courses, current_page)
                    except Exception as e:
                        print(f"Error processing page {current_page}: {str(e)}")
                        continue
                else:
                    break
                current_page +=1

    except Exception as e:
        print(f"Main error: {str(e)}")
    finally:
        await browser.close()

asyncio.run(main())