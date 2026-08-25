import os
import json
import urllib.parse
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="Life-OS | Digital Wellbeing Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Ingestion ---
@st.cache_data
def load_screentime_data(csv_path: str = "assignment 7/screentime.csv") -> pd.DataFrame:
    """Loads and standardizes the screentime dataset."""
    # Fallback to local path if running from inside assignment 7 folder
    if not os.path.exists(csv_path) and os.path.exists("screentime.csv"):
        csv_path = "screentime.csv"
    
    df = pd.read_csv(csv_path)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df["Minutes_Used"] = df["Minutes_Used"].astype(int)
    return df

df = load_screentime_data()

# --- Gemini Coaching & Avatar Generator Function ---
def get_ai_coaching_and_avatar(summary_str: str, total_mins: int, goal_mins: int, api_key_val: str) -> tuple:
    """Invokes Gemini 2.5 Flash to generate holistic lifestyle coaching and dynamic avatar image prompt."""
    try:
        client = genai.Client(api_key=api_key_val)
        
        system_instruction = (
            "You are an elite, holistic digital wellbeing coach and behavioral psychologist. "
            "Your job is to analyze daily screen time usage and provide direct, actionable, and empathetic guidance. "
            "REQUIREMENT: Do not give generic advice like 'use your phone less'. You MUST analyze the specific categories "
            "(Social Media, Entertainment, Coding, Education) and propose concrete, physical real-world replacement habits "
            "(e.g., swapping doomscrolling for outdoor walks, strength training, batch cooking, journaling, or tactile hobbies). "
            "Also provide an image generation prompt representing the user's mental/digital state today (e.g. 'a focused warrior meditating under cherry blossoms' if goal met, or 'a tired zombie mesmerized by a glowing neon screen in darkness' if heavily over goal)."
        )
        
        prompt = f"""
Daily Screen Time Data Analysis:
- Total Time Spent Today: {total_mins} minutes ({total_mins/60:.1f} hours)
- Daily Goal Threshold: {goal_mins} minutes ({goal_mins/60:.1f} hours)
- Variance vs Goal: {total_mins - goal_mins:+d} minutes
- Detailed Usage Breakdown:
{summary_str}

Please generate your response in strict JSON format matching this schema:
{{
  "coaching_markdown": "Your detailed markdown analysis with bold headers, specific real-world replacement suggestions, and a 1-sentence motivational challenge.",
  "status_verdict": "On Track" | "Moderate Overuse" | "Severe Doomscroll Alert",
  "avatar_image_prompt": "A vivid 1-sentence prompt describing a cinematic digital art avatar representing their wellbeing state today"
}}
"""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json"
            )
        )
        
        data = json.loads(response.text.strip())
        return data.get("coaching_markdown", ""), data.get("avatar_image_prompt", ""), data.get("status_verdict", "Status Evaluated")
    except Exception as e:
        return f"⚠️ AI Coaching generation error: {str(e)}", "A serene mindful person taking a deep breath in nature, digital art", "Error"

# --- Sidebar Controls (Phase 2 & Phase 4 URL State) ---
with st.sidebar:
    st.header("⚙️ Life-OS Controls")
    
    # API Key Configuration
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        st.success("🟢 Gemini API Connected")
    else:
        api_key = st.text_input("Enter Gemini API Key:", type="password")
        if not api_key:
            st.warning("⚠️ Enter API Key to enable AI Coaching & Avatars.")

    st.divider()

    # Date Filter
    available_dates = sorted(df["Date"].unique(), reverse=True)
    
    # Check query params for shared date
    query_date = st.query_params.get("date", None)
    default_date_idx = 0
    if query_date:
        try:
            parsed_qdate = pd.to_datetime(query_date).date()
            if parsed_qdate in available_dates:
                default_date_idx = available_dates.index(parsed_qdate)
        except Exception:
            pass

    selected_date = st.selectbox(
        "📅 Select Date to Inspect",
        options=available_dates,
        index=default_date_idx
    )

    # Daily Goal Slider (in hours)
    daily_goal_hours = st.slider(
        "🎯 Daily Screen Time Limit (Hours)",
        min_value=1.0,
        max_value=12.0,
        value=5.5,
        step=0.5,
        help="Set your target ceiling for healthy daily screen usage."
    )
    daily_goal_minutes = int(daily_goal_hours * 60)

    st.divider()
    
    # Phase 4 Innovation: Shareable Accountability Link
    st.subheader("🔗 Accountability Partner")
    if st.button("Generate Shareable Link", use_container_width=True):
        st.query_params["date"] = str(selected_date)
        st.query_params["goal"] = str(daily_goal_hours)
        st.success("✅ URL updated with your stats! Copy the browser address bar to share.")

# --- Main Command Center Dashboard ---
st.title("🌱 Life-OS: Digital Wellbeing & Habit Reclaiming Dashboard")
st.caption(f"Analyzing behavioral screentime telemetry for **{selected_date.strftime('%A, %B %d, %Y')}**")

# Filter data for selected date
day_df = df[df["Date"] == selected_date].copy()

if day_df.empty:
    st.warning("No screentime data available for the selected date.")
else:
    # Aggregations & Metrics
    total_minutes_today = int(day_df["Minutes_Used"].sum())
    total_hours_today = total_minutes_today / 60
    
    # Most used app
    most_used_row = day_df.sort_values(by="Minutes_Used", ascending=False).iloc[0]
    most_used_app = most_used_row["App_Name"]
    most_used_app_mins = most_used_row["Minutes_Used"]
    
    # Delta calculations
    delta_mins = total_minutes_today - daily_goal_minutes
    delta_hours = abs(delta_mins) / 60
    delta_label = f"{delta_hours:.1f}h {'over limit' if delta_mins > 0 else 'under limit'}"

    # --- Phase 2: KPI Row ---
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    
    with kpi_col1:
        st.metric(
            label="Total Screen Time Today",
            value=f"{total_hours_today:.1f} hrs ({total_minutes_today}m)",
            delta=f"{delta_mins:+d}m vs {daily_goal_hours}h goal",
            delta_color="inverse" if delta_mins > 0 else "normal"
        )
        
    with kpi_col2:
        st.metric(
            label="Top Time-Drain App",
            value=most_used_app,
            delta=f"{most_used_app_mins}m ({most_used_row['Category']})",
            delta_color="off"
        )
        
    with kpi_col3:
        goal_status = "Exceeded Goal 🚨" if delta_mins > 0 else "Within Target ✅"
        st.metric(
            label="Daily Wellbeing Status",
            value=goal_status,
            delta=delta_label,
            delta_color="inverse" if delta_mins > 0 else "normal"
        )

    st.divider()

    # --- Phase 2: Visualizations ---
    chart_col1, chart_col2 = st.columns([1, 1])
    
    with chart_col1:
        st.subheader("📊 Category Distribution Today")
        cat_df = day_df.groupby("Category")["Minutes_Used"].sum().reset_index()
        cat_chart_data = cat_df.set_index("Category")["Minutes_Used"]
        st.bar_chart(cat_chart_data)
        
    with chart_col2:
        st.subheader("📈 14-Day Screen Time Trend (Hours)")
        trend_series = (df.groupby("Date")["Minutes_Used"].sum() / 60).round(2)
        st.line_chart(trend_series)

    st.divider()

    # --- Phase 3 & 4: AI Coaching & Guilt-Trip / Victory Avatar ---
    st.subheader("🧠 Gemini AI Holistic Life Coach & Avatar Engine")
    
    # Prepare Data Bridge string (Requirement 8)
    summary_data = {
        "date": str(selected_date),
        "total_minutes": total_minutes_today,
        "daily_goal_minutes": daily_goal_minutes,
        "category_breakdown_minutes": cat_df.set_index("Category")["Minutes_Used"].to_dict(),
        "app_breakdown": day_df[["App_Name", "Category", "Minutes_Used"]].to_dict(orient="records")
    }
    summary_str = json.dumps(summary_data, indent=2)

    # Session caching for AI responses per date
    ai_cache_key = f"ai_coaching_{selected_date}_{daily_goal_minutes}"
    
    if ai_cache_key not in st.session_state:
        st.session_state[ai_cache_key] = None

    if st.session_state[ai_cache_key] is None:
        if st.button("🚀 Analyze Habits & Generate Coaching Report", type="primary"):
            if not api_key:
                st.error("Please enter a Gemini API Key in the sidebar.")
            else:
                with st.spinner("Gemini is diagnosing your digital habits and rendering your Life-OS Avatar..."):
                    coaching_text, avatar_prompt, verdict = get_ai_coaching_and_avatar(
                        summary_str=summary_str,
                        total_mins=total_minutes_today,
                        goal_mins=daily_goal_minutes,
                        api_key_val=api_key
                    )
                    st.session_state[ai_cache_key] = {
                        "coaching": coaching_text,
                        "avatar_prompt": avatar_prompt,
                        "verdict": verdict
                    }
                st.rerun()
    else:
        cached = st.session_state[ai_cache_key]
        
        # Display Severity Alert
        if delta_mins > 90:
            st.error(f"🚨 **High Digital Fatigue Alert:** You spent {total_hours_today:.1f} hours on screens today, exceeding your healthy boundary by {delta_hours:.1f} hours.")
        elif delta_mins > 0:
            st.warning(f"⚠️ **Moderate Screen Overuse:** You exceeded your daily budget by {delta_mins} minutes.")
        else:
            st.success(f"🎉 **Great Focus Day:** You finished {abs(delta_mins)} minutes below your daily screen time ceiling!")

        out_col1, out_col2 = st.columns([2, 1])
        
        with out_col1:
            st.markdown("### 📋 Actionable Behavioral Guidance")
            st.markdown(cached["coaching"])
            
        with out_col2:
            st.markdown("### 🎭 Dynamic Life-OS Avatar")
            avatar_p = cached["avatar_prompt"]
            st.caption(f"*Prompt: {avatar_p}*")
            
            # Pollinations AI Avatar Image Generation
            encoded_prompt = urllib.parse.quote(avatar_p)
            pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true&seed=42"
            
            st.image(
                pollinations_url,
                caption=f"Mindset Avatar ({cached.get('verdict', 'Evaluated')})",
                use_container_width=True
            )
            
        if st.button("🔄 Re-Analyze Day"):
            st.session_state[ai_cache_key] = None
            st.rerun()

    # Raw telemetry viewer expander
    with st.expander("👀 View Raw Screentime Telemetry Table", expanded=False):
        st.dataframe(day_df, use_container_width=True, hide_index=True)
