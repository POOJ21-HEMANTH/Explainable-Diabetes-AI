# auth.py

doctors = {
    "dr_rahul": "rahul123",
    "dr_priya": "priya123",
    "dr_arjun": "arjun123",
    "dr_neha": "neha123"
}

def authenticate(username, password):
    if username in doctors and doctors[username] == password:
        return True
    return False
