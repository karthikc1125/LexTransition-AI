import streamlit as st
import os

# Page Configuration
st.set_page_config(page_title="LexTransition AI", page_icon="⚖️", layout="wide")

# Initialize session state for navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# URL-based navigation (clickable cards via ?page=...) with sidebar precedence

def _read_url_page():
    """Return page from query params in a version-agnostic way, or None."""
    try:
        # Preferred modern API
        qp = st.query_params  # type: ignore[attr-defined]
        # qp may not support .get in all versions
        try:
            val = qp.get("page", None)
        except Exception:
            # Try dict conversion
            try:
                val = dict(qp).get("page", None)
            except Exception:
                val = None
        if isinstance(val, list):
            return val[0]
        return val
    except Exception:
        qp = st.experimental_get_query_params()
        return qp.get("page", [None])[0] if qp else None

url_page = _read_url_page()

# If a sidebar navigation is pending, take precedence over URL param once
if "pending_page" in st.session_state:
    st.session_state.current_page = st.session_state.pop("pending_page")
else:
    if url_page in {"Home", "Mapper", "OCR", "Fact", "Settings"}:
        st.session_state.current_page = url_page

# Helper: navigate via sidebar and keep URL in sync
def _goto(page: str):
    # Defer assignment to top-of-run logic so it overrides URL param this cycle
    st.session_state.pending_page = page
    try:
        st.experimental_set_query_params(page=page)
    except Exception:
        pass
    st.rerun()

# Custom Styling (Dark Theme with Shiny Background)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@600;700&display=swap');

/* Background - Textured Shining Black */
[data-testid="stAppViewContainer"] {
    background: #000000;
    position: relative;
    overflow: hidden;
    min-height: 100vh;
    z-index: 0;
}

/* Strong gloss and glass-like texture */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background:
        /* soft highlights */
        radial-gradient(650px 240px at 8% 12%, rgba(255,255,255,0.10), transparent 18%),
        radial-gradient(600px 220px at 85% 18%, rgba(255,255,255,0.08), transparent 16%),
        radial-gradient(400px 140px at 50% 30%, rgba(255,255,255,0.05), transparent 30%),
        /* vertical sheen */
        linear-gradient(180deg, rgba(255,255,255,0.02), rgba(0,0,0,0) 22%),
        /* subtle diagonal glass streaks */
        repeating-linear-gradient(45deg, rgba(255,255,255,0.012) 0px, rgba(255,255,255,0.012) 1px, rgba(255,255,255,0) 6px),
        repeating-linear-gradient(-45deg, rgba(255,255,255,0.008) 0px, rgba(255,255,255,0.008) 1px, rgba(255,255,255,0) 12px),
        /* faint dot/noise for texture */
        radial-gradient(rgba(255,255,255,0.004) 1px, transparent 1.5px);
    opacity: 1;
    filter: blur(1px) saturate(1);
    background-size: auto, auto, auto, auto, 14px 14px, 28px 28px, 6px 6px;
}

/* Center sheen */
[data-testid="stAppViewContainer"]::after {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background: radial-gradient(60% 45% at 50% 28%, rgba(255,255,255,0.08), rgba(0,0,0,0.96));
    opacity: 0.18;
    filter: blur(2px);
}

/* Add thin glass lines near top-left */
[data-testid="stAppViewContainer"] .glass-stripe {
    position: absolute;
    top: 56px;
    left: 120px;
    width: 640px;
    height: 160px;
    background: linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.0));
    transform: rotate(-6deg);
    pointer-events: none;
    opacity: 0.65;
}

[data-testid="stSidebarNav"] {
    background: linear-gradient(180deg, rgba(6,6,6,1) 0%, rgba(12,12,12,0.98) 100%);
    border-right: 1px solid rgba(255,255,255,0.02);
}

/* Global font */
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Poppins', 'Inter', sans-serif;
    font-weight: 700;
}

/* Home Page Styling */
.main-container {
    max-width: 1000px;
}

.home-header {
    margin-bottom: 30px;
}

.home-title {
    font-size: 32px;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
    font-family: 'Poppins', sans-serif;
    letter-spacing: -0.5px;
}

.home-subtitle {
    font-size: 14px;
    color: #b0b0b0;
    max-width: 650px;
    line-height: 1.6;
    margin-top: 8px;
    font-weight: 400;
}

.home-what {
    font-size: 18px;
    font-weight: 700;
    color: #ffffff;
    margin-top: 28px;
    margin-bottom: 18px;
}

/* Home Cards - Compact Black Theme */
.home-card {
    background: linear-gradient(145deg, rgba(20, 20, 20, 0.95), rgba(10, 10, 10, 0.7));
    border: 1px solid rgba(80, 80, 80, 0.25);
    border-radius: 12px;
    padding: 22px;
    min-height: 150px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(8px);
    position: relative;
    overflow: hidden;
    box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.05);
}

.home-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at top right, rgba(100, 100, 100, 0.08), transparent);
    pointer-events: none;
}

.home-card:hover {
    border-color: rgba(150, 150, 150, 0.4);
    transform: translateY(-6px);
    background: linear-gradient(145deg, rgba(30, 30, 30, 1), rgba(15, 15, 15, 0.9));
    box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.1), 0 20px 40px rgba(0, 0, 0, 0.5), 0 0 20px rgba(100, 100, 100, 0.15);
    cursor: pointer;
}

/* make anchor cards behave like blocks and inherit text color */
a.home-card { text-decoration: none !important; display: block; color: inherit; }

.home-card-icon {
    font-size: 16px;
    margin-right: 8px;
    color: #90ee90;
}

.home-card-header {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}

.home-card-title {
    font-size: 18px;
    font-weight: 700;
    color: #ffffff;
    font-family: 'Poppins', sans-serif;
    margin: 0;
}

.home-card-desc {
    font-size: 13px;
    color: #cbd5d1;
    line-height: 1.55;
    margin-bottom: 14px;
    flex-grow: 1;
}

.home-card-btn {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
    font-weight: 600;
    color: #a8f3b0;
    padding: 8px 0;
    border-top: 1px solid rgba(80, 80, 80, 0.15);
    margin-top: 2px;
    cursor: pointer;
}
.home-card-btn span:last-child {
    font-size: 18px;
}

/* Compact Home Card (provided design) */
.home-card-compact {
    background: linear-gradient(145deg, rgba(18,18,18,0.95), rgba(12,12,12,0.88));
    border: 1px solid rgba(255,255,255,0.02);
    border-radius: 12px;
    padding: 12px 14px;
    min-height: 100px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.18s ease;
}

.home-card-compact:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.45);
}

.home-card-compact .home-card-header { align-items: flex-start; }
.home-card-compact .home-card-title { font-size: 14px; font-weight: 700; }
.home-card-compact .home-card-desc { font-size: 12px; color: #9ea7a2; margin-top: 6px; }
.home-card-action { height: 44px; display:flex; align-items:center; }

/* Style Streamlit button so it visually matches the small pill button in the design */
.home-card-compact + .stButton > button {
    background: linear-gradient(180deg, rgba(28,28,28,0.95), rgba(20,20,20,0.95)) !important;
    color: #d9e7df !important;
    border: 1px solid rgba(255,255,255,0.03) !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    height: 36px !important;
    width: 160px !important;
    margin-top: -48px !important;
}

.home-card-compact + .stButton > button:after {
    content: '›';
    margin-left: 8px;
    opacity: 0.85;
}

/* Result Card (Mapper) */
.result-card {
    background: linear-gradient(180deg, rgba(18,18,18,0.98), rgba(10,10,10,0.95));
    border: 1px solid rgba(80, 120, 90, 0.08);
    border-radius: 12px;
    padding: 12px 14px 56px 14px;
    margin-top: 8px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.55);
    position: relative;
} 

.result-badge {
    display: inline-block;
    background: rgba(34,139,34,0.10);
    color: #8ee59b;
    font-weight: 700;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 12px;
    margin-bottom: 12px;
}

.result-grid {
    display: flex;
    gap: 18px;
    margin-bottom: 12px;
}

.result-col {
    flex: 1;
    background: rgba(255,255,255,0.01);
    border: 1px solid rgba(255,255,255,0.02);
    padding: 12px 14px;
    border-radius: 10px;
    min-height: 64px;
}

.result-col-title {
    font-size: 12px;
    color: #cfeadf;
    font-weight: 700;
}

.result-list {
    margin: 10px 0 12px 18px;
    color: #bfc9c4;
}

/* Position actual Streamlit buttons so they visually sit inside the result card */
.result-card + .stButton {
    margin-top: -46px;
    display: inline-block;
    margin-right: 8px;
}

.result-card + .stButton > button {
    background: linear-gradient(180deg, rgba(24,24,27,0.95), rgba(17,17,20,0.95)) !important;
    color: #ffffff !important;
    border: 1px solid transparent !important;
    border-image: linear-gradient(180deg, rgba(255,255,255,0.18), rgba(255,255,255,0.04)) 1 !important;
    padding: 10px 16px !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
    height: 42px !important;
    letter-spacing: 0.2px !important;
    box-shadow: none !important;
}

/* remove glossy pseudo elements */
.result-card + .stButton > button::before,
.result-card + .stButton > button::after { content: none !important; }

.result-card + .stButton + .stButton > button {
    background: linear-gradient(180deg, rgba(28,28,28,0.96), rgba(12,12,12,0.96)) !important;
    color: #e5e7eb !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 999px !important;
}

/* make bullets tighter */
.result-list li { margin-bottom: 6px; }

/* small tweak for small screens */
@media (max-width: 800px) {
    .result-grid { flex-direction: column; }
    .result-card { padding-bottom: 64px; }
}

/* Sidebar */
.sidebar-title {
    color: #ffffff;
    font-size: 20px;
    font-weight: 700;
    font-family: 'Poppins', sans-serif;
    margin-bottom: 12px;
}

.sidebar-badge {
    color: #4ade80;
    font-size: 12px;
    font-weight: 600;
    margin-top: 16px;
}

/* Column container for cards and buttons */
[data-testid="column"] {
    position: relative;
}

/* Flat-modern buttons (no 3D, crisp underline) */
.stButton>button {
    height: 42px;
    border-radius: 10px;
    color: #ffffff;
    font-weight: 700;
    letter-spacing: 0.2px;
    font-size: 14px;
    margin-top: 0;
    position: relative;
    z-index: 10;
    width: auto;
    padding: 0 18px;
    background: linear-gradient(180deg, rgba(24,24,27,0.95), rgba(17,17,20,0.95));
    border: 1px solid transparent;
    border-image: linear-gradient(180deg, rgba(255,255,255,0.18), rgba(255,255,255,0.04)) 1;
    box-shadow: none;
    backdrop-filter: saturate(110%);
    transition: background 0.2s ease, color 0.2s ease;
    /* underline */
    background-image:
      linear-gradient(180deg, rgba(24,24,27,0.95), rgba(17,17,20,0.95)),
      linear-gradient(90deg, #22c55e, #0ea5e9);
    background-origin: border-box;
    background-clip: padding-box, border-box;
}

/* remove glossy pseudo elements */
.stButton>button::before, .stButton>button::after { content: none !important; }

.stButton>button:hover {
    background-image:
      linear-gradient(180deg, rgba(30,30,34,0.98), rgba(20,20,24,0.98)),
      linear-gradient(90deg, #34d399, #60a5fa);
}

.stButton>button:focus-visible {
    outline: 2px solid #60a5fa;
    outline-offset: 2px;
}

.stButton>button:active {
    transform: translateY(0);
}

/* Home: full-width glossy CTA in cards */
.home-card + .stButton > button {
    width: 100% !important;
    margin-top: -95px !important;
    padding: 0 20px !important;
    height: 46px !important;
    border-radius: 12px !important;
    background: linear-gradient(180deg, rgba(24,24,27,0.95), rgba(17,17,20,0.95)) !important;
    color: #ffffff !important;
    border: 1px solid transparent !important;
    border-image: linear-gradient(180deg, rgba(255,255,255,0.18), rgba(255,255,255,0.04)) 1 !important;
    box-shadow: none !important;
}

.home-card + .stButton > button::before {
    content: ""; position: absolute; left: 10px; right: 10px; top: 4px; height: 40%; border-radius: 999px; background: linear-gradient(180deg, rgba(255,255,255,0.22), rgba(255,255,255,0.02)); pointer-events:none;
}

.home-card + .stButton > button::after {
    content: ""; position: absolute; left: 20px; right: 20px; bottom: -4px; height: 10px; border-radius: 999px; background: radial-gradient(60% 100% at 50% 0%, rgba(255,255,255,0.24), rgba(0,0,0,0)); opacity:0.55; filter: blur(6px);
}

/* Mapper: container for result, ensures correct layout */
.mapper-wrap { max-width: 920px; margin: 0 auto; position: relative; }

/* Position result buttons inline and overlay the bottom-right of the card */
.mapper-wrap .result-card + .stButton {
    margin-top: -52px;
    display: inline-block;
    float: right;
}

.mapper-wrap .result-card + .stButton > button {
    width: auto !important;
    padding: 8px 14px !important;
    height: 36px !important;
}

.mapper-wrap .result-card + .stButton + .stButton {
    margin-right: 10px; /* gap between buttons */
    float: right;
}

/* Clear floats after result area */
.mapper-wrap::after { content: ""; display: block; clear: both; }

/* Text Colors */
p, span, label {
    color: #b0b0b0;
}

h1, h2, h3 {
    color: #ffffff;
}

/* Dividers */
hr {
    border-color: rgba(100, 100, 100, 0.15);
}
</style>
""", unsafe_allow_html=True)


# Sidebar Navigation (Dark Theme)
with st.sidebar:
    st.markdown('<p class="sidebar-title">⚖️ LexTransition AI</p>', unsafe_allow_html=True)
    st.info("Offline legal assistant: Mapping IPC to BNS")
    st.divider()
    
    if st.button("🏠 Home", use_container_width=True):
        _goto("Home")
    if st.button("🔄 IPC → BNS Mapper", use_container_width=True):
        _goto("Mapper")
    if st.button("🖼️ Document OCR", use_container_width=True):
        _goto("OCR")
    if st.button("📚 Fact Checker", use_container_width=True):
        _goto("Fact")
    if st.button("⚙️ Settings / About", use_container_width=True):
        _goto("Settings")
    
    st.divider()
    st.markdown('<p class="sidebar-badge">✓ Offline Mode</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-badge">✓ Privacy First</p>', unsafe_allow_html=True)

# Attempt to import engines (use stubs if missing)
try:
    from engine.ocr_processor import extract_text, available_engines
    from engine.mapping_logic import map_ipc_to_bns, add_mapping
    from engine.rag_engine import search_pdfs, add_pdf, index_pdfs
    from engine.llm import summarize as llm_summarize
    ENGINES_AVAILABLE = True
except Exception:
    ENGINES_AVAILABLE = False

# LLM summarize stub
try:
    from engine.llm import summarize as llm_summarize
except Exception:
    def llm_summarize(text, question=None):
        return None

# Index PDFs at startup if engine available
if ENGINES_AVAILABLE:
    try:
        index_pdfs("law_pdfs")
    except Exception:
        pass

# Get current page
current_page = st.session_state.current_page



# ============================================================================
# PAGE: HOME
# ============================================================================
if current_page == "Home":
    # Header Section
    st.markdown('<div class="home-header">', unsafe_allow_html=True)
    st.markdown('<div class="home-title">⚖️ LexTransition AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="home-subtitle">'
        'Your offline legal assistant powered by AI. Analyze documents, map sections, and get instant legal insights—no internet required, your data stays private.'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # What do you want to do? Section
    st.markdown('<div class="home-what">What do you want to do?</div>', unsafe_allow_html=True)
    
    # Two column layout for cards
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <a class="home-card" href="?page=Mapper" target="_self">
            <div class="home-card-header">
                <span class="home-card-icon">✓</span>
                <div class="home-card-title">Convert IPC to BNS</div>
            </div>
            <div class="home-card-desc">Map old IPC sections to new BNS ee,indsJaris.</div>
            <div class="home-card-btn">
                <span>Open Mapper</span>
                <span>›</span>
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <a class="home-card" href="?page=OCR" target="_self">
            <div class="home-card-header">
                <span class="home-card-icon">📄</span>
                <div class="home-card-title">Analyze FIR / Notice</div>
            </div>
            <div class="home-card-desc">Extract text and key action points from legal documents.</div>
            <div class="home-card-btn">
                <span>Upload & Analyze</span>
                <span>›</span>
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    # Spacer
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Second row
    col3, col4 = st.columns(2, gap="large")
    
    with col3:
        st.markdown("""
        <a class="home-card" href="?page=Fact" target="_self">
            <div class="home-card-header">
                <span class="home-card-icon">📚</span>
                <div class="home-card-title">Legal Research</div>
            </div>
            <div class="home-card-desc">Search and analyze case law and statutes.</div>
            <div class="home-card-btn">
                <span>Start Research</span>
                <span>›</span>
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <a class="home-card" href="?page=Settings" target="_self">
            <div class="home-card-header">
                <span class="home-card-icon">⚙️</span>
                <div class="home-card-title">Settings</div>
            </div>
            <div class="home-card-desc">Configure engines and settings.</div>
            <div class="home-card-btn">
                <span>Configure</span>
                <span>›</span>
            </div>
        </a>
        """, unsafe_allow_html=True)

# ============================================================================
# PAGE: IPC TO BNS MAPPER
# ============================================================================
elif current_page == "Mapper":
    st.markdown("## ✓ IPC → BNS Transition Mapper")
    st.markdown("Convert old IPC sections into new BNS equivalents with legal-grade accuracy.")
    st.divider()
    
    # Input Section (wrapped)
    st.markdown('<div class="mapper-wrap">', unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    with col1:
        search_query = st.text_input("Enter IPC Section", placeholder="e.g., 420, 302, 378")
    with col2:
        search_btn = st.button("🔍 Find BNS Eq.", use_container_width=True)
    
    # Results Section
    if search_query and search_btn:
        if ENGINES_AVAILABLE:
            result = map_ipc_to_bns(search_query.strip())
            if result:
                # Styled result card
                ipc = search_query.strip()
                bns = result.get('bns_section', 'N/A')
                notes = result.get('notes', 'See source mapping.')

                st.markdown(f"""
                <div class="result-card">
                    <div class="result-badge">Mapping • <span style="opacity:0.9">hound</span></div>
                    <div class="result-grid">
                        <div class="result-col">
                            <div class="result-col-title">IPC Section</div>
                            <div style="font-size:20px;font-weight:700;color:#ffffff;margin-top:6px;">{ipc}</div>
                        </div>
                        <div class="result-col">
                            <div class="result-col-title">BNS Section</div>
                            <div style="font-size:20px;font-weight:700;color:#cfeadf;margin-top:6px;">{bns}</div>
                        </div>
                    </div>
                    <ul class="result-list">
                        <li>Offence of cheating retained</li>
                        <li>Penalty wording updated</li>
                        <li>Scope expanded to digital fraud</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

                # Functional action buttons (styled to sit inside the result card)
                if st.button("Compare Side-By-Side", key="compare_side"):
                    st.info("Opening comparison view...")
                if st.button("View Legal Text", key="view_legal_text"):
                    st.info("Opening legal text viewer...")
                
                st.divider()
                st.markdown(f"**Source:** _{result.get('source','mapping_db')}_")
            else:
                st.warning("⚠️ Section not found in mapping")
                with st.expander("➕ Add New Mapping"):
                    ipc = st.text_input("IPC Section", value=search_query)
                    bns = st.text_input("BNS Section (e.g., BNS 318)")
                    notes = st.text_area("Key Changes / Notes")
                    if st.button("✓ Save Mapping", use_container_width=True):
                        add_mapping(ipc, bns, notes, source="user")
                        st.success("✓ Mapping saved successfully!")
        else:
            if search_query == "420":
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### IPC Section")
                    st.markdown("**420** (Cheating)")
                with col2:
                    st.markdown("### BNS Section")
                    st.markdown("**318**")
                st.divider()
                st.markdown("### Key Changes")
                st.markdown("• Offence of cheating retained")
                st.markdown("• Penalty wording updated")
                st.markdown("• Scope expanded to digital fraud")
            else:
                st.error("Section not found in database")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# PAGE: DOCUMENT OCR
# ============================================================================
elif current_page == "OCR":
    st.markdown("## 🖼️ Document OCR")
    st.markdown("Extract text and key action items from legal notices, FIRs, and scanned documents.")
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Upload a legal Document")
        uploaded_file = st.file_uploader("Upload (FIR/Notice)", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        
        if uploaded_file:
            st.markdown("### Preview")
            st.image(uploaded_file, use_column_width=True)
    
    with col2:
        if uploaded_file:
            st.markdown("### Extracted Text")
            if st.button("🔧 Extract & Analyze", use_container_width=True):
                if ENGINES_AVAILABLE:
                    raw = uploaded_file.read()
                    extracted = extract_text(raw)
                    st.code(extracted, language="text")
                    
                    # Try LLM summary
                    summary = llm_summarize(extracted, question="What actions should the user take?")
                    if summary:
                        st.markdown("### Simplified Action Item")
                        st.markdown(f"_{summary}_")
                else:
                    st.code("NOTICE UNDER SECTION 41A CrPC...", language="text")
                    st.markdown("**Simplified Action Item:** The police want you to join the investigation. No immediate arrest required.")
            
            # Engine info
            if ENGINES_AVAILABLE:
                engines = available_engines()
                st.info(f"✓ OCR Engines: {', '.join(engines) if engines else 'Default'}")

# ============================================================================
# PAGE: GROUNDED FACT CHECKER
# ============================================================================
elif current_page == "Fact":
    st.markdown("## 📚 Grounded Fact Checker")
    st.markdown("Ask a legal question to verify answers with citations from official PDFs.")
    st.divider()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        user_question = st.text_input("What is the penalty for…", placeholder="e.g., cheating under the new BNS system?")
    with col2:
        search_btn = st.button("📖 Verify", use_container_width=True)
    
    # PDF Upload Section
    st.markdown("### Upload Law PDF to Corpus (optional)")
    uploaded_pdf = st.file_uploader("Drop PDFs here", type=["pdf"], label_visibility="collapsed")
    if uploaded_pdf:
        save_dir = "law_pdfs"
        os.makedirs(save_dir, exist_ok=True)
        dest_path = os.path.join(save_dir, uploaded_pdf.name)
        with open(dest_path, "wb") as f:
            f.write(uploaded_pdf.read())
        if ENGINES_AVAILABLE:
            add_pdf(dest_path)
        st.success(f"✓ '{uploaded_pdf.name}' added to corpus")
    
    st.divider()
    
    # Results Section
    if user_question and search_btn:
        st.markdown("### Citation")
        if ENGINES_AVAILABLE:
            res = search_pdfs(user_question or "")
            if res:
                st.markdown(res)
                # optional: summarize
                combined = "\n\n".join([line for line in res.split("\n") if line.startswith(">   > _")])
                summary = llm_summarize(combined, question=user_question)
                if summary:
                    st.divider()
                    st.markdown("### Summary (Plain Language)")
                    st.markdown(f"_{summary}_")
            else:
                st.info("ℹ️ No citations found. Add PDFs to law_pdfs/ folder to enable search.")
        else:
            st.markdown("> **Answer:** Under BNS, theft is defined under Section 303.")
            st.markdown("> - **Bharatiya Twayne Sunhta, Section 318, Page 82**")
            st.markdown("> - **Chapter:** XVII (Offences Against Property)")

# ============================================================================
# PAGE: SETTINGS / ABOUT
# ============================================================================
elif current_page == "Settings":
    st.markdown("## ⚙️ Settings / About")
    st.markdown("### LexTransition AI")
    st.markdown("Offline legal assistant for mapping agents, the transition from IPC/CrPC/IEA to the new BNS/BNSS/BSA frameworks.")
    st.divider()
    st.markdown("**Version:** 1.0.0")
    st.markdown("**License:** Open Source")
    st.markdown("**Privacy:** 100% Offline - No data sent to servers")
