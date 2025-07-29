import streamlit as st
import os
import csv
import shutil
import zipfile
from CNCpack2 import cnc_partlist

st.title("🛠 STEELCORP USA CNC Partlist Processor")
st.title("by: V.Suarez ")


# User input: Job code
job_code = st.text_input("Job Code").strip().upper()

# User input: Partlist CSV
uploaded_file = st.file_uploader("Upload Partlist CSV", type=["csv"])

# Output directory
OUTPUT_DIR = "cnc_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

if st.button("Run CNC Processing"):
    if not job_code:
        st.error("❌ Please enter a Job Code.")
    elif not uploaded_file:
        st.error("❌ Please upload a Partlist CSV.")
    else:
        try:
            # Save uploaded file to temporary path
            partlist_path = os.path.join(OUTPUT_DIR, "partlist.csv")
            with open(partlist_path, "wb") as f:
                f.write(uploaded_file.read())

            # Run processing
            cnc_partlist(job_code, partlist_path)

            # Gather output files
            output_files = [
                os.path.join(OUTPUT_DIR, fname)
                for fname in os.listdir(OUTPUT_DIR)
                if fname.endswith(".Parts List") or fname == "skippedparts.csv"
            ]

            if output_files:
                st.success("✅ Processing completed. Download your files below:")

                # Optionally zip all results
                zip_path = os.path.join(OUTPUT_DIR, f"{job_code}_cnc_results.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for file in output_files:
                        zipf.write(file, arcname=os.path.basename(file))

                # Download all as ZIP
                with open(zip_path, "rb") as zip_file:
                    st.download_button(
                        label="📦 Download All CNC Files (.zip)",
                        data=zip_file,
                        file_name=os.path.basename(zip_path),
                        mime="application/zip"
                    )

                # Or download each file individually
                for file_path in output_files:
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label=f"⬇ Download {os.path.basename(file_path)}",
                            data=f,
                            file_name=os.path.basename(file_path),
                            mime="text/plain"
                        )
            else:
                st.warning("⚠️ No CNC output files were generated.")

        except Exception as e:
            st.error(f"❌ Error during processing: {e}")

