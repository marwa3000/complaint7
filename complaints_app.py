import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ✅ تحميل بيانات Google Cloud من secrets.toml
google_creds = st.secrets["GOOGLE_CREDENTIALS"]
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(google_creds, scopes=scopes)
client = gspread.authorize(creds)

# ✅ تحميل معرف Google Sheets من secrets.toml
SPREADSHEET_ID = st.secrets["GOOGLE_SHEETS_ID"]
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# ✅ أسماء الأعمدة المطلوبة في Google Sheets
HEADERS = ["Date Submitted", "Complaint ID", "Product Name", "Severity", "Contact Number", "Details", "Submitted By"]

# ✅ التحقق من وجود العناوين في Google Sheets
def ensure_headers():
    existing_data = sheet.get_all_values()
    if not existing_data or existing_data[0] != HEADERS:
        sheet.insert_row(HEADERS, 1)

# ✅ استدعاء الدالة لضمان وجود العناوين
ensure_headers()

# ✅ توليد رقم الشكوى تلقائيًا بصيغة CcMMYYNN
def generate_complaint_id():
    today = datetime.now()
    month = today.strftime("%m")  # MM
    year = today.strftime("%y")   # YY
    prefix = f"Cc{month}{year}"   # Format: CcMMYY

    complaints = sheet.get_all_records()
    serial_numbers = [
        int(row["Complaint ID"][-2:])
        for row in complaints if "Complaint ID" in row and row["Complaint ID"].startswith(prefix)
    ]

    next_serial = max(serial_numbers, default=0) + 1
    return f"{prefix}{next_serial:02d}"

# ✅ عرض العنوان والصورة بجانبه
col1, col2 = st.columns([3, 1])  # تقسيم الصفحة إلى عمودين
with col1:
    st.title("📋 نظام إدارة الشكاوى")
with col2:
    IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/3/30/Vulpes_vulpes_ssp_fulvus.jpg"
    st.image("https://upload.wikimedia.org/wikipedia/commons/3/30/Vulpes_vulpes_ssp_fulvus.jpg", width=300)  # استبدل بالمسار الصحيح للصورة

st.header("📝 إرسال شكوى جديدة")

# ✅ توليد رقم الشكوى تلقائيًا
complaint_id = generate_complaint_id()
st.text_input("رقم الشكوى (تلقائي)", complaint_id, disabled=True)

# ✅ إدخال بيانات الشكوى
product = st.text_input("اسم المنتج")
severity = st.selectbox("مستوى الخطورة", ["High", "Medium", "Low"])
contact_number = st.text_input("📞 رقم التواصل")
details = st.text_area("تفاصيل الشكوى")

# ✅ حقل "اسم كاتب الشكوى" (اختياري)
submitted_by = st.text_input("✍ اسم كاتب الشكوى (اختياري)")

# ✅ حفظ تاريخ الإرسال تلقائيًا
date_submitted = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if st.button("إرسال الشكوى"):
    if product and details and contact_number:
        new_data = [date_submitted, complaint_id, product, severity, contact_number, details, submitted_by or ""]
        sheet.append_row(new_data)
        st.success(f"✅ تم إرسال الشكوى بنجاح برقم {complaint_id} في {date_submitted}!")
    else:
        st.error("❌ يرجى ملء جميع الحقول الإجبارية!")

# ✅ حماية قسم المسؤول بكلمة مرور (إخفاؤه بالكامل إذا لم يتم إدخال كلمة المرور الصحيحة)
CORRECT_PASSWORD = "admin123"

admin_password = st.text_input("", type="password", placeholder="🔒 أدخل كلمة المرور لعرض الشكاوى", help="متاح فقط للمسؤولين")

if admin_password == CORRECT_PASSWORD:
    st.success("✅ تم تسجيل الدخول كمسؤول.")
    if st.button("📄 تحميل الشكاوى"):
        data = sheet.get_all_values()
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            st.write(df)
        else:
            st.warning("⚠ لا يوجد شكاوى حتى الآن.")
elif admin_password:
    st.error("❌ كلمة المرور غير صحيحة!")
