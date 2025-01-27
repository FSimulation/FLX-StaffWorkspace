import mysql.connector
import streamlit as st
import subfiles.staff_form as staff
import subfiles.home as home

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
        home.dashboard()
    else:
        st.image("assets/DriveConnect.png", use_container_width=True)
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
                        st.session_state.logged_in = True
                        st.success("Please press LOGIN twice.")
                    else:
                        st.warning("Access Denied: You are not allowed to login.")
                else:
                    st.error("Invalid username or password.")
            except mysql.connector.Error as e:
                st.error(f"An error occurred: {e}")
            finally:
                conn.close()






if __name__ == "__main__":
    login_window()
