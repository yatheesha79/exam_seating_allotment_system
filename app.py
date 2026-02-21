import streamlit as st
import pandas as pd
import random
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import base64
# Function to set background image
def add_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        encoded_string = base64.b64encode(f.read())
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{encoded_string.decode()});
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
# ------------------ College Info ------------------
COLLEGE_NAME = "GAYATRI VIDYA PARISHAD COLLEGE OF ENGINEERING"
BRANCHES = [
    "Chemical Engineering",
    "Civil Engineering",
    "Computer Science and Engineering",
    "CSE (AI & ML)",
    "CSE (Data Science)",
    "CSE (Cyber Security)",
    "Electronics and Communications Engineering",
    "Electrical and Electronics Engineering",
    "Information Technology",
    "Mechanical Engineering",
    "Mechanical Engineering (Robotics)"
]
# ------------------ Page Config ------------------
st.set_page_config(
    page_title="Exam Seating Portal - GVPCOE",
    page_icon="🏫",
    layout="wide",
)
#add_bg_from_local("logo.jpg")
# ------------------ Header ------------------
st.markdown(f"""
    <h1 style='text-align:center; color:#154360;'>
         {COLLEGE_NAME}
    </h1>
    <h2 style='text-align:center; color:#2E86C1;'>
        Automatic Exam Seating Allotment System
    </h2>
    <p style='text-align:center; font-size:18px;'>
        AI-Based Smart Seating + Student Seat Lookup + PDF Report
    </p>
    <hr>
""", unsafe_allow_html=True)
# ------------------ Tabs ------------------
tab1, tab2, tab3 = st.tabs([
    "🎓 Student Seat Lookup",
    "🧑‍🏫 Admin Dashboard",
    "📄 Download Seating PDF"
])
# ==========================================================
# 🎓 STUDENT PORTAL
# ==========================================================
with tab1:
    st.subheader("🔍 Student Seating Information")
    roll = st.text_input("Enter Your Roll Number", placeholder="Enter the roll no")
    if st.button("Get My Seating Details"):
        try:
            seating_df = pd.read_csv("final_seating.csv")
            student = seating_df[seating_df["RollNo"].astype(str) == roll]
            if not student.empty:
                row = student.iloc[0]
                st.success("✅ Seating Found!")
                st.markdown(f"""
                <div style="
                    background-color:#F8F9F9;
                    padding:25px;
                    border-radius:15px;
                    border-left:8px solid #2E86C1;
                    width:70%;
                    font-size:18px;
                ">
                <h3>📌 Exam Seating Details</h3>
                <p><b>Roll No:</b> {row['RollNo']}</p>
                <p><b>Name:</b> {row['Name']}</p>
                <p><b>Branch:</b> {row['Branch']}</p>
                <p><b>Block:</b> {row['Block']}</p>
                <p><b>Room:</b> {row['Room']}</p>
                <p><b>Bench:</b> {row['Bench']}</p>
                <p><b>Seat Position:</b> {row['Position']}</p>
                </div>
                """, unsafe_allow_html=True)

            else:
                st.error("❌ Roll Number Not Found")

        except:
            st.warning("⚠ Seating not generated yet. Please wait for admin.")
# ==========================================================
# 🧑‍🏫 ADMIN DASHBOARD
# ==========================================================
with tab2:
    st.subheader("🧑‍🏫 Admin Seating Generator")

    st.info("Upload student list and generate seating dynamically for selected blocks.")
    student_file = st.file_uploader("📌 Upload Student CSV File", type=["csv"])
    if student_file:
        students = pd.read_csv(student_file)
        st.success("✅ Student List Uploaded Successfully!")
        st.write("Preview:")
        st.dataframe(students.head())
        # ------------------ Block Selection ------------------
        st.subheader("🏢 Block & Room Configuration")
        total_blocks = 12
        selected_blocks = st.multiselect(
            "Select Blocks for Seating Allocation",
            [f"Block-{i}" for i in range(1, total_blocks + 1)],
            default=["Block-1", "Block-2", "Block-3"]
        )
        benches_per_room = st.number_input("Benches per Room", min_value=10, value=20)
        rooms_per_block = st.number_input("Rooms per Block", min_value=1, value=3)
        # Each bench has 2 seats
        seats_per_room = benches_per_room * 2
        if st.button("⚡ Generate AI Smart Seating Plan"):
            seating = []
            # ---- AI LOGIC: Branch Mixing ----
            branch_groups = students.groupby("Branch")
            mixed_students = []
            # Round-robin distribution
            branch_lists = [group.to_dict("records") for _, group in branch_groups]
            while any(branch_lists):
                for blist in branch_lists:
                    if blist:
                        mixed_students.append(blist.pop(0))
            # Seating Assignment
            block_index = 0
            room_no = 1
            bench_no = 1
            position = ["Left", "Right"]
            pos_index = 0
            for s in mixed_students:
                block_name = selected_blocks[block_index]
                seating.append({
                    "RollNo": s["RollNo"],
                    "Name": s["Name"],
                    "Branch": s["Branch"],
                    "Block": block_name,
                    "Room": f"Room-{room_no}",
                    "Bench": bench_no,
                    "Position": position[pos_index]
                })
                # Move seat
                pos_index += 1
                if pos_index == 2:
                    pos_index = 0
                    bench_no += 1
                if bench_no > benches_per_room:
                    bench_no = 1
                    room_no += 1
                if room_no > rooms_per_block:
                    room_no = 1
                    block_index = (block_index + 1) % len(selected_blocks)
            seating_df = pd.DataFrame(seating)
            seating_df.to_csv("final_seating.csv", index=False)
            st.success("✅ Seating Plan Generated Successfully!")
            st.dataframe(seating_df)
# ==========================================================
# 📄 PDF REPORT
# ==========================================================
with tab3:
    st.subheader("📄 Seating Plan PDF Download")
    def generate_pdf(data):
        pdf_file = "GVPCOE_Exam_Seating_Report.pdf"
        c = canvas.Canvas(pdf_file, pagesize=A4)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(120, 820, f"{COLLEGE_NAME}")
        c.drawString(180, 800, "Exam Seating Plan Report")
        c.setFont("Helvetica", 10)
        y = 770
        for i, row in data.iterrows():
            line = f"{row['RollNo']} | {row['Name']} | {row['Branch']} | {row['Block']} | {row['Room']} | Bench {row['Bench']} ({row['Position']})"
            c.drawString(30, y, line)
            y -= 18
            if y < 50:
                c.showPage()
                y = 800
        c.save()
        return pdf_file
    try:
        seating_df = pd.read_csv("final_seating.csv")
        if st.button("📄 Generate Seating PDF"):
            pdf_path = generate_pdf(seating_df)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "⬇ Download PDF Report",
                    f,
                    file_name="GVPCOE_Exam_Seating_Report.pdf"
                )
    except:
        st.warning("⚠ Admin must generate seating first.")
