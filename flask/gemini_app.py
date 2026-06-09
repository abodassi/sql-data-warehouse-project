import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
import re

# --------------------------
# Gemini API key
# --------------------------
API_KEY = "AIzaSyBtzzEnQX0vU6yZ4YcawpEW4v9o8lSEpGs"
client = genai.Client(api_key=API_KEY)

st.title("Data Analysis System with Gemini (Plotly)")

# ---- Load backend CSV and remove last 3 rows ----
df = pd.read_csv("data.csv")
if df.shape[0] > 3:
    df = df.iloc[:-3, :] 
st.write("CSV shape after removing last 3 rows:", df.shape)
st.write("CSV Columns:", df.columns.tolist())

# ---- Question input ----
user_question = st.text_input("Ask a question about your data:")

if user_question:
    prompt = f"""
    You are writing Python code inside an existing Python environment.
    You have a DataFrame `df` with these columns: {df.columns.tolist()}.
    import all necessaries libraries 
    Do NOT create or assume any new columns or data. Use only columns that exist in `df`.
    Use Plotly Express to create or charts which exactly the interactive chart suitable for the question.
    if it was one value use card if it few value use pie chart if its more than that use the best chart to express what the question want
    Return the figure object as `fig`.
    Do NOT return text, explanations, or fake data.
    Question: {user_question}
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    gpt_code = response.text.strip()

    # Clean ``` or python
    gpt_code = re.sub(r"^```(?:python)?\n?", "", gpt_code)
    gpt_code = re.sub(r"```$", "", gpt_code)

    # ---- Execute generated code safely ----
    try:
        print(gpt_code)
        local_vars = {'df': df, 'px': px, 'st': st}
        exec(gpt_code, {}, local_vars)

        # ---- Display figure if returned ----
        if 'fig' in local_vars:
            st.plotly_chart(local_vars['fig'], use_container_width=True)
        else:
            st.error("No figure object returned by Gemini code.")
    except Exception as e:
        st.error(f"Error executing the code: {e}")
