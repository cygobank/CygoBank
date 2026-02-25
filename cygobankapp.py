"""
STREAMLIT BANKING APP - Web Version
A fully functional banking system with web interface
"""

import streamlit as st
import json
import os
from datetime import datetime
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import pandas as pd

# ========== CONFIGURATION ==========
TESTING_MODE = True  # Set to False for real emails

EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your_bank_email@gmail.com',
    'sender_password': 'your_app_password',
    'use_tls': True
}

# ========== DATA PERSISTENCE ==========
def load_accounts():
    """Load accounts from JSON file"""
    if os.path.exists('bank_accounts.json'):
        try:
            with open('bank_accounts.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_accounts(accounts):
    """Save accounts to JSON file"""
    with open('bank_accounts.json', 'w') as f:
        json.dump(accounts, f, indent=2)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ========== PHONE VALIDATION ==========
COUNTRY_PHONE_FORMATS = {
    'USA': {
        'code': '+1',
        'pattern': r'^[2-9][0-9]{2}-[2-9][0-9]{2}-[0-9]{4}$',
        'example': '404-401-3601',
        'description': 'XXX-XXX-XXXX'
    },
    'Canada': {
        'code': '+1',
        'pattern': r'^[2-9][0-9]{2}-[2-9][0-9]{2}-[0-9]{4}$',
        'example': '416-555-0123',
        'description': 'XXX-XXX-XXXX'
    },
    'United Kingdom': {
        'code': '+44',
        'pattern': r'^\+44\s?[1-9][0-9]{1,4}[\s.-]?[0-9]{3,4}[\s.-]?[0-9]{3,4}$',
        'example': '+44 20 7946 0958',
        'description': '+44 XXXX XXXX XXXX'
    },
    'Australia': {
        'code': '+61',
        'pattern': r'^\+61\s?[2-9][0-9]{8}$',
        'example': '+61 2 1234 5678',
        'description': '+61 X XXXX XXXX'
    },
    'Germany': {
        'code': '+49',
        'pattern': r'^\+49\s?[1-9][0-9]{1,5}[\s.-]?[0-9]{3,9}$',
        'example': '+49 30 12345678',
        'description': '+49 XX XXXXXXXX'
    },
    'France': {
        'code': '+33',
        'pattern': r'^\+33\s?[1-9][0-9]{8}$',
        'example': '+33 1 42 68 53 00',
        'description': '+33 X XX XX XX XX'
    },
    'India': {
        'code': '+91',
        'pattern': r'^\+91\s?[6-9][0-9]{9}$',
        'example': '+91 98765 43210',
        'description': '+91 XXXXX XXXXX'
    },
    'Japan': {
        'code': '+81',
        'pattern': r'^\+81\s?[1-9][0-9]{1,4}[\s.-]?[0-9]{1,4}[\s.-]?[0-9]{4}$',
        'example': '+81 3-1234-5678',
        'description': '+81 X XXXX XXXX'
    },
    'Cameroon': {
        'code': '+237',
        'pattern': r'^\+237\s?[2367][0-9]{7}$',
        'example': '+237 6 7812 3456',
        'description': '+237 X XXXX XXXX'
    },
    'South Africa': {
        'code': '+27',
        'pattern': r'^\+27\s?[1-9][0-9]{8}$',
        'example': '+27 11 555 1234',
        'description': '+27 XX XXX XXXX'
    },
    'Brazil': {
        'code': '+55',
        'pattern': r'^\+55\s?\(?[1-9][0-9]\)?\s?[3-9][0-9]{3,4}[\s.-]?[0-9]{4}$',
        'example': '+55 (11) 98765-4321',
        'description': '(XX) XXXXX-XXXX'
    },
    'Mexico': {
        'code': '+52',
        'pattern': r'^\+52\s?[1-9][0-9]{9}$',
        'example': '+52 55 1234 5678',
        'description': '+52 XX XXXX XXXX'
    },
    'China': {
        'code': '+86',
        'pattern': r'^\+86\s?1[3-9][0-9]{9}$',
        'example': '+86 138 0001 2345',
        'description': '+86 1XX XXXX XXXX'
    },
    'Russia': {
        'code': '+7',
        'pattern': r'^\+7\s?[1-9][0-9]{9}$',
        'example': '+7 499 123 4567',
        'description': '+7 XXX XXX XXXX'
    },
    'Spain': {
        'code': '+34',
        'pattern': r'^\+34\s?[1-9][0-9]{8}$',
        'example': '+34 912 34 5678',
        'description': '+34 XXX XXX XXXX'
    },
    'Italy': {
        'code': '+39',
        'pattern': r'^\+39\s?[0-9]{6,10}$',
        'example': '+39 06 1234 5678',
        'description': '+39 XX XXXX XXXX'
    },
    'Netherlands': {
        'code': '+31',
        'pattern': r'^\+31\s?[1-9][0-9]{8}$',
        'example': '+31 20 123 4567',
        'description': '+31 XX XXX XXXX'
    },
    'Belgium': {
        'code': '+32',
        'pattern': r'^\+32\s?[1-9][0-9]{8}$',
        'example': '+32 2 123 4567',
        'description': '+32 X XXX XXXX'
    },
    'Switzerland': {
        'code': '+41',
        'pattern': r'^\+41\s?[1-9][0-9]{8}$',
        'example': '+41 44 123 4567',
        'description': '+41 XX XXX XXXX'
    },
    'Sweden': {
        'code': '+46',
        'pattern': r'^\+46\s?[1-9][0-9]{8}$',
        'example': '+46 8 123 4567',
        'description': '+46 X XXX XXXX'
    },
    'Norway': {
        'code': '+47',
        'pattern': r'^\+47\s?[4-9][0-9]{7}$',
        'example': '+47 412 34 567',
        'description': '+47 XXX XX XXX'
    },
    'Denmark': {
        'code': '+45',
        'pattern': r'^\+45\s?[1-9][0-9]{7}$',
        'example': '+45 1234 5678',
        'description': '+45 XXXX XXXX'
    },
    'Poland': {
        'code': '+48',
        'pattern': r'^\+48\s?[1-9][0-9]{8}$',
        'example': '+48 12 123 4567',
        'description': '+48 XX XXX XXXX'
    },
    'New Zealand': {
        'code': '+64',
        'pattern': r'^\+64\s?[1-9][0-9]{7,9}$',
        'example': '+64 9 123 4567',
        'description': '+64 X XXX XXXX'
    },
    'Singapore': {
        'code': '+65',
        'pattern': r'^\+65\s?[6-9][0-9]{7}$',
        'example': '+65 6123 4567',
        'description': '+65 XXXX XXXX'
    },
    'Hong Kong': {
        'code': '+852',
        'pattern': r'^\+852\s?[2-9][0-9]{7}$',
        'example': '+852 2123 4567',
        'description': '+852 XXXX XXXX'
    },
    'Thailand': {
        'code': '+66',
        'pattern': r'^\+66\s?[2-9][0-9]{7,8}$',
        'example': '+66 2 123 4567',
        'description': '+66 X XXXX XXXX'
    },
    'Malaysia': {
        'code': '+60',
        'pattern': r'^\+60\s?[1-9][0-9]{7,9}$',
        'example': '+60 3 1234 5678',
        'description': '+60 X XXXX XXXX'
    },
    'Philippines': {
        'code': '+63',
        'pattern': r'^\+63\s?[2-9][0-9]{8,9}$',
        'example': '+63 2 1234 5678',
        'description': '+63 X XXXX XXXX'
    },
    'Indonesia': {
        'code': '+62',
        'pattern': r'^\+62\s?[1-9][0-9]{7,10}$',
        'example': '+62 21 1234 5678',
        'description': '+62 XX XXXX XXXX'
    },
    'Vietnam': {
        'code': '+84',
        'pattern': r'^\+84\s?[1-9][0-9]{7,9}$',
        'example': '+84 24 1234 5678',
        'description': '+84 XX XXXX XXXX'
    },
    'Pakistan': {
        'code': '+92',
        'pattern': r'^\+92\s?[3][0-9]{9}$',
        'example': '+92 300 1234 567',
        'description': '+92 XXX XXXX XXX'
    },
    'Bangladesh': {
        'code': '+880',
        'pattern': r'^\+880\s?1[1-9][0-9]{8}$',
        'example': '+880 171 234 5678',
        'description': '+880 1XX XXXX XXXX'
    },
    'Nigeria': {
        'code': '+234',
        'pattern': r'^\+234\s?[7-9][0-9]{9}$',
        'example': '+234 701 234 5678',
        'description': '+234 XXX XXXX XXXX'
    },
    'Egypt': {
        'code': '+20',
        'pattern': r'^\+20\s?1[0-1][0-9]{8}$',
        'example': '+20 100 123 4567',
        'description': '+20 1XX XXX XXXX'
    },
    'Kenya': {
        'code': '+254',
        'pattern': r'^\+254\s?[7][0-9]{8}$',
        'example': '+254 701 234 567',
        'description': '+254 XXX XXX XXX'
    },
    'Argentina': {
        'code': '+54',
        'pattern': r'^\+54\s?\(?[1-9]{1,3}\)?\s?[1-9][0-9]{3,4}[\s.-]?[0-9]{4}$',
        'example': '+54 (11) 1234-5678',
        'description': '(XXX) XXXX-XXXX'
    },
    'Chile': {
        'code': '+56',
        'pattern': r'^\+56\s?[2-9][0-9]{8}$',
        'example': '+56 2 1234 5678',
        'description': '+56 X XXXX XXXX'
    },
    'Colombia': {
        'code': '+57',
        'pattern': r'^\+57\s?[1-9][0-9]{8,9}$',
        'example': '+57 1 1234 5678',
        'description': '+57 X XXXX XXXX'
    },
    'Peru': {
        'code': '+51',
        'pattern': r'^\+51\s?[1-9][0-9]{8}$',
        'example': '+51 1 1234 5678',
        'description': '+51 X XXXX XXXX'
    },
    'Turkey': {
        'code': '+90',
        'pattern': r'^\+90\s?[1-9][0-9]{9}$',
        'example': '+90 212 123 4567',
        'description': '+90 XXX XXX XXXX'
    },
    'Saudi Arabia': {
        'code': '+966',
        'pattern': r'^\+966\s?[1-9][0-9]{8}$',
        'example': '+966 11 1234 567',
        'description': '+966 XX XXXX XXX'
    },
    'UAE': {
        'code': '+971',
        'pattern': r'^\+971\s?[1-9][0-9]{7,8}$',
        'example': '+971 4 1234 5678',
        'description': '+971 X XXXX XXXX'
    },
    'Israel': {
        'code': '+972',
        'pattern': r'^\+972\s?[1-9][0-9]{8}$',
        'example': '+972 2 1234 567',
        'description': '+972 X XXXX XXXX'
    },
    'Greece': {
        'code': '+30',
        'pattern': r'^\+30\s?[1-9][0-9]{9}$',
        'example': '+30 2 1234 5678',
        'description': '+30 X XXXX XXXX'
    },
    'Ireland': {
        'code': '+353',
        'pattern': r'^\+353\s?[1-9][0-9]{8}$',
        'example': '+353 1 234 5678',
        'description': '+353 X XXX XXXX'
    },
    'Portugal': {
        'code': '+351',
        'pattern': r'^\+351\s?[1-9][0-9]{8}$',
        'example': '+351 21 1234 567',
        'description': '+351 XX XXXX XXX'
    },
    'Austria': {
        'code': '+43',
        'pattern': r'^\+43\s?[1-9][0-9]{8}$',
        'example': '+43 1 1234 567',
        'description': '+43 X XXXX XXXX'
    },
    'Czech Republic': {
        'code': '+420',
        'pattern': r'^\+420\s?[1-9][0-9]{8}$',
        'example': '+420 2 1234 5678',
        'description': '+420 X XXXX XXXX'
    },
    'Hungary': {
        'code': '+36',
        'pattern': r'^\+36\s?[1-9][0-9]{8}$',
        'example': '+36 1 1234 5678',
        'description': '+36 X XXXX XXXX'
    },
    'Romania': {
        'code': '+40',
        'pattern': r'^\+40\s?[1-9][0-9]{8}$',
        'example': '+40 21 1234 567',
        'description': '+40 XX XXXX XXX'
    },
    'Ukraine': {
        'code': '+380',
        'pattern': r'^\+380\s?[1-9][0-9]{8}$',
        'example': '+380 44 1234 567',
        'description': '+380 XX XXXX XXX'
    },
    'Finland': {
        'code': '+358',
        'pattern': r'^\+358\s?[1-9][0-9]{7,8}$',
        'example': '+358 9 1234 567',
        'description': '+358 X XXXX XXX'
    },
    'Iceland': {
        'code': '+354',
        'pattern': r'^\+354\s?[1-9][0-9]{6}$',
        'example': '+354 123 4567',
        'description': '+354 XXX XXXX'
    },
    'Luxembourg': {
        'code': '+352',
        'pattern': r'^\+352\s?[1-9][0-9]{8}$',
        'example': '+352 1234 5678',
        'description': '+352 XXXX XXXX'
    },
    'Malta': {
        'code': '+356',
        'pattern': r'^\+356\s?[1-9][0-9]{7}$',
        'example': '+356 7123 4567',
        'description': '+356 XXXX XXXX'
    },
    'Cyprus': {
        'code': '+357',
        'pattern': r'^\+357\s?2[0-6][0-9]{6}$',
        'example': '+357 22 1234 567',
        'description': '+357 XX XXXX XXX'
    },
}


def validate_phone(phone_number, country):
    """Validate phone number based on country format"""
    if country not in COUNTRY_PHONE_FORMATS:
        return False
    
    pattern = COUNTRY_PHONE_FORMATS[country]['pattern']
    return re.match(pattern, phone_number) is not None

def get_phone_format_help(country):
    """Get phone format help text for a country"""
    if country in COUNTRY_PHONE_FORMATS:
        fmt = COUNTRY_PHONE_FORMATS[country]
        return f"Example: {fmt['example']} | Format: {fmt['description']}"
    return ""

# ========== SSN VALIDATION ==========
def validate_ssn(ssn):
    """Validate SSN format (XXX-XX-XXXX)"""
    # Acceptable formats: 123-45-6789 or 123456789
    pattern = r'^(?:\d{3}-\d{2}-\d{4}|\d{9})$'
    if not re.match(pattern, ssn):
        return False
    # Additional validation: avoid all zeros or invalid SSN ranges
    digits_only = ssn.replace('-', '')
    if digits_only == '000000000' or digits_only == '666000000':
        return False
    # First three digits cannot be 000
    if digits_only[:3] == '000':
        return False
    # Area number (first 3) cannot be 666
    if digits_only[:3] == '666':
        return False
    return True

# ========== DOB VALIDATION ==========
def validate_dob(dob_str):
    """Validate DOB format (dd/mm/yyyy) and check if it's a valid date"""
    pattern = r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/(\d{4})$'
    if not re.match(pattern, dob_str):
        return False
    
    try:
        day, month, year = dob_str.split('/')
        day, month, year = int(day), int(month), int(year)
        
        # Check if date is valid
        datetime(year, month, day)
        
        # Check if person is at least 18 years old
        today = datetime.now()
        age = today.year - year - ((today.month, today.day) < (month, day))
        if age < 18:
            return False
        
        # Check if year is reasonable (not in future, not too old)
        if year > today.year or year < (today.year - 120):
            return False
        
        return True
    except ValueError:
        return False


# ========== EMAIL FUNCTIONS ==========
def send_email_notification(recipient_email, subject, message_body):
    """Send email notification"""
    if TESTING_MODE:
        st.info(f"📧 Email would be sent to {recipient_email}\n\nSubject: {subject}")
        return True
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message_body, 'plain'))
        
        context = ssl.create_default_context()
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls(context=context)
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            server.send_message(msg)
        
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

# ========== TRANSACTION FUNCTIONS ==========
def log_transaction(account_number, transaction_type, amount, description=""):
    """Record a transaction"""
    accounts = load_accounts()
    if account_number in accounts:
        if 'transactions' not in accounts[account_number]:
            accounts[account_number]['transactions'] = []
        
        accounts[account_number]['transactions'].append({
            'type': transaction_type,
            'amount': amount,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'description': description
        })
        save_accounts(accounts)

def calculate_interest(balance, rate=0.01):
    """Calculate monthly interest"""
    return balance * rate

# ========== STREAMLIT UI ==========
def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_account' not in st.session_state:
        st.session_state.current_account = None
    if 'page' not in st.session_state:
        st.session_state.page = 'main'
    if 'accounts' not in st.session_state:
        st.session_state.accounts = load_accounts()

# ========== MAIN PAGES ==========
def main_menu():
    """Main menu page"""
    st.title("🏦 CyBank - Online Banking")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔑 Existing User")
        if st.button("Login", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()
    
    with col2:
        st.markdown("### 🆕 New User")
        if st.button("Create Account", use_container_width=True):
            st.session_state.page = 'create'
            st.rerun()
    
    # Show stats
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    accounts = load_accounts()
    with col1:
        st.metric("Total Accounts", len(accounts))
    with col2:
        total_balance = sum(float(a['balance']) for a in accounts.values()) if accounts else 0
        st.metric("Total Deposits", f"${total_balance:,.2f}")
    with col3:
        st.metric("Active Users", len([a for a in accounts.values() if float(a['balance']) > 0]))

def create_account_page():
    """Create new account page"""
    st.title("🆕 Create New Account")
    
    # Initialize session state for country selection if not exists
    if 'create_account_country' not in st.session_state:
        st.session_state.create_account_country = list(COUNTRY_PHONE_FORMATS.keys())[0]
    
    # Country selection outside form so it updates dynamically
    st.subheader("Location Information")
    col1, col2 = st.columns(2)
    with col1:
        country = st.selectbox(
            "Country",
            list(COUNTRY_PHONE_FORMATS.keys()),
            key='create_account_country'
        )
    with col2:
        country_code = COUNTRY_PHONE_FORMATS[country]['code']
        st.text_input("Country Code", value=country_code, disabled=True)
    
    st.markdown("---")
    st.subheader("Account Information")
    
    with st.form("create_account_form"):
        account_number = st.text_input("Account Number", help="Choose a unique account number")
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        
        phone_help = get_phone_format_help(country)
        phone_number = st.text_input("Phone Number", help=phone_help, placeholder=COUNTRY_PHONE_FORMATS[country]['example'])
        
        ssn = st.text_input("Social Security Number (SSN)", placeholder="e.g., 123-45-6789", help="Format: XXX-XX-XXXX")
        
        dob = st.text_input("Date of Birth", placeholder="e.g., 15/06/1990", help="Format: DD/MM/YYYY")
        
        st.markdown("---")
        st.subheader("📍 Address Information")
        street_address = st.text_input("Street Address", placeholder="e.g., 123 Main Street")
        
        col1, col2 = st.columns(2)
        with col1:
            apartment = st.text_input("Apt/Suite (Optional)", placeholder="e.g., Apt 456")
        with col2:
            city = st.text_input("City", placeholder="e.g., New York")
        
        col3, col4 = st.columns(2)
        with col3:
            county = st.text_input("County (Optional)", placeholder="e.g., Kings County")
        with col4:
            zip_code = st.text_input("Zip Code", placeholder="e.g., 10001")
        
        st.markdown("---")
        initial_deposit = st.number_input("Initial Deposit ($)", min_value=10.0, value=100.0)
        
        submitted = st.form_submit_button("Create Account", use_container_width=True)
        
        if submitted:
            accounts = load_accounts()
            
            # Validation
            if not account_number:
                st.error("❌ Account number cannot be empty!")
            elif account_number in accounts:
                st.error("❌ Account number already exists!")
            elif not name:
                st.error("❌ Name cannot be empty!")
            elif not validate_email(email):
                st.error("❌ Invalid email format!")
            elif not phone_number:
                st.error("❌ Phone number cannot be empty!")
            elif not validate_phone(phone_number, country):
                st.error(f"❌ Invalid phone format for {country}! Expected format: {get_phone_format_help(country)}")
            elif not ssn:
                st.error("❌ SSN cannot be empty!")
            elif not validate_ssn(ssn):
                st.error("❌ Invalid SSN format! Expected format: XXX-XX-XXXX (e.g., 123-45-6789)")
            elif not dob:
                st.error("❌ Date of Birth cannot be empty!")
            elif not validate_dob(dob):
                st.error("❌ Invalid DOB format or you must be at least 18 years old! Expected format: DD/MM/YYYY (e.g., 15/06/1990)")
            elif not street_address:
                st.error("❌ Street address cannot be empty!")
            elif not city:
                st.error("❌ City cannot be empty!")
            elif not zip_code:
                st.error("❌ Zip code cannot be empty!")
            else:
                # Create account
                accounts[account_number] = {
                    'name': name,
                    'email': email,
                    'phone': phone_number,
                    'ssn': ssn,
                    'dob': dob,
                    'country': country,
                    'address': {
                        'street': street_address,
                        'apartment': apartment,
                        'city': city,
                        'county': county,
                        'zip_code': zip_code
                    },
                    'balance': initial_deposit,
                    'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'transactions': [{
                        'type': 'DEPOSIT',
                        'amount': initial_deposit,
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'description': 'Initial deposit'
                    }],
                    'preferences': {
                        'email_notifications': True,
                        'low_balance_alert': True,
                        'alert_threshold': 100
                    }
                }
                
                save_accounts(accounts)
                
                # Send welcome email
                subject = "🎉 Welcome to Cy_Bank!"
                apt_info = f"\nApartment/Suite: {apartment}" if apartment else ""
                county_info = f"\nCounty: {county}" if county else ""
                body = f"""
Dear {name},

Welcome to Cy_Bank! Your account has been created successfully.

Account Number: {account_number}
Phone Number: {phone_number}
Country: {country}

Address:
{street_address}{apt_info}
{city}, {zip_code}{county_info}

Initial Deposit: ${initial_deposit:.2f}

Thank you for choosing Cy_Bank!
"""
                send_email_notification(email, subject, body)
                
                st.success(f"✅ Account created successfully!")
                st.balloons()
                
                # Auto login
                st.session_state.logged_in = True
                st.session_state.current_account = account_number
                st.session_state.page = 'dashboard'
                st.rerun()
    
    if st.button("← Back to Main Menu"):
        st.session_state.page = 'main'
        st.rerun()

def login_page():
    """Login page"""
    st.title("🔑 Login to Your Account")
    
    accounts = load_accounts()
    
    if not accounts:
        st.warning("No accounts found. Please create an account first.")
        if st.button("Create Account"):
            st.session_state.page = 'create'
            st.rerun()
        return
    
    # Initialize session state for login method
    if 'login_method' not in st.session_state:
        st.session_state.login_method = 'Account Number'
    
    # Login method selector
    st.subheader("Select Login Method")
    login_method = st.radio(
        "How would you like to login?",
        ["Account Number", "Phone Number"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if login_method == "Account Number":
        # Account number login
        account_list = list(accounts.keys())
        account_labels = [f"{acc} - {accounts[acc]['name']}" for acc in account_list]
        
        selected_index = st.selectbox(
            "Select your account",
            range(len(account_list)),
            format_func=lambda i: account_labels[i],
            key='account_number_select'
        )
        
        if st.button("Login", use_container_width=True):
            account_number = account_list[selected_index]
            st.session_state.logged_in = True
            st.session_state.current_account = account_number
            st.session_state.page = 'dashboard'
            st.success(f"✅ Welcome back, {accounts[account_number]['name']}!")
            st.rerun()
    
    else:  # Phone Number login
        phone_input = st.text_input("Enter your phone number", placeholder="e.g., +237 6 7812 3456")
        
        if st.button("Login", use_container_width=True):
            # Search for account with matching phone number
            matching_accounts = []
            for acc_num, acc_data in accounts.items():
                if acc_data.get('phone', '').strip().lower() == phone_input.strip().lower():
                    matching_accounts.append((acc_num, acc_data))
            
            if not matching_accounts:
                st.error("❌ No account found with this phone number. Please try again.")
            elif len(matching_accounts) == 1:
                account_number = matching_accounts[0][0]
                account_name = matching_accounts[0][1]['name']
                st.session_state.logged_in = True
                st.session_state.current_account = account_number
                st.session_state.page = 'dashboard'
                st.success(f"✅ Welcome back, {account_name}!")
                st.rerun()
            else:
                st.warning(f"⚠️ Multiple accounts found with this phone number. Please use Account Number login instead.")
    
    st.markdown("---")
    if st.button("← Back to Main Menu"):
        st.session_state.page = 'main'
        st.rerun()


def dashboard_page():
    """Main dashboard after login"""
    account_number = st.session_state.current_account
    accounts = load_accounts()
    
    if account_number not in accounts:
        st.error("Account not found!")
        st.session_state.logged_in = False
        st.session_state.page = 'main'
        st.rerun()
    
    account = accounts[account_number]
    balance = float(account['balance'])
    
    # Sidebar for navigation
    with st.sidebar:
        st.title(f"Welcome, {account['name']}!")
        st.markdown(f"**Account:** {account_number}")
        st.markdown(f"**Email:** {account.get('email', 'Not set')}")
        st.markdown(f"**Phone:** {account.get('phone', 'Not set')}")
        st.markdown(f"**Country:** {account.get('country', 'Not set')}")
        st.markdown(f"**Balance:** ${balance:,.2f}")
        st.markdown("---")
        
        menu_option = st.radio(
            "Navigation",
            ["Dashboard", "Deposit", "Withdraw", "Transfer", "History", "Settings", "Logout"]
        )
    
    # Main content area
    if menu_option == "Dashboard":
        show_dashboard(account_number, account, balance)
    elif menu_option == "Deposit":
        show_deposit(account_number, balance)
    elif menu_option == "Withdraw":
        show_withdraw(account_number, balance)
    elif menu_option == "Transfer":
        show_transfer(account_number, balance)
    elif menu_option == "History":
        show_history(account_number)
    elif menu_option == "Settings":
        show_settings(account_number)
    elif menu_option == "Logout":
        st.session_state.logged_in = False
        st.session_state.current_account = None
        st.session_state.page = 'main'
        st.success("Logged out successfully!")
        st.rerun()

def show_dashboard(account_number, account, balance):
    """Dashboard home"""
    st.title("📊 Account Dashboard")
    
    # Account summary cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Balance", f"${balance:,.2f}")
    with col2:
        st.metric("Account Status", "Active" if balance > 0 else "Low Balance")
    with col3:
        st.metric("Member Since", account.get('created', 'Unknown')[:10])
    
    # Quick actions
    st.markdown("---")
    st.subheader("Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💰 Deposit", use_container_width=True):
            st.session_state.quick_action = 'deposit'
    with col2:
        if st.button("💸 Withdraw", use_container_width=True):
            st.session_state.quick_action = 'withdraw'
    with col3:
        if st.button("📤 Transfer", use_container_width=True):
            st.session_state.quick_action = 'transfer'
    with col4:
        if st.button("📋 History", use_container_width=True):
            st.session_state.quick_action = 'history'
    
    # Recent transactions
    st.markdown("---")
    st.subheader("Recent Transactions")
    transactions = account.get('transactions', [])[-5:]  # Last 5
    if transactions:
        for t in reversed(transactions):
            amount = t['amount']
            sign = "+" if t['type'] in ['DEPOSIT', 'TRANSFER_IN', 'INTEREST'] else "-"
            color = "green" if sign == "+" else "red"
            
            st.markdown(
                f"**{t['date'][:16]}** | {t['type']} | "
                f":{color}[{sign}${amount:,.2f}] | {t.get('description', '')}"
            )
    else:
        st.info("No transactions yet")

def show_deposit(account_number, balance):
    """Deposit page"""
    st.title("💰 Make a Deposit")
    
    with st.form("deposit_form"):
        amount = st.number_input("Amount to deposit ($)", min_value=0.01, step=10.0)
        description = st.text_input("Description (optional)", placeholder="e.g., Salary, Gift, etc.")
        
        if st.form_submit_button("Deposit", use_container_width=True):
            if amount > 0:
                accounts = load_accounts()
                new_balance = balance + amount
                accounts[account_number]['balance'] = str(new_balance)
                save_accounts(accounts)
                
                log_transaction(account_number, 'DEPOSIT', amount, description)
                
                st.success(f"✅ Successfully deposited ${amount:,.2f}")
                st.metric("New Balance", f"${new_balance:,.2f}")
                st.balloons()
            else:
                st.error("Amount must be positive!")

def show_withdraw(account_number, balance):
    """Withdraw page"""
    st.title("💸 Make a Withdrawal")
    
    with st.form("withdraw_form"):
        amount = st.number_input("Amount to withdraw ($)", min_value=0.01, max_value=balance, step=10.0)
        description = st.text_input("Description (optional)", placeholder="e.g., ATM, Purchase, etc.")
        
        if st.form_submit_button("Withdraw", use_container_width=True):
            if amount > 0 and amount <= balance:
                accounts = load_accounts()
                new_balance = balance - amount
                accounts[account_number]['balance'] = str(new_balance)
                save_accounts(accounts)
                
                log_transaction(account_number, 'WITHDRAWAL', amount, description)
                
                st.success(f"✅ Successfully withdrew ${amount:,.2f}")
                st.metric("New Balance", f"${new_balance:,.2f}")
                
                # Check low balance alert
                if new_balance < 100:
                    st.warning("⚠️ Low balance alert! Your balance is below $100")
            else:
                st.error("Invalid amount or insufficient funds!")

def show_transfer(account_number, balance):
    """Transfer page"""
    st.title("📤 Transfer Money")
    
    accounts = load_accounts()
    other_accounts = [acc for acc in accounts.keys() if acc != account_number]
    
    if not other_accounts:
        st.warning("No other accounts available for transfer")
        return
    
    with st.form("transfer_form"):
        to_account = st.selectbox("Transfer to", other_accounts)
        amount = st.number_input("Amount to transfer ($)", min_value=0.01, max_value=balance, step=10.0)
        description = st.text_input("Description (optional)", placeholder="e.g., Rent, Payment, etc.")
        
        if st.form_submit_button("Transfer", use_container_width=True):
            if amount > 0 and amount <= balance:
                accounts = load_accounts()
                to_balance = float(accounts[to_account]['balance'])
                
                # Update balances
                accounts[account_number]['balance'] = str(balance - amount)
                accounts[to_account]['balance'] = str(to_balance + amount)
                save_accounts(accounts)
                
                # Log transactions
                log_transaction(account_number, 'TRANSFER_OUT', amount, f"To {to_account}")
                log_transaction(to_account, 'TRANSFER_IN', amount, f"From {account_number}")
                
                st.success(f"✅ Successfully transferred ${amount:,.2f} to account {to_account}")
                st.metric("New Balance", f"${balance - amount:,.2f}")
            else:
                st.error("Invalid amount or insufficient funds!")

def show_history(account_number):
    """Transaction history page"""
    st.title("📋 Transaction History")
    
    accounts = load_accounts()
    account = accounts.get(account_number, {})
    transactions = account.get('transactions', [])
    
    if transactions:
        # Convert to DataFrame for better display
        df = pd.DataFrame(transactions)
        df['amount_display'] = df.apply(
            lambda row: f"+${row['amount']:,.2f}" if row['type'] in ['DEPOSIT', 'TRANSFER_IN', 'INTEREST'] 
            else f"-${row['amount']:,.2f}",
            axis=1
        )
        
        # Display as table
        st.dataframe(
            df[['date', 'type', 'amount_display', 'description']].rename(
                columns={'date': 'Date', 'type': 'Type', 'amount_display': 'Amount', 'description': 'Description'}
            ),
            use_container_width=True
        )
        
        # Summary stats
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        total_deposits = sum(t['amount'] for t in transactions if t['type'] in ['DEPOSIT', 'TRANSFER_IN', 'INTEREST'])
        total_withdrawals = sum(t['amount'] for t in transactions if t['type'] in ['WITHDRAWAL', 'TRANSFER_OUT'])
        
        with col1:
            st.metric("Total Deposits", f"${total_deposits:,.2f}")
        with col2:
            st.metric("Total Withdrawals", f"${total_withdrawals:,.2f}")
        with col3:
            st.metric("Net Flow", f"${total_deposits - total_withdrawals:,.2f}")
    else:
        st.info("No transactions found")

def show_settings(account_number):
    """Settings page"""
    st.title("⚙️ Account Settings")
    
    accounts = load_accounts()
    account = accounts[account_number]
    
    # Initialize session state for country selection in settings
    if 'settings_edit_country' not in st.session_state:
        st.session_state.settings_edit_country = account.get('country', 'USA')
    
    # Location information outside form so country code updates dynamically
    st.subheader("Personal Information")
    name = st.text_input("Name", value=account['name'])
    email = st.text_input("Email", value=account.get('email', ''))
    
    st.markdown("---")
    st.subheader("Location & Contact")
    col1, col2 = st.columns(2)
    with col1:
        country = st.selectbox("Country", list(COUNTRY_PHONE_FORMATS.keys()), 
                               index=list(COUNTRY_PHONE_FORMATS.keys()).index(st.session_state.settings_edit_country),
                               key='settings_edit_country')
    with col2:
        country_code = COUNTRY_PHONE_FORMATS[country]['code']
        st.text_input("Country Code", value=country_code, disabled=True)
    
    phone_help = get_phone_format_help(country)
    phone = st.text_input("Phone Number", value=account.get('phone', ''), 
                          help=phone_help, placeholder=COUNTRY_PHONE_FORMATS[country]['example'])
    
    ssn = st.text_input("Social Security Number (SSN)", value=account.get('ssn', ''), 
                        placeholder="e.g., 123-45-6789", help="Format: XXX-XX-XXXX")
    
    dob = st.text_input("Date of Birth", value=account.get('dob', ''), 
                        placeholder="e.g., 15/06/1990", help="Format: DD/MM/YYYY")
    
    st.markdown("---")
    st.subheader("📍 Address Information")
    address = account.get('address', {})
    street_address = st.text_input("Street Address", value=address.get('street', ''))
    
    col1, col2 = st.columns(2)
    with col1:
        apartment = st.text_input("Apt/Suite (Optional)", value=address.get('apartment', ''))
    with col2:
        city = st.text_input("City", value=address.get('city', ''))
    
    col3, col4 = st.columns(2)
    with col3:
        county = st.text_input("County (Optional)", value=address.get('county', ''))
    with col4:
        zip_code = st.text_input("Zip Code", value=address.get('zip_code', ''))
    
    st.markdown("---")
    
    with st.form("settings_form"):
        st.subheader("Notification Preferences")
        prefs = account.get('preferences', {})
        email_notifications = st.checkbox("Enable email notifications", value=prefs.get('email_notifications', True))
        low_balance_alerts = st.checkbox("Enable low balance alerts", value=prefs.get('low_balance_alert', True))
        alert_threshold = st.number_input(
            "Low balance alert threshold ($)",
            min_value=10,
            value=prefs.get('alert_threshold', 100)
        )
        
        if st.form_submit_button("Save Settings", use_container_width=True):
            # Validate phone number
            if phone and not validate_phone(phone, country):
                st.error(f"❌ Invalid phone format for {country}! Expected format: {get_phone_format_help(country)}")
            elif not name:
                st.error("❌ Name cannot be empty!")
            elif not validate_email(email):
                st.error("❌ Invalid email format!")
            elif not ssn:
                st.error("❌ SSN cannot be empty!")
            elif not validate_ssn(ssn):
                st.error("❌ Invalid SSN format! Expected format: XXX-XX-XXXX (e.g., 123-45-6789)")
            elif not dob:
                st.error("❌ Date of Birth cannot be empty!")
            elif not validate_dob(dob):
                st.error("❌ Invalid DOB format or you must be at least 18 years old! Expected format: DD/MM/YYYY (e.g., 15/06/1990)")
            elif not street_address:
                st.error("❌ Street address cannot be empty!")
            elif not city:
                st.error("❌ City cannot be empty!")
            elif not zip_code:
                st.error("❌ Zip code cannot be empty!")
            else:
                accounts[account_number]['name'] = name
                accounts[account_number]['email'] = email
                accounts[account_number]['phone'] = phone
                accounts[account_number]['ssn'] = ssn
                accounts[account_number]['dob'] = dob
                accounts[account_number]['country'] = country
                accounts[account_number]['address'] = {
                    'street': street_address,
                    'apartment': apartment,
                    'city': city,
                    'county': county,
                    'zip_code': zip_code
                }
                accounts[account_number]['preferences'] = {
                    'email_notifications': email_notifications,
                    'low_balance_alert': low_balance_alerts,
                    'alert_threshold': alert_threshold
                }
                save_accounts(accounts)
                st.success("✅ Settings saved successfully!")
                st.rerun()

# ========== MAIN APP ==========
def main():
    """Main application"""
    st.set_page_config(
        page_title="CyBank",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize session state
    init_session_state()
    
    # Page routing
    if st.session_state.logged_in:
        dashboard_page()
    else:
        if st.session_state.page == 'main':
            main_menu()
        elif st.session_state.page == 'create':
            create_account_page()
        elif st.session_state.page == 'login':
            login_page()
        else:
            main_menu()

if __name__ == "__main__":
    main()