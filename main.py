import streamlit as st
import sqlite3
import os
import pandas as pd
import base64
# Directory for storing uploaded PDFs
pdfs_directory = './pdfs'
if not os.path.exists(pdfs_directory):
    os.makedirs(pdfs_directory)

# Initialize database and create table if not exists
def init_db():
    with sqlite3.connect('profiles.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_name TEXT NOT NULL,
                business_name TEXT,
                federal_tax_classification TEXT,
                exemptions TEXT,
                address_street TEXT NOT NULL,
                address_city TEXT NOT NULL,
                address_state TEXT NOT NULL,
                address_zip TEXT NOT NULL,
                account_numbers TEXT,
                ssn_or_ein TEXT NOT NULL,
                signature_reference TEXT,
                form_date DATE NOT NULL,
                email TEXT,
                phone_number TEXT,
                certification_status BOOLEAN
            )
        ''')

# Function to add a profile to the database
def add_profile(data, signature_path):
    with sqlite3.connect('profiles.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO profiles (vendor_name, business_name, federal_tax_classification, exemptions, address_street, 
            address_city, address_state, address_zip, account_numbers, ssn_or_ein, signature_reference, form_date, email, 
            phone_number, certification_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*data, signature_path))
        conn.commit()

# Load profiles from the database
def load_profiles():
    with sqlite3.connect('profiles.db') as conn:
        return pd.read_sql('SELECT * FROM profiles', conn)


def display_profiles():
    st.write("## Profiles")
    profiles_df = load_profiles()
    if not profiles_df.empty:
        # Hide signature path for privacy and adjust columns as needed
        profiles_display_df = profiles_df.drop(['signature_reference'], axis=1)

        # Display profiles as an interactive table
        st.dataframe(profiles_display_df)

        # Directly use vendor names for selection
        vendor_names = profiles_df['vendor_name'].tolist()
        selected_vendor_name = st.selectbox("Select a vendor name to view more details", options=vendor_names)

        # Find the first matching profile for the selected vendor name
        selected_profile = profiles_df[profiles_df['vendor_name'] == selected_vendor_name].iloc[0]

        if st.button("View Details"):
            st.write("### Profile Details")
            for col in profiles_display_df.columns:
                st.text(f"{col}: {selected_profile[col]}")

            # Add a download button for the profile's PDF if the path exists
            signature_path = selected_profile['signature_reference']
            if signature_path and os.path.isfile(signature_path):
                with open(signature_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                    b64 = base64.b64encode(pdf_bytes).decode()
                    href = f'<a href="data:application/pdf;base64,{b64}" download="{os.path.basename(signature_path)}">Download PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)



# Streamlit UI
def main():
    st.title("W-9 Form Management System")

    # Database initialization
    init_db()

    # Form submission
    with st.form("profile_form", clear_on_submit=True):
        vendor_name = st.text_input("Vendor Name", max_chars=50)
        business_name = st.text_input("Business Name", max_chars=50)
        federal_tax_classification = st.selectbox("Federal Tax Classification", ["", "Individual/Sole proprietor", "C Corporation", "S Corporation", "Partnership", "Trust/estate"])
        exemptions = st.text_input("Exemptions", max_chars=50)
        address_street = st.text_input("Street Address", max_chars=100)
        address_city = st.text_input("City", max_chars=50)
        address_state = st.text_input("State", max_chars=50)
        address_zip = st.text_input("ZIP", max_chars=10)
        account_numbers = st.text_input("Account Numbers", max_chars=100)
        ssn_or_ein = st.text_input("SSN or EIN", max_chars=11)
        form_date = st.date_input("Form Date")
        email = st.text_input("Email", max_chars=50)
        phone_number = st.text_input("Phone Number", max_chars=15)
        certification_status = st.checkbox("Certification Status")

        pdf = st.file_uploader("Upload Signature PDF", type=["pdf"])
        submitted = st.form_submit_button("Submit")

        if submitted and pdf is not None:
            signature_path = os.path.join(pdfs_directory, pdf.name)
            with open(signature_path, "wb") as f:
                f.write(pdf.getbuffer())

            profile_data = (vendor_name, business_name, federal_tax_classification, exemptions, address_street, address_city, address_state, address_zip, account_numbers, ssn_or_ein, form_date, email, phone_number, certification_status)
            add_profile(profile_data, signature_path)
            st.success("Profile submitted successfully.")

    # Display profiles in a clickable table


    display_profiles()
        # Optional: Implement functionality to view more details or the signature PDF for a selected profile

if __name__ == "__main__":
    main()
