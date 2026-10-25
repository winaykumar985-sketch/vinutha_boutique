import streamlit as st
from PIL import Image
import sqlite3
import datetime
import os

# Page configuration
st.set_page_config(page_title="VO Boutique Management", page_icon="✂️", layout="wide")

# Ensure directories for saving images exist
os.makedirs("faces", exist_ok=True)
os.makedirs("designs", exist_ok=True)

# Database initialization
def init_db():
    conn = sqlite3.connect('boutique.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        name TEXT, phone TEXT UNIQUE, password TEXT, face_image TEXT, role TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        customer_face TEXT,
        shape_image TEXT,
        delivery_date TEXT,
        status TEXT,
        ref_image TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = None

# --- AUTHENTICATION, REGISTRATION & FORGOT PASSWORD ---
if not st.session_state.logged_in:
    st.title("🔐 VO Boutique Portal - Account Access")
    
    auth_mode = st.radio("Choose Action", ["Login", "Register (New User)", "Forgot Password"])
    
    if auth_mode == "Register (New User)":
        st.subheader("📝 New Account Registration with Face Capture & OTP")
        reg_name = st.text_input("Full Name")
        reg_phone = st.text_input("Phone Number")
        reg_pass = st.text_input("Create Password", type="password")
        reg_role = st.selectbox("Select Role", ["Customer", "Shop Owner / Admin"])
        
        st.write("📸 **Capture Your Face Image for Profile / Verification**")
        face_cam = st.camera_input("Take a photo of your face")
        
        otp_input = st.text_input("Enter 4-Digit OTP (Enter '1234' for testing)")
        
        if st.button("Verify OTP & Complete Registration"):
            if not reg_name or not reg_phone or not reg_pass or not face_cam:
                st.warning("Please fill in all fields and capture your face image.")
            elif otp_input != "1234":
                st.error("Invalid OTP. Please enter '1234'.")
            else:
                face_path = f"faces/{reg_phone}.jpg"
                img = Image.open(face_cam)
                img.save(face_path)
                
                conn = sqlite3.connect('boutique.db')
                c = conn.cursor()
                try:
                    c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", 
                              (reg_name, reg_phone, reg_pass, face_path, reg_role))
                    conn.commit()
                    st.success("Registration successful! You can now log in.")
                except sqlite3.IntegrityError:
                    st.error("Phone number already registered!")
                conn.close()
                
    elif auth_mode == "Login":
        st.subheader("🔑 Login to Your Account")
        login_phone = st.text_input("Registered Phone Number")
        login_pass = st.text_input("Password", type="password")
        
        if st.button("Login"):
            conn = sqlite3.connect('boutique.db')
            c = conn.cursor()
            c.execute("SELECT name, role, password FROM users WHERE phone = ?", (login_phone,))
            user = c.fetchone()
            conn.close()
            
            if user and user[2] == login_pass:
                st.session_state.logged_in = True
                st.session_state.username = user[0]
                st.session_state.user_role = user[1]
                st.success(f"Welcome back, {user[0]}!")
                st.rerun()
            else:
                st.error("Invalid phone number or password.")

    else:
        st.subheader("🔄 Reset Your Password")
        fp_phone = st.text_input("Registered Phone Number", key="fp_phone")
        otp_fp = st.text_input("Enter 4-Digit OTP (Enter '1234' for testing)", key="fp_otp")
        new_pass = st.text_input("Enter New Password", type="password", key="fp_new_pass")
        
        if st.button("Reset Password"):
            if not fp_phone or not new_pass:
                st.warning("Please fill in all required fields.")
            elif otp_fp != "1234":
                st.error("Invalid OTP. Please enter '1234'.")
            else:
                conn = sqlite3.connect('boutique.db')
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE phone = ?", (fp_phone,))
                user_exists = c.fetchone()
                
                if user_exists:
                    c.execute("UPDATE users SET password = ? WHERE phone = ?", (new_pass, fp_phone))
                    conn.commit()
                    st.success("Password reset successfully! You can now switch to Login and sign in.")
                else:
                    st.error("This phone number is not registered in the database.")
                conn.close()

else:
    # --- LOGOUT BUTTON IN SIDEBAR ---
    st.sidebar.write(f"👤 Logged in as: **{st.session_state.username}** ({st.session_state.user_role})")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.username = None
        st.rerun()

    # --- ADMIN DASHBOARD ---
    if st.session_state.user_role == "Shop Owner / Admin":
        st.title("🛠️ Shop Owner Dashboard & Orders")
        
        st.subheader("⚠️ 2-Day Delivery Countdown Alerts")
        st.info("Orders due within 2 days require immediate attention and finishing.")

        st.write("### Active Customer Orders")
        
        conn = sqlite3.connect('boutique.db')
        c = conn.cursor()
        c.execute("SELECT order_id, customer_name, customer_face, shape_image, delivery_date, status FROM orders")
        orders = c.fetchall()
        conn.close()
        
        if not orders:
            st.write("No orders placed yet.")
        else:
            for order in orders:
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.write(f"**ID:** {order[0]}")
                    st.write(f"**Name:** {order[1]}")
                with col2:
                    if os.path.exists(order[2]):
                        st.image(order[2], caption="Customer Face", width=100)
                    else:
                        st.write("No face image")
                with col3:
                    if os.path.exists(order[3]):
                        st.image(order[3], caption="Chosen Shape", width=100)
                    else:
                        st.write("Shape preview")
                with col4:
                    st.write(f"**Due Date:** {order[4]}")
                    st.write(f"**Status:** {order[5]}")
                with col5:
                    if st.button(f"Mark Completed {order[0]}", key=f"complete_{order[0]}"):
                        conn = sqlite3.connect('boutique.db')
                        c = conn.cursor()
                        c.execute("UPDATE orders SET status = 'Completed' WHERE order_id = ?", (order[0],))
                        conn.commit()
                        conn.close()
                        st.success(f"Order {order[0]} marked as completed!")
                        st.rerun()
                st.markdown("---")

    # --- CUSTOMER PORTAL ---
    else:
        st.title("👗 Customer Design Selection & Order Portal")
        st.write("Select your desired shape visually, upload your fabric reference, and place your order.")
        
        conn = sqlite3.connect('boutique.db')
        c = conn.cursor()
        c.execute("SELECT face_image FROM users WHERE name = ?", (st.session_state.username,))
        res = c.fetchone()
        conn.close()
        customer_face_path = res[0] if res else ""

        st.subheader("Choose Your Shape (Visual Selection)")
        
        shape_choice = st.radio(
            "Select Neck / Sleeve Shape Style",
            ["V-Neck Style", "U-Neck Style", "Designer Curve Style", "Custom Shape Upload"]
        )
        
        shape_img_path = ""
        if shape_choice == "V-Neck Style":
            st.info("Selected Shape: V-Neck")
            shape_img_path = "designs/v_neck.png"
        elif shape_choice == "U-Neck Style":
            st.info("Selected Shape: U-Neck")
            shape_img_path = "designs/u_neck.png"
        elif shape_choice == "Designer Curve Style":
            st.info("Selected Shape: Designer Curve")
            shape_img_path = "designs/curve.png"
        else:
            custom_shape_file = st.file_uploader("Upload your custom shape drawing/image", type=["png", "jpg", "jpeg"])
            if custom_shape_file:
                shape_img_path = f"designs/custom_{st.session_state.username}.jpg"
                img = Image.open(custom_shape_file)
                img.save(shape_img_path)

        delivery_date = st.date_input("Select Required Delivery Date")
        fabric_img = st.file_uploader("Upload Fabric / Reference Photo", type=["jpg", "png", "jpeg"])
        
        ref_path = ""
        if fabric_img:
            ref_path = f"designs/ref_{st.session_state.username}.jpg"
            Image.open(fabric_img).save(ref_path)

        if st.button("Submit Order"):
            if not shape_img_path:
                st.warning("Please select or upload a shape image.")
            else:
                conn = sqlite3.connect('boutique.db')
                c = conn.cursor()
                c.execute("INSERT INTO orders (customer_name, customer_face, shape_image, delivery_date, status, ref_image) VALUES (?, ?, ?, ?, ?, ?)",
                          (st.session_state.username, customer_face_path, shape_img_path, str(delivery_date), "Pending Stitching", ref_path))
                conn.commit()
                conn.close()
                st.success("Your design order has been submitted successfully to the shop owner!")
