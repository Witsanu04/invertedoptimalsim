import streamlit as st
import pandas as pd
import random
import time

# ---------------------------------------------------------
# 1. Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Inverted-Optimal Sim",
    layout="wide",
    page_icon="🥀"
)

# ---------------------------------------------------------
# 2. CSS Design (Theme: Midnight Luxury)
# ---------------------------------------------------------
CUSTOM_CSS = """
<style>
/* Reset & Background */
.stApp {
    background-color: #000000;
    color: #e0e0e0;
}

/* Custom Cards for Dashboard */
.metric-card {
    background: linear-gradient(160deg, #111 0%, #000 100%);
    border: 1px solid #C5A059; /* Classic Gold */
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(197, 160, 89, 0.15);
    transition: transform 0.2s;
}
.metric-card:hover {
    transform: translateY(-5px);
    border-color: #FFD700;
    box-shadow: 0 8px 25px rgba(255, 215, 0, 0.25);
}

/* Typography inside cards */
.metric-title {
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #888;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 36px;
    font-weight: 700;
    color: #F2C94C; /* Soft Gold */
    font-family: 'Helvetica Neue', sans-serif;
}
.metric-sub {
    font-size: 12px;
    color: #EB5757; /* Red for 'Worst Case' */
}

/* Headers */
h1, h2, h3 {
    color: #F2C94C !important;
    font-weight: 700 !important;
}
.highlight {
    color: #F2C94C;
    text-decoration: underline;
    text-decoration-color: #555;
}

/* Control Panel Container (New Layout) */
.control-container {
    background-color: #0a0a0a;
    border: 1px solid #333;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 20px;
}

/* Page Circle */
.page-badge {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #222;
    border: 2px solid #555;
    color: #fff;
    font-weight: bold;
    margin: 0 auto;
}

/* Frames Visualization */
.frame-box {
    display: inline-block;
    padding: 6px 12px;
    margin: 0 4px;
    border: 1px solid #444;
    border-radius: 6px;
    color: #888;
    background: #050505;
    min-width: 35px;
    text-align: center;
}
.frame-box.victim {
    border-color: #EB5757;
    color: #EB5757;
    background: rgba(235, 87, 87, 0.1);
}
.frame-box.new {
    border-color: #F2C94C;
    color: #F2C94C;
    font-weight: bold;
}

/* Summary Box */
.summary-box {
    background: #111; 
    border: 1px dashed #C5A059; 
    border-radius: 15px; 
    padding: 20px; 
    margin-top: 30px;
}
.summary-text {
    font-size: 16px;
    color: #ddd;
    line-height: 1.6;
}

/* Button Styling */
.stButton>button {
    border-radius: 20px;
    background: linear-gradient(to right, #C5A059, #F2C94C);
    color: black;
    font-weight: bold;
    border: none;
}
.stDownloadButton>button {
    background-color: #222;
    color: #F2C94C;
    border: 1px solid #F2C94C;
    border-radius: 20px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. Algorithm Logic: Inverted-Optimal
# ---------------------------------------------------------
def run_inverted_optimal(pages, frame_size):
    frames = []
    faults = 0
    logs = []

    for i, current_page in enumerate(pages):
        status = "HIT"
        victim = None
        
        # Check Hit/Fault
        if current_page not in frames:
            status = "FAULT"
            faults += 1
            
            if len(frames) < frame_size:
                frames.append(current_page)
            else:
                # Inverted-Optimal Logic: Replace the one needed SOONEST
                future_pages = pages[i+1:]
                victim_candidate = None
                candidates_with_future = []
                
                for frm_p in frames:
                    if frm_p in future_pages:
                        dist = future_pages.index(frm_p)
                        candidates_with_future.append((frm_p, dist))
                    else:
                        pass # Not in future
                
                if candidates_with_future:
                    # Pick MIN distance (Nearest Future)
                    victim_candidate = min(candidates_with_future, key=lambda x: x[1])[0]
                else:
                    # FIFO fallback
                    victim_candidate = frames[0]
                
                victim = victim_candidate
                idx = frames.index(victim)
                frames[idx] = current_page
        
        logs.append({
            "step": i + 1,
            "page": current_page,
            "status": status,
            "frames": list(frames),
            "victim": victim
        })
        
    return faults, logs

# ---------------------------------------------------------
# 4. Main Layout & Inputs (Moved to Top)
# ---------------------------------------------------------

st.title("🥀 Inverted-Optimal Simulator")
st.markdown("### **Worst-Case Scenario Analysis** (Pessimal Algorithm)")
st.markdown("ระบบจำลองการทำงานอัลกอริทึมแบบ Inverted-Optimal เพื่อศึกษาผลกระทบเมื่อระบบเลือกลบหน้าที่มีความจำเป็นต้องใช้เร็วที่สุด")

st.markdown("---")

# --- Control Panel Section (Top) ---
st.markdown("#### ⚙️ Configuration Panel")

# Create a container for inputs to look neat
with st.container():
    # Row 1: Input Source & Frame Size
    col1, col2 = st.columns([2, 1])
    
    with col1:
        input_mode = st.radio(
            "📂 Data Source:",
            ["Manual Input", "Random Generate", "Upload CSV"],
            index=1,
            horizontal=True
        )
        
        page_reference = []
        if input_mode == "Manual Input":
            default_val = "7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1"
            user_str = st.text_input("Reference String (comma separated):", default_val)
            try:
                page_reference = [int(x.strip()) for x in user_str.split(',') if x.strip().isdigit()]
            except:
                st.error("Format Error!")
                
        elif input_mode == "Random Generate":
            sub_c1, sub_c2 = st.columns([1, 1])
            count = sub_c1.number_input("Number of Pages:", 10, 200, 20)
            if sub_c2.button("🎲 Randomize"):
                st.session_state['rnd_pages'] = [random.randint(0, 9) for _ in range(count)]
            
            # Use session state or default
            if 'rnd_pages' in st.session_state:
                page_reference = st.session_state['rnd_pages']
            else:
                page_reference = [7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1]
            st.caption(f"Current String: {page_reference}")

        elif input_mode == "Upload CSV":
            uploaded_file = st.file_uploader("Choose CSV File", type=["csv"])
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file, header=None)
                    vals = df.values.flatten()
                    page_reference = [int(x) for x in vals if str(x).isnumeric()]
                    st.success(f"Loaded {len(page_reference)} pages.")
                except:
                    st.error("Error reading CSV.")

    with col2:
        selected_frame_size = st.slider("Target Frames:", 3, 8, 3)
        
        # [NEW FEATURE] Animation Speed
        st.markdown("<br>", unsafe_allow_html=True)
        anim_speed = st.slider("⏱️ Animation Speed (Seconds):", 0.0, 1.0, 0.05, step=0.1)
        st.caption("0.0 = Instant, 1.0 = Slow Motion")

if not page_reference:
    st.warning("Please provide input data.")
    st.stop()

# ---------------------------------------------------------
# 5. Dashboard & Simulation
# ---------------------------------------------------------
st.markdown("---")

# --- Overview Dashboard ---
st.markdown("#### 📊 Performance Spectrum (Overview)")
cols = st.columns(6)
for idx, f_size in enumerate(range(3, 9)):
    f_count, _ = run_inverted_optimal(page_reference, f_size)
    fault_rate = (f_count / len(page_reference)) * 100
    with cols[idx]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">FRAMES: {f_size}</div>
            <div class="metric-value">{fault_rate:.0f}%</div>
            <div class="metric-sub">FAULTS: {f_count}</div>
        </div>
        """, unsafe_allow_html=True)

# --- Detailed Trace ---
st.markdown("---")
st.markdown(f"#### 👁️ Trace Execution: **{selected_frame_size} Frames**")

# Calculate results
curr_faults, curr_logs = run_inverted_optimal(page_reference, selected_frame_size)
curr_rate = (curr_faults / len(page_reference)) * 100

# [NEW FEATURE] Export CSV Button
csv_data = []
for l in curr_logs:
    csv_data.append({
        "Step": l["step"],
        "Page": l["page"],
        "Status": l["status"],
        "Victim": l["victim"],
        "Memory": str(l["frames"])
    })
df_export = pd.DataFrame(csv_data)
csv = df_export.to_csv(index=False).encode('utf-8')

col_res, col_btn = st.columns([3, 1])
with col_res:
    st.markdown(f"**Total Faults:** <span style='color:#EB5757'>{curr_faults}</span> ({curr_rate:.2f}%)", unsafe_allow_html=True)
with col_btn:
    st.download_button(
        label="📥 Download Report (CSV)",
        data=csv,
        file_name='inverted_optimal_result.csv',
        mime='text/csv',
        use_container_width=True
    )

# Header Table
col_h1, col_h2, col_h3, col_h4 = st.columns([1, 1.5, 1, 4])
col_h1.markdown("**PAGE**")
col_h2.markdown("**STATUS**")
col_h3.markdown("**VICTIM**")
col_h4.markdown("**MEMORY STATE**")
st.markdown("<hr style='border-color: #333; margin: 0 0 10px 0;'>", unsafe_allow_html=True)

# Loop Logs with Animation
placeholder = st.empty()

# We iterate and print
for log in curr_logs:
    # Animation Delay
    if anim_speed > 0:
        time.sleep(anim_speed)

    c1, c2, c3, c4 = st.columns([1, 1.5, 1, 4])
    
    # 1. Page
    c1.markdown(f"<div class='page-badge'>{log['page']}</div>", unsafe_allow_html=True)
    
    # 2. Status
    if log['status'] == "FAULT":
        status_html = "<span style='color:#EB5757; font-weight:bold;'>🔴 FAULT</span>"
    else:
        status_html = "<span style='color:#27AE60; font-weight:bold;'>🟢 HIT</span>"
    c2.markdown(status_html, unsafe_allow_html=True)
    
    # 3. Victim
    vic = log['victim'] if log['victim'] is not None else "-"
    c3.markdown(f"<span style='color:#888;'>{vic}</span>", unsafe_allow_html=True)
    
    # 4. Frames
    frames_html = ""
    for f in log['frames']:
        classes = "frame-box"
        if f == log['page']:
            classes += " new" 
        frames_html += f"<span class='{classes}'>{f}</span>"
    
    empty_slots = selected_frame_size - len(log['frames'])
    for _ in range(empty_slots):
        frames_html += "<span class='frame-box' style='opacity:0.3;'>-</span>"

    c4.markdown(frames_html, unsafe_allow_html=True)
    st.markdown("<div style='border-bottom: 1px solid #1a1a1a; margin: 8px 0;'></div>", unsafe_allow_html=True)

# --- Summary ---
st.markdown("### 📝 บทสรุปผลการจำลอง")
summary_html = f"""
<div class="summary-box">
    <h4 style="color: #F2C94C; margin-top: 0;">📋 Analysis Report</h4>
    <ul class="summary-text">
        <li><b>Total Pages:</b> {len(page_reference)}</li>
        <li><b>Memory Frames:</b> {selected_frame_size}</li>
        <li><b>Page Faults:</b> <span style="color:#EB5757; font-weight:bold;">{curr_faults}</span></li>
        <li><b>Fault Rate:</b> {curr_rate:.2f}%</li>
    </ul>
    <p class="summary-text">
        การจำลองแสดงให้เห็นว่า Inverted-Optimal Algorithm สร้าง Page Fault สูงสุดเนื่องจากเลือกลบหน้าที่จำเป็นต้องใช้ในอนาคตอันใกล้ที่สุดออกไป
    </p>
</div>
"""
st.markdown(summary_html, unsafe_allow_html=True)
