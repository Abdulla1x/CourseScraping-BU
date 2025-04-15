import os
import streamlit as st
import pandas as pd
from mainPro import main,ollama_func  # Import the main function from mainPro.py
import asyncio
from PIL import Image

# Streamlit UI
st.set_page_config(page_title="Course Scraper App", page_icon="📚", layout="wide")


st.title("📚 Course Scraper App")
st.write("Enter your credentials to fetch course data.")

# Sidebar for inputs
st.sidebar.image("canadian-university-dubai-seeklogo.png", use_container_width=True)
st.sidebar.header("Login to Fetch Courses")
username = st.sidebar.text_input("Enter your username:", help="Your university username.")
password = st.sidebar.text_input("Enter your password:", type="password", help="Your university password.")
semester = st.sidebar.selectbox("Select Semester:", [
    "FA 2025-26", "SU 1 2024-25", "SP 2024-25", "FA 2024-25",
    "SU 2 2023-24", "SU 1 2023-24", "SP 2023-24", "FA 2023-24",
    "SU 2 2022-23", "SU 1 2022-23", "SP 2022-23", "FA 2022-23",
    "SU 2 2021-22", "SU 1 2021-22", "SP 2021-22", "FA 2021-22",
    "SU 2 2020-21", "SU 1 2020-21", "SP 2020-21", "FA 2020-21",
    "SU 2 2019-20", "SU 1 2019-20", "SP 2019-20", "FA 2019-20",
    "SU 2 2018-19", "SU 1 2018-19", "SP 2018-19", "FA 2018-19",
    "SU 2 2017-18", "SU 1 2017-18", "SP 2017-18", "FA 2017-18",
    "SU 2 2016-17", "SU 1 2016-17", "SP 2016-17", "FA 2016-17",
    "SU 2 2015-16", "SU 1 2015-16", "SP 2015-16", "FA 2015-16",
    "SU 2 2014-15", "SU 1 2014-15", "SP 2014-15", "FA 2014-15",
    "SU 2 2013-14", "SU 1 2013-14", "SP 2013-14", "FA 2013-14",
    "SU 2 2012-13", "SU 1 2012-13", "SP 2012-13", "FA 2012-13"
], help="Select the semester for which you want to fetch courses.")


# Fetch Courses Button
if st.sidebar.button("Fetch Courses"):
    if username and password and semester:
        # Run the main function from mainPro.py
        try:
            # Show progress bar
            with st.spinner("Fetching courses..."):
                asyncio.set_event_loop(asyncio.new_event_loop())  # Ensure a new event loop for Streamlit
                courses = asyncio.run(main(username, password, semester))  # Call the main function

            if os.path.exists("courses.csv"):
                df = pd.read_csv("courses.csv")
                st.success("Courses fetched successfully!")
                st.write("### Courses:")
                st.dataframe(df, use_container_width=True)  # Display the courses in a table

                # Add a download button
                st.download_button(
                    label="Download Courses as CSV",
                    data=df.to_csv(index=False),
                    file_name="courses.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No courses found.")
        except Exception as e:
            st.error("An error occurred while fetching courses.")
            st.write(str(e))
    else:
        st.warning("Please enter username, password and select an appropriate semester.")

if st.sidebar.button("Test Local LLM"):
        with st.spinner("Running Local LLM to find Capital of Brazil....."):
            asyncio.set_event_loop(asyncio.new_event_loop()) 
            courses = asyncio.run(ollama_func())