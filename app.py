import os
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# ==================================
# PAGE CONFIG
# ==================================

st.set_page_config(
    page_title="Hotel Contracts Assistant",
    page_icon="📄",
    layout="wide"
)

# ==================================
# CREATE CONTRACTS FOLDER
# ==================================

contracts_folder = "contracts"

if not os.path.exists(contracts_folder
