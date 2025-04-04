from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig, Controller
from pydantic import SecretStr, BaseModel
from typing import List
import os
import csv
import pandas as pd
import asyncio
import sys
import getpass
from dotenv import load_dotenv
load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

#username = input("Enter your username: ")
#password = getpass.getpass("Enter your password: ")
api_key = os.getenv("GEMINI_API_KEY")

async def extract_course_data(page):
    courses = []
    await page.wait_for_selector("table")
    table = await page.query_selector("table")
    rows = await table.query_selector_all("tr")
    for row in rows[1:]:
        cell = await row.query_selector_all("td")
        data = [await cell.inner_text() for cell in cell]
        if data:
            courses.append(data)
    return courses

async def click_next_page(page, current_page):
    next_button = await page.query_selector(f"text='{current_page + 1}'")
    if next_button:
        await next_button.click()
        await page.wait_for_timeout(1500)
        return True
    return False

async def format_data(page):
    formatted_data = []
    current_page = 1
    last_page = 8
    last_course = None

    while current_page <= last_page:
        courses = await extract_course_data(page)
        current_course = None

        for course in courses:
            if len(course) == 7 and "Credits" not in course[2]:  # Check for valid course entry
                course_key = f"{course[0]}|{course[1]}"
                if course_key == last_course:
                    continue

                current_course = {
                    "Course Code": course[0].strip(),
                    "Course Name": course[1].strip(),
                    "Credits": course[2].strip(),
                    "Start Date": course[3].strip(),
                    "End Date": course[4].strip(),
                    "Max Enrollment": course[5].strip(),
                    "Total Enrollment": course[6].strip(),
                    "Instructor": "",  # Placeholder
                    "Room": "",
                    "Days": "",
                    "Start Time": "",
                    "End Time": "",
                    "Date": "",
                }
                last_course = course_key

            elif current_course and any("Instructor" in data for data in course):
                # Handling instructor and additional data
                mult_data = course[0].strip()
                if '\n' in mult_data:
                    inst_data = mult_data.split('\n')
                    for data in inst_data:
                        if "\t" in data and 'Instructor' not in data:
                            part = data.strip().split("\t")
                            if len(part) >= 8:
                                formatted_data.append({
                                    **current_course,  # Use existing course details
                                    "Instructor": part[0].strip(),
                                    "Room": part[1].strip(),
                                    "Days": part[2].strip(),
                                    "Date": part[3].strip(),
                                    "Start Time": part[4].strip(),
                                    "End Time": part[5].strip(),
                                    "Max Enrollment": part[6].strip(),
                                    "Total Enrollment": part[7].strip(),
                                })

        if current_page < last_page:
            success = await click_next_page(page, current_page)
            if not success:
                print("Failed to go to next page")
                break
        current_page += 1

    return formatted_data
    


# class Course(BaseModel):
#     course_code: str
#     course_name: str
#     credits: int
#     instructor: List[str]
#     room: str
#     days: str
#     start_time: str
#     end_time: str
#     max_enroll: str
#     total_enroll: str

# class Courses(BaseModel):
#     courses: List[Course]

# controller = Controller(output_model=Courses)




# def save_to_file(data,filename="courses.csv"):
#     courses_data = []
#     for course in data:
#         course_dict = {
#             "Course Code": course.course_code,
#             "Course Name": course.course_name,
#             "Credits": course.credits,
#             "Instructor": ", ".join(course.instructor),  # If there is multiple professors seperate by comma
#             "Room": course.room,
#             "Days": course.days,
#             "Start Time": course.start_time,
#             "End Time": course.end_time,
#             "Max Enroll": course.max_enroll,
#             "Total Enroll": course.total_enroll
#         }
#         courses_data.append(course_dict)

#     df = pd.DataFrame(courses_data)
#     df.to_csv(filename, index=False)
#     print(f"Data saved to {filename}")

def save_to_file(data, filename="courses.csv"):
    headers = [
        "Course Code", "Course Name", "Credits", "Instructor",
        "Room", "Days", "Date", "Start Time", "End Time",
        "Max Enrollment", "Total Enrollment"
    ]
    df = pd.DataFrame(data, columns=headers)
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"Data saved to {filename}")


# Initialize the model
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(os.getenv('GEMINI_API_KEY')))
browser = Browser()

# async def main(username, password, semester):
#     username = username
#     password = password
#     semester = semester
#     task = f"""
#     ### Step 1: Navigate to Website
#     Open "https://cudportal.cud.ac.ae/student/login.asp" in a web browser.
#     ### Step 2: Enter Credentials
#     Enter the following credentials:
#     - Username: {username}
#     - Password: {password}
#     - Semester: {semester} # Select the semester from the dropdown
#     ### Step 3: Login
#     Click the "Login" button.
#     ### Step 4: Access Courses
#     Click on the "Course Offerings" tab.
#     ### Step 5: Filter Courses
#     Filter the courses by selecting the "Show Filter" option.
#     Select SEAST from the division dropdown
#     Click the "Apply Filter" button.
#     ### Step 6: Obtain Courses
#     Only Obtain the following information for each course from pages 1-3 (Make sure its in JSON format):
#     - Course Code
#     - Course Name
#     - Credits
#     - Instructor
#     - Room
#     - Days
#     - Start Time
#     - End Time
#     - Max Enroll
#     - Total Enroll
#     ### Step 7: Return Courses
#     Return the obtained information.
#     ```
# """
#     agent = Agent(
#         task=task,
#         llm=llm,
#         use_vision=False,
#         controller=controller,
#     )
#     results = await agent.run()
#     #print(results.final_result())
#     data = results.final_result()
#     if data:
#         parsed: Courses = Courses.model_validate_json(data)
#         if parsed.courses != []:  
#             save_to_file(parsed.courses)
#             await browser.close()
#             return parsed.courses
#         else:
#             print("Not able to fetch courses")
#             await browser.close()
#     else:
#         print("Parsing error")
#         await browser.close()

async def main(username,password, semester):
    print("")
    window = await browser.new_context()
    task = f"""
    ### Step 1: Navigate to Website
    Open "https://cudportal.cud.ac.ae/student/login.asp" in a web browser.
    ### Step 2: Enter Credentials
    Enter the following credentials:
    - Username: {username}
    - Password: {password}
    - Semester: {semester} # Select the semester from the dropdown
    ### Step 3: Login
    Click the "Login" button.
    ### Step 4: Access Courses
    Click on the "Course Offerings" tab.
    ### Step 5: Filter Courses
    Filter the courses by selecting the "Show Filter" option.
    Select SEAST from the division dropdown
    Click the "Apply Filter" button.
    ```
    """
    agent=Agent(
        task=task,
        llm=llm,
        use_vision=False,
        browser=browser,
        browser_context=window
    )
    await agent.run()
    page = await window.get_current_page()
    
    formatted_data=[]
    formatted_data = await format_data(page)
    save_to_file(formatted_data)

    print("✅ All pages scraped and saved to courses.csv")
    await window.close()
    print("Browser closed automatically.")

#asyncio.run(main(username,password, semester))
