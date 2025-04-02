import streamlit as st
import pandas as pd
from mainPro import main  # Import the main function from mainPro.py
import asyncio

# Streamlit UI
st.title("Course Scraper App")
st.write("Enter your credentials to fetch course data.")

# Input fields for username and password
username = st.text_input("Enter your username:")
password = st.text_input("Enter your password:", type="password")

# Button to trigger the scraping process
if st.button("Fetch Courses"):
    if username and password:
        # Run the main function from mainPro.py
        try:
            # Pass the username and password to the main function
            asyncio.set_event_loop(asyncio.new_event_loop())  # Ensure a new event loop for Streamlit
            courses = asyncio.run(main(username, password))  # Call the main function
            
            # Check if courses were returned
            if courses:
                st.success("Courses fetched successfully!")
                
                # Convert the list of courses to a DataFrame for display
                df = pd.DataFrame([course.model_dump() for course in courses])  # Convert Pydantic models to dicts
                st.write("### Courses:")
                st.dataframe(df, use_container_width=True)  # Display the courses in a table
            else:
                st.warning("No courses found.")
        except Exception as e:
            st.error("An error occurred while fetching courses.")
            st.write(str(e))
    else:
        st.warning("Please enter both username and password.")