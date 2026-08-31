import datetime as dt
import re
import uuid
import html

import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import streamlit.components.v1 as components

try:
    from weasyprint import HTML
except Exception:
    HTML = None


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
            min-height: 68px;
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
                min-height: 62px;
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
    "Client Type",
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
    "Fabric Name",
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
    """Return a worksheet and add any missing headers without breaking existing data."""
    spreadsheet = get_google_sheet()
    try:
        worksheet = spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=name,
            rows=1000,
            cols=max(len(headers), 10),
        )
        worksheet.update("A1", [headers], value_input_option="USER_ENTERED")
        return worksheet

    existing_headers = worksheet.row_values(1)
    if not existing_headers:
        worksheet.update("A1", [headers], value_input_option="USER_ENTERED")
        return worksheet

    for header in headers:
        if header not in existing_headers:
            next_col = len(existing_headers) + 1
            worksheet.update_cell(1, next_col, header)
            existing_headers.append(header)
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
    customer = {
        "Customer ID": customer_id,
        "Registration Date": now,
        "Last Visit": now,
        "Full Name": customer_data["name"],
        "Email": customer_data["email"],
        "WhatsApp": customer_data["phone"],
        "Country": customer_data["country"],
        "Governorate": customer_data["governorate"],
        "Factory / Brand": customer_data["factory_brand"],
        "Client Type": customer_data["client_type"],
        "Job Title": customer_data["job_title"],
        "Newsletter": "نعم" if customer_data["newsletter"] else "لا",
        "Lead Source": "Consumption Model",
        "Total Calculations": 0,
        "Last Calculation": "",
        "Status": "Active",
    }

    sheet = get_worksheet("Customers", CUSTOMERS_HEADERS)
    sheet_headers = sheet.row_values(1)
    sheet.append_row([customer.get(h, "") for h in sheet_headers], value_input_option="USER_ENTERED")
    return customer


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

    calc_data = {
        "Calculation ID": calculation_id,
        "Date": _now_str(),
        "Customer ID": customer.get("Customer ID", ""),
        "Email": customer.get("Email", ""),
        "Model ID / Name": result["model_id"],
        "Fabric Type": result["fabric_type"],
        "Fabric Name": result.get("fabric_name", ""),
        "Calculation Type": result["calculation_type"],
        "Order Quantity": result["order_qty"],
        "Rack Length": result["rack_length"],
        "Rack Length Unit": result["rack_length_unit"],
        "Fabric Width": result.get("fabric_width", ""),
        "GSM": result.get("gsm", ""),
        "Pieces / Rack": result["pieces_per_rack"],
        "Insurance %": result["insurance_pct"],
        "Unit Price": result["unit_price"],
        "Net Consumption / Piece": result["net_per_piece"],
        "Net Requirement": result["net_total"],
        "Insurance Quantity": result["insurance_qty"],
        "Recommended Purchase": result["recommended_purchase"],
        "Total Cost": result["total_cost"],
        "Cost / Garment": result["cost_per_garment"],
    }

    calc_headers = calc_sheet.row_values(1)
    calc_sheet.append_row([calc_data.get(h, "") for h in calc_headers], value_input_option="USER_ENTERED")
    update_customer_activity(customer, calculation_id)

    events = get_worksheet("Events", EVENTS_HEADERS)
    event_headers = events.row_values(1)
    event_data = {
        "Event ID": f"EVT-{uuid.uuid4().hex[:10].upper()}",
        "Date": _now_str(),
        "Customer ID": customer.get("Customer ID", ""),
        "Email": customer.get("Email", ""),
        "Event": "Calculation Completed",
        "Details": f"{result['calculation_type']} | {calculation_id}",
    }
    events.append_row([event_data.get(h, "") for h in event_headers], value_input_option="USER_ENTERED")
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


def build_report_html(customer: dict, result: dict, calculation_id: str) -> str:
    """Build a clean A4 report used by both print preview and PDF export."""
    esc = lambda v: html.escape(str(v if v is not None else ""))
    is_knit = result["fabric_type"] == "تريكو"
    fabric_name = result.get("fabric_name") or "—"

    if is_knit:
        inputs_rows = f"""
        <tr><th>كمية الأمر</th><td>{result['order_qty']:,} قطعة</td><th>طول الراق الفعلي</th><td>{result['rack_length']:,.2f} سم</td></tr>
        <tr><th>عدد القطع</th><td>{result['pieces_per_rack']:,} قطعة</td><th>عرض القماش</th><td>{result['fabric_width']:,.0f} سم</td></tr>
        <tr><th>وزن المتر المربع (GSM)</th><td>{result['gsm']:,.0f}</td><th>نسبة التأمين</th><td>{result['insurance_pct']:.1f}%</td></tr>
        <tr><th>سعر الكيلو</th><td>{result['unit_price']:,.2f} جنيه / كجم</td><th>طريقة الحساب</th><td>حساب دقيق بالبيانات المدخلة</td></tr>
        """
        consumption_rows = f"""
        <tr><th>الاستهلاك الصافي للقطعة</th><td>{result['piece_display_value']:,.1f} جرام</td><th>إجمالي الاستهلاك الصافي</th><td>{result['net_total']:,.2f} كجم</td></tr>
        <tr><th>كمية التأمين</th><td>{result['insurance_qty']:,.2f} كجم</td><th>كمية الشراء المقترحة</th><td>{result['recommended_purchase']:,.2f} كجم</td></tr>
        """
    else:
        inputs_rows = f"""
        <tr><th>كمية الأمر</th><td>{result['order_qty']:,} قطعة</td><th>طول الراق الفعلي</th><td>{result['rack_length']:,.2f} متر</td></tr>
        <tr><th>عدد القطع</th><td>{result['pieces_per_rack']:,} قطعة</td><th>نسبة التأمين</th><td>{result['insurance_pct']:.1f}%</td></tr>
        <tr><th>سعر المتر</th><td>{result['unit_price']:,.2f} جنيه / متر</td><th>طريقة الحساب</th><td>حساب دقيق بالبيانات المدخلة</td></tr>
        """
        consumption_rows = f"""
        <tr><th>الاستهلاك الصافي للقطعة</th><td>{result['piece_display_value']:,.4f} متر</td><th>إجمالي الاستهلاك الصافي</th><td>{result['net_total']:,.2f} متر</td></tr>
        <tr><th>كمية التأمين</th><td>{result['insurance_qty']:,.2f} متر</td><th>كمية الشراء المقترحة</th><td>{result['recommended_purchase']:,.2f} متر</td></tr>
        """

    return f"""
<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<style>
@page {{ size:A4; margin:11mm; }}
* {{ box-sizing:border-box; }}
body {{ font-family:'Noto Sans Arabic','Noto Sans',Arial,sans-serif; margin:0; color:#1b1e23; background:#fff; direction:rtl; }}
.report {{ position:relative; overflow:hidden; min-height:260mm; padding:4mm; }}
.report:before {{ content:'ABDELWAHAB GARMENTS'; position:absolute; top:45%; left:5%; transform:rotate(-24deg); font-size:38px; font-weight:800; letter-spacing:2px; color:rgba(110,90,35,.055); white-space:nowrap; z-index:0; }}
.content {{ position:relative; z-index:1; }}
.header {{ display:flex; justify-content:space-between; gap:18px; align-items:flex-start; border-bottom:2px solid #d4af37; padding-bottom:12px; }}
.brand {{ font-size:21px; font-weight:800; color:#8b6a06; letter-spacing:.8px; }}
.title {{ font-size:15px; font-weight:800; margin-top:3px; }}
.meta {{ font-size:10px; color:#666; line-height:1.75; text-align:left; }}
h2 {{ font-size:12px; color:#8b6a06; margin:15px 0 7px; }}
table {{ width:100%; border-collapse:collapse; font-size:10px; }}
th,td {{ border:1px solid #dfdfdf; padding:6px 7px; vertical-align:middle; }}
th {{ width:20%; background:#f7f7f7; font-weight:700; }}
td {{ width:30%; }}
.result {{ margin-top:10px; border:1px solid #d4af37; border-radius:7px; padding:9px; }}
.result-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:7px; }}
.result-box {{ border:1px solid #e5e5e5; border-radius:6px; padding:8px; }}
.result-label {{ font-size:9px; color:#727272; }}
.result-value {{ font-size:15px; font-weight:800; margin-top:3px; }}
.result-main {{ border-color:#d4af37; background:#fffaf0; }}
.total {{ margin-top:9px; text-align:center; padding:9px; border:2px solid #d4af37; border-radius:7px; font-size:13px; font-weight:800; }}
.footer {{ margin-top:18px; padding-top:9px; border-top:1px solid #ddd; font-size:9px; color:#666; line-height:1.8; text-align:center; }}
.print-button {{ display:inline-block; margin-bottom:10px; padding:9px 14px; border-radius:7px; background:#d4af37; color:#111; text-decoration:none; font-size:12px; font-weight:800; border:0; cursor:pointer; }}
@media print {{ .print-button {{ display:none; }} body {{ background:#fff; }} .report {{ min-height:auto; }} }}
</style>
</head>
<body>
<div class="report">
<div class="content">
<button class="print-button" onclick="window.print()">🖨 طباعة التقرير</button>
<div class="header">
<div>
<div class="brand">ABDELWAHAB GARMENTS</div>
<div class="title">تقرير استهلاك القماش</div>
</div>
<div class="meta">رقم التقرير: {esc(calculation_id)}<br>التاريخ: {esc(result['calculation_date'])}</div>
</div>

<h2>بيانات الموديل والخامة</h2>
<table>
<tr><th>رقم / اسم الموديل</th><td>{esc(result['model_id'])}</td><th>نوع القماش</th><td>{esc(result['fabric_type'])}</td></tr>
<tr><th>اسم الخامة</th><td>{esc(fabric_name)}</td><th>العميل</th><td>{esc(customer.get('Factory / Brand',''))}</td></tr>
<tr><th>المستخدم</th><td>{esc(customer.get('Full Name',''))}</td><th>صفة العميل</th><td>{esc(customer.get('Client Type',''))}</td></tr>
</table>

<h2>بيانات التشغيل</h2>
<table>{inputs_rows}</table>

<h2>نتائج الاستهلاك</h2>
<div class="result">
<div class="result-grid">
<div class="result-box result-main"><div class="result-label">الاستهلاك الصافي للقطعة</div><div class="result-value">{result['piece_display_value']:,.1f} {result['piece_display_unit'] if is_knit else result['piece_display_unit']}</div></div>
<div class="result-box"><div class="result-label">إجمالي الاستهلاك الصافي</div><div class="result-value">{result['net_total']:,.2f} {result['total_display_unit']}</div></div>
<div class="result-box"><div class="result-label">كمية التأمين</div><div class="result-value">{result['insurance_qty']:,.2f} {result['insurance_display_unit']}</div></div>
<div class="result-box result-main"><div class="result-label">كمية الشراء المقترحة</div><div class="result-value">{result['recommended_purchase']:,.2f} {result['purchase_display_unit']}</div></div>
</div>
</div>

<h2>التكلفة</h2>
<table>
<tr><th>سعر الوحدة</th><td>{result['unit_price']:,.2f} {result['price_unit']}</td><th>إجمالي تكلفة القماش</th><td>{result['total_cost']:,.2f} جنيه</td></tr>
<tr><th>تكلفة القماش / القطعة</th><td>{result['cost_per_garment']:,.2f} جنيه</td><th>نسبة التأمين</th><td>{result['insurance_pct']:.1f}%</td></tr>
</table>
<div class="total">الكمية المقترحة للشراء: {result['recommended_purchase']:,.2f} {result['purchase_display_unit']}</div>

<div class="footer">
<strong>ABDELWAHAB GARMENTS</strong><br>
abdelwahabgarments.com · abdelwahab.garments@gmail.com · Facebook: Abdelwahab Garments
<br>هذا التقرير صادر من Consumption Model بناءً على بيانات التشغيل المدخلة وحُفظ برقم مرجعي {esc(calculation_id)}.
</div>
</div>
</div>
</body>
</html>
"""


def make_pdf(report_html: str):
    """Return PDF bytes using WeasyPrint when available."""
    if HTML is None:
        return None
    return HTML(string=report_html).write_pdf()


def render_print_report(customer: dict, result: dict, calculation_id: str) -> None:
    report_html = build_report_html(customer, result, calculation_id)
    pdf_bytes = make_pdf(report_html)

    c1, c2 = st.columns(2)
    with c1:
        # Actual print action is inside a dedicated print-ready document.
        st.markdown("**التقرير الجاهز للطباعة**")
    with c2:
        if pdf_bytes:
            st.download_button(
                "⬇️ تحميل التقرير PDF",
                data=pdf_bytes,
                file_name=f"{calculation_id}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.warning("تعذر تجهيز PDF لأن مكتبة إنشاء PDF غير متاحة في بيئة التشغيل.")

    components.html(report_html, height=930, scrolling=True)


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
                <div class="brand-subtitle">Consumption Model — نموذج احترافي لحساب استهلاك الأقمشة</div>
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
                client_type = st.selectbox(
                    "صفة العميل *",
                    [
                        "اختر الصفة...",
                        "صاحب مصنع",
                        "صاحب براند",
                        "موظف / مدير داخل مصنع أو براند",
                        "استشاري / مقدم خدمة",
                        "أخرى",
                    ],
                )
                job_title = st.selectbox(
                    "الوظيفة / المسمى الوظيفي *",
                    [
                        "اختر المسمى الوظيفي...",
                        "مدير إنتاج",
                        "مدير تخطيط ومتابعة",
                        "مدير جودة",
                        "مهندس تخطيط ومتابعة",
                        "مصمم / باترونيست",
                        "مسؤول مشتريات",
                        "مالك / مؤسس",
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
            elif client_type == "اختر الصفة...":
                st.error("يرجى اختيار صفة العميل.")
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
                    "client_type": client_type,
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
                <div class="welcome-meta">{customer.get('Factory / Brand', '')} · {customer.get('Client Type', '')} · {customer.get('Job Title', '')} · {customer.get('Country', '')} / {customer.get('Governorate', '')}</div>
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
    st.markdown('<div class="section-title">حاسبة استهلاك الأقمشة</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-description">أدخل بيانات الموديل والخامة وبيانات التشغيل. ستظهر طريقة الحساب المناسبة حسب نوع القماش، وتحفظ كل عملية حساب مع بيانات العميل كمرجع تشغيلي.</div>',
        unsafe_allow_html=True,
    )

    model_c1, model_c2 = st.columns(2)
    with model_c1:
        model_id = st.text_input("رقم الموديل / اسم الموديل", placeholder="مثال: POLO-047 (اختياري)")
    with model_c2:
        fabric_type = st.selectbox("نوع القماش *", ["تريكو", "منسوج"])
    fabric_name = st.text_input("اسم الخامة (English)", placeholder="Example: Jersey / Denim", help="حقل اختياري لتعريف الخامة مثل Jersey أو Denim.")

    if fabric_type == "تريكو":
        st.markdown('<div class="model-chip"><strong>01</strong> تريكو · حساب دقيق</div>', unsafe_allow_html=True)
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
                "fabric_name": fabric_name.strip(),
                "calculation_type": "Knitwear - Accurate",
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
        st.markdown('<div class="model-chip"><strong>02</strong> منسوج · حساب دقيق</div>', unsafe_allow_html=True)
        with st.form("woven_form"):
            c1, c2 = st.columns(2)
            with c1:
                order_qty_w = st.number_input("كمية الأمر (قطعة)", min_value=1, value=1000, step=50, key="woven_qty")
                rack_length_m = st.number_input("طول الراق الفعلي (متر)", min_value=0.1, value=12.5, step=0.5, key="woven_rack_length")
            with c2:
                pieces_per_rack_w = st.number_input("عدد القطع في الراق", min_value=1, value=8, step=1, key="woven_pieces")
                insurance_pct_w = st.number_input("نسبة التأمين (%)", min_value=0.0, max_value=30.0, value=5.0, step=0.5, key="woven_insurance")
                unit_price_w = st.number_input("سعر المتر (جنيه)", min_value=0.0, value=90.0, step=5.0, key="woven_price")
            st.caption("طول الراق الفعلي هو طول الـ lay المستخدم فعليًا، وعدد القطع هو الناتج الفعلي لكل راق.")

            calculate_woven = st.form_submit_button("حساب استهلاك المنسوج")

        if calculate_woven:
            net_per_piece_m = rack_length_m / pieces_per_rack_w
            net_total_m = order_qty_w * net_per_piece_m
            insurance_qty_m = net_total_m * (insurance_pct_w / 100.0)
            recommended_purchase_m = net_total_m + insurance_qty_m
            total_cost_w = recommended_purchase_m * unit_price_w
            cost_per_garment_w = total_cost_w / order_qty_w

            result = {
                "model_id": model_id.strip(),
                "fabric_type": "منسوج",
                "fabric_name": fabric_name.strip(),
                "calculation_type": "Woven - Accurate",
                "order_qty": order_qty_w,
                "rack_length": rack_length_m,
                "rack_length_unit": "m",
                "fabric_width": "",
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
        '<div class="trust-note">ملاحظة تشغيلية: النتائج تعتمد على البيانات الفعلية التي تدخلها. التأمين هو هامش إضافي للشراء وليس هو نفسه فاقد الـ marker أو الهدر الفني للقص.</div>',
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
