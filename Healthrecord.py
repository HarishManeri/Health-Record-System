import streamlit as st
import pandas as pd
import sqlite3
import os
import json
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Health Record System",
    page_icon="🏥",
    layout="wide"
)

# Database setup
DB_FILE = "health_records.db"

def initialize_database():
    """Create database and tables if they don't exist"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create patients table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        contact_info TEXT,
        medical_info TEXT,
        insurance_info TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on app start
initialize_database()

# Database functions
def add_patient(patient_data):
    """Add a new patient to the database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Check if patient already exists
    cursor.execute("SELECT id FROM patients WHERE id = ?", (patient_data['id'],))
    if cursor.fetchone():
        conn.close()
        return False, "Patient ID already exists"
    
    # Prepare data
    contact_info = json.dumps(patient_data.get('contact', {}))
    medical_info = json.dumps(patient_data.get('medical', {}))
    insurance_info = json.dumps(patient_data.get('insurance', {}))
    current_time = datetime.now().isoformat()
    
    # Insert patient
    cursor.execute('''
    INSERT INTO patients (id, name, age, gender, contact_info, medical_info, insurance_info, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        patient_data['id'],
        patient_data['name'],
        patient_data['age'],
        patient_data['gender'],
        contact_info,
        medical_info,
        insurance_info,
        current_time,
        current_time
    ))
    
    conn.commit()
    conn.close()
    return True, "Patient added successfully"

def get_patient(patient_id):
    """Get a patient by ID"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT * FROM patients WHERE id = ?
    ''', (patient_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        # Convert row to dict and parse JSON fields
        patient = dict(row)
        patient['contact'] = json.loads(patient['contact_info'])
        patient['medical'] = json.loads(patient['medical_info'])
        patient['insurance'] = json.loads(patient['insurance_info'])
        return patient
    
    return None

def update_patient(patient_id, updated_data):
    """Update an existing patient"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Check if patient exists
    cursor.execute("SELECT id FROM patients WHERE id = ?", (patient_id,))
    if not cursor.fetchone():
        conn.close()
        return False, "Patient not found"
    
    # Prepare data
    contact_info = json.dumps(updated_data.get('contact', {}))
    medical_info = json.dumps(updated_data.get('medical', {}))
    insurance_info = json.dumps(updated_data.get('insurance', {}))
    current_time = datetime.now().isoformat()
    
    # Update patient
    cursor.execute('''
    UPDATE patients 
    SET name = ?, age = ?, gender = ?, contact_info = ?, medical_info = ?, insurance_info = ?, updated_at = ?
    WHERE id = ?
    ''', (
        updated_data['name'],
        updated_data['age'],
        updated_data['gender'],
        contact_info,
        medical_info,
        insurance_info,
        current_time,
        patient_id
    ))
    
    conn.commit()
    conn.close()
    return True, "Patient updated successfully"

def delete_patient(patient_id):
    """Delete a patient by ID"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Check if patient exists
    cursor.execute("SELECT id FROM patients WHERE id = ?", (patient_id,))
    if not cursor.fetchone():
        conn.close()
        return False, "Patient not found"
    
    # Delete patient
    cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    
    conn.commit()
    conn.close()
    return True, "Patient deleted successfully"

def get_all_patients():
    """Get all patients summary"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, age, gender, created_at FROM patients ORDER BY name")
    
    rows = cursor.fetchall()
    patients = [dict(row) for row in rows]
    
    conn.close()
    return patients

# Application title and description
st.title("🏥 Health Record System")
st.markdown("Manage patient records with this easy-to-use interface.")

# Create tabs for different functionality
tab1, tab2, tab3, tab4 = st.tabs(["Add Patient", "View Patient", "Update Patient", "Delete Patient"])

# Tab 1: Add Patient
with tab1:
    st.header("Add New Patient")
    
    # Create form for adding patient
    with st.form("add_patient_form"):
        patient_id = st.text_input("Patient ID*", key="add_id")
        name = st.text_input("Full Name*", key="add_name")
        age = st.number_input("Age", min_value=0, max_value=120, key="add_age")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="add_gender")
        
        # Contact information
        st.subheader("Contact Information")
        phone = st.text_input("Phone Number", key="add_phone")
        email = st.text_input("Email", key="add_email")
        address = st.text_area("Address", key="add_address")
        
        # Medical details
        st.subheader("Medical Information")
        blood_type = st.selectbox("Blood Type", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], key="add_blood")
        allergies = st.text_area("Allergies", key="add_allergies")
        medical_conditions = st.text_area("Existing Medical Conditions", key="add_conditions")
        
        # Insurance details
        st.subheader("Insurance Details")
        insurance_provider = st.text_input("Insurance Provider", key="add_provider")
        insurance_id = st.text_input("Insurance ID", key="add_insurance_id")
        
        submit_button = st.form_submit_button("Add Patient")
        
        if submit_button:
            if not patient_id or not name:
                st.error("Patient ID and Full Name are required!")
            else:
                # Create patient data dictionary
                patient_data = {
                    "id": patient_id,
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "contact": {
                        "phone": phone,
                        "email": email,
                        "address": address
                    },
                    "medical": {
                        "blood_type": blood_type,
                        "allergies": allergies,
                        "conditions": medical_conditions
                    },
                    "insurance": {
                        "provider": insurance_provider,
                        "id": insurance_id
                    }
                }
                
                success, message = add_patient(patient_data)
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")

# Tab 2: View Patient
with tab2:
    st.header("View Patient Records")
    
    # Create a search box for patient ID
    search_patient_id = st.text_input("Enter Patient ID to search", key="search_id")
    search_button = st.button("Search")
    
    if search_button and search_patient_id:
        patient_data = get_patient(search_patient_id)
        if patient_data:
            # Display patient information
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Personal Information")
                st.write(f"**Name:** {patient_data.get('name')}")
                st.write(f"**ID:** {patient_data.get('id')}")
                st.write(f"**Age:** {patient_data.get('age')}")
                st.write(f"**Gender:** {patient_data.get('gender')}")
                
                st.subheader("Contact Information")
                contact = patient_data.get('contact', {})
                st.write(f"**Phone:** {contact.get('phone', 'N/A')}")
                st.write(f"**Email:** {contact.get('email', 'N/A')}")
                st.write(f"**Address:** {contact.get('address', 'N/A')}")
            
            with col2:
                st.subheader("Medical Information")
                medical = patient_data.get('medical', {})
                st.write(f"**Blood Type:** {medical.get('blood_type', 'N/A')}")
                st.write("**Allergies:**")
                st.write(medical.get('allergies', 'None'))
                st.write("**Medical Conditions:**")
                st.write(medical.get('conditions', 'None'))
                
                st.subheader("Insurance Details")
                insurance = patient_data.get('insurance', {})
                st.write(f"**Provider:** {insurance.get('provider', 'N/A')}")
                st.write(f"**Insurance ID:** {insurance.get('id', 'N/A')}")
            
            # Record timestamps
            st.divider()
            st.caption(f"Created: {patient_data.get('created_at')}")
            st.caption(f"Last Updated: {patient_data.get('updated_at')}")
            
            # Show JSON data option
            if st.checkbox("Show Raw Data"):
                st.json(patient_data)
        else:
            st.error("Patient not found!")
    
    # Option to view all patients
    if st.button("View All Patients"):
        patients_list = get_all_patients()
        
        if patients_list:
            # Create a DataFrame for display
            df = pd.DataFrame([
                {
                    "ID": p["id"],
                    "Name": p["name"],
                    "Age": p["age"],
                    "Gender": p["gender"],
                    "Created": p["created_at"]
                } for p in patients_list
            ])
            
            st.dataframe(df)
            st.caption(f"Total Patients: {len(patients_list)}")
        else:
            st.info("No patients found in the database.")

# Tab 3: Update Patient
with tab3:
    st.header("Update Patient Record")
    
    # First get the patient ID
    update_patient_id = st.text_input("Enter Patient ID to update", key="update_id")
    search_update_button = st.button("Search for Update")
    
    if search_update_button and update_patient_id:
        patient_data = get_patient(update_patient_id)
        if patient_data:
            st.success(f"Found patient: {patient_data.get('name')}")
            
            # Create form with existing data
            with st.form("update_patient_form"):
                name = st.text_input("Full Name", value=patient_data.get('name', ''), key="update_name")
                age = st.number_input("Age", min_value=0, max_value=120, value=patient_data.get('age', 0), key="update_age")
                gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                     index=["Male", "Female", "Other"].index(patient_data.get('gender', 'Male')), 
                                     key="update_gender")
                
                # Contact information
                st.subheader("Contact Information")
                contact = patient_data.get('contact', {})
                phone = st.text_input("Phone Number", value=contact.get('phone', ''), key="update_phone")
                email = st.text_input("Email", value=contact.get('email', ''), key="update_email")
                address = st.text_area("Address", value=contact.get('address', ''), key="update_address")
                
                # Medical details
                st.subheader("Medical Information")
                medical = patient_data.get('medical', {})
                blood_options = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
                blood_index = blood_options.index(medical.get('blood_type')) if medical.get('blood_type') in blood_options else 0
                blood_type = st.selectbox("Blood Type", blood_options, index=blood_index, key="update_blood")
                allergies = st.text_area("Allergies", value=medical.get('allergies', ''), key="update_allergies")
                medical_conditions = st.text_area("Existing Medical Conditions", value=medical.get('conditions', ''), key="update_conditions")
                
                # Insurance details
                st.subheader("Insurance Details")
                insurance = patient_data.get('insurance', {})
                insurance_provider = st.text_input("Insurance Provider", value=insurance.get('provider', ''), key="update_provider")
                insurance_id = st.text_input("Insurance ID", value=insurance.get('id', ''), key="update_insurance_id")
                
                update_submit_button = st.form_submit_button("Update Patient")
                
                if update_submit_button:
                    # Create updated patient data dictionary
                    updated_data = {
                        "name": name,
                        "age": age,
                        "gender": gender,
                        "contact": {
                            "phone": phone,
                            "email": email,
                            "address": address
                        },
                        "medical": {
                            "blood_type": blood_type,
                            "allergies": allergies,
                            "conditions": medical_conditions
                        },
                        "insurance": {
                            "provider": insurance_provider,
                            "id": insurance_id
                        }
                    }
                    
                    success, message = update_patient(update_patient_id, updated_data)
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
        else:
            st.error("Patient not found!")

# Tab 4: Delete Patient
with tab4:
    st.header("Delete Patient Record")
    
    delete_patient_id = st.text_input("Enter Patient ID to delete", key="delete_id")
    
    if delete_patient_id:
        # Try to fetch the patient first to show details
        patient_data = get_patient(delete_patient_id)
        if patient_data:
            st.warning(f"You are about to delete the record for: **{patient_data.get('name')}**")
            
            # Add a confirmation check before deleting
            confirm_delete = st.checkbox("I confirm I want to delete this patient record", key="confirm_delete")
            
            delete_button = st.button("Delete Patient")
            
            if delete_button:
                if not confirm_delete:
                    st.warning("Please confirm deletion by checking the confirmation box")
                else:
                    success, message = delete_patient(delete_patient_id)
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
        else:
            if st.button("Search"):
                st.error("Patient not found!")

# Add a footer
st.markdown("---")
st.markdown("© 2025 Health Record System - SQLite Edition")

# Display database stats
if st.sidebar.checkbox("Show Database Stats"):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM patients")
    count = cursor.fetchone()[0]
    conn.close()
    
    st.sidebar.metric("Total Patients", count)
    
    if os.path.exists(DB_FILE):
        file_size = round(os.path.getsize(DB_FILE) / 1024, 2)
        st.sidebar.metric("Database Size", f"{file_size} KB")
    
    st.sidebar.caption(f"Database: {DB_FILE}")
