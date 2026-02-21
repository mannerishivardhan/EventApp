import streamlit as st
import requests

# -------------------------
# 🔗 GOOGLE APPS SCRIPT WEBHOOK URL
# -------------------------

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyspPUcruKHALsS6BAbenm3rNnJShnxV9LWkuRGhMCCPgqRcVVJ_bTOhAEWOg_hMa8/exec"

def send_to_google_sheet(data):
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        return response.text
    except Exception as e:
        return str(e)

# -------------------------
# 🖥 STREAMLIT UI
# -------------------------

st.title("VTTP ANDHRA PRADESH")

# -------------------------
# PARTICIPANT DETAILS
# -------------------------

st.subheader("Participant Details")

name = st.text_input("Name")

aadhar = st.text_input("Aadhar Number (12 digits only)", max_chars=12)
phone = st.text_input("Phone Number (10 digits only)", max_chars=10)

# Allow only digits
aadhar = ''.join(filter(str.isdigit, aadhar))
phone = ''.join(filter(str.isdigit, phone))

aadhar_valid = len(aadhar) == 12
phone_valid = len(phone) == 10

# -------------------------
# TRAVEL DETAILS
# -------------------------

st.subheader("Travel Details")

num_entries = st.number_input(
    "Number of Travel Entries",
    min_value=0,
    max_value=10,
    value=1
)

travel_rows = []
total_fare = 0
reason_no_travel = ""

if num_entries > 0:
    for i in range(num_entries):
        st.markdown(f"### Travel Entry {i+1}")
        from_loc = st.text_input("From Location", key=f"from_{i}")
        to_loc = st.text_input("To Location", key=f"to_{i}")
        fare = st.number_input("Sub Fare", min_value=0.0, key=f"fare_{i}")

        total_fare += fare

        travel_rows.append({
            "From": from_loc,
            "To": to_loc,
            "Sub Fare": fare
        })
else:
    reason_no_travel = st.text_input("Reason for No Travel (Mandatory)")

# -------------------------
# DOCUMENT SECTION
# -------------------------

st.subheader("Document Verification")

form_submitted = st.selectbox("Application Form Submitted?", ["Yes", "No"])

form_mode = ""
if form_submitted == "Yes":
    form_mode = st.selectbox(
        "Submitted Through",
        ["Post", "Hard Copy", "WhatsApp"]
    )

if num_entries == 0:
    ticket_submitted = "No"
    st.selectbox("Ticket Submitted?", ["No"], disabled=True)
else:
    ticket_submitted = st.selectbox("Ticket Submitted?", ["Yes", "No"])

# -------------------------
# REMARKS
# -------------------------

remarks = []

if form_submitted == "No":
    remarks.append("Form Missing")

if ticket_submitted == "No":
    remarks.append("Ticket Missing")

if num_entries == 0:
    remarks.append("No Travel")

remarks_text = ", ".join(remarks) if remarks else "OK"

st.write("### Total Fare:", total_fare)

# -------------------------
# SAVE BUTTON
# -------------------------

if st.button("Save"):

    # Validation
    if name == "":
        st.error("Name is required.")
        st.stop()

    if not aadhar_valid:
        st.error("Aadhar must be exactly 12 digits.")
        st.stop()

    if not phone_valid:
        st.error("Phone number must be exactly 10 digits.")
        st.stop()

    if num_entries == 0 and reason_no_travel == "":
        st.error("Reason for no travel is required.")
        st.stop()

    phone_with_code = "+91" + phone

    # -------------------------
    # SEND DATA TO GOOGLE SHEET
    # -------------------------

    if num_entries > 0:

        for i, row in enumerate(travel_rows):

            payload = {
                "name": name if i == 0 else "",
                "from_location": row["From"],
                "to_location": row["To"],
                "sub_fare": row["Sub Fare"],
                "total_fare": total_fare if i == 0 else "",
                "aadhar": aadhar if i == 0 else "",
                "phone": phone_with_code if i == 0 else "",
                "form_submitted": form_submitted if i == 0 else "",
                "form_mode": form_mode if i == 0 else "",
                "ticket_submitted": ticket_submitted if i == 0 else "",
                "reason": "",
                "remarks": remarks_text if i == 0 else ""
            }

            send_to_google_sheet(payload)

        # Add blank row after participant
        send_to_google_sheet({
            "name": "",
            "from_location": "",
            "to_location": "",
            "sub_fare": "",
            "total_fare": "",
            "aadhar": "",
            "phone": "",
            "form_submitted": "",
            "form_mode": "",
            "ticket_submitted": "",
            "reason": "",
            "remarks": ""
        })

    else:

        payload = {
            "name": name,
            "from_location": "",
            "to_location": "",
            "sub_fare": 0,
            "total_fare": 0,
            "aadhar": aadhar,
            "phone": phone_with_code,
            "form_submitted": form_submitted,
            "form_mode": form_mode,
            "ticket_submitted": ticket_submitted,
            "reason": reason_no_travel,
            "remarks": remarks_text
        }

        send_to_google_sheet(payload)

        # Blank row spacing
        send_to_google_sheet({
            "name": "",
            "from_location": "",
            "to_location": "",
            "sub_fare": "",
            "total_fare": "",
            "aadhar": "",
            "phone": "",
            "form_submitted": "",
            "form_mode": "",
            "ticket_submitted": "",
            "reason": "",
            "remarks": ""
        })

    st.success("✅ Participant Saved Successfully!")