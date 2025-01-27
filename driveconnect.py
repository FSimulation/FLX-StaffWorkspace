import mysql.connector
import streamlit as st
import subfiles.dashboard as dashboard  
import subfiles.staff_workspace as staff_w


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
    st.image("assets/DriveConnect.png", use_container_width=True)
    st.title("Login")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):
        conn = get_connection()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT is_staff FROM users WHERE username = %s AND password = %s",
                (username, password)
            )
            access = cursor.fetchone()

            if access:
                st.session_state.is_staff = access[0] == 1
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
                load_page()
            else:
                st.error("Invalid username or password.")
        except mysql.connector.Error as e:
            st.error(f"An error occurred: {e}")
        finally:
            conn.close()


def load_page():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.page = "login" 

    if st.session_state.logged_in:

        menu_options = ["Dashboard", "Settings"]
        if st.session_state.is_staff:
            menu_options.append("Staff Workspace")
        selected_page = st.selectbox("select", menu_options, label_visibility="hidden")
        
        if selected_page == "Dashboard":
            dashboard.show()
        elif selected_page == "Staff Workspace":
            staff_w.show_form()

            
    else:
        login_window()


if __name__ == "__main__":
    load_page()