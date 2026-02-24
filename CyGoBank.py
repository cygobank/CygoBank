"""
COMPLETE BANKING PROGRAM WITH EMAIL NOTIFICATIONS
A fully functional banking system with account management, transaction history,
data persistence, and email notifications for all transactions.
"""

import json
import os
from datetime import datetime
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re  # For email validation

# ========== ENHANCEMENT 1: Email Configuration ==========
# Email settings for sending notifications
# NOTE: For testing, you can use a Gmail account with "App Password"

# Define TESTING_MODE at the global level
TESTING_MODE = True  # Set to False when you have real email credentials

EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',  # For Gmail
    'smtp_port': 587,
    'sender_email': 'your_bank_email@gmail.com',  # CHANGE THIS to your email
    'sender_password': 'your_app_password',  # CHANGE THIS to your app password
    'use_tls': True
}

# ========== ENHANCEMENT 2: Email Validation Function ==========
def validate_email(email):
    """Validate email format using regex"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ========== ENHANCEMENT 3: Email Notification Function ==========
def send_email_notification(recipient_email, subject, message_body):
    """Send email notification to customer"""
    
    # FIXED: Use the global TESTING_MODE without redeclaring it
    if TESTING_MODE:
        # In testing mode, just print the email instead of sending
        print("\n" + "="*60)
        print("📧 EMAIL NOTIFICATION (TESTING MODE)")
        print("="*60)
        print(f"To: {recipient_email}")
        print(f"Subject: {subject}")
        print("-"*60)
        print(message_body)
        print("="*60)
        print("✅ Email would be sent in production mode")
        return True
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(message_body, 'plain'))
        
        # Create secure connection
        context = ssl.create_default_context()
        
        # Send email
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls(context=context)
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            server.send_message(msg)
        
        print(f"📧 Email notification sent to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

# ========== ENHANCEMENT 4: Transaction Email Templates (FIXED) ==========
def get_email_template(transaction_type, account_data, amount, balance):
    """Generate email template based on transaction type"""
    
    templates = {
        'WELCOME': {
            'subject': '🎉 Welcome to Cy_Bank! Your Account Has Been Created',
            'body': f"""
Dear {account_data['name']},

Welcome to Cy_Bank! We're thrilled to have you as our customer.

Your new account has been successfully created with the following details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Account Number: {account_data['account_number']}
Account Holder: {account_data['name']}
Email: {account_data['email']}
Initial Deposit: ${amount:.2f}
Current Balance: ${balance:.2f}
Created Date: {account_data['created']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You can now:
• Check your balance anytime
• Make deposits and withdrawals
• Transfer money to other accounts
• View transaction history
• Earn interest on your savings

Thank you for choosing Cy_Bank!

Best regards,
The Cy_Bank Team
"""
        },
        
        'DEPOSIT': {
            'subject': '💰 Deposit Confirmation - Cy_Bank',
            'body': f"""
Dear {account_data['name']},

Your deposit has been successfully processed!

Transaction Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Account Number: {account_data['account_number']}
Transaction Type: DEPOSIT
Amount: +${amount:.2f}
Previous Balance: ${balance - amount:.2f}
New Balance: ${balance:.2f}
Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thank you for banking with us!

Best regards,
The Cy_Bank Team
"""
        },
        
        'WITHDRAWAL': {
            'subject': '💳 Withdrawal Confirmation - Cy_Bank',
            'body': f"""
Dear {account_data['name']},

Your withdrawal has been successfully processed!

Transaction Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Account Number: {account_data['account_number']}
Transaction Type: WITHDRAWAL
Amount: -${amount:.2f}
Previous Balance: ${balance + amount:.2f}
New Balance: ${balance:.2f}
Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If you did not authorize this transaction, please contact us immediately.

Best regards,
The Cy_Bank Team
"""
        },
        
        'TRANSFER_SENT': {
            'subject': '💸 Transfer Sent Confirmation - Cy_Bank',
            'body': f"""
Dear {account_data['name']},

Your transfer has been successfully sent!

Transaction Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Account Number: {account_data['account_number']}
Transaction Type: TRANSFER SENT
To Account: {account_data.get('to_account', 'Unknown')}
Amount: -${amount:.2f}
Previous Balance: ${balance + amount:.2f}
New Balance: ${balance:.2f}
Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thank you for using our transfer service!

Best regards,
The Cy_Bank Team
"""
        },
        
        'TRANSFER_RECEIVED': {
            'subject': '📥 Transfer Received Notification - Cy_Bank',
            'body': f"""
Dear {account_data['name']},

You have received a transfer!

Transaction Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Account Number: {account_data['account_number']}
Transaction Type: TRANSFER RECEIVED
From Account: {account_data.get('from_account', 'Unknown')}
Amount: +${amount:.2f}
Previous Balance: ${balance - amount:.2f}
New Balance: ${balance:.2f}
Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Best regards,
The Cy_Bank Team
"""
        },
        
        'INTEREST': {
            'subject': '💹 Interest Credited - Cy_Bank',
            'body': f"""
Dear {account_data['name']},

Interest has been credited to your account!

Transaction Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Account Number: {account_data['account_number']}
Transaction Type: INTEREST
Amount: +${amount:.2f}
Previous Balance: ${balance - amount:.2f}
New Balance: ${balance:.2f}
Interest Rate: 1% monthly
Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your money is growing with us!

Best regards,
The Cy_Bank Team
"""
        },
        
        'LOW_BALANCE': {
            'subject': '⚠️ Low Balance Alert - Cy_Bank',
            'body': f"""
Dear {account_data['name']},

This is an alert regarding your account balance.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Account Number: {account_data['account_number']}
Current Balance: ${balance:.2f}
Alert Type: LOW BALANCE (below $100)
Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please consider making a deposit to maintain sufficient funds.

Best regards,
The Cy_Bank Team
"""
        }
    }
    
    # Get the template or use default
    template = templates.get(transaction_type)
    
    if template:
        return template
    else:
        # Default template for unknown transaction types
        return {
            'subject': 'Cy_Bank Transaction Notification',
            'body': f"""
Dear {account_data['name']},

A transaction has occurred on your account.

Account: {account_data['account_number']}
Amount: ${amount:.2f}
New Balance: ${balance:.2f}

Thank you for banking with Cy_Bank.
"""
        }

# ========== Data Persistence Functions ==========
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

def log_transaction(account_number, transaction_type, amount, description=""):
    """Record a transaction in account history"""
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

def show_transaction_history(account_number):
    """Display transaction history"""
    accounts = load_accounts()
    if account_number not in accounts:
        print("❌ Account not found!")
        return
    
    print("\n" + "="*60)
    print("TRANSACTION HISTORY")
    print("="*60)
    
    transactions = accounts[account_number].get('transactions', [])
    if not transactions:
        print("No transactions found.")
        return
    
    print(f"{'Date':<20} {'Type':<15} {'Amount':>12} {'Description'}")
    print("-"*70)
    
    for t in transactions:
        date = t.get('date', 'Unknown')[:16]  # Truncate to YYYY-MM-DD HH:MM
        trans_type = t.get('type', '')
        amount = t.get('amount', 0)
        desc = t.get('description', '')
        
        if trans_type in ['DEPOSIT', 'TRANSFER_IN', 'INTEREST']:
            print(f"{date:<20} {trans_type:<15} +${amount:>10.2f}  {desc}")
        else:
            print(f"{date:<20} {trans_type:<15} -${amount:>10.2f}  {desc}")
    
    print("-"*70)

def calculate_interest(balance, rate=0.01):
    """Calculate monthly interest on balance"""
    interest = balance * rate
    return interest

def show_balance_enhanced(account_number):
    """Enhanced balance display with account info"""
    accounts = load_accounts()
    if account_number not in accounts:
        print("❌ Account not found!")
        return
    
    account = accounts[account_number]
    balance = float(account['balance'])
    
    print("\n" + "="*50)
    print(f"ACCOUNT STATEMENT")
    print("="*50)
    print(f"Account Number: {account_number}")
    print(f"Account Holder: {account['name']}")
    print(f"Account Created: {account.get('created', 'Unknown')}")
    print("-"*50)
    print(f"Current Balance: ${balance:,.2f}")
    
    if balance > 10000:
        print("⭐ Premium Account Status")
    elif balance > 1000:
        print("✓ Standard Account")
    elif balance > 100:
        print("ℹ️ Basic Account")
    else:
        print("⚠️ Low Balance")
    
    print("="*50)

def show_account_summary(account_number):
    """Display comprehensive account summary"""
    accounts = load_accounts()
    if account_number not in accounts:
        return
    
    account = accounts[account_number]
    balance = float(account['balance'])
    transactions = account.get('transactions', [])
    
    print("\n" + "="*60)
    print("ACCOUNT SUMMARY")
    print("="*60)
    print(f"Account: {account_number}")
    print(f"Holder: {account['name']}")
    print(f"Balance: ${balance:,.2f}")
    
    if transactions:
        total_deposits = sum(t['amount'] for t in transactions if t['type'] in ['DEPOSIT', 'TRANSFER_IN', 'INTEREST'])
        total_withdrawals = sum(t['amount'] for t in transactions if t['type'] in ['WITHDRAWAL', 'TRANSFER_OUT'])
        
        print("\n📊 STATISTICS")
        print("-"*40)
        print(f"Total Deposits: ${total_deposits:,.2f}")
        print(f"Total Withdrawals: ${total_withdrawals:,.2f}")
        print(f"Net Flow: ${total_deposits - total_withdrawals:,.2f}")
        print(f"Transaction Count: {len(transactions)}")
    
    if 'created' in account:
        created = datetime.strptime(account['created'], '%Y-%m-%d %H:%M:%S')
        age_days = (datetime.now() - created).days
        print(f"Account Age: {age_days} days")
    
    print("="*60)

def login():
    """Login to existing account"""
    print("\n" + "="*50)
    print("ACCOUNT LOGIN")
    print("="*50)
    
    accounts = load_accounts()
    
    if not accounts:
        print("❌ No accounts found. Please create an account first.")
        return None
    
    print("Available accounts:")
    for acc_num, acc_data in accounts.items():
        print(f"  • {acc_num} - {acc_data['name']}")
    
    print()
    account_number = input("Enter your account number: ").strip()
    
    if account_number not in accounts:
        print(f"❌ Account '{account_number}' not found!")
        return None
    
    print(f"\n✅ Welcome back, {accounts[account_number]['name']}!")
    return account_number

# ========== ENHANCEMENT 5: Account Management with Email ==========
def create_account():
    """Create a new bank account with email capture"""
    print("\n" + "="*50)
    print("CREATE NEW ACCOUNT")
    print("="*50)
    
    accounts = load_accounts()
    
    # Get account number
    while True:
        account_number = input("Enter new account number: ").strip()
        if not account_number:
            print("❌ Account number cannot be empty!")
            continue
        if account_number in accounts:
            print("❌ Account number already exists!")
            continue
        break
    
    # Get account holder name
    account_name = input("Enter account holder name: ").strip()
    if not account_name:
        account_name = "Unknown"
    
    # Capture and validate email
    while True:
        email = input("Enter email address for notifications: ").strip().lower()
        if not email:
            print("❌ Email address cannot be empty!")
            continue
        if not validate_email(email):
            print("❌ Invalid email format! Please enter a valid email (e.g., name@domain.com)")
            continue
        break
    
    # Get initial deposit
    initial_deposit = 0
    while True:
        try:
            initial_deposit = float(input("Enter initial deposit (minimum $10): "))
            if initial_deposit < 10:
                print("❌ Initial deposit must be at least $10!")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid number!")
    
    # Create account with email
    accounts[account_number] = {
        'name': account_name,
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
    account_data = accounts[account_number]
    template = get_email_template('WELCOME', {
        'name': account_name,
        'account_number': account_number,
        'email': email,
        'created': account_data['created']
    }, initial_deposit, initial_deposit)
    
    send_email_notification(email, template['subject'], template['body'])
    
    print(f"\n✅ Account created successfully!")
    print(f"Account Number: {account_number}")
    print(f"Account Holder: {account_name}")
    print(f"Email: {email}")
    print(f"Initial Balance: ${initial_deposit:.2f}")
    print(f"📧 Welcome email sent to {email}")
    
    return account_number

# ========== ENHANCEMENT 6: Transaction Notification Helper ==========
def send_transaction_notification(account_number, transaction_type, amount, balance, **kwargs):
    """Send email notification for transactions"""
    accounts = load_accounts()
    
    if account_number not in accounts:
        return False
    
    account = accounts[account_number]
    
    # Check if email notifications are enabled
    if not account.get('preferences', {}).get('email_notifications', True):
        return False
    
    email = account.get('email')
    if not email:
        return False
    
    # Prepare account data for template
    account_data = {
        'name': account['name'],
        'account_number': account_number,
        'email': email
    }
    
    # Add any additional data (for transfers, etc.)
    account_data.update(kwargs)
    
    # Get template
    template = get_email_template(transaction_type, account_data, amount, balance)
    
    # Send email
    return send_email_notification(email, template['subject'], template['body'])

# ========== ENHANCEMENT 7: Check and Send Low Balance Alert ==========
def check_low_balance_alert(account_number, balance):
    """Check if balance is low and send alert"""
    accounts = load_accounts()
    
    if account_number not in accounts:
        return False
    
    account = accounts[account_number]
    
    # Check if alerts are enabled
    if not account.get('preferences', {}).get('low_balance_alert', True):
        return False
    
    threshold = account.get('preferences', {}).get('alert_threshold', 100)
    
    if balance < threshold:
        account_data = {
            'name': account['name'],
            'account_number': account_number,
            'email': account.get('email', '')
        }
        
        template = get_email_template('LOW_BALANCE', account_data, 0, balance)
        send_email_notification(account.get('email'), template['subject'], template['body'])
        return True
    
    return False

# ========== ENHANCEMENT 8: Update Notification Preferences ==========
def update_notification_preferences(account_number):
    """Allow customer to update email notification preferences"""
    accounts = load_accounts()
    
    if account_number not in accounts:
        print("❌ Account not found!")
        return False
    
    print("\n" + "="*50)
    print("NOTIFICATION PREFERENCES")
    print("="*50)
    
    prefs = accounts[account_number].get('preferences', {})
    
    print(f"Current email: {accounts[account_number].get('email', 'Not set')}")
    
    # Option to update email
    change_email = input("\nDo you want to update your email? (y/n): ").lower()
    if change_email == 'y':
        while True:
            new_email = input("Enter new email address: ").strip().lower()
            if validate_email(new_email):
                accounts[account_number]['email'] = new_email
                print(f"✅ Email updated to {new_email}")
                break
            else:
                print("❌ Invalid email format!")
    
    # Update notification preferences
    print("\nNotification Settings:")
    
    current = prefs.get('email_notifications', True)
    new_value = input(f"Enable email notifications? (y/n) [current: {'yes' if current else 'no'}]: ").lower()
    if new_value in ['y', 'n']:
        prefs['email_notifications'] = (new_value == 'y')
    
    current = prefs.get('low_balance_alert', True)
    new_value = input(f"Enable low balance alerts? (y/n) [current: {'yes' if current else 'no'}]: ").lower()
    if new_value in ['y', 'n']:
        prefs['low_balance_alert'] = (new_value == 'y')
    
    if prefs.get('low_balance_alert', True):
        current = prefs.get('alert_threshold', 100)
        try:
            new_threshold = float(input(f"Set low balance alert threshold (current: ${current}): $"))
            if new_threshold > 0:
                prefs['alert_threshold'] = new_threshold
        except ValueError:
            print(f"Keeping current threshold: ${current}")
    
    accounts[account_number]['preferences'] = prefs
    save_accounts(accounts)
    
    print("\n✅ Notification preferences updated!")
    return True

# ========== ENHANCEMENT 9: Enhanced Deposit with Notification ==========
def deposit_enhanced(account_number):
    """Enhanced deposit with validation, logging, and email notification"""
    print("\n" + "="*50)
    print("DEPOSIT FUNDS")
    print("="*50)
    
    try:
        amount = float(input("Enter amount to deposit: $"))
    except ValueError:
        print("❌ Invalid amount! Please enter a number.")
        return 0
    
    if amount <= 0:
        print("❌ Deposit amount must be positive!")
        return 0
    
    # Optional: Add maximum deposit limit
    if amount > 10000:
        print("⚠️ Large deposit detected. May be subject to review.")
    
    # Get current balance
    accounts = load_accounts()
    current_balance = float(accounts[account_number]['balance'])
    new_balance = current_balance + amount
    
    # Update balance
    accounts[account_number]['balance'] = str(new_balance)
    save_accounts(accounts)
    
    # Log the transaction
    log_transaction(account_number, 'DEPOSIT', amount, "Branch deposit")
    
    # Send deposit notification
    send_transaction_notification(
        account_number, 
        'DEPOSIT', 
        amount, 
        new_balance
    )
    
    print(f"✅ Successfully deposited ${amount:.2f}")
    return amount

# ========== ENHANCEMENT 10: Enhanced Withdrawal with Notification ==========
def withdraw_enhanced(account_number, balance):
    """Enhanced withdraw with validation, logging, and email notification"""
    print("\n" + "="*50)
    print("WITHDRAW FUNDS")
    print("="*50)
    
    try:
        amount = float(input("Enter amount to withdraw: $"))
    except ValueError:
        print("❌ Invalid amount! Please enter a number.")
        return 0
    
    if amount <= 0:
        print("❌ Withdrawal amount must be positive!")
        return 0
    
    if amount > balance:
        print("❌ Insufficient funds!")
        print(f"Available balance: ${balance:.2f}")
        return 0
    
    # Optional: Add daily withdrawal limit
    daily_limit = 2000
    if amount > daily_limit:
        print(f"⚠️ Amount exceeds daily limit of ${daily_limit}")
        return 0
    
    # Calculate new balance
    new_balance = balance - amount
    
    # Update balance in accounts
    accounts = load_accounts()
    accounts[account_number]['balance'] = str(new_balance)
    save_accounts(accounts)
    
    # Log the transaction
    log_transaction(account_number, 'WITHDRAWAL', amount, "ATM withdrawal")
    
    # Send withdrawal notification
    send_transaction_notification(
        account_number, 
        'WITHDRAWAL', 
        amount, 
        new_balance
    )
    
    # Check for low balance
    check_low_balance_alert(account_number, new_balance)
    
    print(f"✅ Please take your cash: ${amount:.2f}")
    return amount

# ========== ENHANCEMENT 11: Enhanced Transfer with Notifications ==========
def transfer_funds(from_account, to_account):
    """Transfer money between accounts with email notifications for both parties"""
    accounts = load_accounts()
    
    if from_account not in accounts:
        print("❌ Your account not found!")
        return False
    
    if to_account not in accounts:
        print("❌ Destination account not found!")
        return False
    
    if from_account == to_account:
        print("❌ Cannot transfer to the same account!")
        return False
    
    try:
        amount = float(input("Enter amount to transfer: $"))
    except ValueError:
        print("❌ Invalid amount!")
        return False
    
    if amount <= 0:
        print("❌ Amount must be positive!")
        return False
    
    from_balance = float(accounts[from_account]['balance'])
    if amount > from_balance:
        print("❌ Insufficient funds!")
        return False
    
    to_balance = float(accounts[to_account]['balance'])
    
    # Perform transfer
    accounts[from_account]['balance'] = str(from_balance - amount)
    accounts[to_account]['balance'] = str(to_balance + amount)
    
    # Log transactions for both accounts
    log_transaction(from_account, 'TRANSFER_OUT', amount, f"To account {to_account}")
    log_transaction(to_account, 'TRANSFER_IN', amount, f"From account {from_account}")
    
    save_accounts(accounts)
    
    # Send notifications to both parties
    # Notification to sender
    send_transaction_notification(
        from_account,
        'TRANSFER_SENT',
        amount,
        from_balance - amount,
        to_account=to_account
    )
    
    # Notification to receiver
    send_transaction_notification(
        to_account,
        'TRANSFER_RECEIVED',
        amount,
        to_balance + amount,
        from_account=from_account
    )
    
    # Check low balance for sender
    check_low_balance_alert(from_account, from_balance - amount)
    
    print(f"✅ Successfully transferred ${amount:.2f} to account {to_account}")
    return True

# ========== ENHANCEMENT 12: Enhanced Interest Application with Notification ==========
def apply_interest(account_number):
    """Apply monthly interest to account with notification"""
    accounts = load_accounts()
    if account_number not in accounts:
        return False
    
    balance = float(accounts[account_number]['balance'])
    interest = calculate_interest(balance)
    new_balance = balance + interest
    
    accounts[account_number]['balance'] = str(new_balance)
    
    # Log the interest transaction
    accounts[account_number].setdefault('transactions', []).append({
        'type': 'INTEREST',
        'amount': interest,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'description': f'Monthly interest at 1%'
    })
    
    save_accounts(accounts)
    
    # Send interest notification
    send_transaction_notification(
        account_number,
        'INTEREST',
        interest,
        new_balance
    )
    
    print(f"✅ Interest of ${interest:.2f} applied to your account!")
    return True

# ========== ENHANCEMENT 13: Display Account Info with Email ==========
def show_account_info(account_number):
    """Display account information including email"""
    accounts = load_accounts()
    if account_number not in accounts:
        print("❌ Account not found!")
        return
    
    account = accounts[account_number]
    
    print("\n" + "="*50)
    print("ACCOUNT INFORMATION")
    print("="*50)
    print(f"Account Number: {account_number}")
    print(f"Account Holder: {account['name']}")
    print(f"Email Address: {account.get('email', 'Not set')}")
    print(f"Balance: ${float(account['balance']):,.2f}")
    print(f"Created: {account.get('created', 'Unknown')}")
    
    # Show notification preferences
    prefs = account.get('preferences', {})
    print("\nNotification Preferences:")
    print(f"  Email Notifications: {'✅ Enabled' if prefs.get('email_notifications', True) else '❌ Disabled'}")
    print(f"  Low Balance Alerts: {'✅ Enabled' if prefs.get('low_balance_alert', True) else '❌ Disabled'}")
    if prefs.get('low_balance_alert', True):
        print(f"  Alert Threshold: ${prefs.get('alert_threshold', 100)}")
    
    print("="*50)

# ========== ENHANCEMENT 14: Test Email Configuration ==========
def test_email_configuration():
    """Test if email configuration is working"""
    print("\n" + "="*50)
    print("TEST EMAIL CONFIGURATION")
    print("="*50)
    
    # FIXED: Use global TESTING_MODE with proper declaration
    global TESTING_MODE
    
    if TESTING_MODE:
        print("📧 Currently in TESTING MODE - emails are printed to console")
        change = input("Do you want to switch to production mode? (y/n): ").lower()
        if change == 'y':
            TESTING_MODE = False
            print("✅ Testing mode disabled - now attempting to send real emails")
    
    test_email = input("Enter email address to send test message: ").strip()
    
    if not validate_email(test_email):
        print("❌ Invalid email format!")
        return
    
    print("\n📧 Sending test email...")
    
    result = send_email_notification(
        test_email,
        "🔧 Test Email from Cy_Bank",
        f"""
This is a test email from Cy_Bank Banking System.

If you received this, your email configuration is working correctly!

Time sent: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Best regards,
The Cy_Bank Team
        """
    )
    
    if result:
        print("✅ Test email sent successfully!")
    else:
        print("❌ Failed to send test email. Check your email configuration.")

# ========== ENHANCEMENT 15: Enhanced Main Menu ==========
def main_menu(account_number):
    """Enhanced main menu with email notification options"""
    accounts = load_accounts()
    
    if account_number not in accounts:
        print("❌ Account error!")
        return False
    
    balance = float(accounts[account_number]['balance'])
    
    while True:
        print("\n" + "="*60)
        print(f"  CY_BANK - Welcome {accounts[account_number]['name']}")
        print("="*60)
        print(f"Account: {account_number}")
        print(f"Email: {accounts[account_number].get('email', 'Not set')}")
        print(f"Balance: ${balance:,.2f}")
        print("-"*60)
        print("1. 💰 Show Balance")
        print("2. 📥 Deposit Money")
        print("3. 📤 Withdraw Money")
        print("4. 📋 Transaction History")
        print("5. 💸 Transfer Money")
        print("6. 📊 Account Summary")
        print("7. 💹 Apply Interest")
        print("8. 📧 Notification Preferences")
        print("9. ℹ️  Account Information")
        print("10. 🚪 Logout")
        print("-"*60)
        
        choice = input("Enter your choice (1-10): ").strip()
        
        if choice == '1':
            show_balance_enhanced(account_number)
            
        elif choice == '2':
            deposit_amount = deposit_enhanced(account_number)
            if deposit_amount > 0:
                accounts = load_accounts()
                balance = float(accounts[account_number]['balance'])
            
        elif choice == '3':
            withdraw_amount = withdraw_enhanced(account_number, balance)
            if withdraw_amount > 0:
                accounts = load_accounts()
                balance = float(accounts[account_number]['balance'])
            
        elif choice == '4':
            show_transaction_history(account_number)
            
        elif choice == '5':
            print("\n" + "-"*40)
            print("TRANSFER MONEY")
            print("-"*40)
            to_account = input("Enter destination account number: ").strip()
            transfer_funds(account_number, to_account)
            accounts = load_accounts()
            balance = float(accounts[account_number]['balance'])
            
        elif choice == '6':
            show_account_summary(account_number)
            
        elif choice == '7':
            apply_interest(account_number)
            accounts = load_accounts()
            balance = float(accounts[account_number]['balance'])
            
        elif choice == '8':
            update_notification_preferences(account_number)
            accounts = load_accounts()
            
        elif choice == '9':
            show_account_info(account_number)
            
        elif choice == '10':
            print("\n✅ Logging out...")
            print(f"Thank you for banking with Cy_Bank, {accounts[account_number]['name']}!")
            return True
            
        else:
            print("❌ Invalid choice! Please enter 1-10.")

# ========== ENHANCEMENT 16: Main Program with Email Test Option ==========
def main():
    """Main program entry point with email test option"""
    print("\n" + "="*60)
    print("  WELCOME TO CY_BANK - With Email Notifications")
    print("="*60)
    
    while True:
        print("\n" + "="*40)
        print("MAIN MENU")
        print("="*40)
        print("1. 🔑 Login to Existing Account")
        print("2. 🆕 Create New Account (with email)")
        print("3. 📧 Test Email Configuration")
        print("4. 🚪 Exit")
        print("-"*40)
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            account_number = login()
            if account_number:
                main_menu(account_number)
                
        elif choice == '2':
            account_number = create_account()
            if account_number:
                print("\n✅ Please login with your new account")
                
        elif choice == '3':
            test_email_configuration()
                
        elif choice == '4':
            print("\n" + "="*40)
            print("Thank you for choosing Cy_Bank!")
            print("Have a wonderful day!")
            print("="*40)
            break
            
        else:
            print("❌ Invalid choice! Please enter 1-4.")

if __name__ == '__main__':
    main()
