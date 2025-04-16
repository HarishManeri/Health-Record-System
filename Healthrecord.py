import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

# Set page configuration
st.set_page_config(
    page_title="Health Record System",
    page_icon="🏥",
    layout="wide"
)

# Initialize Firebase
@st.cache_resource
def initialize_firebase():
    """Initialize Firebase if not already initialized"""
    if not firebase_admin._apps:
        # Check if running locally or deployed (adjust file path accordingly)
        try:
            cred = credentials.Certificate("healthrecordsystem-eb0df-firebase-adminsdk-fbsvc-2c9dae1f26.json")
            firebase_admin.initialize_app(cred)
        except:
            # For demo purposes, allow running without credentials
            st.warning("⚠️ Firebase credentials not found. Running in demo mode.")
            # Create a dummy app for demo purposes
            cred = None
            firebase_admin.initialize_app(cred, {'projectId': 'demo-project'})
    return firestore.client()

# Get Firestore client
db = initialize_firebase()

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
                
                try:
                    # Add patient to Firestore
                    db.collection("patients").document(patient_id).set(patient_data)
                    st.success(f"✅ Patient {name} added successfully!")
                except Exception as e:
                    st.error(f"Error adding patient: {e}")

# Tab 2: View Patient
with tab2:
    st.header("View Patient Records")
    
    # Create a search box for patient ID
    search_patient_id = st.text_input("Enter Patient ID to search", key="search_id")
    search_button = st.button("Search")
    
    if search_button and search_patient_id:
        try:
            # Get patient from Firestore
            doc = db.collection("patients").document(search_patient_id).get()
            if doc.exists:
                patient_data = doc.to_dict()
                
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
                
                # Show JSON data option
                if st.checkbox("Show Raw Data"):
                    st.json(patient_data)
            else:
                st.error("Patient not found!")
        except Exception as e:
            st.error(f"Error retrieving patient data: {e}")
    
    # Option to view all patients
    if st.button("View All Patients"):
        try:
            # Get all patients from Firestore
            patients_ref = db.collection("patients").stream()
            patients_list = []
            
            for doc in patients_ref:
                patient = doc.to_dict()
                patients_list.append({
                    "ID": patient.get("id"),
                    "Name": patient.get("name"),
                    "Age": patient.get("age"),
                    "Gender": patient.get("gender")
                })
            
            if patients_list:
                st.dataframe(pd.DataFrame(patients_list))
            else:
                st.info("No patients found in the database.")
        except Exception as e:
            st.error(f"Error retrieving patients: {e}")

# Tab 3: Update Patient
with tab3:
    st.header("Update Patient Record")
    
    # First get the patient ID
    update_patient_id = st.text_input("Enter Patient ID to update", key="update_id")
    search_update_button = st.button("Search for Update")
    
    if search_update_button and update_patient_id:
        try:
            # Get patient from Firestore
            doc = db.collection("patients").document(update_patient_id).get()
            if doc.exists:
                patient_data = doc.to_dict()
                st.success(f"Found patient: {patient_data.get('name')}")
                
                # Create form with existing data
                with st.form("update_patient_form"):
                    name = st.text_input("Full Name", value=patient_data.get('name', ''), key="update_name")
                    age = st.number_input("Age", min_value=0, max_value=120, value=patient_data.get('age', 0), key="update_age")
                    gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(patient_data.get('gender', 'Male')), key="update_gender")
                    
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
                        
                        try:
                            # Update patient in Firestore
                            db.collection("patients").document(update_patient_id).update(updated_data)
                            st.success(f"✅ Patient {name} updated successfully!")
                        except Exception as e:
                            st.error(f"Error updating patient: {e}")
            else:
                st.error("Patient not found!")
        except Exception as e:
            st.error(f"Error retrieving patient data: {e}")

# Tab 4: Delete Patient
with tab4:
    st.header("Delete Patient Record")
    
    delete_patient_id = st.text_input("Enter Patient ID to delete", key="delete_id")
    
    # Add a confirmation check before deleting
    confirm_delete = st.checkbox("I confirm I want to delete this patient record", key="confirm_delete")
    
    delete_button = st.button("Delete Patient")
    
    if delete_button:
        if not delete_patient_id:
            st.error("Please enter a Patient ID")
        elif not confirm_delete:
            st.warning("Please confirm deletion by checking the confirmation box")
        else:
            try:
                # Check if patient exists
                doc = db.collection("patients").document(delete_patient_id).get()
                if doc.exists:
                    patient_name = doc.to_dict().get('name', 'Unknown')
                    
                    # Delete patient from Firestore
                    db.collection("patients").document(delete_patient_id).delete()
                    st.success(f"✅ Patient {patient_name} (ID: {delete_patient_id}) deleted successfully!")
                else:
                    st.error("Patient not found!")
            except Exception as e:
                st.error(f"Error deleting patient: {e}")

# Add a footer
st.markdown("---")
st.markdown("© 2025 Health Record System - Streamlit Edition")
