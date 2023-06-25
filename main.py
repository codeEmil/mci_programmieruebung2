import json
import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
from ekgdata import ECGdata
import os


def load_person_data():
    '''loading th patients data'''
    file = open("data/person_db.json")
    person_data = json.load(file)
    return person_data


def get_person_list(person_data):
    '''creating a list with the names'''
    list_of_names = []
    for entry in person_data:
        list_of_names.append(entry["lastname"] + ", " + entry["firstname"])
    return list_of_names


def find_person_data_by_name(searchstring):
    '''select from which patient the data is needed '''
    person_data = load_person_data()
    if searchstring == "None":
        return {}
    whole_name = searchstring.split(", ")
    firstname = whole_name[1]
    lastname = whole_name[0]
    for entry in person_data:
        if entry["lastname"] == lastname and entry["firstname"] == firstname:
            return entry
    else:
        return {}
    

def login():
    '''Log-In with multiple users is possible'''
    file = open("data/users.json")
    user_data = json.load(file)

    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    st.write("For correction: Username = test / PW = test - would not be written if used correctly of course :)")
    if not st.button("Login"):
        return
    if user_data[username]:
        if user_data[username] == password:
            st.session_state.logged_in = True
        else:
            st.error("Invalid password (" + user_data[username] + ")")
    else:
        st.error("Invalid username")


def add_new_patient():
    '''creating a new patient and save the data'''
    st.subheader("Add New Patient")
    firstname = st.text_input("Firstname")
    lastname = st.text_input("Lastname")
    date_of_birth = st.date_input("Date of Birth")
    picture = st.file_uploader("Upload Picture", type=["jpg", "jpeg", "png"])
    ekg_csv = st.file_uploader("Upload EKG Data (csv)")

    if st.button("Save new Patient"):
        person_data = load_person_data()
        new_patient = {
            "id": len(person_data) + 1,
            "firstname": firstname,
            "lastname": lastname,
            "date_of_birth": str(date_of_birth),
            "picture_path": None,
            "ekg_tests": []
        }

        if picture:
            image = Image.open(picture)
            picture_path = f"data/pictures/{firstname}_{lastname}.jpg"
            image.save(picture_path)
            new_patient["picture_path"] = picture_path

        if ekg_csv:
            ekg_data = ekg_csv.read().decode("utf-8")
            ekg_csv_path = f"data/ekg_data/{firstname}_{lastname}.csv"
            with open(ekg_csv_path, "w") as f:
                f.write(ekg_data)
            new_patient["ekg_tests"].append({
                "id": 1,
                "date": str(date_of_birth),
                "result_link": ekg_csv_path
            })

        person_data.append(new_patient)
        with open("data/person_db.json", "w") as file:
            json.dump(person_data, file)
        st.success("New patient was added successfully.")


def delete_patient():
    '''delete a Patient and its data'''
    st.subheader("Delete Patient")
    selected_patient = st.selectbox("Select a Patient to delete:", person_names)
    st.write("Warning: If a Patient gets deleted the whole data of the Patient will be deleted as well!")

    if st.button("Delete the Patient"):
        person_data = load_person_data()
        for i, entry in enumerate(person_data):
            if entry["lastname"] + ", " + entry["firstname"] == selected_patient:
                # Remove patient's picture
                picture_path = entry["picture_path"]
                if picture_path:
                    os.remove(picture_path)
                # Remove patient's EKG data
                ekg_tests = entry["ekg_tests"]
                for test in ekg_tests:
                    result_link = test["result_link"]
                    if result_link:
                        os.remove(result_link)
                # Remove patient entry
                del person_data[i]
                with open("data/person_db.json", "w") as file:
                    json.dump(person_data, file)
                st.success("Patient deleted successfully.")
                break


def add_bg_from_url():
    '''adding a background for better illustration'''
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://cdn.pixabay.com/photo/2017/07/08/09/49/sky-2483934_1280.jpg");
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )
add_bg_from_url()


def main():
    global person_names
    st.title("ECG Analysis")
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        login()
    else:
        st.subheader("Select Patient or Action")
        person_names = get_person_list(load_person_data())

        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        current_user = st.selectbox('ECG Data', options=['Please select Action', 'Add a Patient', 'Delete a Patient'] + person_names, key="sbVersuchsperson")
        st.write("The current path is:", current_user)

        if current_user == 'Add a Patient':
            add_new_patient()
        elif current_user == 'Delete a Patient':
            delete_patient()
        elif current_user != 'Please select Action':
            patient_data = find_person_data_by_name(current_user)
            if patient_data:
                picture_path = patient_data["picture_path"]
                if picture_path:
                    col1, col2 = st.columns(2) #creating a table with the informations of a patient
                    with col1:
                        st.image(patient_data["picture_path"], width=200)
                    with col2:
                        st.subheader("Patient Information")
                        st.write(f"ID: {patient_data['id']}")
                        st.write(f"Date of Birth: {patient_data['date_of_birth']}")
                        st.write(f"Firstname: {patient_data['firstname']}")
                        st.write(f"Lastname: {patient_data['lastname']}")

                st.subheader("Select a Test")
                tests = patient_data["ekg_tests"]
                selected_test = st.selectbox('Select Test', options=[f'Date: {test["date"]}, ID: {test["id"]}' for test in tests])
                if not selected_test:
                    st.error("No selected test!")
                    return

                selected_test_id = int(selected_test.split(", ID: ")[1])
                test_info = None
                for test in tests:
                    if test["id"] == selected_test_id:
                        test_info = test
                        break

                #Choosing a test
                if test_info:
                    st.write("Selected test:")
                    test_info_str = json.dumps(test_info, indent=4)
                    test_info_str = test_info_str.replace('"', '').replace('{', '').replace('}', '')

                    st.text_area("Test Informations", value=test_info_str, height=150)
                    st.subheader("ECG Data")
                    result_link = f"{test_info['result_link']}"
                    my_ecg_data = ECGdata(result_link)

                    #printing the test time in seconds and minutes
                    time = my_ecg_data.df_ekg.iloc[-1]['Time [ms]']
                    st.write("The ECG is", time/1000, "seconds long (", time/1000/60,"minutes)")

                    #All the Plots within a test
                    show_line_plot = st.checkbox("ECG [Time / Voltage]", value=False)
                    if show_line_plot:
                        st.write("Use the Slider to choose a certain timeframe.")
                        st.write("Please be aware that the upper Slider needs to be smaller the the bottom one. Otherwise the axes will be from left to right!")
                        max_value = int(my_ecg_data.df_ekg.iloc[-1]['Time [ms]'])
                        x_min_value = st.slider("Minimum Time Value", min_value=0, max_value=max_value, value=0, step=1)
                        x_max_value = st.slider("Maximum Time Value", min_value=0, max_value=max_value, value=max_value, step=1)
                        plt.figure()
                        plt.grid()
                        my_ecg_data.plot_time_series()
                        plt.xlim(x_min_value, x_max_value)
                        st.pyplot(plt)
                    
                    show_histogram = st.checkbox("Histogram of Peaks", value=False)
                    if show_histogram:
                        plt.figure()
                        my_ecg_data.show_histogram_hr()
                        st.pyplot(plt)
                    
                    show_boxplot = st.checkbox("Boxplot of Distances between Peaks", value=False)
                    if show_boxplot:
                        plt.figure()
                        my_ecg_data.show_boxplot_distances()
                        st.pyplot(plt)
                    
                    show_bpm_plot = st.checkbox("BPM [Time / Heartrate]", value=False)
                    if show_bpm_plot:
                        plt.figure()
                        plt.grid()
                        my_ecg_data.plot_bpm()
                        st.pyplot(plt)

            #Log-Out of the App
            if st.button("Log Out"):
                st.session_state.logged_in = False
                st.session_state.current_user = None


if __name__ == '__main__':
    main()
