import streamlit as st
import pandas as pd
import os
import csv
from CNCpack2 import cnc_partlist

# Constants
HISTORY_FILE = "execution_history.csv"

def save_execution_history(job_code, partlist_file):
    """Save the input values to a CSV file."""
    with open(HISTORY_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["job_code", "partlist_file"])
        writer.writerow([job_code, partlist_file])

def load_last_execution():
    """Load the last saved input values from the CSV file."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, mode="r") as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header
            try:
                return next(reader)
            except StopIteration:
                return None
    return None

# Streamlit UI
st.title("🛠 CNC Partlist Processor")

# Load last execution values (if any)
last_execution = load_last_execution()
default_job_code = last_execution[0] if last_execution else ""
default_partlist_path = last_execution[1] if last_execution else None

# Job code input
job_code = st.text_input("Job Code", value=default_job_code).strip().upper()

# File uploader
uploaded_file = st.file_uploader("Upload Partlist CSV", type=["csv"])

# If using default from last session
use_last_file = st.checkbox("Use last uploaded file", value=not uploaded_file and default_partlist_path is not None)

# Execute
if st.button("Run CNC Processing"):
    if not job_code:
        st.error("Please enter a job code.")
    elif not uploaded_file and not use_last_file:
        st.error("Please upload a partlist CSV or check 'Use last uploaded file'.")
    else:
        try:
            # Determine which file to use
            if use_last_file:
                partlist_file_path = default_partlist_path
                if not os.path.exists(partlist_file_path):
                    st.error(f"Last used file not found: {partlist_file_path}")
                    st.stop()
            else:
                # Save uploaded file to a temporary location
                temp_path = os.path.join("temp_partlist.csv")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())
                partlist_file_path = temp_path

            # Run your logic
            cnc_partlist(job_code, partlist_file_path)

            # Save to history
            save_execution_history(job_code, partlist_file_path)

            st.success("✅ CNC Partlist processed successfully.")
        except Exception as e:
            st.error(f"❌ Error: {e}")

