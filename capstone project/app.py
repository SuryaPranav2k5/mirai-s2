import os
from datetime import datetime, timedelta
import io
import json
import pandas as pd
from PIL import Image
from dotenv import load_dotenv
import streamlit as st
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="BurnRate AI | Expense Roaster & Recovery Terminal",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Category & Type Definitions ---
CATEGORIES = [
    "Housing",
    "Groceries",
    "Food & Dining",
    "Subscriptions",
    "Utilities",
    "Transport",
    "Tech & Gadgets",
    "Shopping",
    "Healthcare",
    "Entertainment",
    "Other"
]

EXPENSE_TYPES = ["Essential", "Discretionary"]


# --- Session State Architecture ---
def init_session_state():
    """Initializes and persists all session state variables."""
    if "transactions_df" not in st.session_state:
        st.session_state.transactions_df = pd.DataFrame(
            columns=["Date", "Category", "Description", "Amount", "Type"]
        )
    
    if "monthly_income" not in st.session_state:
        st.session_state.monthly_income = 96400.0

    if "monthly_budget" not in st.session_state:
        st.session_state.monthly_budget = 65000.0

    if "roast_result" not in st.session_state:
        st.session_state.roast_result = None

    if "recovery_plan" not in st.session_state:
        st.session_state.recovery_plan = None

    if "receipt_scans" not in st.session_state:
        st.session_state.receipt_scans = []


def get_mock_transactions() -> pd.DataFrame:
    """Generates realistic mock transaction data in INR for testing."""
    today = datetime.today()
    mock_data = [
        {"Date": (today - timedelta(days=1)).strftime("%Y-%m-%d"), "Category": "Housing", "Description": "Apartment Rent & Maintenance", "Amount": 28000.0, "Type": "Essential"},
        {"Date": (today - timedelta(days=2)).strftime("%Y-%m-%d"), "Category": "Groceries", "Description": "Blinkit & Nature's Basket Essentials", "Amount": 4250.0, "Type": "Essential"},
        {"Date": (today - timedelta(days=3)).strftime("%Y-%m-%d"), "Category": "Food & Dining", "Description": "Third Wave Coffee Artisan Cold Brews", "Amount": 1250.0, "Type": "Discretionary"},
        {"Date": (today - timedelta(days=4)).strftime("%Y-%m-%d"), "Category": "Food & Dining", "Description": "Late-Night Zomato Gourmet Pizza", "Amount": 1850.0, "Type": "Discretionary"},
        {"Date": (today - timedelta(days=5)).strftime("%Y-%m-%d"), "Category": "Tech & Gadgets", "Description": "Keychron Mechanical Keyboard", "Amount": 8999.0, "Type": "Discretionary"},
        {"Date": (today - timedelta(days=6)).strftime("%Y-%m-%d"), "Category": "Subscriptions", "Description": "Netflix & Spotify Premium", "Amount": 1199.0, "Type": "Discretionary"},
        {"Date": (today - timedelta(days=7)).strftime("%Y-%m-%d"), "Category": "Subscriptions", "Description": "Cult.fit Gym Annual Membership", "Amount": 3500.0, "Type": "Discretionary"},
        {"Date": (today - timedelta(days=8)).strftime("%Y-%m-%d"), "Category": "Utilities", "Description": "Jio Fiber & BESCOM Electricity Bill", "Amount": 3200.0, "Type": "Essential"},
        {"Date": (today - timedelta(days=10)).strftime("%Y-%m-%d"), "Category": "Transport", "Description": "Surge Uber Cab to Airport", "Amount": 1450.0, "Type": "Discretionary"},
        {"Date": (today - timedelta(days=12)).strftime("%Y-%m-%d"), "Category": "Shopping", "Description": "Sony Noise-Cancelling Headphones (EMI)", "Amount": 6500.0, "Type": "Discretionary"},
        {"Date": (today - timedelta(days=14)).strftime("%Y-%m-%d"), "Category": "Food & Dining", "Description": "Weekend Craft Microbrewery Bill", "Amount": 4800.0, "Type": "Discretionary"},
        {"Date": (today - timedelta(days=16)).strftime("%Y-%m-%d"), "Category": "Groceries", "Description": "Zepto Quick Supermarket Restock", "Amount": 3100.0, "Type": "Essential"},
        {"Date": (today - timedelta(days=18)).strftime("%Y-%m-%d"), "Category": "Subscriptions", "Description": "ChatGPT Plus & GitHub Copilot", "Amount": 3200.0, "Type": "Discretionary"},
    ]
    df = pd.DataFrame(mock_data)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df["Amount"] = df["Amount"].astype(float)
    return df


def process_uploaded_csv(uploaded_file) -> pd.DataFrame:
    """Parses, cleans, and standardizes an uploaded expense CSV file."""
    try:
        raw_df = pd.read_csv(uploaded_file)
        col_map = {c.lower().strip(): c for c in raw_df.columns}
        
        date_col = next((col_map[c] for c in col_map if "date" in c or "time" in c), None)
        desc_col = next((col_map[c] for c in col_map if "desc" in c or "name" in c or "item" in c or "merchant" in c), None)
        amount_col = next((col_map[c] for c in col_map if "amount" in c or "price" in c or "cost" in c or "total" in c), None)
        cat_col = next((col_map[c] for c in col_map if "cat" in c or "type" in c), None)

        standard_df = pd.DataFrame()
        
        if date_col:
            standard_df["Date"] = pd.to_datetime(raw_df[date_col], errors="coerce").dt.date
            standard_df["Date"] = standard_df["Date"].fillna(datetime.today().date())
        else:
            standard_df["Date"] = datetime.today().date()

        if cat_col:
            standard_df["Category"] = raw_df[cat_col].astype(str).str.title()
        else:
            standard_df["Category"] = "Other"

        if desc_col:
            standard_df["Description"] = raw_df[desc_col].astype(str)
        else:
            standard_df["Description"] = "Expense Item"

        if amount_col:
            clean_amt = raw_df[amount_col].astype(str).str.replace(r'[\$,₹,€,£,Rs\.,rs,INR,inr]', '', regex=True).str.replace(',', '').str.strip()
            standard_df["Amount"] = pd.to_numeric(clean_amt, errors="coerce").abs().fillna(0.0)
        else:
            standard_df["Amount"] = 0.0

        essential_keywords = ["rent", "housing", "grocery", "groceries", "utility", "utilities", "electricity", "water", "health", "insurance", "medical", "bill", "maid", "cook"]
        def classify_type(row):
            text = f"{row['Category']} {row['Description']}".lower()
            if any(k in text for k in essential_keywords):
                return "Essential"
            return "Discretionary"

        standard_df["Type"] = standard_df.apply(classify_type, axis=1)

        return standard_df[["Date", "Category", "Description", "Amount", "Type"]]
    except Exception as e:
        st.error(f"Error parsing CSV file: {str(e)}")
        return pd.DataFrame(columns=["Date", "Category", "Description", "Amount", "Type"])


def scan_receipt_with_gemini(image_file, api_key_val: str) -> dict:
    """Extracts structured JSON expense data from a receipt image in INR using Gemini Vision."""
    try:
        client = genai.Client(api_key=api_key_val)
        image = Image.open(image_file)
        
        prompt = (
            "Analyze this receipt image and extract the following details in pure JSON format:\n"
            "{\n"
            '  "merchant": "Name of store / merchant",\n'
            '  "date": "YYYY-MM-DD",\n'
            '  "total_amount": 0.00,\n'
            '  "category": "One of [Housing, Groceries, Food & Dining, Subscriptions, Utilities, Transport, Tech & Gadgets, Shopping, Healthcare, Entertainment, Other]",\n'
            '  "type": "Essential or Discretionary",\n'
            '  "items_summary": "Short 1-line summary of items purchased in INR (₹)"\n'
            "}\n"
            "Note: The total_amount should be a numeric float in Indian Rupees (INR ₹).\n"
            "Return ONLY the valid raw JSON object. Do not include markdown ticks or explanations."
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        result_json = json.loads(response.text.strip())
        return result_json
    except Exception as e:
        st.error(f"Receipt Vision Scan failed: {str(e)}")
        return {}


def generate_roast_and_recovery(df: pd.DataFrame, income: float, budget: float, intensity: str, target_savings: float, api_key_val: str):
    """Generates both the AI Roast and 50/30/20 Recovery Plan in INR using Gemini 2.5 Flash."""
    try:
        client = genai.Client(api_key=api_key_val)
        
        total_spend = float(df["Amount"].sum())
        essential_spend = float(df[df["Type"] == "Essential"]["Amount"].sum())
        discretionary_spend = float(df[df["Type"] == "Discretionary"]["Amount"].sum())
        discretionary_pct = (discretionary_spend / total_spend * 100) if total_spend > 0 else 0.0
        
        cat_summary = df.groupby("Category")["Amount"].sum().to_dict()
        top_items = df.sort_values(by="Amount", ascending=False).head(5)[["Description", "Amount", "Category"]].to_dict(orient="records")

        # 1. Roast Generation
        roast_prompt = f"""
You are a witty, mathematically precise, and brutally sarcastic Indian financial auditor and chartered accountant (CA / CFO).
Analyze the user's spending data in Indian Rupees (₹ / INR) and ROAST their financial habits based on the requested intensity level: {intensity}.

User Baseline Financials (in INR ₹):
- Monthly Income: ₹{income:,.2f}
- Target Monthly Budget: ₹{budget:,.2f}
- Total Spend Tracked: ₹{total_spend:,.2f}
- Essential Spend: ₹{essential_spend:,.2f}
- Discretionary (Non-Essential) Spend: ₹{discretionary_spend:,.2f} ({discretionary_pct:.1f}% of total)
- Category Totals: {json.dumps(cat_summary)}
- Top 5 Largest Expenses: {json.dumps(top_items)}

Formatting Instructions:
- Quote all monetary figures in Indian Rupees (₹).
- Call out specific ridiculous purchases, Zomato/Swiggy habits, impulse gadgets, and category drains by name and price in ₹.
- Use sharp humor and relatable context (e.g. CTC vs in-hand, Bangalore/tier-1 lifestyle inflation, SIPs sacrificed).
- Include a "Financial Health Score" from 1/10 to 10/10.
- Keep the roast punchy, funny, and structured with clear markdown headings.
"""

        # 2. Recovery Plan Generation
        recovery_prompt = f"""
You are an expert Certified Financial Planner (CFP) and wealth advisor.
Generate a structured, actionable, and realistic 30-Day Financial Recovery & Budget Plan for this user in Indian Rupees (₹ / INR).

Financial Context (in INR ₹):
- Monthly Net In-Hand Income: ₹{income:,.2f}
- Target Monthly Budget: ₹{budget:,.2f}
- Current Total Spend: ₹{total_spend:,.2f}
- Desired Target Monthly Savings: ₹{target_savings:,.2f}
- Essential Expenses: ₹{essential_spend:,.2f}
- Discretionary Expenses: ₹{discretionary_spend:,.2f}
- Category Breakdown: {json.dumps(cat_summary)}
- Top 5 Largest Items: {json.dumps(top_items)}

Generate a structured recovery plan in markdown with the following sections:
1. ⚖️ **50/30/20 Rule Gap Analysis**: Compare current % allocation vs ideal (50% Needs, 30% Wants, 20% Savings / Emergency Fund / Mutual Funds).
2. ✂️ **Immediate High-Impact Cuts**: Specific 3 to 5 transactions or subscription habits to cut immediately with estimated ₹ saved.
3. 🎯 **Weekly Spending Guardrails**: Exact weekly discretionary allowance in INR (₹).
4. 📈 **30-Day Milestones**: Week 1 to Week 4 action checkpoints to hit the ₹{target_savings:,.2f} target savings.
"""

        with st.spinner("🔥 Gemini is analyzing your transactions and preparing the roast..."):
            roast_resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=roast_prompt
            )
            st.session_state.roast_result = roast_resp.text

        with st.spinner("📊 Gemini is building your custom 50/30/20 Recovery Plan..."):
            recovery_resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=recovery_prompt
            )
            st.session_state.recovery_plan = recovery_resp.text

    except Exception as e:
        st.error(f"AI Generation failed: {str(e)}")


# Initialize state
init_session_state()

# --- Sidebar: Controls & Baseline Setup ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        st.success("Gemini API Key: Connected")
    else:
        api_key = st.text_input("Gemini API Key:", type="password")
        if not api_key:
            st.warning("Please provide a Gemini API Key to enable AI features.")

    st.divider()

    st.subheader("💼 Financial Baseline (₹ INR)")
    income_val = st.number_input(
        "Monthly Take-Home Income (₹)",
        min_value=5000.0,
        max_value=5000000.0,
        value=float(st.session_state.monthly_income),
        step=5000.0,
        help="Net take-home monthly salary in INR."
    )
    budget_val = st.number_input(
        "Target Monthly Budget (₹)",
        min_value=2000.0,
        max_value=5000000.0,
        value=float(st.session_state.monthly_budget),
        step=5000.0,
        help="Target total spend limit for the month."
    )
    st.session_state.monthly_income = income_val
    st.session_state.monthly_budget = budget_val

    st.divider()

    st.subheader("🧪 Dataset Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Mock Data", use_container_width=True):
            st.session_state.transactions_df = get_mock_transactions()
            st.session_state.roast_result = None
            st.session_state.recovery_plan = None
            st.rerun()

    with col2:
        if st.button("🗑️ Reset All", use_container_width=True):
            st.session_state.transactions_df = pd.DataFrame(
                columns=["Date", "Category", "Description", "Amount", "Type"]
            )
            st.session_state.roast_result = None
            st.session_state.recovery_plan = None
            st.rerun()

# --- Main App Header ---
st.title("🔥 BurnRate AI: Expense Roaster & Recovery Terminal")
st.caption("Multimodal Financial Analytics & AI-Powered Budget Optimization in Indian Rupees (₹)")

df = st.session_state.transactions_df

# --- Analytics & KPI Dashboard ---
if not df.empty:
    st.subheader("📊 Financial Overview & KPIs (₹)")
    
    total_spend = float(df["Amount"].sum())
    monthly_budget = float(st.session_state.monthly_budget)
    budget_remaining = monthly_budget - total_spend
    
    essential_spend = float(df[df["Type"] == "Essential"]["Amount"].sum())
    discretionary_spend = float(df[df["Type"] == "Discretionary"]["Amount"].sum())
    discretionary_pct = (discretionary_spend / total_spend * 100) if total_spend > 0 else 0.0
    
    unique_days = len(pd.to_datetime(df["Date"]).dt.date.unique())
    daily_burn_rate = total_spend / max(unique_days, 1)
    
    category_totals = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    top_category = category_totals.index[0] if not category_totals.empty else "N/A"
    top_cat_amount = category_totals.iloc[0] if not category_totals.empty else 0.0

    # 4 Dynamic KPI Cards with Deltas in INR
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        st.metric(
            label="Total Tracked Spend",
            value=f"₹{total_spend:,.2f}",
            delta=f"₹{budget_remaining:,.2f} remaining" if budget_remaining >= 0 else f"-₹{abs(budget_remaining):,.2f} over budget",
            delta_color="normal" if budget_remaining >= 0 else "inverse"
        )
    
    with kpi2:
        st.metric(
            label="Discretionary Leak Rate",
            value=f"{discretionary_pct:.1f}%",
            delta=f"₹{discretionary_spend:,.2f} non-essential",
            delta_color="inverse" if discretionary_pct > 30 else "normal"
        )
        
    with kpi3:
        st.metric(
            label="Daily Burn Rate",
            value=f"₹{daily_burn_rate:,.2f}/day",
            delta=f"Across {unique_days} active days",
            delta_color="off"
        )
        
    with kpi4:
        st.metric(
            label="Top Spending Drain",
            value=f"₹{top_cat_amount:,.2f}",
            delta=top_category,
            delta_color="off"
        )

    st.divider()

    # Visual Charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("##### 📌 Spending by Category (₹)")
        if not category_totals.empty:
            st.bar_chart(category_totals)
            
    with chart_col2:
        st.markdown("##### 📈 Cumulative Spending Trend (₹)")
        trend_df = df.copy()
        trend_df["Date"] = pd.to_datetime(trend_df["Date"])
        daily_spend = trend_df.groupby("Date")["Amount"].sum().sort_index()
        cumulative_spend = daily_spend.cumsum()
        st.area_chart(cumulative_spend)

    st.divider()

# --- AI Roast & Recovery Engine (Form Batched) ---
if not df.empty:
    st.subheader("⚡ AI Fiscal Audit & Recovery Engine")
    st.caption("Trigger Gemini 2.5 Flash to audit your expenses, roast your leaks, and generate a 50/30/20 recovery blueprint.")
    
    with st.form("ai_roast_form"):
        form_col1, form_col2 = st.columns(2)
        with form_col1:
            roast_intensity = st.select_slider(
                "🔥 Roast Severity Level",
                options=["Gentle Feedback", "Spicy Realist", "Brutal Wall Street CFO"],
                value="Brutal Wall Street CFO",
                help="Adjust the AI persona sharpness."
            )
        with form_col2:
            target_savings = st.number_input(
                "🎯 Desired Monthly Savings Goal (₹)",
                min_value=500.0,
                max_value=1000000.0,
                value=float(min(st.session_state.monthly_income * 0.20, 20000.0)),
                step=1000.0,
                help="Target savings goal in INR."
            )
            
        submitted = st.form_submit_button("🚀 Run AI Audit & Generate Recovery Plan", type="primary", use_container_width=True)

    if submitted:
        if not api_key:
            st.warning("Please provide a Gemini API Key in the sidebar.")
        else:
            generate_roast_and_recovery(
                df=df,
                income=st.session_state.monthly_income,
                budget=st.session_state.monthly_budget,
                intensity=roast_intensity,
                target_savings=target_savings,
                api_key_val=api_key
            )
            st.rerun()

    # Display AI Outputs if generated
    if st.session_state.roast_result or st.session_state.recovery_plan:
        out_tab1, out_tab2 = st.tabs(["🔥 The Brutal Roast", "📊 50/30/20 Recovery Blueprint"])
        
        with out_tab1:
            if st.session_state.roast_result:
                st.markdown(st.session_state.roast_result)
            else:
                st.info("Submit the form above to generate your roast.")
                
        with out_tab2:
            if st.session_state.recovery_plan:
                st.markdown(st.session_state.recovery_plan)
                
                # Download recovery plan button
                st.download_button(
                    label="📥 Download Recovery Blueprint (.md)",
                    data=st.session_state.recovery_plan,
                    file_name=f"financial_recovery_plan_inr_{datetime.today().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )
            else:
                st.info("Submit the form above to generate your recovery plan.")

    st.divider()

# --- Ingestion, Vision Scanner & Interactive Ledger ---
tab_ledger, tab_receipt, tab_upload = st.tabs([
    "📋 Interactive Ledger (`st.data_editor`)",
    "📷 Scan Receipt (Gemini Vision)",
    "📁 Import CSV File"
])

with tab_receipt:
    st.subheader("📷 Multimodal Receipt OCR Scanner (INR ₹)")
    st.caption("Snap a photo of your receipt using your camera or upload an image file. Gemini Vision will OCR and extract line items in Indian Rupees.")

    scan_mode = st.radio("Select Input Method:", ["Camera Input", "Image File Uploader"], horizontal=True)
    
    receipt_img = None
    if scan_mode == "Camera Input":
        receipt_img = st.camera_input("Take a photo of the receipt")
    else:
        receipt_img = st.file_uploader("Upload Receipt Image", type=["png", "jpg", "jpeg", "webp"])

    if receipt_img is not None:
        img_col1, img_col2 = st.columns([1, 1])
        with img_col1:
            st.image(receipt_img, caption="Captured Receipt", use_container_width=True)
        
        with img_col2:
            st.markdown("##### 🧠 AI OCR Analysis")
            if not api_key:
                st.warning("Please enter your Gemini API Key in the sidebar to run Vision OCR.")
            else:
                if st.button("🔍 Scan & Extract Receipt Data", type="primary"):
                    with st.spinner("Gemini Vision is analyzing receipt items in INR..."):
                        extracted_data = scan_receipt_with_gemini(receipt_img, api_key)
                        
                    if extracted_data:
                        st.json(extracted_data)
                        
                        try:
                            parsed_date = datetime.strptime(extracted_data.get("date", ""), "%Y-%m-%d").date()
                        except Exception:
                            parsed_date = datetime.today().date()

                        new_row = {
                            "Date": parsed_date,
                            "Category": extracted_data.get("category", "Shopping"),
                            "Description": f"{extracted_data.get('merchant', 'Store')}: {extracted_data.get('items_summary', 'Receipt purchase')}",
                            "Amount": float(extracted_data.get("total_amount", 0.0)),
                            "Type": extracted_data.get("type", "Discretionary")
                        }

                        new_row_df = pd.DataFrame([new_row])
                        st.session_state.transactions_df = pd.concat(
                            [st.session_state.transactions_df, new_row_df],
                            ignore_index=True
                        )
                        st.session_state.roast_result = None
                        st.session_state.recovery_plan = None
                        st.success("Receipt successfully scanned and added to ledger in ₹!")
                        st.rerun()

with tab_upload:
    st.subheader("Upload Bank Statement or Expense CSV")
    uploaded_file = st.file_uploader(
        "Choose an Expense CSV file",
        type=["csv"],
        help="Upload a CSV with Date, Description, Amount, and Category columns."
    )
    
    if uploaded_file is not None:
        if st.button("⚡ Ingest and Merge into Ledger", type="primary"):
            new_df = process_uploaded_csv(uploaded_file)
            if not new_df.empty:
                if st.session_state.transactions_df.empty:
                    st.session_state.transactions_df = new_df
                else:
                    st.session_state.transactions_df = pd.concat(
                        [st.session_state.transactions_df, new_df],
                        ignore_index=True
                    )
                st.session_state.roast_result = None
                st.session_state.recovery_plan = None
                st.success(f"Successfully ingested {len(new_df)} transactions!")
                st.rerun()

with tab_ledger:
    if df.empty:
        st.info("Your active ledger is currently empty. Click **'📥 Mock Data'** in the sidebar to populate instant test data, scan a receipt, or import a CSV.")
    else:
        st.subheader(f"Transaction Ledger ({len(df)} Records)")
        st.caption("Double-click any cell to edit details inline, add rows using the bottom toolbar, or toggle between Essential / Discretionary types.")

        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Date": st.column_config.DateColumn(
                    "Transaction Date",
                    format="YYYY-MM-DD",
                    required=True
                ),
                "Category": st.column_config.SelectboxColumn(
                    "Category",
                    options=CATEGORIES,
                    required=True
                ),
                "Description": st.column_config.TextColumn(
                    "Description / Merchant",
                    required=True,
                    width="large"
                ),
                "Amount": st.column_config.NumberColumn(
                    "Amount (₹)",
                    min_value=0.0,
                    max_value=10000000.0,
                    format="₹%.2f",
                    required=True
                ),
                "Type": st.column_config.SelectboxColumn(
                    "Spending Type",
                    options=EXPENSE_TYPES,
                    required=True
                )
            },
            key="ledger_data_editor"
        )

        if not edited_df.equals(st.session_state.transactions_df):
            st.session_state.transactions_df = edited_df

        col_export, col_summary = st.columns([1, 2])
        with col_export:
            csv_buffer = io.StringIO()
            edited_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="💾 Export Active Ledger (CSV)",
                data=csv_buffer.getvalue(),
                file_name=f"burnrate_ledger_inr_{datetime.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_summary:
            total_spend = float(edited_df["Amount"].sum())
            essential_spend = float(edited_df[edited_df["Type"] == "Essential"]["Amount"].sum())
            discretionary_spend = float(edited_df[edited_df["Type"] == "Discretionary"]["Amount"].sum())
            st.write(
                f"**Total Spend:** `₹{total_spend:,.2f}` | **Essential:** `₹{essential_spend:,.2f}` | **Discretionary:** `₹{discretionary_spend:,.2f}`"
            )
