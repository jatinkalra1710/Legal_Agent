import streamlit as st
import base64
import json
from pathlib import Path
import tempfile
import os
from PIL import Image
import io
import time

# Page configuration
st.set_page_config(
    page_title="Indian Legal Document Assistant - Multi-Agent",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .disclaimer-box {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .agent-result {
        background-color: #f8f9fa;
        border-left: 4px solid #28a745;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .analysis-section {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        padding: 20px;
        margin: 15px 0;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button {
        width: 100%;
        background-color: #0d6efd;
        color: white;
        font-weight: 600;
        padding: 0.75rem;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #0b5ed7;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        padding-bottom: 1rem;
    }
    .info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .ocr-status {
        background-color: #e7f3ff;
        border-left: 4px solid #0066cc;
        padding: 10px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .agent-progress {
        background-color: #fff;
        border: 2px solid #0d6efd;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Title and header
st.markdown("""
    <div class="info-card">
        <h1>⚖️ Indian Legal Document Assistant - Multi-Agent AI</h1>
        <p style="text-align: center; font-size: 1.1rem; margin: 0;">
            Advanced Multi-Agent System with OCR • Powered by Google Gemini 2.5 Flash
        </p>
    </div>
""", unsafe_allow_html=True)

# Prominent disclaimer
st.markdown("""
    <div class="disclaimer-box">
        <h3>⚠️ Important Disclaimer</h3>
        <p><strong>This is an AI-powered tool and NOT a substitute for professional legal advice.</strong></p>
        <ul>
            <li>This service is NOT regulated by any legal authority</li>
            <li>The analysis provided is for informational purposes only</li>
            <li>Always consult a qualified lawyer for legal matters</li>
            <li>The AI may make errors or provide incomplete information</li>
            <li>Do not make legal decisions based solely on this analysis</li>
        </ul>
    </div>
""", unsafe_allow_html=True)

# Sidebar with information
with st.sidebar:
    st.header("🤖 Multi-Agent System")
    st.write("""
    This advanced system uses **5 specialized AI agents** working together:
    
    1. **📸 OCR Agent** - Extracts text from images
    2. **🔍 Classification Agent** - Identifies document type
    3. **📋 Extraction Agent** - Pulls key information
    4. **⚖️ Legal Analysis Agent** - Interprets legal content
    5. **💡 Simplification Agent** - Converts to simple language
    """)
    
    st.header("📄 Supported Formats")
    st.write("- PDF Documents")
    st.write("- Images (JPG, PNG, JPEG) with OCR")
    
    st.header("🔑 API Configuration")
    gemini_api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        help="Get your free API key from https://ai.google.dev/"
    )
    
    if gemini_api_key:
        st.success("✅ API Key configured")
    else:
        st.warning("⚠️ Please enter your Gemini API key")
        st.info("Get it free at: https://ai.google.dev/")
    
    st.header("📚 Document Types")
    st.write("""
    - GST Notices & Circulars
    - Income Tax Notices
    - Criminal Law Documents
    - Civil Law Notices
    - Company Law Documents
    - Labour Law Notices
    - Property Legal Documents
    """)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Upload Your Document")
    uploaded_file = st.file_uploader(
        "Choose a legal document (PDF or Image)",
        type=['pdf', 'png', 'jpg', 'jpeg'],
        help="Upload a PDF or image of your legal notice, circular, or document"
    )
    
    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Show file details
        file_size = len(uploaded_file.getvalue()) / 1024
        st.write(f"**File size:** {file_size:.2f} KB")
        st.write(f"**File type:** {uploaded_file.type}")
        
        # Show image preview if it's an image
        if uploaded_file.type in ["image/jpeg", "image/jpg", "image/png"]:
            st.image(uploaded_file, caption="Document Preview", use_container_width=True)

with col2:
    st.subheader("🎯 Analysis Options")
    
    language = st.selectbox(
        "Preferred explanation language",
        ["English", "Hindi + English (Hinglish)", "English with Hindi legal terms"],
        help="Choose the language for the explanation"
    )
    
    detail_level = st.select_slider(
        "Level of detail",
        options=["Brief Summary", "Standard", "Detailed Analysis"],
        value="Standard",
        help="Choose how detailed you want the analysis to be"
    )
    
    use_ocr = st.checkbox(
        "Enable OCR for images (extracts text from photos)",
        value=True,
        help="Uses OCR to extract text from images for better accuracy"
    )
    
    include_actions = st.checkbox(
        "Include suggested actions and next steps",
        value=True,
        help="Get recommendations on what to do next"
    )

# OCR Function using pytesseract
def extract_text_with_ocr(image_bytes):
    """Extract text from image using OCR"""
    try:
        # Try importing pytesseract
        import pytesseract
        from PIL import Image
        
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Perform OCR
        extracted_text = pytesseract.image_to_string(image, lang='eng+hin')
        
        return extracted_text.strip()
    except ImportError:
        # If pytesseract not available, try easyocr
        try:
            import easyocr
            
            # Save image temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name
            
            # Initialize reader
            reader = easyocr.Reader(['en', 'hi'])
            
            # Extract text
            results = reader.readtext(tmp_path)
            extracted_text = ' '.join([text[1] for text in results])
            
            # Clean up
            os.unlink(tmp_path)
            
            return extracted_text.strip()
        except:
            return None
    except Exception as e:
        st.error(f"OCR Error: {str(e)}")
        return None

# Gemini API call function
def call_gemini_api(api_key, prompt, system_instruction="", image_data=None, image_mime_type=None):
    """Call Google Gemini API with text or image"""
    try:
        import google.generativeai as genai
        
        # Configure API
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.5 Flash
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-exp',
            system_instruction=system_instruction
        )
        
        # Prepare content
        if image_data:
            # Create image part
            image_part = {
                'mime_type': image_mime_type,
                'data': image_data
            }
            response = model.generate_content([prompt, image_part])
        else:
            response = model.generate_content(prompt)
        
        return response.text
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"

# Agent 1: OCR Agent
def ocr_agent(file_content, file_type, use_ocr):
    """Agent 1: Extract text from images using OCR"""
    if not use_ocr or file_type == "application/pdf":
        return None
    
    st.markdown('<div class="agent-progress">🤖 **OCR Agent** is processing your image...</div>', unsafe_allow_html=True)
    
    extracted_text = extract_text_with_ocr(file_content)
    
    if extracted_text:
        st.markdown(f'''
        <div class="agent-result">
            <h4>✅ OCR Agent - Text Extraction Complete</h4>
            <p><strong>Extracted {len(extracted_text)} characters</strong></p>
            <details>
                <summary>View extracted text</summary>
                <pre style="white-space: pre-wrap; max-height: 200px; overflow-y: auto;">{extracted_text[:500]}...</pre>
            </details>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown('''
        <div class="ocr-status">
            ℹ️ OCR not available. Install pytesseract or easyocr for text extraction from images.
            Continuing with image analysis...
        </div>
        ''', unsafe_allow_html=True)
    
    return extracted_text

# Agent 2: Classification Agent
def classification_agent(api_key, file_content, file_type, ocr_text=None):
    """Agent 2: Classify document type"""
    st.markdown('<div class="agent-progress">🤖 **Classification Agent** is identifying document type...</div>', unsafe_allow_html=True)
    
    system_instruction = """You are a legal document classification expert specializing in Indian laws.
Your task is to identify the type of legal document and categorize it accurately.

Possible categories:
- GST Notice/Circular
- Income Tax Notice
- Criminal Law Document (FIR, Summons, etc.)
- Civil Notice
- Company Law Document
- Labour Law Notice
- Property Document
- Court Order/Judgment
- Legal Notice (General)
- Other

Provide a brief classification with confidence level."""

    prompt = """Analyze this legal document and provide:
1. Document Type (be specific)
2. Issuing Authority (who sent it)
3. Confidence Level (High/Medium/Low)
4. Brief reasoning for classification

Be concise but accurate."""

    if ocr_text:
        prompt += f"\n\nExtracted Text:\n{ocr_text[:2000]}"
    
    # Prepare image data if needed
    image_data = None
    image_mime_type = None
    
    if file_type in ["image/jpeg", "image/jpg", "image/png"]:
        image_data = base64.b64encode(file_content).decode('utf-8')
        image_mime_type = file_type
    
    result = call_gemini_api(api_key, prompt, system_instruction, image_data, image_mime_type)
    
    st.markdown(f'''
    <div class="agent-result">
        <h4>✅ Classification Agent - Document Identified</h4>
        <div>{result}</div>
    </div>
    ''', unsafe_allow_html=True)
    
    return result

# Agent 3: Content Extraction Agent
def extraction_agent(api_key, file_content, file_type, classification, ocr_text=None):
    """Agent 3: Extract key information from document"""
    st.markdown('<div class="agent-progress">🤖 **Extraction Agent** is pulling key information...</div>', unsafe_allow_html=True)
    
    system_instruction = """You are a legal information extraction expert for Indian legal documents.
Your task is to extract key structured information from legal documents including:
- Case/Notice Numbers
- Dates and Deadlines
- Amounts/Penalties
- Sections/Acts cited
- Parties involved
- Key demands or orders"""

    prompt = f"""Based on this classification: {classification}

Extract the following information from the document:
1. Reference/Case/Notice Number
2. Date of Issue
3. Critical Deadlines (if any)
4. Legal Provisions/Sections Cited
5. Parties Involved (Sender, Recipient)
6. Key Demands/Orders/Actions Required
7. Financial Amounts (if any)

Present in a structured format. Mark items as "Not Found" if not present."""

    if ocr_text:
        prompt += f"\n\nExtracted Text:\n{ocr_text[:2000]}"
    
    # Prepare image data if needed
    image_data = None
    image_mime_type = None
    
    if file_type in ["image/jpeg", "image/jpg", "image/png"]:
        image_data = base64.b64encode(file_content).decode('utf-8')
        image_mime_type = file_type
    
    result = call_gemini_api(api_key, prompt, system_instruction, image_data, image_mime_type)
    
    st.markdown(f'''
    <div class="agent-result">
        <h4>✅ Extraction Agent - Key Information Retrieved</h4>
        <div>{result}</div>
    </div>
    ''', unsafe_allow_html=True)
    
    return result

# Agent 4: Legal Analysis Agent
def legal_analysis_agent(api_key, file_content, file_type, classification, extraction, ocr_text=None):
    """Agent 4: Provide legal analysis and interpretation"""
    st.markdown('<div class="agent-progress">🤖 **Legal Analysis Agent** is interpreting legal implications...</div>', unsafe_allow_html=True)
    
    system_instruction = """You are an expert Indian legal analyst with deep knowledge of:
- GST laws and regulations
- Income Tax Act
- Criminal laws (IPC, CrPC, BNSS)
- Civil Procedure Code
- Company law
- Labour laws
- Property laws

Your role is to provide accurate legal interpretation and implications analysis."""

    prompt = f"""Document Classification: {classification}

Extracted Information: {extraction}

Provide a legal analysis covering:
1. Legal Basis - What law/section is this based on?
2. Implications - What does this mean legally for the recipient?
3. Seriousness Level - How serious is this matter? (Critical/High/Medium/Low)
4. Rights of Recipient - What rights does the recipient have?
5. Potential Consequences - What could happen if ignored or not addressed?
6. Time Sensitivity - How urgent is action required?

Be accurate and professional in your analysis."""

    if ocr_text:
        prompt += f"\n\nDocument Text (for reference):\n{ocr_text[:1500]}"
    
    # Prepare image data if needed
    image_data = None
    image_mime_type = None
    
    if file_type in ["image/jpeg", "image/jpg", "image/png"]:
        image_data = base64.b64encode(file_content).decode('utf-8')
        image_mime_type = file_type
    
    result = call_gemini_api(api_key, prompt, system_instruction, image_data, image_mime_type)
    
    st.markdown(f'''
    <div class="agent-result">
        <h4>✅ Legal Analysis Agent - Professional Assessment Complete</h4>
        <div>{result}</div>
    </div>
    ''', unsafe_allow_html=True)
    
    return result

# Agent 5: Simplification Agent
def simplification_agent(api_key, classification, extraction, legal_analysis, language, include_actions):
    """Agent 5: Convert to simple layman language"""
    st.markdown('<div class="agent-progress">🤖 **Simplification Agent** is creating easy-to-understand explanation...</div>', unsafe_allow_html=True)
    
    language_instruction = {
        "English": "Use simple English that a common person can understand. Avoid legal jargon.",
        "Hindi + English (Hinglish)": "Use a mix of Hindi and English (Hinglish) that's comfortable for Indian users. Example: 'Aapko is notice ka reply dena hoga within 30 days.'",
        "English with Hindi legal terms": "Use English but keep common Hindi legal terms that people are familiar with (like 'nyay', 'kanoon', 'adalat')."
    }
    
    system_instruction = f"""You are a legal communicator specializing in making complex Indian legal documents understandable to common people.

Language Preference: {language_instruction[language]}

Your goal is to explain legal matters in the simplest possible way while maintaining accuracy."""

    prompt = f"""Based on this analysis:

Classification: {classification}

Key Information: {extraction}

Legal Analysis: {legal_analysis}

Create a simple, easy-to-understand explanation covering:

1. **What is this document?** (In one simple sentence)

2. **Who sent it and why?** (Plain language)

3. **What does it say?** (Main points in simple terms)

4. **Important dates to remember** (If any deadlines)

5. **What it means for you** (Real impact in simple words)

6. **How serious is this?** (Use emoji: 🔴 Very Serious, 🟡 Moderately Serious, 🟢 Not Very Serious)
"""

    if include_actions:
        prompt += """
7. **What should you do now?** (Step-by-step action plan)
   - Immediate actions (do today/this week)
   - Short-term actions (do this month)
   - When to definitely consult a lawyer

8. **Red Flags** (Things that make it urgent to see a lawyer immediately)
"""

    prompt += """
Remember: Use simple language that a person without legal knowledge can easily understand. Imagine explaining to a family member or friend."""

    result = call_gemini_api(api_key, prompt, system_instruction)
    
    return result

# Main Analysis Function - Multi-Agent Orchestration
def multi_agent_analysis(api_key, file_content, file_name, file_type, language, detail_level, use_ocr, include_actions):
    """Orchestrate all agents for comprehensive analysis"""
    
    results = {}
    
    st.markdown("## 🤖 Multi-Agent Analysis in Progress")
    st.markdown("---")
    
    # Agent 1: OCR (if image and OCR enabled)
    ocr_text = None
    if file_type in ["image/jpeg", "image/jpg", "image/png"] and use_ocr:
        ocr_text = ocr_agent(file_content, file_type, use_ocr)
        results['ocr'] = ocr_text
        time.sleep(0.5)
    
    # Agent 2: Classification
    classification = classification_agent(api_key, file_content, file_type, ocr_text)
    results['classification'] = classification
    time.sleep(0.5)
    
    # Agent 3: Extraction
    extraction = extraction_agent(api_key, file_content, file_type, classification, ocr_text)
    results['extraction'] = extraction
    time.sleep(0.5)
    
    # Agent 4: Legal Analysis
    legal_analysis = legal_analysis_agent(api_key, file_content, file_type, classification, extraction, ocr_text)
    results['legal_analysis'] = legal_analysis
    time.sleep(0.5)
    
    # Agent 5: Simplification
    st.markdown("---")
    st.markdown("## 📝 Final Analysis - Simple Language Explanation")
    simplified = simplification_agent(api_key, classification, extraction, legal_analysis, language, include_actions)
    results['simplified'] = simplified
    
    return results

# Analysis button and results
if uploaded_file and gemini_api_key:
    st.markdown("---")
    
    if st.button("🚀 Start Multi-Agent Analysis", key="analyze_btn"):
        with st.spinner("🔄 Multi-Agent system working... This may take 30-60 seconds..."):
            # Get file content
            file_content = uploaded_file.getvalue()
            file_type = uploaded_file.type
            file_name = uploaded_file.name
            
            # Run multi-agent analysis
            results = multi_agent_analysis(
                gemini_api_key,
                file_content,
                file_name,
                file_type,
                language,
                detail_level,
                use_ocr,
                include_actions
            )
            
            # Display final simplified analysis
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown(results['simplified'])
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Additional disclaimer after results
            st.warning("⚠️ **Reminder**: This is an AI-generated analysis from multiple AI agents. Please consult a qualified lawyer for official legal advice.")
            
            # Download options
            col1, col2 = st.columns(2)
            
            with col1:
                # Download simple analysis
                st.download_button(
                    label="💾 Download Simple Analysis",
                    data=results['simplified'],
                    file_name=f"simple_analysis_{file_name}.txt",
                    mime="text/plain"
                )
            
            with col2:
                # Download full report
                full_report = f"""INDIAN LEGAL DOCUMENT ANALYSIS - FULL REPORT
Generated by Multi-Agent AI System
{'='*60}

DOCUMENT: {file_name}
ANALYSIS DATE: {time.strftime('%Y-%m-%d %H:%M:%S')}

{'='*60}
AGENT 1: CLASSIFICATION
{'='*60}
{results['classification']}

{'='*60}
AGENT 2: KEY INFORMATION EXTRACTION
{'='*60}
{results['extraction']}

{'='*60}
AGENT 3: LEGAL ANALYSIS
{'='*60}
{results['legal_analysis']}

{'='*60}
FINAL: SIMPLIFIED EXPLANATION
{'='*60}
{results['simplified']}

{'='*60}
DISCLAIMER
{'='*60}
This is an AI-generated analysis and NOT legal advice.
Always consult a qualified lawyer for legal matters.
This analysis is for informational purposes only.
"""
                st.download_button(
                    label="📄 Download Full Report",
                    data=full_report,
                    file_name=f"full_analysis_{file_name}.txt",
                    mime="text/plain"
                )

elif uploaded_file and not gemini_api_key:
    st.error("⚠️ Please enter your Google Gemini API key in the sidebar to continue.")
    st.info("👉 Get your free API key at: https://ai.google.dev/")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p><strong>Indian Legal Document Assistant - Multi-Agent System</strong></p>
        <p>Powered by Google Gemini 2.5 Flash • 5 Specialized AI Agents</p>
        <p style="font-size: 0.9rem;">
            For emergencies or serious legal matters, please contact a lawyer immediately.<br>
            This tool is for informational purposes only and does not constitute legal advice.
        </p>
    </div>
""", unsafe_allow_html=True)
