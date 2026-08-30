import datetime
import re
from google.oauth2.service_account import Credentials
import gspread
import streamlit as st

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="حاسبة استهلاك الأقمشة | Abdelwahab Garments",
    page_icon="📐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 2. التنسيق البصري وفرض اتجاه اللغة العربية (RTL)
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"], .stApp, div[data-testid="stForm"] {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        background-color: #0d0e11 !important;
        color: #e0e0e0;
    }

    .stTextInput label, .stNumberInput label, .stSelectbox label, .stCheckbox label, div[role="radiogroup"] label {
        text-align: right !important;
        width: 100% !important;
        display: block !important;
        color: #ffffff !important;
    }

    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        direction: rtl !important;
        text-align: right !important;
        background-color: #1c1f28 !important;
        color: #ffffff !important;
        border: 1px solid #2e3444 !important;
        border-radius: 8px !important;
    }

    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #d4af37 !important;
        box-shadow: 0 0 6px rgba(212, 175, 55, 0.4) !important;
    }

    div[data-baseweb="select"] > div {
        text-align: right !important;
        direction: rtl !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Cairo', sans-serif !important;
        color: #ffffff !important;
        font-weight: 700;
        text-align: right !important;
    }

    .brand-header {
        text-align: center !important;
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

    .custom-card {
        background-color: #15171e;
        border: 1px solid #242834;
        border-radius: 12px;
        padding: 28px;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }

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

    .result-card {
        background-color: #1a1d26;
        border-right: 4px solid #d4af37;
        padding: 18px;
        border-radius: 8px;
        margin-bottom: 14px;
        text-align: right !important;
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

    .footer-container {
        background-color: #12141a;
        border-top: 1px solid #222632;
        padding: 35px 25px 20px 25px;
        margin-top: 50px;
        border-radius: 12px 12px 0 0;
        text-align: right !important;
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
        margin-bottom: 20px;
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
        text-align: center !important;
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


# 3. إعداد الاتصال بقاعدة البيانات
@st.cache_resource
def get_google_sheet():
    try:
        if "gcp_service_account" not in st.secrets:
            return None, "مفاتيح GCP غير موجودة في Secrets."

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scopes
        )
        client = gspread.authorize(creds)
        spreadsheet = client.open("حاسبة استهلاك الأقمشة - البيانات")
        return spreadsheet, None
    except Exception as e:
        err_str = str(e)
        if "200" in err_str:
            return client, None
        return None, err_str


def log_page_visit():
    if "visited_logged" not in st.session_state:
        spreadsheet, _ = get_google_sheet()
        if spreadsheet:
            try:
                sheet = spreadsheet.worksheet("سجل_الزيارات")
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sheet.append_row([now_str, "زائر جديد", "تصفح الحاسبة"])
                st.session_state["visited_logged"] = True
            except Exception:
                pass


log_page_visit()

# 4. الهيدر الرئيسي
st.markdown(
    """
    <div class="brand-header">
        <div class="brand-title">ABDELWAHAB GARMENTS</div>
        <div class="brand-subtitle">حاسبة استهلاك الأقمشة وتقدير الاحتياجات التشغيلية للمصانع</div>
    </div>
""",
    unsafe_allow_html=True,
)

if "user_registered" not in st.session_state:
    st.session_state["user_registered"] = False

# 5. نموذج التسجيل
if not st.session_state["user_registered"]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("بيانات التسجيل لتفعيل الحاسبة")
    st.caption("جميع الحقول مطلوبة لتفعيل الحاسبة وتوثيق طلبك.")

    with st.form("client_register_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("الاسم بالكامل *")
            phone = st.text_input("رقم الواتساب *", placeholder="01xxxxxxxxx")
            job_title = st.selectbox(
                "الوظيفة / المسمى الوظيفي *",
                [
                    "اختر المسمى الوظيفي...",
                    "صاحب مصنع / البراند",
                    "مدير إنتاج",
                    "مدير جودة",
                    "مهندس تخطيط ومتابعة",
                    "مصمم / باترونيست",
                    "مسؤول مشتريات",
                    "أخرى",
                ],
            )

        with col2:
            email = st.text_input(
                "البريد الإلكتروني *", placeholder="example@domain.com"
            )
            factory_brand = st.text_input("اسم المصنع أو البراند *")
            newsletter = st.checkbox(
                "الاشتراك في النشرة البريدية والتحديثات التشغيلية", value=True
            )

        submit_btn = st.form_submit_button("الانتقال إلى الحاسبة")

        if submit_btn:
            email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            clean_phone = re.sub(r"\D", "", phone)

            if (
                name.strip() == ""
                or phone.strip() == ""
                or email.strip() == ""
                or factory_brand.strip() == ""
            ):
                st.error("يرجى ملء جميع الحقول المطلوبة.")
            elif job_title == "اختر المسمى الوظيفي...":
                st.error("يرجى اختيار المسمى الوظيفي من القائمة.")
            elif not re.match(email_regex, email.strip()):
                st.error("يرجى إدخال بريد إلكتروني صحيح.")
            elif len(clean_phone) < 10:
                st.error("يرجى إدخال رقم واتساب صحيح.")
            else:
                spreadsheet, err = get_google_sheet()
                if spreadsheet:
                    try:
                        sheet = spreadsheet.worksheet("العملاء")
                        now_str = datetime.datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        sheet.append_row(
                            [
                                name.strip(),
                                email.strip(),
                                phone.strip(),
                                factory_brand.strip(),
                                job_title,
                                "نعم" if newsletter else "لا",
                                now_str,
                            ]
                        )
                        st.session_state["user_registered"] = True
                        st.rerun()
                    except Exception:
                        st.session_state["user_registered"] = True
                        st.rerun()
                else:
                    st.session_state["user_registered"] = True
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# 6. الحاسبة التشغيلية (المعادلات الرياضية الدقيقة المطابقة لطلبك)
else:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("معطيات أمر التصنيع واستهلاك الأقمشة")

    fabric_type = st.selectbox(
        "اختر نوع القماش وطريقة الحساب",
        [
            (
                "1. أقمشة التريكو - من واقع معطيات الماركر (الأكثر دقة)"
                if "1." in "1."
                else "أقمشة التريكو - من واقع معطيات الماركر"
            ),
            "2. أقمشة التريكو - التقدير المباشر لأبعاد الباترون",
            "3. أقمشة المنسوج - من واقع طول الماركر",
            "4. أقمشة المنسوج - من مجموع مكونات الباترون (تقديري)",
        ],
    )

    order_qty = st.number_input(
        "كمية الأمر (عدد القطع المطلوب إنتاجها)", min_value=1, value=1000, step=50
    )

    col1, col2 = st.columns(2)

    # 1. تريكو - ماركر
    if "1." in fabric_type:
        with col1:
            marker_length = st.number_input(
                "طول الماركر (سم)", min_value=1.0, value=650.0, step=10.0
            )
            fabric_width = st.number_input(
                "عرض القماش الشغال (سم)", min_value=1.0, value=180.0, step=5.0
            )
            gsm = st.number_input(
                "وزن المتر المربع (GSM)", min_value=1.0, value=200.0, step=10.0
            )
        with col2:
            pieces_in_marker = st.number_input(
                "عدد القطع في الماركر", min_value=1, value=10, step=1
            )
            wastage_pct = st.number_input(
                "نسبة الهدر (%)",
                min_value=0.0,
                max_value=30.0,
                value=5.0,
                step=0.5,
            )
            price_per_unit = st.number_input(
                "سعر الكيلو (جنيه)", min_value=0.0, value=120.0, step=5.0
            )

        # المعادلة: [(طول الماركر سم × عرض القماش سم × GSM) ÷ (عدد القطع × 10,000,000)] × (1 + نسبة الهدر %)
        single_net_kg = (marker_length * fabric_width * gsm) / (
            pieces_in_marker * 10000000.0
        )
        single_total_kg = single_net_kg * (1.0 + (wastage_pct / 100.0))
        net_fabric_needed = order_qty * single_net_kg
        total_fabric_needed = order_qty * single_total_kg
        unit_label = "كجم"

    # 2. تريكو - أبعاد باترون
    elif "2." in fabric_type:
        with col1:
            part_length = st.number_input(
                "طول القطعة بالسماحات (سم)", min_value=1.0, value=75.0, step=1.0
            )
            part_width = st.number_input(
                "عرض نصف الصدر بالسماحات (سم)",
                min_value=1.0,
                value=56.0,
                step=1.0,
            )
            gsm = st.number_input(
                "وزن المتر المربع (GSM)", min_value=1.0, value=180.0, step=10.0
            )
        with col2:
            wastage_pct = st.number_input(
                "نسبة الهدر (%)",
                min_value=0.0,
                max_value=30.0,
                value=5.0,
                step=0.5,
            )
            price_per_unit = st.number_input(
                "سعر الكيلو (جنيه)", min_value=0.0, value=120.0, step=5.0
            )

        # المعادلة: [طول بالسماحات × عرض بالسماحات × 2 × GSM ÷ 10,000] × (1 + نسبة الهدر %) ثم التقسيم على 1000 للحصول على الكيلو
        single_net_grams = (
            part_length * part_width * 2.0 * gsm
        ) / 10000.0  # وزن القطعة بالجرام الصافي
        single_net_kg = single_net_grams / 1000.0
        single_total_kg = (single_net_kg * (1.0 + (wastage_pct / 100.0)))
        net_fabric_needed = order_qty * single_net_kg
        total_fabric_needed = order_qty * single_total_kg
        unit_label = "كجم"

    # 3. منسوج - طول الماركر
    elif "3." in fabric_type:
        with col1:
            marker_length_m = st.number_input(
                "طول الماركر (متر)", min_value=0.1, value=12.5, step=0.5
            )
            pieces_in_marker = st.number_input(
                "عدد القطع في الماركر", min_value=1, value=8, step=1
            )
        with col2:
            wastage_pct = st.number_input(
                "نسبة الهدر (%)",
                min_value=0.0,
                max_value=30.0,
                value=5.0,
                step=0.5,
            )
            price_per_unit = st.number_input(
                "سعر المتر (جنيه)", min_value=0.0, value=90.0, step=5.0
            )

        # المعادلة: [طول الماركر (متر) ÷ عدد القطع] × (1 + نسبة الهدر %)
        single_net_m = (
            marker_length_m / pieces_in_marker if pieces_in_marker > 0 else 0
        )
        single_total_m = single_net_m * (1.0 + (wastage_pct / 100.0))
        net_fabric_needed = order_qty * single_net_m
        total_fabric_needed = order_qty * single_total_m
        unit_label = "متر"

    # 4. منسوج - مكونات الباترون
    else:
        with col1:
            body_len = st.number_input(
                "طول الجسم الرئيسي (سم)", min_value=1.0, value=78.0, step=1.0
            )
            sleeve_len = st.number_input(
                "طول الكم والأجزاء الفرعية (سم)",
                min_value=0.0,
                value=64.0,
                step=1.0,
            )
            allowances = st.number_input(
                "سماحات الخياطة والتثنيات (سم)",
                min_value=0.0,
                value=12.0,
                step=1.0,
            )
        with col2:
            wastage_pct = st.number_input(
                "نسبة الهدر (%)",
                min_value=0.0,
                max_value=30.0,
                value=5.0,
                step=0.5,
            )
            price_per_unit = st.number_input(
                "سعر المتر (جنيه)", min_value=0.0, value=90.0, step=5.0
            )

        # المعادلة: [(طول الجسم + طول الكم + السماحات) ÷ 100] × (1 + نسبة الهدر %)
        total_cm = body_len + sleeve_len + allowances
        single_net_m = total_cm / 100.0
        single_total_m = single_net_m * (1.0 + (wastage_pct / 100.0))
        net_fabric_needed = order_qty * single_net_m
        total_fabric_needed = order_qty * single_total_m
        unit_label = "متر"

    total_cost = total_fabric_needed * price_per_unit
    cost_per_garment = total_cost / order_qty if order_qty > 0 else 0.0

    st.markdown("</div>", unsafe_allow_html=True)

    # عرض النتائج التشغيلية
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("نتائج التقدير والاحتياجات التشغيلية")

    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-label">الاستهلاك الصافي للقطعة الواحدة</div>
                <div class="result-value">{(net_fabric_needed/order_qty):,.4f} {unit_label}</div>
            </div>
            <div class="result-card">
                <div class="result-label">إجمالي الكمية الصافية المطلوبة</div>
                <div class="result-value">{net_fabric_needed:,.2f} {unit_label}</div>
            </div>
            <div class="result-card">
                <div class="result-label">إجمالي الكمية المطلوبة شاملة الهدر</div>
                <div class="result-value" style="color:#d4af37;">{total_fabric_needed:,.2f} {unit_label}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with res_col2:
        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-label">سعر الوحدة</div>
                <div class="result-value">{price_per_unit:,.2f} جنيه</div>
            </div>
            <div class="result-card">
                <div class="result-label">إجمالي التكلفة المالية للقماش</div>
                <div class="result-value">{total_cost:,.2f} جنيه</div>
            </div>
            <div class="result-card">
                <div class="result-label">نصيب القطعة من تكلفة القماش</div>
                <div class="result-value">{cost_per_garment:,.2f} جنيه</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

# الفوتر الرئيسي النهائي
st.markdown("---")

st.markdown(
    """
    <div style="direction: rtl; text-align: center; font-family: sans-serif; padding: 10px;">
        <h3 style="color: #d4af37; margin-bottom: 8px;">Abdelwahab Garments</h3>
        <p style="color: #a0a6b8; font-size: 14px; line-height: 1.6; max-width: 600px; margin: 0 auto 15px auto;">
            نساعد مصانع الملابس الصغيرة والمتوسطة على الانتقال من الإدارة بالإحساس إلى الإدارة بالأرقام.
        </p>
        <div style="margin: 15px 0; display: flex; justify-content: center; gap: 25px; font-size: 14px; flex-wrap: wrap;">
            <a href="mailto:abdelwahab.garments@gmail.com" style="color: #d4af37; text-decoration: none;">راسلنا بريدياً</a>
            <a href="https://www.facebook.com/abdelwahab.garments" target="_blank" style="color: #d4af37; text-decoration: none;">صفحة الفيسبوك</a>
            <a href="https://wa.me/201002002202" target="_blank" style="color: #d4af37; text-decoration: none;">تواصل واتساب</a>
        </div>
        <p style="color: #636a79; font-size: 12px; margin-top: 20px;">
            جميع الحقوق محفوظة © 2026 Abdelwahab Garments - محمد عبد الوهاب
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
