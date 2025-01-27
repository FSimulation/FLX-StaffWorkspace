import random, requests, mysql.connector
import streamlit as st
import driveconnect as dc



def show_form():
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

        conn = dc.get_connection()
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