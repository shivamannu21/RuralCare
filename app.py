import sqlite3
from datetime import date

from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

app.secret_key ="RuralCare-secret-key-2026"

DATABASE = "ruralcare.db"


# ==============================
# DATABASE
# ==============================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT,
            village TEXT,
            symptoms TEXT,
            token_number INTEGER NOT NULL,
            visit_date TEXT NOT NULL,
            status TEXT DEFAULT 'Waiting'
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ==============================
# HOME
# ==============================

@app.route("/")
def home():
    return render_template("index.html")


# ==============================
# HOSPITALS
# ==============================

@app.route("/hospitals")
def hospitals():
    return render_template("hospitals.html")


# ==============================
# PATIENT REGISTRATION
# ==============================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        phone = request.form.get("phone", "").strip()
        village = request.form.get("village", "").strip()
        symptoms = request.form.get("symptoms", "").strip()

        # Basic validation
        if not name or not age or not gender:
            return render_template(
                "register.html",
                error="Please fill all required details."
            )

        try:
            age = int(age)
        except ValueError:
            return render_template(
                "register.html",
                error="Age must be a number."
            )

        today = date.today().isoformat()

        conn = get_db()

        # ==============================
        # GENERATE TODAY'S TOKEN
        # ==============================

        row = conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM patients
            WHERE visit_date = ?
            """,
            (today,)
        ).fetchone()

        token = row["total"] + 1

        # ==============================
        # GENERATE PATIENT ID
        # ==============================

        row = conn.execute(
            "SELECT COUNT(*) AS total FROM patients"
        ).fetchone()

        patient_id = f"RC-P-{row['total'] + 1:04d}"

        # ==============================
        # SAVE PATIENT
        # ==============================

        conn.execute(
            """
            INSERT INTO patients
            (
                patient_id,
                name,
                age,
                gender,
                phone,
                village,
                symptoms,
                token_number,
                visit_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                patient_id,
                name,
                age,
                gender,
                phone,
                village,
                symptoms,
                token,
                today
            )
        )

        conn.commit()
        conn.close()

        # ==============================
        # SHOW TOKEN PAGE
        # ==============================

        return render_template(
            "token.html",
            patient_id=patient_id,
            name=name,
            age=age,
            gender=gender,
            phone=phone,
            village=village,
            symptoms=symptoms,
            token=token,
            visit_date=today
        )

    return render_template("register.html")


# ==============================
# SYMPTOMS
# ==============================

@app.route("/symptoms", methods=["GET", "POST"])
def symptoms():

    result = ""

    if request.method == "POST":

        selected = request.form.getlist("symptoms")

        if not selected:

            result = "Please select at least one symptom."

        elif "shortness_breath" in selected:

            result = (
                "⚠️ Breathing difficulty can sometimes require urgent "
                "medical attention. Please seek medical help immediately, "
                "especially if symptoms are severe or worsening."
            )

        elif (
            ("fever" in selected and "cough" in selected)
            or
            ("fever" in selected and "sore_throat" in selected)
        ):

            result = (
                "Your symptoms may be related to a respiratory infection. "
                "Rest, drink fluids, and consult a healthcare professional "
                "if symptoms are severe, persistent, or worsening."
            )

        elif (
            ("fever" in selected and "body_pain" in selected)
            or
            ("fever" in selected and "chills" in selected)
        ):

            result = (
                "Fever with body pain or chills may occur with an infection. "
                "Rest, stay hydrated, and consult a healthcare professional "
                "for proper evaluation."
            )

        elif (
            ("stomach_pain" in selected and "nausea" in selected)
            or
            ("stomach_pain" in selected and "vomiting" in selected)
        ):

            result = (
                "Stomach pain with nausea or vomiting may need medical "
                "evaluation. Drink fluids if you can and seek professional "
                "care if symptoms are severe, persistent, or worsening."
            )

        elif "headache" in selected and "dizziness" in selected:

            result = (
                "Headache with dizziness can have different causes. "
                "Rest in a safe place, stay hydrated, and consult a "
                "healthcare professional if symptoms are severe or persistent."
            )

        elif "eye_pain" in selected:

            result = (
                "Eye pain should be evaluated by a healthcare professional, "
                "especially if there is vision change, injury, redness, "
                "or severe pain."
            )

        elif "tooth_pain" in selected:

            result = (
                "Tooth pain may be related to dental problems. "
                "Please arrange a visit with a qualified dentist, "
                "especially if there is swelling, fever, or severe pain."
            )

        elif "vomiting" in selected:

            result = (
                "Vomiting can lead to dehydration. Take small sips of fluids "
                "if tolerated and seek medical care if vomiting is severe, "
                "persistent, or accompanied by severe pain or weakness."
            )

        elif "nausea" in selected:

            result = (
                "Nausea can have many causes. Rest, stay hydrated, "
                "and consult a healthcare professional if it persists."
            )

        elif "fatigue" in selected:

            result = (
                "Fatigue or weakness can have many causes. Ensure adequate "
                "rest, food, and fluids, and consult a healthcare professional "
                "if it is severe or persistent."
            )

        elif "sore_throat" in selected:

            result = (
                "A sore throat may occur with an infection or irritation. "
                "Stay hydrated and seek medical advice if symptoms become "
                "severe or do not improve."
            )

        elif "runny_nose" in selected:

            result = (
                "A runny nose may occur with allergies or an infection. "
                "Monitor your symptoms and consult a healthcare professional "
                "if they become severe or persistent."
            )

        elif "chills" in selected:

            result = (
                "Chills can occur with infections or other conditions. "
                "Keep warm, stay hydrated, and seek medical advice if "
                "symptoms are severe or persistent."
            )

        elif "dizziness" in selected:

            result = (
                "Dizziness can have many causes. Sit or lie down safely, "
                "avoid driving if you feel unwell, and seek medical advice "
                "if dizziness is severe, sudden, or persistent."
            )

        elif "fever" in selected:

            result = (
                "Fever may occur with an infection. Rest, drink fluids, "
                "and consult a healthcare professional if the fever is "
                "high, persistent, or accompanied by concerning symptoms."
            )

        elif "cough" in selected:

            result = (
                "A cough can have different causes, including respiratory "
                "infections or irritation. Stay hydrated and consult a "
                "healthcare professional if it persists or worsens."
            )

        elif "headache" in selected:

            result = (
                "Headaches can have many causes. Rest and stay hydrated. "
                "Seek medical care if the headache is sudden, severe, "
                "or accompanied by other concerning symptoms."
            )

        elif "stomach_pain" in selected:

            result = (
                "Stomach pain can have many causes. Monitor your symptoms "
                "and seek medical care if the pain is severe, persistent, "
                "or worsening."
            )

        elif "body_pain" in selected:

            result = (
                "Body pain can occur due to strain, infection, or other "
                "conditions. Rest and consult a healthcare professional "
                "if the pain is severe or persistent."
            )

        else:

            result = (
                "Please consult a qualified healthcare professional "
                "for proper evaluation."
            )

        return render_template(
            "result.html",
            result=result
        )

    return render_template("symptoms.html")


# ==============================
# APPOINTMENT
# ==============================


@app.route("/appointment", methods=["GET", "POST"])
def appointment():

    if request.method == "POST":

        # Get all information from the appointment form
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        phone = request.form.get("phone", "").strip()
        hospital = request.form.get("hospital", "").strip()
        department = request.form.get("department", "").strip()
        appointment_date = request.form.get("date", "").strip()
        appointment_time = request.form.get("time", "").strip()

        # Show confirmation page with the submitted details
        return render_template(
            "confirmation.html",
            name=name,
            age=age,
            phone=phone,
            hospital=hospital,
            department=department,
            date=appointment_date,
            time=appointment_time
        )

    # When opening the appointment page normally
    return render_template("appointment.html")
# ==============================
# EMERGENCY
# ==============================

@app.route("/emergency")
def emergency():
    return render_template("emergency.html")


# ==============================
# CONFIRMATION
# ==============================

@app.route("/confirmation")
def confirmation():
    return render_template("confirmation.html")


# ==============================
# RECORDS
# ==============================

@app.route("/records", methods=["GET", "POST"])
def records():

    # Check whether Records have already been unlocked
    if not session.get("records_access"):

        # PIN submitted
        if request.method == "POST":

            pin = request.form.get("pin", "")

            # Correct PIN
            if pin == "2127":

                session["records_access"] = True

                return redirect(url_for("records"))

            # Wrong PIN
            return render_template(
                "records_pin.html",
                error="Incorrect PIN. Please try again."
            )

        # Show PIN screen
        return render_template("records_pin.html")

    # -----------------------------
    # PIN CORRECT - SHOW RECORDS
    # -----------------------------

    conn = get_db()

    patients = conn.execute(
        "SELECT * FROM patients ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "records.html",
        patients=patients
    )
# ============================================================
# REMOVE PATIENT RECORD
# ============================================================

@app.route('/delete_patient/<patient_id>', methods=['POST'])
def delete_patient(patient_id):

    conn = get_db()

    conn.execute(
        'DELETE FROM patients WHERE patient_id = ?',
        (patient_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('records'))

# ==============================
# START APPLICATION
# ==============================

if __name__ == "__main__":
    app.run(debug=True)