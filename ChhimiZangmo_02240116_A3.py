import random
import os # os is a  module that lets us use operating system-dependent functionality such as reading or writing to a file, checking if a file exists, etc.
from abc import ABC, abstractmethod # allows functions like abstract classes and abstract methods (for inheritance and polymorphism) 

# Custom Exceptions
class BankingError(Exception): # parent class or base class - (for error handling)
    """Base class for banking exceptions"""
    pass # place holder (pass - is for  when we have nothing to write but want to use the class for inheritance in subclass ))
class InsufficientFundsError(BankingError): # Subclass -to handel errors when the money is insufficent while transfering, withdrawing, or topping up
    """Raised when account has insufficient funds"""
    pass # pass - again to use as base class

class InvalidAmountError(BankingError): # subclass- for invalid inputs such as alphabetical character, zero, negative number or any other characters such as <.{+_
    """Raised when invalid amount is entered"""
    pass

class AccountNotFoundError(BankingError): #subclass- For when logging in and putting invalid account number or deleted account or any other
    """Raised when account doesn't exist"""
    pass

class AuthenticationError(BankingError): # subclass - to check passcode (when password is wrong , also when account is not found)
    """Raised when login information are invalid"""
    pass

# Abstract Base Class
class Account(ABC): # ABC - Abstract Base Class - is used as a blueprint for other classes to inherit from (basically the parent)
    """Abstract base class for bank accounts"""
    def __init__(self, account_id, passcode, account_type, funds=0): #
        self.account_id = account_id
        self.passcode = passcode
        self.account_type = account_type
        self.funds = funds
    
    @abstractmethod # abstaract method uses @abstractmethod (decorator) to implement in subclass
    def get_account_details(self):
        pass # 

    def deposit(self, amount):
        """Deposit money into account"""
        if amount <= 0 or round(amount, 2) != amount: # checks if amount is less then or zero and if it has maximum just 2 decimals or it raises Invalid amount error
            raise InvalidAmountError("Amount must be positive and have at most 2 decimal places")
        self.funds += amount # else money deposited to acount
        return f"Deposited ${amount:.2f}. New balance: ${self.funds:.2f}"

    def withdraw(self, amount):
        """Withdraw money from account"""
        if amount <= 0 or round(amount, 2) != amount: # similiar invalid error case to depositing invalid inputs
            raise InvalidAmountError("Amount must be positive and have at most 2 decimal places")
        if amount > self.funds:
            # gives insufficeient fund error if the balance is less then amount we want to withdraw
            raise InsufficientFundsError("Insufficient funds for withdrawal")
        self.funds -= amount # else amount to withdraw is subtracted from balance
        return f"Withdrew ${amount:.2f}. New balance: ${self.funds:.2f}"
    
    def transfer(self, amount, recipient):
        """Transfer money to another account"""
        if not isinstance(recipient, Account): # isinstance (s.note - an inbuilt function) checks if recipient is an instance of account class that is if the account exists
            raise AccountNotFoundError("Recipient account not found") # if account not an instance of annount class gives error
        self.withdraw(amount)  # else it withdraws money 
        recipient.deposit(amount) # and deposits to the recipient account
        return f"Transferred ${amount:.2f} to account {recipient.account_id}"

# Concrete Account Classes
class PersonalAccount(Account): # inherits from Account
    """Class for personal bank accounts"""
    def __init__(self, account_id, passcode, funds=0):
        super().__init__(account_id, passcode, "Personal", funds) #  getting the Account methods 
        self.mobile_balance = 0  # Added for mobile top-up feature
    
    def get_account_details(self): # this method is implemented from the abstract method in Account class to get account details
        """Returns formatted account details"""
        return (f"Personal Account {self.account_id}\n"
                f"Balance: ${self.funds:.2f}\n"
                f"Mobile Balance: ${self.mobile_balance:.2f}")
    
    def top_up_mobile(self, amount): # (Talk time or data)
        """Top up mobile phone balance"""
        if amount <= 0:
            raise InvalidAmountError("Top-up amount must be positive")
        if amount > self.funds:
            raise InsufficientFundsError("Insufficient funds for mobile top-up")
        self.funds -= amount # subtractig from balance 
        self.mobile_balance += amount # and adding to mobile 
        return f"Mobile topped up with ${amount:.2f}. Account balance: ${self.funds:.2f}"

class BusinessAccount(Account):
    """Class for business bank accounts"""
    def __init__(self, account_id, passcode, funds=0): # similiar to personal account but without mobile top up function
        super().__init__(account_id, passcode, "Business", funds) # inheritng from account class and its methods
    
    def get_account_details(self):
        """Returns formatted account details"""
        return f"Business Account {self.account_id}\nBalance: ${self.funds:.2f}"

# Banking System Class
class BankingSystem: # 
    """Main banking system that manages accounts and file operations"""
    def __init__(self, filename="accounts.txt"): # initializing the banking system with a file name to store accounts
        self.filename = filename
        self.accounts = {}
        self.load_accounts() # loading accounts from file storage
    
    def load_accounts(self): 
        """Load accounts from file storage""" 
        if not os.path.exists(self.filename): # check if the file exists
            return
        
        with open(self.filename, "r") as file:
            for line in file: # iterating through each line in the file
                try:
                    data = line.strip().split(",")
                    if len(data) < 4: # lenth of data should be at least 4 (account_id, passcode, account_type, funds)
                        continue 
                    
                    account_id, passcode, account_type, funds = data[:4] # unpacking the data
                    funds = float(funds) # converting funds to float in particular for currency handling
                    
                    # Handle mobile balance for personal accounts
                    if len(data) > 4 and account_type == "Personal":
                        mobile_balance = float(data[4]) # if there is a mobile balance it is converted to float
                    else:
                        mobile_balance = (0) # default mobile balance for business accounts
                    
                    if account_type == "Personal":
                        account = PersonalAccount(account_id, passcode, funds)
                        account.mobile_balance = mobile_balance
                    else:
                        account = BusinessAccount(account_id, passcode, funds)
                    
                    self.accounts[account_id] = account
                except (ValueError, IndexError) as e: # catching errors such as value error (if funds is not a number) or index error (if data is not enough)
                    print(f"Error loading account data: {e}")
                    continue
    
    def save_accounts(self): # 
        """Save accounts to file storage"""
        with open(self.filename, "w") as file: # opening the file in write mode
            for account in self.accounts.values(): # iterating through each account in the accounts dictionary
                if isinstance(account, PersonalAccount):
                    file.write(f"{account.account_id},{account.passcode},{account.account_type},{account.funds},{account.mobile_balance}\n")
                    # writing personal account details and mobile balance
                else:
                    file.write(f"{account.account_id},{account.passcode},{account.account_type},{account.funds}\n")
    
    def create_account(self, account_type):
        """Create a new bank account"""
        account_id = str(random.randint(10000, 99999)) # the account can contain 5 digit numbers beteween 10000 and 99999 
        passcode = str(random.randint(1000, 9999)) # str used instead of int because there could be leading zeros and integers in python do not preserve leading zeros so the accountid or passcode will have lesser digits then 5 and 4 respectively
        
        if account_type.lower() == "personal": # 
            account = PersonalAccount(account_id, passcode)
        else:
            account = BusinessAccount(account_id, passcode)
        
        self.accounts[account_id] = account
        self.save_accounts()
        return account

    def login(self, account_id, passcode):
        account = self.accounts.get(account_id)
        if not account or account.passcode != passcode: # for incorrect account number or passcode
            raise AuthenticationError("Invalid credentials") 
        return account
        

    def delete_account(self, account_id):
        if account_id not in self.accounts:
            raise AccountNotFoundError("Account not found")
        del self.accounts[account_id]
        self.save_accounts() # saving account after deletion 
    
    def account_exists(self, account_id):
        """Check if an account exists"""
        return account_id in self.accounts # returns true or flase

# Main Application
def main():
    """Main application entry point"""
    bank = BankingSystem()
    
    while True:
        print("\n=== Banking Application ===")
        print("1. Open Account")
        print("2. Login")
        print("3. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            process_create_account(bank)
        elif choice == "2":
            process_login(bank)
        elif choice == "3":
            print("Thank you for using our banking service!")
            break
        else: # for error handeling
            print("Invalid choice. Please try again.")

def process_create_account(bank):
    """Handle account creation process"""
    print("\nAccount Types:")
    print("1. Personal")
    print("2. Business")
    
    while True:
        account_type = input("Select account type (1/2): ")
        if account_type == "1":
            account = bank.create_account("Personal")
            break
        elif account_type == "2":
            account = bank.create_account("Business")
            break
        else:
            print("Invalid choice. Please select 1 or 2.")
    
    print("\nAccount created successfully!")
    print(f"Account Number: {account.account_id}")
    print(f"Temporary Passcode: {account.passcode}")
    print("Please change your passcode after first login.")

def process_login(bank):
    """Handle user login and account operations"""
    account_id = input("Enter account number: ")
    passcode = input("Enter passcode: ")
    
    try:
        account = bank.login(account_id, passcode)
        print(f"\nLogin successful! Welcome, {account.account_type} account holder.")
        
        while True:
            print("\nAccount Menu:")
            print("1. View Balance")
            print("2. Deposit")
            print("3. Withdraw")
            print("4. Transfer")
            print("5. Mobile Top-Up (Personal Only)")
            print("6. Delete Account")
            print("7. Logout")
            
            choice = input("Enter your choice: ")
            
            try:
                if choice == "1":
                    print("\n" + account.get_account_details())
                elif choice == "2":
                    process_deposit(account, bank)
                elif choice == "3":
                    process_withdraw(account, bank)
                elif choice == "4":
                    process_transfer(account, bank)
                elif choice == "5":
                    if isinstance(account, PersonalAccount):
                        process_mobile_topup(account, bank)
                    else:
                        print("Mobile top-up only available for personal accounts")
                elif choice == "6":
                    if input("Are you sure you want to delete your account? (y/n): ").lower() == "y":
                        bank.delete_account(account.account_id)
                        print("Account deleted successfully")
                        return
                elif choice == "7":
                    print("Logged out successfully")
                    return
                else: # 
                    print("Invalid choice. Please try again.")
            except BankingError as e: # - insufficient funds, invalid amount, etc.. except for errors that are raised in the methods (deposit, withdraw, transfer, etc..) 
                print(f"Error: {e}")
    except BankingError as e:
        print(f"Login failed: {e}") # gives outut - "Login failed: Invalid credentials" if the account number or passcode is wrong

def process_deposit(account, bank): # Actuallu taking in user inputs and handeling errors
    """Handle deposit operation"""
    try:
        amount = float(input("Enter amount to deposit: "))
        print(account.deposit(amount))
        bank.save_accounts()
    except ValueError:
        print("Invalid amount entered")

def process_withdraw(account, bank):
    """Handle withdrawal operation"""
    try:
        amount = float(input("Enter amount to withdraw: "))
        print(account.withdraw(amount))
        bank.save_accounts()
    except ValueError: # for if input not number or is negative or 0
        print("Invalid amount entered")

def process_transfer(account, bank):
    """Handle transfer operation"""
    recipient_id = input("Enter recipient account number: ")
    if not bank.account_exists(recipient_id):
        print("Recipient account not found")
        return # returns to the previous menu
    # else..
    try:
        amount = float(input("Enter amount to transfer: "))
        recipient = bank.accounts[recipient_id]
        print(account.transfer(amount, recipient))
        bank.save_accounts()
    except ValueError:
        print("Invalid amount entered")

def process_mobile_topup(account, bank):
    """Handle mobile top-up operation"""
    try:
        amount = float(input("Enter top-up amount: "))
        print(account.top_up_mobile(amount))
        bank.save_accounts()
    except ValueError:
        print("Invalid amount entered")

if __name__ == "__main__":
    main()