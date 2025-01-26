import random
import requests
import mysql.connector
import streamlit as st

login = {
    "host": "mysql-flxvtc.alwaysdata.net",
    "user": "flxvtc",
    "password": "Fire112k#",
    "database": "flxvtc_db"
}




def get_connection():
    try:
        return mysql.connector.connect(
            host=login["host"],
            user=login["user"],
            password=login["password"],
            database=login["database"],
        )
    except mysql.connector.Error as e:
        st.error(f"Unable to connect to the database: {e}")
        return None




def login_window():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        form_window()
    else:
        st.image("logo.png", use_container_width=True)
        st.title("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            conn = get_connection()
            if conn is None:
                return

            try:
                cursor = conn.cursor()
                cursor.execute("SELECT is_staff FROM users WHERE username = %s AND password = %s", (username, password))
                result = cursor.fetchone()

                if result:
                    is_staff = result[0]
                    if is_staff == 1:
                        st.success("Welcome to the staff workspace!")
                        st.session_state.logged_in = True  # Mettre à jour l'état de la session
                    else:
                        st.warning("Access Denied: You are not allowed to login.")
                else:
                    st.error("Invalid username or password.")
            except mysql.connector.Error as e:
                st.error(f"An error occurred: {e}")
            finally:
                conn.close()




def form_window():
    st.title("Logbook Entry")

    labels = [
        "Discord ID", "Date (YYYY-MM-DD)", "From", "To", "Cargo", "Weight",
        "Distance", "Price", "Fuel", "Costs", "Truck", "Trailer", "Game",
        "Weigh Station", "Proof Picture", "Document Link"
    ]

    data = {}
    for label in labels:
        data[label] = st.text_input(label)

    if st.button("Submit"):
        mandatory_fields = [
            "Discord ID", "Date (YYYY-MM-DD)", "From", "To", "Cargo", "Weight",
            "Distance", "Price", "Fuel", "Costs", "Truck", "Trailer", "Game",
            "Weigh Station", "Proof Picture", "Document Link"
        ]
        
        for field in mandatory_fields:
            if not data[field]:
                st.error(f"The field '{field}' is mandatory.")
                return

        conn = get_connection()
        if conn is None:
            return

        try:
            cursor = conn.cursor()

            cursor.execute("SELECT licence, jobs, mileage FROM drivers WHERE id = %s", (data["Discord ID"],))
            result = cursor.fetchone()
            if not result:
                st.error("Driver not found.")
                return

            licence, jobs, mileage = result
            mileage += float(data["Distance"])
            jobs += 1
            for threshold, new_licence in [(5000, "Licence 1"), (10000, "Licence 2"), (15000, "Licence 3")]:
                if mileage >= threshold and licence != new_licence:
                    licence = new_licence
                    message = f"<@{data['Discord ID']}> has reached a new level: {licence} 🎉"
                    requests.post(
                        "https://discord.com/api/webhooks/1328426834953502720/vu_8I3nBKuEO0sSo93cb0r7WyQrR9pXQU0JsxZDWDUELihqifnT7erJFBvoQNmkoOBaS",
                        json={"content": message}
                    )

            cursor.execute("UPDATE drivers SET licence = %s, jobs = %s, mileage = %s WHERE id = %s",
                           (licence, jobs, mileage, data["Discord ID"]))
            conn.commit()

            job_id = random.randint(100000, 999999)
            final_income = float(data["Price"]) - float(data["Costs"])

            query = """
            INSERT INTO logbook (job_id, driver_id, date, departure, arrival, cargo, weight, distance, price, costs, final_income, truck, trailer, fuel, w_station, game, proof, document_link) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                job_id, data["Discord ID"], data["Date (YYYY-MM-DD)"], data["From"], data["To"], 
                data["Cargo"], data["Weight"], data["Distance"], data["Price"], data["Costs"],
                final_income, data["Truck"], data["Trailer"], data["Fuel"], data["Weigh Station"],
                data["Game"], data["Proof Picture"], data["Document Link"]
            ))
            conn.commit()

            cursor.execute("SELECT balance, costs_total FROM company")
            result = cursor.fetchone()
            if result:
                balance, costs_total = result
                balance += final_income
                costs_total += float(data["Costs"])

                cursor.execute("UPDATE company SET balance = %s, costs_total = %s", (balance, costs_total))
                conn.commit()

            embed = {
                "title": "New Delivery",
                "description": f"Your delivery **{job_id}** was recorded by the staff and is now available on your profile.",
                "color": 3323865,
                "fields": [
                    {"name": "Check your logbook", "value": "https://freightlinevtc.vercel.app/account", "inline": False}
                ]
            }
            payload = {"content": f"<@{data['Discord ID']}>", "embeds": [embed]}
            requests.post(
                "https://discord.com/api/webhooks/1328304879571046451/PdM2e30pu1nWn2J4NAQZy0Gm9w5wjjsty8gSvDV5kkg6AK2c-QMqJu4mpQXDGx10NBTc",
                json=payload)

            st.success("Delivery recorded successfully!")
        except mysql.connector.Error as e:
            st.error(f"An error occurred: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    login_window()
