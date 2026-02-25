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
    
    with col3:
        st.markdown("### 📧 Test")
        if st.button("Test Email", use_container_width=True):
            st.session_state.page = 'test_email'
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
    
    with st.form("create_account_form"):
        account_number = st.text_input("Account Number", help="Choose a unique account number")
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
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
            else:
                # Create account
                accounts[account_number] = {
                    'name': name,
                    'email': email,
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
                body = f"""
Dear {name},

Welcome to Cy_Bank! Your account has been created successfully.

Account Number: {account_number}
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
    
    # Account selection dropdown
    account_list = list(accounts.keys())
    account_labels = [f"{acc} - {accounts[acc]['name']}" for acc in account_list]
    
    selected_index = st.selectbox(
        "Select your account",
        range(len(account_list)),
        format_func=lambda i: account_labels[i]
    )
    
    if st.button("Login", use_container_width=True):
        account_number = account_list[selected_index]
        st.session_state.logged_in = True
        st.session_state.current_account = account_number
        st.session_state.page = 'dashboard'
        st.success(f"✅ Welcome back, {accounts[account_number]['name']}!")
        st.rerun()
    
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
    
    with st.form("settings_form"):
        st.subheader("Personal Information")
        name = st.text_input("Name", value=account['name'])
        email = st.text_input("Email", value=account.get('email', ''))
        
        st.markdown("---")
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
            accounts[account_number]['name'] = name
            accounts[account_number]['email'] = email
            accounts[account_number]['preferences'] = {
                'email_notifications': email_notifications,
                'low_balance_alert': low_balance_alerts,
                'alert_threshold': alert_threshold
            }
            save_accounts(accounts)
            st.success("✅ Settings saved successfully!")
            st.rerun()

def test_email_page():
    """Test email configuration"""
    st.title("📧 Test Email Configuration")
    
    st.info(f"Testing Mode: {'ON' if TESTING_MODE else 'OFF'}")
    
    test_email = st.text_input("Enter email to send test message")
    
    if st.button("Send Test Email"):
        if validate_email(test_email):
            result = send_email_notification(
                test_email,
                "🔧 Test Email from CyBank",
                f"This is a test email from your CyBank application.\n\nTime: {datetime.now()}"
            )
            if result:
                st.success("✅ Test email processed successfully!")
            else:
                st.error("❌ Failed to send email")
        else:
            st.error("Invalid email format")
    
    if st.button("← Back to Main Menu"):
        st.session_state.page = 'main'
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
        elif st.session_state.page == 'test_email':
            test_email_page()
        else:
            main_menu()

if __name__ == "__main__":
    main()