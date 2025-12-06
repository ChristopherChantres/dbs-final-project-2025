"""UI funciones para aplicar un tema personalizado a la app."""

import streamlit as st


def aplicar_tema_personalizado():
    """Aplica un tema personalizado a la app."""
    st.markdown(
        """
        <style>
            /* ===== COLOR PALETTE ===== */
            /* Main background - Soft dark gray */
            .stApp {
                background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%) !important;
            }
            
            /* Main container background */
            .block-container {
                background-color: transparent !important;
                padding-top: 2rem !important;
            }
            
            /* Sidebar background - Slightly lighter for contrast */
            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #1e2329 0%, #252b33 100%) !important;
                border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
            }
            
            /* ===== TYPOGRAPHY ===== */
            /* Text colors - High contrast for readability */
            .stApp, .stMarkdown, .markdown-text-container, 
            .stText, .stTitle, h1, h2, h3, h4, h5, h6, 
            .stHeader, .stSubheader, p, span, div {
                color: #e4e7eb !important;
            }
            
            /* Headings with subtle accent */
            h1, h2, h3 {
                color: #f0f3f6 !important;
                font-weight: 600 !important;
            }
            
            /* ===== BUTTONS ===== */
            /* Primary button - Modern blue with hover effect */
            .stButton > button {
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
                color: #ffffff !important;
                border: none !important;
                border-radius: 8px !important;
                font-weight: 500 !important;
                transition: all 0.2s ease !important;
                box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3) !important;
            }
            
            .stButton > button:hover {
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4) !important;
                transform: translateY(-1px) !important;
            }
            
            /* ===== INPUT FIELDS ===== */
            /* Text inputs */
            .stTextInput>div>div>input,
            .stNumberInput>div>div>input,
            .stTextArea>div>div>textarea {
                background-color: #1e2329 !important;
                color: #e4e7eb !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 6px !important;
                padding: 0.5rem 0.75rem !important;
            }
            
            .stTextInput>div>div>input:focus,
            .stNumberInput>div>div>input:focus,
            .stTextArea>div>div>textarea:focus {
                border-color: #3b82f6 !important;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
            }
            
            /* Selectbox */
            .stSelectbox>div>div>div {
                background-color: #1e2329 !important;
                color: #e4e7eb !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 6px !important;
            }
            
            .stSelectbox>div>div>div:focus-within {
                border-color: #3b82f6 !important;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
            }
            
            /* Date input */
            .stDateInput>div>div>input {
                background-color: #1e2329 !important;
                color: #e4e7eb !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 6px !important;
            }
            
            /* ===== CARDS AND CONTAINERS ===== */
            /* Metric cards */
            [data-testid="stMetricValue"] {
                color: #60a5fa !important;
            }
            
            /* Expander */
            .streamlit-expanderHeader {
                background-color: rgba(255, 255, 255, 0.03) !important;
                color: #e4e7eb !important;
                border-radius: 6px !important;
            }
            
            /* ===== SCROLLBAR ===== */
            /* Custom scrollbar for dark mode */
            ::-webkit-scrollbar {
                width: 10px !important;
                height: 10px !important;
            }
            
            ::-webkit-scrollbar-track {
                background: #0f1419 !important;
                border-radius: 5px !important;
            }
            
            ::-webkit-scrollbar-thumb {
                background: #374151 !important;
                border-radius: 5px !important;
                border: 2px solid #0f1419 !important;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: #4b5563 !important;
            }
            
            /* ===== TABLES ===== */
            table {
                background-color: rgba(255, 255, 255, 0.02) !important;
                border-radius: 8px !important;
            }
            
            thead {
                background-color: rgba(255, 255, 255, 0.05) !important;
            }
            
            th {
                color: #f0f3f6 !important;
                font-weight: 600 !important;
            }
            
            td {
                color: #e4e7eb !important;
            }
            
            /* ===== CODE BLOCKS ===== */
            code {
                background-color: rgba(255, 255, 255, 0.08) !important;
                color: #60a5fa !important;
                padding: 2px 6px !important;
                border-radius: 4px !important;
            }
            
            pre {
                background-color: #1e2329 !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 6px !important;
            }
            
            /* ===== ALERTS AND INFO BOXES ===== */
            .stAlert {
                background-color: rgba(59, 130, 246, 0.1) !important;
                border-left: 4px solid #3b82f6 !important;
                border-radius: 6px !important;
            }
            
            /* ===== SIDEBAR SPECIFIC ===== */
            [data-testid="stSidebar"] .stMarkdown {
                color: #cbd5e1 !important;
            }
            
            /* ===== REMOVE STREAMLIT BRANDING ===== */
            # MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )

