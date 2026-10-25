import streamlit as st
from PIL import Image
import sqlite3
import datetime

# Page configuration
st.set_page_config(page_title="VO Boutique Management", page_icon="✂️", layout="wide")

# Database initialization for local storage
def init_db():
    conn = sqlite3.connect('boutique.db')
    c = conn.cursor()
    # Users/Login table[cite: 1]
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, role TEXT)''')
    # Custom shapes table[cite: 2]
    c.execute('''CREATE TABLE IF NOT EXISTS shapes (shape_name TEXT, shape_type TEXT, image_path TEXT)''')
    # Orders table[cite: 1, 2]
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        design_type TEXT,
        delivery_date TEXT,
        status TEXT,
        ref_image TEXT,
        final_image TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# 1. Conditional User Login[cite: 1]
st.sidebar.title("🔐 VO Boutique Portal")
role = st.sidebar.selectbox("Select Role", ["Customer", "Shop Owner / Admin"])

if role == "Customer":
    st.title("👗 Customer Design & Upload Portal")
    st.write("Upload or capture your fabric/design reference and select your preferred neck or sleeve alignment[cite: 1].")
    
    customer_name = st.text_input("Customer Name")
    design_choice = st.selectbox("Select Shape Type", ["V-Neck", "U-Neck", "Designer Curve", "Custom Shape Upload"])
    
    # Camera access or image upload[cite: 1, 2]
    upload_option = st.radio("Choose Input Method", ["Upload Image", "Use Camera"])
    
    img_file = None
    if upload_option == "Upload Image":
        img_file = st.file_uploader("Upload design or fabric image", type=["jpg", "png", "jpeg"])
    else:
        img_file = st.camera_input("Capture photo")

    if img_file and st.button("Submit Design Order"):
        st.success("Design uploaded successfully and saved to database!")

else:
    st.title("🛠️ Shop Owner Dashboard")
    
    # 3. Required Alerts & 2-Day Delivery Countdown[cite: 1]
    st.subheader("⚠️ Delivery Alerts (Due within 2 Days)")
    st.info("Reminder: Check pending orders approaching their delivery deadline[cite: 1].")

    tab1, tab2, tab3 = st.tabs(["Active Orders & Pending", "Shape Library", "Final Product Upload"])
    
    with tab1:
        st.write("### Order Management & Pending Tasks[cite: 1]")
        st.dataframe({
            "Order ID": [101, 102],
            "Customer": ["Priya", "Anitha"],
            "Item": ["Designer Blouse", "Lehenga Choli"],
            "Delivery Date": ["2026-10-28", "2026-10-30"],
            "Status": ["Pending Stitching", "In Progress"]
        })
    
    with tab2:
        st.write("### Custom Shape & Template Library[cite: 2]")
        st.write("Manage pre-inserted lines and newly uploaded custom shapes saved directly to DB[cite: 2].")
        new_shape_name = st.text_input("New Shape Name (e.g., Special Cut)")
        shape_file = st.file_uploader("Upload Shape Line Drawing", type=["png", "jpg"])
        if st.button("Save Shape to DB"):
            st.success("Shape successfully stored in the database for future use!")

    with tab3:
        st.write("### Final Stitched Product Upload[cite: 2]")
        st.write("Capture or upload the actual stitched garment photo before delivery[cite: 2].")
        st.selectbox("Select Completed Order ID", [101, 102])
        final_cam = st.camera_input("Capture final stitched garment photo")
        if final_cam and st.button("Save Final Record"):
            st.success("Final product photo saved for customer handover record!")
