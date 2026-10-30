import streamlit as st
import pyotp
import bcrypt


def verify_login(username, password, otp_code):
    """Verify username, password hash, and authenticator-app code."""

    config = st.secrets.get("auth", {})

    saved_username = config.get("username", "")
    saved_password_hash = config.get("password_hash", "")
    totp_secret = config.get("totp_secret", "")

    if not saved_username or not saved_password_hash or not totp_secret:
        return False, "MFA settings are missing. Configure secrets.toml first."

    if username != saved_username:
        return False, "Incorrect username or password."

    try:
        password_ok = bcrypt.checkpw(
            password.encode("utf-8"),
            saved_password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        password_ok = False

    if not password_ok:
        return False, "Incorrect username or password."

    if not otp_code.isdigit() or len(otp_code) != 6:
        return False, "Enter the 6-digit authenticator code."

    try:
        totp = pyotp.TOTP(totp_secret)
        if not totp.verify(otp_code, valid_window=1):
            return False, "Incorrect or expired authenticator code."
    except (ValueError, TypeError):
        return False, "MFA settings are invalid."

    return True, "Login successful."


def show_login():
    """Display the login form and remember successful login in this session."""

    if st.session_state.get("authenticated", False):
        return True

    st.title("🔐 PhishGuard AI Login")
    st.write("Enter your username, password, and authenticator-app code.")

    with st.form("mfa_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        otp_code = st.text_input(
            "6-digit authenticator code",
            max_chars=6,
        )
        submitted = st.form_submit_button("Log in")

    if submitted:
        success, message = verify_login(username, password, otp_code)

        if success:
            st.session_state["authenticated"] = True
            st.success(message)
            st.rerun()
        else:
            st.error(message)

    return st.session_state.get("authenticated", False)