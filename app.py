import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="حاسبة استهلاك الأقمشة - محمد عبدالوهاب", layout="wide")

# تنسيق واجهة التطبيق لتكون من اليمين إلى اليسار (RTL)
st.markdown("""
    <style>
    html, body, [class*="css"], .stApp {
        direction: rtl;
        text-align: right;
    }
    
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        text-align: right !important;
        direction: rtl !important;
    }
    
    button[data-baseweb="tab"] {
        direction: rtl !important;
    }
    
    section[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    
    div[class*="stRadio"] > label, div[class*="stNumberInput"] > label, div[class*="stTextInput"] > label {
        text-align: right !important;
        direction: rtl !important;
    }
    
    .social-btn-web {
        display: block;
        width: 100%;
        background-color: #1E3A8A;
        color: white !important;
        text-align: center;
        padding: 10px;
        margin-bottom: 8px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: bold;
    }
    .social-btn-fb {
        display: block;
        width: 100%;
        background-color: #1877F2;
        color: white !important;
        text-align: center;
        padding: 10px;
        margin-bottom: 8px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# إدارة حالة الدخول
if 'registered' not in st.session_state:
    st.session_state['registered'] = False

# الشريط الجانبي
with st.sidebar:
    st.header("محمد عبدالوهاب")
    st.write("استشارات وتخطيط إنتاج مصانع الملابس")
    st.markdown("---")
    
    st.markdown('<a href="https://abdelwahabgarments.com/" target="_blank" class="social-btn-web">زيارة الموقع الرسمي</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://www.facebook.com/abdelwahab.garments" target="_blank" class="social-btn-fb">متابعة صفحة الفيسبوك</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("تطوير وتشغيل: الرادار - Abdelwahab Garments")

# دالة حفظ تسجيل جديد
def save_new_lead(name, email, whatsapp, company, job_title, newsletter_opt_in):
    file_path = "leads.csv"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([{
        "التاريخ والوقت": timestamp,
        "الاسم": name,
        "البريد الإلكتروني": email.strip().lower(),
        "رقم الواتساب": whatsapp.strip(),
        "المصنع / البراند": company,
        "الوظيفة": job_title,
        "الاشتراك في النشرة": "نعم" if newsletter_opt_in else "لا",
        "عدد الزيارات": 1
    }])
    
    if os.path.exists(file_path):
        new_data.to_csv(file_path, mode='a', header=False, index=False, encoding='utf-8-sig')
    else:
        new_data.to_csv(file_path, mode='w', header=True, index=False, encoding='utf-8-sig')

# دالة التحقق من زائر سابق
def check_returning_lead(identifier):
    file_path = "leads.csv"
    if not os.path.exists(file_path):
        return False
    
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    identifier_clean = identifier.strip().lower()
    
    # البحث بالبريد أو برقم الواتساب
    emails = df['البريد الإلكتروني'].astype(str).str.strip().str.lower().tolist() if 'البريد الإلكتروني' in df.columns else []
    phones = df['رقم الواتساب'].astype(str).str.strip().tolist() if 'رقم الواتساب' in df.columns else []
    
    if identifier_clean in emails or identifier_clean in phones:
        return True
    return False

# شاشة الوصول للتطبيق
if not st.session_state['registered']:
    st.title("حاسبة استهلاك الأقمشة (تريكو ومنسوج)")
    
    access_type = st.radio(
        "يرجى تحديد نوع الدخول:",
        ["دخول سريع (لمستخدم مسجل سابقاً)", "تسجيل جديد (لأول مرة)"],
        horizontal=True
    )
    
    st.markdown("---")
    
    # نموذج الدخول السريع
    if access_type == "دخول سريع (لمستخدم مسجل سابقاً)":
        st.subheader("الدخول السريع")
        with st.form("quick_login_form"):
            user_input = st.text_input("ادخل البريد الإلكتروني أو رقم الواتساب المسجل لدينا:")
            submit_quick = st.form_submit_button("فتح الحاسبة")
            
            if submit_quick:
                if user_input:
                    if check_returning_lead(user_input):
                        st.session_state['registered'] = True
                        st.success("تم التحقق بنجاح. جاري فتح الحاسبة...")
                        st.rerun()
                    else:
                        st.error("البيانات المدخلة غير مسجلة لدينا مسبقاً. يرجى اختيار 'تسجيل جديد (لأول مرة)' لإكمال البيانات.")
                else:
                    st.warning("يرجى كتابة البريد الإلكتروني أو رقم الواتساب للتحقق.")

    # نموذج التسجيل الكامل لأول مرة
    else:
        st.subheader("تسجيل البيانات لأول مرة")
        with st.form("registration_form"):
            col_reg1, col_reg2 = st.columns(2)
            
            with col_reg1:
                user_name = st.text_input("الاسم بالكامل *")
                user_email = st.text_input("البريد الإلكتروني *")
                user_whatsapp = st.text_input("رقم الواتساب *")
                
            with col_reg2:
                user_company = st.text_input("اسم المصنع أو البراند *")
                user_job = st.selectbox(
                    "الوظيفة / طبيعة العمل *",
                    ["صاحب مصنع", "صاحب براند ملابس", "مدير إنتاج", "مخطط إنتاج / PPC", "باترونيست / مصمم", "أخرى"]
                )
            
            newsletter_opt = st.checkbox(
                "أود الاشتراك في النشرة البريدية الأسبوعية الخاصة بتخطيط وتطوير إنتاج الملابس",
                value=True
            )
            
            submit_button = st.form_submit_button("حفظ البيانات وبدء استخدام الحاسبة")
            
            if submit_button:
                if user_name and user_email and user_whatsapp and user_company:
                    save_new_lead(user_name, user_email, user_whatsapp, user_company, user_job, newsletter_opt)
                    st.session_state['registered'] = True
                    st.success("تم الحفظ بنجاح. جاري فتح الحاسبة...")
                    st.rerun()
                else:
                    st.error("يرجى إكمال جميع الخانات المطلوبة للبدء.")

# الشاشة الرئيسية - الحاسبة
else:
    st.title("حاسبة استهلاك الأقمشة (تريكو ومنسوج)")
    st.write("أداة حساب الاستهلاك الفعلي والتقديري للقطع وأوامر التشغيل")

    tab1, tab2 = st.tabs(["أقمشة التريكو (بالوزن)", "أقمشة المنسوج (بالمتر)"])

    # تبويب التريكو
    with tab1:
        st.header("حساب استهلاك التريكو بالكيلوجرام")
        
        calc_type_knit = st.radio(
            "طريقة الحساب:",
            ["بناءً على معطيات الماركر (دقيق)", "بناءً على أبعاد القطعة (تقديري)"]
        )
        
        col1, col2 = st.columns(2)
        
        if calc_type_knit == "بناءً على معطيات الماركر (دقيق)":
            with col1:
                marker_len = st.number_input("طول الماركر (سم)", value=650.0, step=10.0)
                fabric_width = st.number_input("عرض القماش الشغال (سم)", value=180.0, step=5.0)
                gsm = st.number_input("وزن المتر المربع GSM (جرام)", value=200.0, step=5.0)
            with col2:
                garments_count = st.number_input("عدد القطع في الماركر", value=10, step=1)
                wastage_knit = st.number_input("نسبة الهدر والعوادم (%)", value=5.0, step=0.5)
                order_qty_knit = st.number_input("كمية الأمر (عدد القطع)", value=1000, step=100, key="k1")
                
            net_kg = (marker_len * fabric_width * gsm) / (garments_count * 10000000)
            gross_kg = net_kg * (1 + (wastage_knit / 100))
            total_order_kg = gross_kg * order_qty_knit
            
        else:
            with col1:
                garment_len = st.number_input("طول القطعة شامل السماحات (سم)", value=75.0, step=1.0)
                garment_width = st.number_input("عرض نصف الصدر شامل السماحات (سم)", value=56.0, step=1.0)
                gsm = st.number_input("وزن المتر المربع GSM (جرام)", value=180.0, step=5.0, key="gsm2")
            with col2:
                wastage_knit = st.number_input("نسبة الهدر والقص (%)", value=7.0, step=0.5, key="w2")
                order_qty_knit = st.number_input("كمية الأمر (عدد القطع)", value=1000, step=100, key="k2")
                
            gross_grams = ((garment_len * garment_width * 2 * gsm) / 10000) * (1 + (wastage_knit / 100))
            gross_kg = gross_grams / 1000
            total_order_kg = gross_kg * order_qty_knit

        st.markdown("---")
        res_c1, res_c2, res_c3 = st.columns(3)
        res_c1.metric("استهلاك القطعة (جرام)", f"{gross_kg * 1000:.1f} جرام")
        res_c2.metric("استهلاك القطعة (كجم)", f"{gross_kg:.3f} كجم")
        res_c3.metric("إجمالي قماش الأمر (كجم)", f"{total_order_kg:.1f} كجم")

    # تبويب المنسوج
    with tab2:
        st.header("حساب استهلاك المنسوج بالمتر الطولي")
        
        calc_type_woven = st.radio(
            "طريقة الحساب:",
            ["بناءً على معطيات الماركر", "حساب تقديري بمكونات القطعة"]
        )
        
        col1_w, col2_w = st.columns(2)
        
        if calc_type_woven == "بناءً على معطيات الماركر":
            with col1_w:
                marker_meters = st.number_input("طول الماركر (متر)", value=12.50, step=0.5)
                garments_in_marker = st.number_input("عدد القطع في الماركر", value=8, step=1, key="wm1")
            with col2_w:
                wastage_woven = st.number_input("إجمالي نسبة الهدر ونهايات التواب (%)", value=5.0, step=0.5)
                order_qty_woven = st.number_input("كمية الأمر (عدد القطع)", value=500, step=50, key="wq1")
                
            net_meters = marker_meters / garments_in_marker
            gross_meters = net_meters * (1 + (wastage_woven / 100))
            total_order_meters = gross_meters * order_qty_woven
            
        else:
            with col1_w:
                body_len = st.number_input("طول الجسم الرئيسي (سم)", value=78.0, step=1.0)
                sleeve_len = st.number_input("طول الكم / الأجزاء الفرعية (سم)", value=64.0, step=1.0)
                seam_allowance = st.number_input("سماحات الخياطة والثنيات (سم)", value=12.0, step=1.0)
            with col2_w:
                wastage_woven = st.number_input("نسبة الهدر والقص (%)", value=5.0, step=0.5, key="ww2")
                order_qty_woven = st.number_input("كمية الأمر (عدد القطع)", value=500, step=50, key="wq2")
                
            total_cm = body_len + sleeve_len + seam_allowance
            gross_meters = (total_cm / 100) * (1 + (wastage_woven / 100))
            total_order_meters = gross_meters * order_qty_woven

        st.markdown("---")
        w_res1, w_res2 = st.columns(2)
        w_res1.metric("استهلاك القطعة الواحدة", f"{gross_meters:.3f} متر")
        w_res2.metric("إجمالي أمتار القماش المطلوبة", f"{total_order_meters:.1f} متر")
