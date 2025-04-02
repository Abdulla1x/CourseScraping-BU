### Step 1: Install Dependencies
Open the terminal and run the following commands:
```sh
pip install browser-use
pip install playwright
playwright install
pip install google-genai langchain
```

### Step 2: Set Up Gemini API Key
1. Generate your Gemini API key by visiting [Google AI Studio](https://ai.google.dev/).
2. Navigate to "Explore Models in Google AI Studio".
3. Click on "Get API Key".
4. Click on "Create API Key" and copy the generated key.
5. Open VSCode and create a new file named `.env`.
6. Paste your API key in the following format:
   ```sh
   GEMINI_API_KEY=your_api_key
   ```
### Step 3: Clone the repo
   ```sh
   git clone https://github.com/suhailsameer/CourseScraping-BU.git
   ```
### Step 4: Run Streamlit
Once above steps are completed, run the following command in the terminal to start the program
   ```sh
   steamlit run .\streamlitApp.py
   ```



