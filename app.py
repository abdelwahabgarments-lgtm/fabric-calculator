import datetime as dt
import re
import uuid

import gspread
import streamlit as st
from google.oauth2.service_account import Credentials


# ==========================================================
# 1) Page configuration
# ==========================================================
st.set_page_config(
    page_title="Consumption Model | Abdelwahab Garments",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==========================================================
# 2) Visual system
# ==========================================================
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');

        :root {
            --bg: #0b0d10;
            --panel: #12161c;
            --panel-2: #171c23;
            --line: #252c36;
            --text: #f4f5f7;
            --muted: #98a1ae;
            --gold: #d4af37;
            --gold-2: #f1d675;
            --success: #4ade80;
            --danger: #f87171;
        }

        html, body, [class*="css"], .stApp {
            font-family: 'Cairo', sans-serif !important;
            direction: rtl !important;
        }

        .stApp {
            background:
                radial-gradient(circle at 90% 0%, rgba(212,175,55,.08), transparent 28%),
                radial-gradient(circle at 10% 20%, rgba(255,255,255,.025), transparent 24%),
                var(--bg) !important;
            color: var(--text) !important;
        }

        [data-testid="stHeader"] {
            background: transparent !important;
        }

        [data-testid="stToolbar"] {
            visibility: hidden;
        }

        .block-container {
            max-width: 1120px !important;
            padding-top: 1.25rem !important;
            padding-bottom: 2rem !important;
        }

        h1, h2, h3, h4, h5, h6,
        p, label, span, div {
            font-family: 'Cairo', sans-serif !important;
        }

        h1, h2, h3, h4 {
            color: #fff !important;
        }

        .brand-wrap {
            padding: 12px 0 28px;
            border-bottom: 1px solid var(--line);
            margin-bottom: 28px;
        }

        .brand-row {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            gap: 20px;
        }

        .eyebrow {
            color: var(--gold-2);
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1.6px;
            text-transform: uppercase;
            margin-bottom: 4px;
        }

        .brand-title {
            color: var(--gold) !important;
            font-size: 32px;
            line-height: 1.2;
            font-weight: 800;
            letter-spacing: 1px;
        }

        .brand-subtitle {
            margin-top: 8px;
            color: var(--muted);
            font-size: 15px;
        }

        .system-status {
            color: #c9d0d8;
            background: rgba(74,222,128,.08);
            border: 1px solid rgba(74,222,128,.18);
            border-radius: 999px;
            padding: 7px 12px;
            font-size: 12px;
            white-space: nowrap;
        }

        .system-status span {
            color: var(--success) !important;
        }

        .panel {
            background: linear-gradient(180deg, rgba(255,255,255,.018), rgba(255,255,255,.008));
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 24px;
            box-shadow: 0 18px 45px rgba(0,0,0,.22);
            margin-bottom: 20px;
        }

        .panel-tight {
            padding: 18px 20px;
        }

        .section-kicker {
            color: var(--gold);
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 1px;
            margin-bottom: 6px;
        }

        .section-title {
            color: #fff;
            font-size: 22px;
            font-weight: 800;
            margin-bottom: 7px;
        }

        .section-description {
            color: var(--muted);
            font-size: 13px;
            line-height: 1.8;
            margin-bottom: 18px;
        }

        .login-hint {
            color: var(--muted);
            font-size: 13px;
            line-height: 1.8;
            margin: 8px 0 18px;
        }

        .welcome-card {
            background: linear-gradient(135deg, rgba(212,175,55,.09), rgba(212,175,55,.025));
            border: 1px solid rgba(212,175,55,.2);
            border-radius: 14px;
            padding: 14px 16px;
            margin-bottom: 18px;
        }

        .welcome-title {
            font-size: 15px;
            font-weight: 800;
            color: #fff;
        }

        .welcome-meta {
            font-size: 12px;
            color: var(--muted);
            margin-top: 3px;
        }

        .model-chip {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 999px;
            background: #171c23;
            border: 1px solid var(--line);
            color: #d7dce3;
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 12px;
        }

        .model-chip strong {
            color: var(--gold-2);
        }

        .result-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px;
            margin-top: 10px;
        }

        .metric-card {
            background: var(--panel-2);
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 11px 13px;
            min-height: 82px;
        }

        .metric-card.primary {
            border-color: rgba(212,175,55,.38);
            box-shadow: inset 0 1px 0 rgba(212,175,55,.08);
        }

        .metric-label {
            color: var(--muted);
            font-size: 12px;
            line-height: 1.7;
        }

        .metric-value {
            margin-top: 5px;
            color: #fff;
            font-size: 19px;
            font-weight: 800;
            direction: ltr;
            text-align: right;
            line-height: 1.25;
        }

        .metric-value.gold {
            color: var(--gold-2);
        }

        .metric-sub {
            color: #6f7885;
            font-size: 11px;
            margin-top: 2px;
        }

        .formula-note {
            background: #0f1318;
            border: 1px dashed #2a313b;
            border-radius: 12px;
            color: #b2bac5;
            font-size: 12px;
            line-height: 1.9;
            padding: 12px 14px;
            margin-top: 15px;
        }

        .formula-note strong {
            color: #e6e8eb;
        }

        .trust-note {
            color: #87909d;
            font-size: 11px;
            line-height: 1.8;
            margin-top: 10px;
        }

        .print-actions {
            margin: 8px 0 12px;
        }

        .print-report {
            display: none;
            background: #fff;
            color: #15171b;
            border: 1px solid #e2e2e2;
            border-radius: 10px;
            padding: 28px;
            position: relative;
            overflow: hidden;
            direction: rtl;
        }

        .print-report::after {
            content: 'ABDELWAHAB GARMENTS';
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%) rotate(-24deg);
            font-size: 42px;
            font-weight: 800;
            letter-spacing: 3px;
            color: rgba(70,70,70,.055);
            white-space: nowrap;
            pointer-events: none;
            z-index: 0;
        }

        .print-inner {
            position: relative;
            z-index: 1;
        }

        .print-head {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 20px;
            border-bottom: 2px solid #d4af37;
            padding-bottom: 14px;
            margin-bottom: 16px;
        }

        .print-brand {
            color: #8a6a00;
            font-size: 21px;
            font-weight: 800;
            letter-spacing: 1px;
        }

        .print-title {
            font-size: 16px;
            font-weight: 800;
            margin-top: 3px;
        }

        .print-meta {
            font-size: 11px;
            color: #666;
            line-height: 1.7;
            text-align: left;
        }

        .print-section-title {
            margin: 14px 0 8px;
            font-size: 13px;
            font-weight: 800;
            color: #8a6a00;
        }

        .print-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
        }

        .print-table th, .print-table td {
            border: 1px solid #e5e5e5;
            padding: 7px 8px;
            text-align: right;
        }

        .print-table th {
            background: #f7f7f7;
            font-weight: 700;
        }

        .print-total {
            margin-top: 12px;
            border: 2px solid #d4af37;
            padding: 11px 12px;
            border-radius: 8px;
            font-weight: 800;
            text-align: center;
        }

        .print-footer {
            margin-top: 18px;
            padding-top: 10px;
            border-top: 1px solid #e5e5e5;
            font-size: 10px;
            color: #666;
            line-height: 1.8;
            text-align: center;
        }

        .stCaption, [data-testid="stCaptionContainer"] {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }

        @media print {
            @page { margin: 10mm; size: A4 portrait; }
            body * { visibility: hidden !important; }
            .print-report, .print-report * { visibility: visible !important; }
            .print-report {
                display: block !important;
                position: absolute !important;
                top: 0 !important;
                left: 0 !important;
                width: 100% !important;
                border: none !important;
                border-radius: 0 !important;
                box-shadow: none !important;
                margin: 0 !important;
                padding: 0 !important;
            }
        }

        .footer {
            margin-top: 34px;
            padding: 24px 0 4px;
            border-top: 1px solid var(--line);
            text-align: center;
        }

        .footer-brand {
            color: var(--gold);
            font-weight: 800;
            letter-spacing: 1px;
            font-size: 18px;
        }

        .footer-copy {
            color: #6c7581;
            font-size: 11px;
            margin-top: 7px;
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        .stNumberInput input,
        .stTextInput input {
            background: #151a21 !important;
            color: #fff !important;
            border-color: #2a313b !important;
            border-radius: 10px !important;
        }

        div[data-baseweb="select"] * {
            color: #fff !important;
        }

        .stTextInput input,
        .stNumberInput input {
            direction: ltr !important;
            text-align: left !important;
        }

        label {
            color: #eef0f3 !important;
            font-weight: 600 !important;
        }

        .stCheckbox label {
            color: #d8dde4 !important;
            font-size: 12px !important;
        }

        .stButton > button,
        .stFormSubmitButton > button {
            width: 100%;
            min-height: 48px;
            border: 0 !important;
            border-radius: 10px !important;
            font-family: 'Cairo', sans-serif !important;
            font-weight: 800 !important;
            font-size: 14px !important;
            background: linear-gradient(135deg, #d4af37, #b88d13) !important;
            color: #0b0d10 !important;
            transition: .2s ease;
        }

        .stButton > button:hover,
        .stFormSubmitButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 24px rgba(212,175,55,.18);
        }

        .secondary-btn .stButton > button {
            background: #171c23 !important;
            color: #fff !important;
            border: 1px solid var(--line) !important;
            box-shadow: none !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: transparent;
        }

        .stTabs [data-baseweb="tab"] {
            background: #131820;
            border: 1px solid var(--line);
            border-radius: 10px;
            color: #aeb7c2 !important;
            padding: 8px 18px;
        }

        .stTabs [aria-selected="true"] {
            color: #fff !important;
            border-color: rgba(212,175,55,.45) !important;
            background: rgba(212,175,55,.08) !important;
        }

        @media (max-width: 900px) {
            .brand-row {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }
            .panel {
                padding: 18px;
            }
        }

        @media (max-width: 560px) {
            .result-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 8px;
            }
            .brand-title {
                font-size: 23px;
            }
            .brand-subtitle {
                font-size: 12px;
            }
            .panel {
                padding: 14px;
                border-radius: 14px;
            }
            .section-title {
                font-size: 18px;
            }
            .metric-card {
                padding: 9px 10px;
                min-height: 74px;
            }
            .metric-label {
                font-size: 10px;
            }
            .metric-value {
                font-size: 15px;
            }
            .metric-sub {
                font-size: 9px;
            }
            .print-report {
                padding: 18px;
            }
            .print-head {
                flex-direction: column;
            }
            .print-meta {
                text-align: right;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# 3) Google Sheets data layer
# ==========================================================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SPREADSHEET_ID = "1aYYZ9g52aCR8EFe0rxQtnPEDtjx_sqiTX7uNlRP8-pU"

CUSTOMERS_HEADERS = [
    "Customer ID",
    "Registration Date",
    "Last Visit",
    "Full Name",
    "Email",
    "WhatsApp",
    "Country",
    "Governorate",
    "Factory / Brand",
    "Job Title",
    "Newsletter",
    "Lead Source",
    "Total Calculations",
    "Last Calculation",
    "Status",
]

VISITS_HEADERS = [
    "Visit ID",
    "Date",
    "Customer ID",
    "Email",
    "Event",
]

CALCULATIONS_HEADERS = [
    "Calculation ID",
    "Date",
    "Customer ID",
    "Email",
    "Model ID / Name",
    "Fabric Type",
    "Calculation Type",
    "Order Quantity",
    "Rack Length",
    "Rack Length Unit",
    "Fabric Width",
    "GSM",
    "Pieces / Rack",
    "Insurance %",
    "Unit Price",
    "Net Consumption / Piece",
    "Net Requirement",
    "Insurance Quantity",
    "Recommended Purchase",
    "Total Cost",
    "Cost / Garment",
]

EVENTS_HEADERS = [
    "Event ID",
    "Date",
    "Customer ID",
    "Email",
    "Event",
    "Details",
]


def _now_str() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@st.cache_resource
def get_google_sheet():
    """Create and cache the Google Sheets client resource."""
    if "gcp_service_account" not in st.secrets:
        raise RuntimeError("مفاتيح GCP غير موجودة في Secrets.")

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID)


def get_worksheet(name: str, headers: list[str]):
    """Return a worksheet and create it with headers if missing."""
    spreadsheet = get_google_sheet()
    try:
        return spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=name, rows=1000, cols=max(len(headers), 10))
        worksheet.append_row(headers, value_input_option="USER_ENTERED")
        return worksheet


def find_customer_by_email(email: str):
    """Return customer dict if email exists, otherwise None."""
    email = email.strip().lower()
    sheet = get_worksheet("Customers", CUSTOMERS_HEADERS)
    records = sheet.get_all_records()

    for row in records:
        row_email = str(row.get("Email", "")).strip().lower()
        if row_email == email:
            return row
    return None


def create_customer(customer_data: dict) -> dict:
    """Create a new customer and return the stored customer record."""
    existing = find_customer_by_email(customer_data["email"])
    if existing:
        return existing

    customer_id = f"AWG-{uuid.uuid4().hex[:8].upper()}"
    now = _now_str()
    row = [
        customer_id,
        now,
        now,
        customer_data["name"],
        customer_data["email"],
        customer_data["phone"],
        customer_data["country"],
        customer_data["governorate"],
        customer_data["factory_brand"],
        customer_data["job_title"],
        "نعم" if customer_data["newsletter"] else "لا",
        "Consumption Model",
        0,
        "",
        "Active",
    ]

    sheet = get_worksheet("Customers", CUSTOMERS_HEADERS)
    sheet.append_row(row, value_input_option="USER_ENTERED")

    return {
        "Customer ID": customer_id,
        "Registration Date": now,
        "Last Visit": now,
        "Full Name": customer_data["name"],
        "Email": customer_data["email"],
        "WhatsApp": customer_data["phone"],
        "Country": customer_data["country"],
        "Governorate": customer_data["governorate"],
        "Factory / Brand": customer_data["factory_brand"],
        "Job Title": customer_data["job_title"],
        "Newsletter": "نعم" if customer_data["newsletter"] else "لا",
        "Lead Source": "Consumption Model",
        "Total Calculations": 0,
        "Last Calculation": "",
        "Status": "Active",
    }


def record_visit(customer: dict, event_name: str = "Login") -> None:
    now = _now_str()
    visits = get_worksheet("Visits", VISITS_HEADERS)
    visits.append_row(
        [
            f"VIS-{uuid.uuid4().hex[:10].upper()}",
            now,
            customer.get("Customer ID", ""),
            customer.get("Email", ""),
            event_name,
        ],
        value_input_option="USER_ENTERED",
    )


def update_customer_activity(customer: dict, calculation_id: str | None = None) -> None:
    """Update last visit and calculation counters by Customer ID."""
    sheet = get_worksheet("Customers", CUSTOMERS_HEADERS)
    rows = sheet.get_all_values()
    if not rows:
        return

    header = rows[0]
    try:
        id_col = header.index("Customer ID") + 1
        last_visit_col = header.index("Last Visit") + 1
        total_calc_col = header.index("Total Calculations") + 1
        last_calc_col = header.index("Last Calculation") + 1
    except ValueError:
        return

    for row_idx, row in enumerate(rows[1:], start=2):
        if len(row) >= id_col and row[id_col - 1] == customer.get("Customer ID"):
            sheet.update_cell(row_idx, last_visit_col, _now_str())
            current_count = 0
            if len(row) >= total_calc_col:
                try:
                    current_count = int(float(row[total_calc_col - 1] or 0))
                except (ValueError, TypeError):
                    current_count = 0
            sheet.update_cell(row_idx, total_calc_col, current_count + (1 if calculation_id else 0))
            if calculation_id:
                sheet.update_cell(row_idx, last_calc_col, calculation_id)
            break


def record_calculation(customer: dict, result: dict) -> str:
    calculation_id = f"CALC-{dt.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    calc_sheet = get_worksheet("Calculations", CALCULATIONS_HEADERS)

    row = [
        calculation_id,
        _now_str(),
        customer.get("Customer ID", ""),
        customer.get("Email", ""),
        result["model_id"],
        result["fabric_type"],
        result["calculation_type"],
        result["order_qty"],
        result["rack_length"],
        result["rack_length_unit"],
        result.get("fabric_width", ""),
        result.get("gsm", ""),
        result["pieces_per_rack"],
        result["insurance_pct"],
        result["unit_price"],
        result["net_per_piece"],
        result["net_total"],
        result["insurance_qty"],
        result["recommended_purchase"],
        result["total_cost"],
        result["cost_per_garment"],
    ]
    calc_sheet.append_row(row, value_input_option="USER_ENTERED")

    update_customer_activity(customer, calculation_id)

    events = get_worksheet("Events", EVENTS_HEADERS)
    events.append_row(
        [
            f"EVT-{uuid.uuid4().hex[:10].upper()}",
            _now_str(),
            customer.get("Customer ID", ""),
            customer.get("Email", ""),
            "Calculation Completed",
            f"{result['calculation_type']} | {calculation_id}",
        ],
        value_input_option="USER_ENTERED",
    )

    return calculation_id


# ==========================================================
# 4) Validation helpers
# ==========================================================
def normalize_email(value: str) -> str:
    return value.strip().lower()


def valid_email(value: str) -> bool:
    pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    return bool(re.match(pattern, normalize_email(value)))


def normalize_phone(value: str) -> str:
    return re.sub(r"\D", "", value)


def valid_phone(value: str) -> bool:
    digits = normalize_phone(value)
    return 10 <= len(digits) <= 15


def safe_float(value: float) -> float:
    return float(value or 0.0)


def render_print_report(customer: dict, result: dict, calculation_id: str) -> None:
    """Render a compact, branded report that is formatted for browser printing."""
    is_knit = result["fabric_type"] == "تريكو"
    piece_value = result["piece_display_value"]
    piece_unit = result["piece_display_unit"]
    total_unit = result["total_display_unit"]
    insurance_unit = result["insurance_display_unit"]
    purchase_unit = result["purchase_display_unit"]
    st.markdown(
        f"""
        <div class="print-actions">
            <a href="#" onclick="window.print(); return false;" style="display:inline-block;padding:10px 18px;border-radius:9px;background:#d4af37;color:#0b0d10;text-decoration:none;font-weight:800;font-size:13px;">🖨️ طباعة تقرير الاستهلاك</a>
        </div>
        <div class="print-report">
          <div class="print-inner">
            <div class="print-head">
              <div>
                <div class="print-brand">ABDELWAHAB GARMENTS</div>
                <div class="print-title">تقرير استهلاك القماش</div>
              </div>
              <div class="print-meta">
                رقم التقرير: {calculation_id}<br>
                التاريخ: {result['calculation_date']}
              </div>
            </div>

            <div class="print-section-title">بيانات الموديل والقماش</div>
            <table class="print-table">
              <tr><th>رقم / اسم الموديل</th><td>{result['model_id']}</td><th>نوع القماش</th><td>{result['fabric_type']}</td></tr>
              <tr><th>العميل</th><td>{customer.get('Factory / Brand','')}</td><th>المستخدم</th><td>{customer.get('Full Name','')}</td></tr>
            </table>

            <div class="print-section-title">بيانات التشغيل</div>
            <table class="print-table">
              <tr><th>كمية الأمر</th><td>{result['order_qty']:,} قطعة</td><th>طول الراق الفعلي</th><td>{result['rack_length']:,.2f} {result['rack_length_unit']}</td></tr>
              <tr><th>عدد القطع في الراق</th><td>{result['pieces_per_rack']:,} قطعة</td><th>عرض القماش</th><td>{result.get('fabric_width_display','—')}</td></tr>
              {'<tr><th>وزن المتر المربع (GSM)</th><td>'+f"{result['gsm']:,.0f}"+'</td><th>نسبة التأمين</th><td>'+f"{result['insurance_pct']:.1f}%"+'</td></tr>' if is_knit else '<tr><th>نسبة التأمين</th><td>'+f"{result['insurance_pct']:.1f}%"+'</td><th>سعر المتر</th><td>'+f"{result['unit_price']:,.2f} جنيه / متر"+'</td></tr>'}
              {'<tr><th>سعر الكيلو</th><td>'+f"{result['unit_price']:,.2f} جنيه / كجم"+'</td><th>طريقة الحساب</th><td>من واقع الراق الفعلي</td></tr>' if is_knit else '<tr><th>طريقة الحساب</th><td>من واقع الراق الفعلي</td><th>وحدة الاستهلاك</th><td>متر</td></tr>'}
            </table>

            <div class="print-section-title">نتائج الاستهلاك</div>
            <table class="print-table">
              <tr><th>الاستهلاك الصافي للقطعة</th><td>{piece_value:,.4f} {piece_unit}</td><th>إجمالي الاستهلاك الصافي</th><td>{result['net_total']:,.2f} {total_unit}</td></tr>
              <tr><th>كمية التأمين</th><td>{result['insurance_qty']:,.2f} {insurance_unit}</td><th>كمية الشراء المقترحة</th><td>{result['recommended_purchase']:,.2f} {purchase_unit}</td></tr>
              <tr><th>إجمالي تكلفة القماش</th><td>{result['total_cost']:,.2f} جنيه</td><th>تكلفة القماش / القطعة</th><td>{result['cost_per_garment']:,.2f} جنيه</td></tr>
            </table>

            <div class="print-total">الكمية المقترحة للشراء: {result['recommended_purchase']:,.2f} {purchase_unit}</div>

            <div class="print-footer">
              ABDELWAHAB GARMENTS · abdelwahabgarments.com · abdelwahab.garments@gmail.com · Facebook: Abdelwahab Garments
              <br>هذا التقرير صادر من Consumption Model ويُستخدم كمرجع للحساب المبني على بيانات الراق الفعلي المدخلة من المستخدم.
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# 5) Header
# ==========================================================
st.markdown(
    """
    <div class="brand-wrap">
        <div class="brand-row">
            <div>
                <div class="eyebrow">GARMENTS PLANNING TOOL</div>
                <div class="brand-title">ABDELWAHAB GARMENTS</div>
                <div class="brand-subtitle">Consumption Model — نموذج احترافي لحساب استهلاك الأقمشة من واقع الراق الفعلي</div>
            </div>
            <div class="system-status"><span>●</span> SYSTEM ONLINE</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# 6) Session state
# ==========================================================
for key, default in {
    "authenticated": False,
    "customer": None,
    "login_error": "",
    "registration_email": "",
    "last_calculation_id": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ==========================================================
# 7) Authentication / registration flow
# ==========================================================
if not st.session_state["authenticated"]:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">ACCESS</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">ابدأ باستخدام Consumption Model</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="login-hint">اكتب بريدك الإلكتروني فقط. إذا كنت مستخدمًا مسجلًا ستدخل مباشرة، وإذا كانت هذه أول مرة فسنطلب بياناتك مرة واحدة فقط لإنشاء ملفك.</div>',
        unsafe_allow_html=True,
    )

    with st.form("email_lookup_form"):
        email = st.text_input("البريد الإلكتروني", placeholder="example@factory.com")
        continue_btn = st.form_submit_button("متابعة")

    if continue_btn:
        if not valid_email(email):
            st.error("يرجى إدخال بريد إلكتروني صحيح.")
        else:
            normalized = normalize_email(email)
            st.session_state["login_error"] = ""
            st.session_state["registration_email"] = normalized
            try:
                existing_customer = find_customer_by_email(normalized)
                if existing_customer:
                    st.session_state["customer"] = existing_customer
                    st.session_state["authenticated"] = True
                    record_visit(existing_customer, "Login")
                    update_customer_activity(existing_customer)
                    st.rerun()
                else:
                    st.rerun()
            except Exception as exc:
                st.session_state["login_error"] = str(exc)

    if st.session_state["login_error"]:
        st.error("تعذر الوصول إلى قاعدة البيانات حاليًا. راجع إعدادات Google Sheets ثم حاول مرة أخرى.")

    if st.session_state["registration_email"]:
        st.markdown("---")
        st.markdown('<div class="section-kicker">NEW USER</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">أنشئ ملفك للمرة الأولى</div>', unsafe_allow_html=True)
        st.caption(f"سيتم استخدام البريد: {st.session_state['registration_email']}")

        with st.form("registration_form"):
            c1, c2 = st.columns(2)
            with c1:
                full_name = st.text_input("الاسم بالكامل *")
                phone = st.text_input("رقم WhatsApp *", placeholder="01xxxxxxxxx")
                country = st.text_input("الدولة *", value="مصر")
                governorate = st.text_input("المحافظة / المنطقة *")
            with c2:
                factory_brand = st.text_input("اسم المصنع أو البراند *")
                job_title = st.selectbox(
                    "الوظيفة / المسمى الوظيفي *",
                    [
                        "اختر المسمى الوظيفي...",
                        "صاحب مصنع / البراند",
                        "مدير إنتاج",
                        "مدير تخطيط ومتابعة",
                        "مدير جودة",
                        "مهندس تخطيط ومتابعة",
                        "مصمم / باترونيست",
                        "مسؤول مشتريات",
                        "أخرى",
                    ],
                )
                newsletter = st.checkbox(
                    "الاشتراك في النشرة والتحديثات التشغيلية",
                    value=False,
                )

            create_btn = st.form_submit_button("إنشاء الحساب والبدء")

        if create_btn:
            if not full_name.strip() or not phone.strip() or not country.strip() or not governorate.strip() or not factory_brand.strip():
                st.error("يرجى استكمال جميع الحقول المطلوبة.")
            elif job_title == "اختر المسمى الوظيفي...":
                st.error("يرجى اختيار المسمى الوظيفي.")
            elif not valid_phone(phone):
                st.error("يرجى إدخال رقم WhatsApp صحيح.")
            else:
                customer_data = {
                    "name": full_name.strip(),
                    "email": st.session_state["registration_email"],
                    "phone": normalize_phone(phone),
                    "country": country.strip(),
                    "governorate": governorate.strip(),
                    "factory_brand": factory_brand.strip(),
                    "job_title": job_title,
                    "newsletter": newsletter,
                }
                try:
                    customer = create_customer(customer_data)
                    record_visit(customer, "Registration")
                    update_customer_activity(customer)
                    st.session_state["customer"] = customer
                    st.session_state["authenticated"] = True
                    st.session_state["registration_email"] = ""
                    st.rerun()
                except Exception:
                    st.error("تعذر حفظ بياناتك حاليًا. لا يتم فتح الحاسبة حتى يتم تسجيل البيانات بنجاح.")

    st.markdown('</div>', unsafe_allow_html=True)

else:
    customer = st.session_state["customer"] or {}

    # ======================================================
    # 8) Logged-in user header
    # ======================================================
    st.markdown('<div class="panel panel-tight">', unsafe_allow_html=True)
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown(
            f"""
            <div class="welcome-card">
                <div class="welcome-title">أهلًا بك، {customer.get('Full Name', 'مستخدم')}</div>
                <div class="welcome-meta">{customer.get('Factory / Brand', '')} · {customer.get('Job Title', '')} · {customer.get('Country', '')} / {customer.get('Governorate', '')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("تسجيل الخروج"):
            st.session_state["authenticated"] = False
            st.session_state["customer"] = None
            st.session_state["last_calculation_id"] = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ======================================================
    # 9) Consumption Model
    # ======================================================
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">CONSUMPTION ENGINE</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">حاسبة الاستهلاك الفعلي من واقع الراق</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-description">أدخل بيانات الموديل والراق الفعلي. ستظهر الحاسبة المناسبة حسب نوع القماش، وتحفظ كل عملية حساب مع بيانات العميل كمرجع تشغيلي.</div>',
        unsafe_allow_html=True,
    )

    model_c1, model_c2 = st.columns(2)
    with model_c1:
        model_id = st.text_input("رقم الموديل / اسم الموديل *", placeholder="مثال: POLO-047")
    with model_c2:
        fabric_type = st.selectbox("نوع القماش *", ["تريكو", "منسوج"])

    if fabric_type == "تريكو":
        st.markdown('<div class="model-chip"><strong>01</strong> تريكو · حساب من الراق الفعلي</div>', unsafe_allow_html=True)
        with st.form("knit_form"):
            c1, c2 = st.columns(2)
            with c1:
                order_qty = st.number_input("كمية الأمر (قطعة)", min_value=1, value=1000, step=50, key="knit_qty")
                rack_length = st.number_input("طول الراق الفعلي (سم)", min_value=1.0, value=650.0, step=10.0, key="knit_rack_length")
                fabric_width = st.number_input("عرض القماش (سم)", min_value=1.0, value=180.0, step=5.0, key="knit_width")
                gsm = st.number_input("وزن المتر المربع (GSM)", min_value=1.0, value=200.0, step=10.0, key="knit_gsm")
            with c2:
                pieces_per_rack = st.number_input("عدد القطع في الراق", min_value=1, value=10, step=1, key="knit_pieces")
                insurance_pct = st.number_input("نسبة التأمين (%)", min_value=0.0, max_value=30.0, value=5.0, step=0.5, key="knit_insurance")
                unit_price = st.number_input("سعر الكيلو (جنيه)", min_value=0.0, value=120.0, step=5.0, key="knit_price")
                st.caption("التأمين يضاف فوق الاستهلاك الصافي لتحديد كمية الشراء المقترحة.")

            calculate_knit = st.form_submit_button("حساب استهلاك التريكو")

        if calculate_knit:
            if not model_id.strip():
                st.error("يرجى إدخال رقم الموديل / اسم الموديل أولًا.")
                st.stop()
            # cm × cm × GSM → kg
            net_per_piece = (rack_length * fabric_width * gsm) / (pieces_per_rack * 10_000_000.0)
            net_total = order_qty * net_per_piece
            insurance_qty = net_total * (insurance_pct / 100.0)
            recommended_purchase = net_total + insurance_qty
            total_cost = recommended_purchase * unit_price
            cost_per_garment = total_cost / order_qty

            result = {
                "model_id": model_id.strip(),
                "fabric_type": "تريكو",
                "calculation_type": "Knitwear - Actual Rack",
                "order_qty": order_qty,
                "rack_length": rack_length,
                "rack_length_unit": "cm",
                "fabric_width": fabric_width,
                "fabric_width_display": f"{fabric_width:,.0f} سم",
                "gsm": gsm,
                "pieces_per_rack": pieces_per_rack,
                "insurance_pct": insurance_pct,
                "unit_price": unit_price,
                "net_per_piece": net_per_piece,
                "net_total": net_total,
                "insurance_qty": insurance_qty,
                "recommended_purchase": recommended_purchase,
                "total_cost": total_cost,
                "cost_per_garment": cost_per_garment,
                "piece_display_value": net_per_piece * 1000.0,
                "piece_display_unit": "جرام",
                "total_display_unit": "كجم",
                "insurance_display_unit": "كجم",
                "purchase_display_unit": "كجم",
                "price_unit": "جنيه / كجم",
                "calculation_date": _now_str(),
            }

            try:
                calculation_id = record_calculation(customer, result)
                st.session_state["last_calculation_id"] = calculation_id

                st.markdown('<div class="result-grid">', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="metric-card primary"><div class="metric-label">الاستهلاك الصافي للقطعة</div><div class="metric-value gold">{net_per_piece * 1000.0:,.1f} جرام</div></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="metric-card"><div class="metric-label">إجمالي الاستهلاك الصافي</div><div class="metric-value">{net_total:,.2f} كجم</div></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="metric-card"><div class="metric-label">كمية التأمين</div><div class="metric-value">{insurance_qty:,.2f} كجم</div><div class="metric-sub">{insurance_pct:.1f}%</div></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="metric-card primary"><div class="metric-label">كمية الشراء المقترحة</div><div class="metric-value gold">{recommended_purchase:,.2f} كجم</div></div>',
                    unsafe_allow_html=True,
                )
                st.markdown('</div>', unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(
                        f'<div class="metric-card"><div class="metric-label">إجمالي تكلفة القماش</div><div class="metric-value">{total_cost:,.2f} جنيه</div></div>',
                        unsafe_allow_html=True,
                    )
                with c2:
                    st.markdown(
                        f'<div class="metric-card"><div class="metric-label">نصيب القطعة من تكلفة القماش</div><div class="metric-value">{cost_per_garment:,.2f} جنيه</div></div>',
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    '<div class="formula-note"><strong>منهج الحساب:</strong> مساحة الراق الفعلي × GSM ÷ عدد القطع في الراق = الوزن الصافي، ثم تضاف نسبة التأمين لتحديد كمية الشراء المقترحة.</div>',
                    unsafe_allow_html=True,
                )
                st.success(f"تم حفظ العملية بنجاح — Calculation ID: {calculation_id}")
                render_print_report(customer, result, calculation_id)
            except Exception:
                st.error("تم إجراء الحساب، لكن تعذر حفظ العملية في قاعدة البيانات. لم نعتبر العملية محفوظة.")

    else:
        st.markdown('<div class="model-chip"><strong>02</strong> منسوج · حساب من الراق الفعلي</div>', unsafe_allow_html=True)
        with st.form("woven_form"):
            c1, c2 = st.columns(2)
            with c1:
                order_qty_w = st.number_input("كمية الأمر (قطعة)", min_value=1, value=1000, step=50, key="woven_qty")
                rack_length_m = st.number_input("طول الراق الفعلي (متر)", min_value=0.1, value=12.5, step=0.5, key="woven_rack_length")
                fabric_width_w = st.number_input("عرض القماش (سم)", min_value=1.0, value=150.0, step=5.0, key="woven_width")
            with c2:
                pieces_per_rack_w = st.number_input("عدد القطع في الراق", min_value=1, value=8, step=1, key="woven_pieces")
                insurance_pct_w = st.number_input("نسبة التأمين (%)", min_value=0.0, max_value=30.0, value=5.0, step=0.5, key="woven_insurance")
                unit_price_w = st.number_input("سعر المتر (جنيه)", min_value=0.0, value=90.0, step=5.0, key="woven_price")
            st.caption("طول الراق الفعلي هو طول الـ lay المستخدم فعليًا، وعدد القطع هو الناتج الفعلي للراق.")

            calculate_woven = st.form_submit_button("حساب استهلاك المنسوج")

        if calculate_woven:
            if not model_id.strip():
                st.error("يرجى إدخال رقم الموديل / اسم الموديل أولًا.")
                st.stop()
            net_per_piece_m = rack_length_m / pieces_per_rack_w
            net_total_m = order_qty_w * net_per_piece_m
            insurance_qty_m = net_total_m * (insurance_pct_w / 100.0)
            recommended_purchase_m = net_total_m + insurance_qty_m
            total_cost_w = recommended_purchase_m * unit_price_w
            cost_per_garment_w = total_cost_w / order_qty_w

            result = {
                "model_id": model_id.strip(),
                "fabric_type": "منسوج",
                "calculation_type": "Woven - Actual Rack",
                "order_qty": order_qty_w,
                "rack_length": rack_length_m,
                "rack_length_unit": "m",
                "fabric_width": fabric_width_w,
                "fabric_width_display": f"{fabric_width_w:,.0f} سم",
                "gsm": "",
                "pieces_per_rack": pieces_per_rack_w,
                "insurance_pct": insurance_pct_w,
                "unit_price": unit_price_w,
                "net_per_piece": net_per_piece_m,
                "net_total": net_total_m,
                "insurance_qty": insurance_qty_m,
                "recommended_purchase": recommended_purchase_m,
                "total_cost": total_cost_w,
                "cost_per_garment": cost_per_garment_w,
                "piece_display_value": net_per_piece_m,
                "piece_display_unit": "متر",
                "total_display_unit": "متر",
                "insurance_display_unit": "متر",
                "purchase_display_unit": "متر",
                "price_unit": "جنيه / متر",
                "calculation_date": _now_str(),
            }

            try:
                calculation_id = record_calculation(customer, result)
                st.session_state["last_calculation_id"] = calculation_id

                st.markdown('<div class="result-grid">', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="metric-card primary"><div class="metric-label">الاستهلاك الصافي للقطعة</div><div class="metric-value gold">{net_per_piece_m:,.4f} متر</div></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="metric-card"><div class="metric-label">إجمالي الاستهلاك الصافي</div><div class="metric-value">{net_total_m:,.2f} متر</div></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="metric-card"><div class="metric-label">كمية التأمين</div><div class="metric-value">{insurance_qty_m:,.2f} متر</div><div class="metric-sub">{insurance_pct_w:.1f}%</div></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="metric-card primary"><div class="metric-label">كمية الشراء المقترحة</div><div class="metric-value gold">{recommended_purchase_m:,.2f} متر</div></div>',
                    unsafe_allow_html=True,
                )
                st.markdown('</div>', unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(
                        f'<div class="metric-card"><div class="metric-label">إجمالي تكلفة القماش</div><div class="metric-value">{total_cost_w:,.2f} جنيه</div></div>',
                        unsafe_allow_html=True,
                    )
                with c2:
                    st.markdown(
                        f'<div class="metric-card"><div class="metric-label">نصيب القطعة من تكلفة القماش</div><div class="metric-value">{cost_per_garment_w:,.2f} جنيه</div></div>',
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    '<div class="formula-note"><strong>منهج الحساب:</strong> طول الراق الفعلي ÷ عدد القطع في الراق = الاستهلاك الصافي للقطعة، ثم تضاف نسبة التأمين لتحديد كمية الشراء المقترحة.</div>',
                    unsafe_allow_html=True,
                )
                st.success(f"تم حفظ العملية بنجاح — Calculation ID: {calculation_id}")
                render_print_report(customer, result, calculation_id)
            except Exception:
                st.error("تم إجراء الحساب، لكن تعذر حفظ العملية في قاعدة البيانات. لم نعتبر العملية محفوظة.")

    st.markdown(
        '<div class="trust-note">ملاحظة تشغيلية: النتائج تعتمد على البيانات الفعلية التي تدخلها عن الراق. التأمين هو هامش إضافي للشراء وليس هو نفسه فاقد الـ marker أو الهدر الفني للقص.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================================
# 10) Footer
# ==========================================================
st.markdown(
    """
    <div class="footer">
        <div class="footer-brand">ABDELWAHAB GARMENTS</div>
        <div class="footer-copy">نساعد مصانع الملابس الصغيرة والمتوسطة على الانتقال من الإدارة بالإحساس إلى الإدارة بالأرقام.</div>
        <div class="footer-copy">abdelwahabgarments.com · abdelwahab.garments@gmail.com · Facebook: Abdelwahab Garments</div>
        <div class="footer-copy">© 2026 Mohamed Abdelwahab — Consumption Model</div>
    </div>
    """,
    unsafe_allow_html=True,
)
