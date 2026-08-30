import streamlit as st

st.set_page_config(page_title="حاسبة استهلاك الأقمشة", layout="wide")

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
