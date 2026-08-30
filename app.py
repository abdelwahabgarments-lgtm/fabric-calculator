import datetime
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="حاسبة استهلاك الأقمشة | Abdelwahab Garments",
    page_icon="📐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 2. التنسيق البصري والتصميم (CSS Custom Theme)
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
        background-color: #0d0e11 !important;
        color: #e0e0e0;
    }

    .stApp {
        background-color: #0d0e11;
    }

    /* العناوين الرئيسيّة والفرعيّة */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Cairo', sans-serif !important;
        color: #ffffff !important;
        font-weight: 700;
    }

    /* الهيدر العلوي */
    .brand-header {
        text-align: center;
        padding: 20px 0 30px 0;
        border-bottom: 1px solid #1f232d;
        margin-bottom: 30px;
    }
    .brand-title {
        font-size: 28px;
        font-weight: 800;
        color: #d4af37;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }
    .brand-subtitle {
        font-size: 15px;
        color: #9aa0a6;
    }

    /* الكروت والحاويات */
    .custom-card {
        background-color: #15171e;
        border: 1px solid #242834;
        border-radius: 12px;
        padding: 28px;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }

    /* الأزرار الرئيسية */
    .stButton > button {
        background: linear-gradient(135deg, #d4af37 0%, #aa820a 100%) !important;
        color: #0d0e11 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 12px 24px !important;
        width: 100%;
        transition: all 0.3s ease-in-out !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #e5be48 0%, #c29613 100%) !important;
        box-shadow: 0 0 18px rgba(212, 175, 55, 0.35) !important;
        transform: translateY(-2px);
    }

    /* حقول الإدخال */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #1c1f28 !important;
        color: #ffffff !important;
        border: 1px solid #2e3444 !important;
        border-radius: 8px !important;
    }

    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #d4af37 !important;
        box-shadow: 0 0 6px rgba(212, 175, 55, 0.4) !important;
    }

    /* كروت النتائج والمؤشرات */
    .result-card {
        background-color: #1a1d26;
        border-right: 4px solid #d4af37;
        padding: 18px;
        border-radius: 8px;
        margin-bottom: 14px;
    }
    .result-value {
        font-size: 22px;
        font-weight: 800;
        color: #ffffff;
    }
    .result-label {
        font-size: 13px;
        color: #a0a6b5;
    }

    /* الفوتر السفلية */
    .footer-container {
        background-color: #12141a;
        border-top: 1px solid #222632;
        padding: 35px 25px 20px 25px;
        margin-top: 50px;
        border-radius: 12px 12px 0 0;
    }

    .footer-brand {
        font-size: 20px;
        font-weight: 800;
        color: #d4af37;
        margin-bottom: 12px;
    }

    .footer-text {
        font-size: 14px;
        line-height: 1.8;
        color: #a0a6b5;
        margin-bottom: 24px;
    }

    .social-row {
        display: flex;
        gap: 14px;
        align-items: center;
        margin-top: 15px;
    }

    .social-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 8px;
        background-color: #1c1f28;
        border: 1px solid #2e3444;
        color: #d4af37;
        text-decoration: none;
        transition: all 0.3s ease;
    }

    .social-btn:hover {
        background-color: #d4af37;
        color: #0d0e11;
        border-color: #d4af37;
        transform: translateY(-2px);
    }

    .copyright {
        text-align: center;
        font-size: 13px;
        color: #636a79;
        margin-top: 25px;
        padding-top: 18px;
        border-top: 1px solid #1c1f28;
    }
</style>
""",
    unsafe_allow_html=True,
)


# 3. إعداد الاتصال مع Google Sheets
@st.cache_resource
def get_google_sheet():
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scopes
        )
        client = gspread.authorize(creds)
        return client.open("حاسبة استهلاك الأقمشة - البيانات")
    except Exception:
        return None


# تسجيل الزيارات التلقائي
def log_page_visit():
    if "visited_logged" not in st.session_state:
        spreadsheet = get_google_sheet()
        if spreadsheet:
            try:
                sheet = spreadsheet.worksheet("سجل_الزيارات")
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sheet.append_row([now_str, "زائر جديد", "تصفح الحاسبة"])
                st.session_state["visited_logged"] = True
            except Exception:
                pass


log_page_visit()

# 4. الهيدر الرئيسي للتطبيق
st.markdown(
    """
    <div class="brand-header">
        <div class="brand-title">ABDELWAHAB GARMENTS</div>
        <div class="brand-subtitle">حاسبة استهلاك الأقمشة وتقدير الاحتياجات التشغيلية للمصانع</div>
    </div>
""",
    unsafe_allow_html=True,
)

# إدارة حالة التسجيل
if "user_registered" not in st.session_state:
    st.session_state["user_registered"] = False

# 5. القسم الأول: تسجيل البيانات الأساسية
if not st.session_state["user_registered"]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("بيانات التسجيل لتفعيل الحاسبة")
    st.caption("يرجى إدخال البيانات الأساسية للبدء في حساب احتياجات الأقمشة.")

    with st.form("client_register_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("الاسم بالكامل")
            phone = st.text_input("رقم الواتساب")
            job_title = st.text_input("الوظيفة / المسمى الوظيفي")
        with col2:
            email = st.text_input("البريد الإلكتروني")
            factory_brand = st.text_input("اسم المصنع أو البراند")
            newsletter = st.checkbox(
                "الاشتراك في النشرة البريدية والتحديثات التشغيلية", value=True
            )

        submit_btn = st.form_submit_button("الانتقال إلى الحاسبة")

        if submit_btn:
            if name.strip() == "" or phone.strip() == "":
                st.error("يرجى كتابة الاسم ورقم الواتساب على الأقل للمتابعة.")
            else:
                spreadsheet = get_google_sheet()
                if spreadsheet:
                    try:
                        sheet = spreadsheet.worksheet("العملاء")
                        now_str = datetime.datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        sheet.append_row(
                            [
                                name,
                                email,
                                phone,
                                factory_brand,
                                job_title,
                                "نعم" if newsletter else "لا",
                                now_str,
                            ]
                        )
                    except Exception:
                        pass
                st.session_state["user_registered"] = True
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# 6. القسم الثاني: الحاسبة التشغيلية
else:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("معطيات أمر التصنيع")

    col_unit, col_qty = st.columns(2)
    with col_unit:
        unit_type = st.selectbox(
            "وحدة حساب القماش",
            ["بالكيلوجرام (Kg)", "بالمتر (Meter)"],
            index=0,
        )
    with col_qty:
        order_qty = st.number_input(
            "عدد القطع المطلوب إنتاجها (قطع)",
            min_value=1,
            value=1000,
            step=50,
        )

    col1, col2 = st.columns(2)
    with col1:
        if "كيلوجرام" in unit_type:
            garment_consumption = st.number_input(
                "استهلاك القطعة الصافي (جرام)",
                min_value=1.0,
                value=250.0,
                step=10.0,
            )
            garment_cons_unit = garment_consumption / 1000.0
        else:
            garment_cons_unit = st.number_input(
                "استهلاك القطعة الصافي (متر)",
                min_value=0.1,
                value=1.35,
                step=0.05,
            )

        roll_size = st.number_input(
            f"وزن / طول الثوب المعياري ({'كيلو' if 'كيلوجرام' in unit_type else 'متر'})",
            min_value=1.0,
            value=20.0,
            step=1.0,
        )

    with col2:
        wastage_pct = st.number_input(
            "نسبة الهالك الفني والقص (%)",
            min_value=0.0,
            max_value=30.0,
            value=5.0,
            step=0.5,
        )

        price_per_unit = st.number_input(
            f"سعر {'الكيلو' if 'كيلوجرام' in unit_type else 'المتر'} (اختياري)",
            min_value=0.0,
            value=0.0,
            step=5.0,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # الحسابات البرمجية
    net_fabric_needed = order_qty * garment_cons_unit
    wastage_amount = net_fabric_needed * (wastage_pct / 100.0)
    total_fabric_needed = net_fabric_needed + wastage_amount
    estimated_rolls = (
        total_fabric_needed / roll_size if roll_size > 0 else 0.0
    )

    total_cost = total_fabric_needed * price_per_unit
    cost_per_garment = total_cost / order_qty if order_qty > 0 else 0.0

    unit_label = "كيلوجرام" if "كيلوجرام" in unit_type else "متر"

    # عرض النتائج
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("نتائج التتقدير والاحتياجات الإجمالية")

    res_col1, res_col2 = st.columns(2)

    with res_col1:
        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-label">إجمالي القماش الصافي المطلوب</div>
                <div class="result-value">{net_fabric_needed:,.2f} {unit_label}</div>
            </div>
            <div class="result-card">
                <div class="result-label">كمية الهالك المتوقعة ({wastage_pct}%)</div>
                <div class="result-value">{wastage_amount:,.2f} {unit_label}</div>
            </div>
            <div class="result-card">
                <div class="result-label">إجمالي القماش المطلوب لطلبه</div>
                <div class="result-value" style="color:#d4af37;">{total_fabric_needed:,.2f} {unit_label}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with res_col2:
        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-label">عدد الأثواب / الرولات المتوقع</div>
                <div class="result-value">{estimated_rolls:,.1f} ثوب</div>
            </div>
            <div class="result-card">
                <div class="result-label">إجمالي تكلفة القماش</div>
                <div class="result-value">{total_cost:,.2f}</div>
            </div>
            <div class="result-card">
                <div class="result-label">متوسط تكلفة القماش للقطعة</div>
                <div class="result-value">{cost_per_garment:,.2f}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

# 7. الفوتر الرئيسي
st.markdown(
    """
    <div class="footer-container">
        <div class="footer-brand">Abdelwahab Garments</div>
        <div class="footer-text">
            نساعد مصانع الملابس الصغيرة والمتوسطة على الانتقال من الإدارة بالإحساس إلى الإدارة بالأرقام. خبرة ميدانية فى صناعة الملابس الجاهزة منذ عام 2011، متخصص فى التخطيط والمتابعة وإدارة طلبات التصنيع.
        </div>
        <div class="social-row">
            <a href="https://abdelwahabgarments.com" target="_blank" class="social-btn" title="الموقع الرسمي">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="2" y1="12" x2="22" y2="12"></line>
                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                </svg>
            </a>
            <a href="https://facebook.com" target="_blank" class="social-btn" title="فيسبوك">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
            </a>
            <a href="https://wa.me/" target="_blank" class="social-btn" title="واتساب">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981z"/>
                </svg>
            </a>
        </div>
        <div class="copyright">
            جميع الحقوق محفوظة © 2026 Abdelwahab Garments - محمد عبد الوهاب
        </div>
    </div>
""",
    unsafe_allow_html=True,
)
