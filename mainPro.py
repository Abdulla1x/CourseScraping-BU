from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig, Controller
from pydantic import SecretStr, BaseModel
from typing import List
import os
import asyncio
import getpass
from dotenv import load_dotenv
import pandas as pd
load_dotenv()

username = input("Enter your username: ")
password = getpass.getpass("Enter your password: ")
api_key = os.getenv("GEMINI_API_KEY")

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
    Only Obtain the following information for each course the first page (Make sure its in JSON format):
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
    Return the obtained information.
    ```
"""

def save_to_file(data,filename="courses.csv"):
    courses_data = []
    for course in data:
        course_dict = {
            "Course Code": course.course_code,
            "Course Name": course.course_name,
            "Credits": course.credits,
            "Instructor": ", ".join(course.instructor),  # If there is multiple professors seperate by comma
            "Room": course.room,
            "Days": course.days,
            "Start Time": course.start_time,
            "End Time": course.end_time,
            "Max Enroll": course.max_enroll,
            "Total Enroll": course.total_enroll
        }
        courses_data.append(course_dict)

    df = pd.DataFrame(courses_data)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")


# Initialize the model
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(os.getenv('GEMINI_API_KEY')))
browser = Browser()
async def main():
    agent = Agent(
        task=task,
        llm=llm,
        use_vision=False,
        controller=controller,
    )
    results = await agent.run()
    #print(results.final_result())
    data = results.final_result()
    if data:
        parsed: Courses = Courses.model_validate_json(data)
        save_to_file(parsed.courses)
    input("Press Enter to continue...")
    await browser.close()

asyncio.run(main())
