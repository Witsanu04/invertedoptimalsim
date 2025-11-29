import streamlit as st
import pandas as pd
import random

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

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #0a0a0a;
    border-right: 1px solid #333;
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
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. Algorithm Logic: Inverted-Optimal
# ---------------------------------------------------------
def run_inverted_optimal(pages, frame_size):
    """
    Inverted-Optimal (Pessimal) Algorithm:
    - Look ahead into the future.
    - Replace the page that will be used SOONEST (min distance).
    - Goal: Maximize Page Faults (Worst Case).
    """
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
                # Still have space
                frames.append(current_page)
            else:
                # Frame Full -> Replacement Logic
                future_pages = pages[i+1:] # Look ahead
                
                # Find the page in memory that appears SOONEST in the future
                victim_candidate = None
                
                candidates_with_future = []
                
                for frm_p in frames:
                    if frm_p in future_pages:
                        dist = future_pages.index(frm_p)
                        candidates_with_future.append((frm_p, dist))
                    else:
                        # If not in future, skip or treat as very far
                        pass
                
                if candidates_with_future:
                    # Pick the one with MINIMUM distance (Nearest Future) -> TO KILL IT
                    victim_candidate = min(candidates_with_future, key=lambda x: x[1])[0]
                else:
                    # None needed again, pick FIFO
                    victim_candidate = frames[0]
                
                victim = victim_candidate
                
                # Perform Swap
                idx = frames.index(victim)
                frames[idx] = current_page
        
        # Log the step
        logs.append({
            "step": i + 1,
            "page": current_page,
            "status": status,
            "frames": list(frames), # snapshot
            "victim": victim
        })
        
    return faults, logs

# ---------------------------------------------------------
# 4. Sidebar Controls
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛠️ Control Panel")
    st.write("การตั้งค่าจำลอง Inverted-Optimal")
    
    st.markdown("---")
    
    # Input Selection
    input_mode = st.radio(
        "📂 Data Source:",
        ["Manual Input", "Random Generate", "Upload CSV"],
        index=0
    )
    
    page_reference = []
    
    if input_mode == "Manual Input":
        default_val = "7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1"
        user_str = st.text_area("Reference String (comma separated):", default_val, height=100)
        try:
            page_reference = [int(x.strip()) for x in user_str.split(',') if x.strip().isdigit()]
        except:
            st.error("Format Error! Please enter numbers separated by comma.")

    elif input_mode == "Random Generate":
        count = st.number_input("Number of Pages:", 10, 200, 20)
        if st.button("🎲 Randomize"):
            page_reference = [random.randint(0, 9) for _ in range(count)]
            st.session_state['rnd_pages'] = page_reference
        
        if 'rnd_pages' in st.session_state:
            page_reference = st.session_state['rnd_pages']
            st.code(str(page_reference), language=None)
        else:
            page_reference = [7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1] # Default fallback

    elif input_mode == "Upload CSV":
        uploaded_file = st.file_uploader("Choose CSV File", type=["csv"])
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file, header=None)
                # Flatten any shape of CSV into a single list of numbers
                vals = df.values.flatten()
                page_reference = [int(x) for x in vals if str(x).isnumeric()]
                st.success(f"Loaded {len(page_reference)} pages from file.")
            except Exception as e:
                st.error(f"Error reading file: {e}")

    st.markdown("---")
    
    # Frame Selection
    st.markdown("### 📼 Memory Config")
    selected_frame_size = st.slider("Target Frames (for Details):", 3, 8, 3)

# ---------------------------------------------------------
# 5. Main Dashboard
# ---------------------------------------------------------

st.title("🥀 Inverted-Optimal Simulator")
st.markdown("### **Worst-Case Scenario Analysis** (Pessimal Algorithm)")
st.caption("ระบบจำลองการทำงานอัลกอริทึมแบบ Inverted-Optimal เพื่อศึกษาผลกระทบเมื่อระบบเลือกลบหน้าที่มีความจำเป็นต้องใช้เร็วที่สุด")

if not page_reference:
    st.warning("⚠️ Waiting for input... (Please use the sidebar)")
    st.stop()

# --- Section A: Overview Dashboard ---
st.markdown("---")
st.markdown("#### 📊 Performance Spectrum (Overview)")
st.write("เปรียบเทียบ Page Fault ในกรณีที่แย่ที่สุด (Worst Case) กับขนาดหน่วยความจำ (Frames) ต่างๆ")

cols = st.columns(6)
frame_options = range(3, 9)

for idx, f_size in enumerate(frame_options):
    f_count, _ = run_inverted_optimal(page_reference, f_size)
    fault_rate = (f_count / len(page_reference)) * 100
    
    with cols[idx]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">FRAMES: {f_size}</div>
            <div class="metric-value">{fault_rate:.0f}%</div>
            <div class="metric-sub">TOTAL FAULTS: {f_count}</div>
        </div>
        """, unsafe_allow_html=True)

# --- Section B: Deep Dive Simulation ---
st.markdown("---")
st.markdown(f"#### 👁️ Trace Execution: **{selected_frame_size} Frames**")

curr_faults, curr_logs = run_inverted_optimal(page_reference, selected_frame_size)
curr_rate = (curr_faults / len(page_reference)) * 100

st.markdown(f"""
<div style="background:#151515; border-left:4px solid #F2C94C; padding:15px; border-radius:5px; margin-bottom:20px;">
    <h4 style="margin:0; color:#F2C94C;">Selected Configuration Result</h4>
    <p style="margin:0; color:#aaa;">
       Pages: {len(page_reference)} | 
       Total Faults: <strong style="color:#EB5757;">{curr_faults}</strong> | 
       Rate: {curr_rate:.2f}%
    </p>
</div>
""", unsafe_allow_html=True)

# Header for list
col_h1, col_h2, col_h3, col_h4 = st.columns([1, 1.5, 1, 4])
col_h1.markdown("**PAGE**")
col_h2.markdown("**STATUS**")
col_h3.markdown("**VICTIM**")
col_h4.markdown("**MEMORY STATE**")
st.markdown("<hr style='border-color: #333; margin: 0 0 10px 0;'>", unsafe_allow_html=True)

# Loop Logs
for log in curr_logs:
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
        # Style classes
        classes = "frame-box"
        if f == log['page']:
            classes += " new"  # Highlight new page
        
        frames_html += f"<span class='{classes}'>{f}</span>"
    
    # Fill empty slots visuals
    empty_slots = selected_frame_size - len(log['frames'])
    for _ in range(empty_slots):
        frames_html += "<span class='frame-box' style='opacity:0.3;'>-</span>"

    c4.markdown(frames_html, unsafe_allow_html=True)
    
    # Divider line
    st.markdown("<div style='border-bottom: 1px solid #1a1a1a; margin: 8px 0;'></div>", unsafe_allow_html=True)

# --- Section C: Summary & Conclusion (New Feature) ---
st.markdown("---")
st.markdown("### 📝 บทสรุปผลการจำลอง (Simulation Summary)")

summary_html = f"""
<div class="summary-box">
    <h3 style="color: #F2C94C; margin-top: 0;">📋 รายงานผลสรุป (Analysis Report)</h3>
    <ul class="summary-text">
        <li><b>จำนวนข้อมูลทั้งหมด (Total Input):</b> {len(page_reference)} หน้า</li>
        <li><b>ขนาดหน่วยความจำ (Frames):</b> {selected_frame_size} เฟรม</li>
        <li><b>จำนวนความล้มเหลว (Page Faults):</b> <span style="color:#EB5757; font-weight:bold;">{curr_faults} ครั้ง</span></li>
        <li><b>อัตราความล้มเหลว (Fault Rate):</b> {curr_rate:.2f}%</li>
    </ul>
    <hr style="border-color: #333;">
    <h4 style="color: #F2C94C;">💡 วิเคราะห์ผล (Conclusion):</h4>
    <p class="summary-text">
        จากการจำลองด้วยอัลกอริทึม <b>Inverted-Optimal</b> พบว่าระบบมีการเลือกเปลี่ยนหน้า (Page Replacement) 
        โดยจงใจเลือกหน้าที่จะถูกเรียกใช้ใน <i>อนาคตอันใกล้ที่สุด</i> ออกไป 
        <br><br>
        ส่งผลให้เกิด Page Fault สูงถึง <b>{curr_rate:.2f}%</b> ซึ่งสะท้อนถึงประสิทธิภาพที่ <u>แย่ที่สุด (Worst-Case)</u> 
        ตามทฤษฎี เหมาะสำหรับการศึกษาเพื่อหาขอบเขตล่าง (Lower Bound) ของประสิทธิภาพการจัดการหน่วยความจำ
    </p>
</div>
"""
st.markdown(summary_html, unsafe_allow_html=True)

# Footer
st.markdown("<br><br><div style='text-align:center; color:#444; font-size:12px;'>Operating System Simulator • Inverted-Optimal Edition</div>", unsafe_allow_html=True)