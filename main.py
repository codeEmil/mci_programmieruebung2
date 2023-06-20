import json
import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt

def load_person_data():
    file = open("data/person_db.json")
    person_data = json.load(file)
    return person_data


def get_person_list(person_data):
    list_of_names = []
    for entry in person_data:
        list_of_names.append(entry["lastname"] + ", " + entry["firstname"])
    return list_of_names


def find_person_data_by_name(suchstring):
    person_data = load_person_data()
    if suchstring == "None":
        return {}
    two_names = suchstring.split(", ")
    vorname = two_names[1]
    nachname = two_names[0]
    for entry in person_data:
        if entry["lastname"] == nachname and entry["firstname"] == vorname:
            return entry
    else:
        return {}
    

def login():
    file = open("data/users.json")
    user_data = json.load(file)

    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if not st.button("Login"):
        return

    if user_data[username]:
        if user_data[username] == password:
            st.session_state.logged_in = True
        else:
            st.error("Invalid password (" + user_data[username] + ")")
    else:
        st.error("Invalid username")


def main():
    global person_names

    st.title("ECG Analysis")
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        login()
        return

    st.subheader("Select Patient")
    person_names = get_person_list(load_person_data())
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None

    current_user = st.selectbox('ECG Data', options=['Please select Patient'] + person_names, key="sbVersuchsperson")
    if current_user == 'Please select Patient':
        return

    st.write("The current patient is:", current_user)
    patient_data = find_person_data_by_name(current_user)
    if not patient_data:
        st.error("No data available for the selected patient.")
        return

    picture_path = patient_data["picture_path"]
    image = Image.open(picture_path)
    st.image(image, caption=current_user)

    st.subheader("Patient Information")
    st.write(f"ID: {patient_data['id']}")
    st.write(f"Date of Birth: {patient_data['date_of_birth']}")
    st.write(f"Firstname: {patient_data['firstname']}")
    st.write(f"Lastname: {patient_data['lastname']}")

    st.subheader("Select Test")
    tests = patient_data["ekg_tests"]
    selected_test = st.selectbox('Select Test', options=[f'Date: {test["date"]}, ID: {test["id"]}' for test in tests])
    if not selected_test:
        return

    selected_test_id = int(selected_test.split(", ID: ")[1])
    test_info = None
    for test in tests:
        if test["id"] == selected_test_id:
            test_info = test
            break
    if not test_info:
        return

    st.write("Selected test:")
    test_info_str = json.dumps(test_info, indent=4)
    test_info_str = test_info_str.replace('"', '').replace('{', '').replace('}', '')
    st.text_area("Test Informations", value=test_info_str, height=150)

    st.subheader("ECG Data")
    result_link = f"{test_info['result_link']}"
    df = pd.read_csv(result_link, delimiter="\t", header=None)
    df.columns = ["Time [ms]", "Voltage [mV]"]
    plt.plot(df["Voltage [mV]"], df["Time [ms]"])
    plt.xlabel("Time [ms]")
    plt.ylabel("Voltage [mV]")
    plt.title("ECG Data")
    plt.xlim(15000, 20000)  # Set X-axis limit to 0-1000 ms
    st.pyplot(plt)
    


if __name__ == '__main__':
    main()
