 # unittest is a module that lets us do writing and running tests
import unittest # Has functions such as assertEqual ( it is used to check if two values are equal ), assertRaises (it is used to check if an error is raised), etc.
import os # 
from ChhimiZangmo_02240116_A3 import (Account, PersonalAccount, BusinessAccount, #imports classes from assignment Part A
                                      BankingSystem, InsufficientFundsError, 
                                      InvalidAmountError, AccountNotFoundError,
                                      AuthenticationError)
class TestBankAccount(unittest.TestCase): # TestCase is a class that is used to create test cases in unittest module
    """Test cases for base Account functionality"""
    
    def setUp(self):# to set up the environment for each test using setUp method with a temporary file
        self.test_file = "test_accounts.txt" # Temporary file to store data
        if os.path.exists(self.test_file): # os here is used to check if the file exists, 
            # and path is an inbuilt module in Py that has functions to intereact with file system
            os.remove(self.test_file)# removes the file if it exists
        # Initialize the banking system with a test file
        self.bank = BankingSystem(self.test_file)
        self.account1 = self.bank.create_account("Personal")
        self.account2 = self.bank.create_account("Business")
    
    def tearDown(self): 
        """ TearDown is a method that cleans up after each test for clean up
        - if it is not used, the test file will remain after the tests are run 
        and it will cause problems for the next test run """
        if os.path.exists(self.test_file):
            os.remove(self.test_file) 
    
    def test_account_creation(self): 
        """Test account creation assigns correct properties"""
        self.assertEqual(self.account1.account_type, "Personal")#.assertEqual checks the Equality of two values here it checks equality of account type and "Personal"
        self.assertEqual(self.account2.account_type, "Business") # if values are unequal it will raise an assertionError (error that is raised when an assert statement fails)
        self.assertEqual(self.account1.funds, 0) # checks if the funds is initialized to 0
        self.assertTrue(len(self.account1.account_id) == 5) # checks if the account-id is 5 characters (.asertTrue checks if the condition is True)
        self.assertTrue(len(self.account1.passcode) == 4) # checks if the passcode is 4 characters
        # Both .assertEqual and asertTrue are from the unittest module
    
    def test_deposit(self):
        """Test deposit functionality"""
        result = self.account1.deposit(100) # calls the deposit method of the account1 object with 100 as an argument that is the amount to be deposited
        self.assertEqual(self.account1.funds, 100) # checks if the funds of account1 is 100 after the deposit
        self.assertIn("Deposited $100.00", result) # checks if the result of the deposit method contains the string "Deposited $100.00"
        
        with self.assertRaises(InvalidAmountError):# with statement used to check if an error is raised
            self.account1.deposit(-50) # in this case it checks if negative ammount is passed as input; if it is it gives InvalidAmountError
            # if the error is raised, the test passes, otherwise it fails
    
    def test_withdraw(self): 
        """Test withdraw functionality checks if withdrawl methode works corectly;
          for insufficient amount and invalid inputs """
        self.account1.deposit(200) # 
        result = self.account1.withdraw(50)# calls withdrawl methode for argument 50
        self.assertEqual(self.account1.funds, 150) # checks if the funds of account1 is 150 after the withdrawal
        self.assertIn("Withdrew $50.00", result) # checks if we get withdrawl amount "WIthdrew $50.00"
        
        with self.assertRaises(InsufficientFundsError): #
            self.account1.withdraw(200) # Trying to withdraw 200 when only 150 is available to see if it raises InsufficientFundsError
        
        with self.assertRaises(InvalidAmountError):
            self.account1.withdraw(-10) #Trying out negative amount to see if it raises InvalidAmountError
    
    def test_transfer(self): 
        """Test transfer between accounts and its error realted handeling
        like insufficient funds and transfer to non-existing account"""
        self.account1.deposit(300) # initializing account1 with 300 funds
        result = self.account1.transfer(100, self.account2) # transfering 100 to account using transfer method ( inheriting from Account class in part a)
        self.assertEqual(self.account1.funds, 200) # checks account 1 balance for 200 after transfer
        self.assertEqual(self.account2.funds, 100) # checks account 2 balance for 100 after transfer
        self.assertIn("Transferred $100.00", result) #checks if it returns "Transferred $100.00"
        
        with self.assertRaises(InsufficientFundsError): # similiar to withdrawl, it checks if the funds are sufficient for the transfer
            self.account1.transfer(300, self.account2) # transfering 300 as theirs only 200 in balance - should return InsufficientFundsError
        
        with self.assertRaises(AccountNotFoundError): 
            self.account1.transfer(50, None) # transfering to a nonexistence account to see it raise - AccountNotFoundError

class TestPersonalAccount(unittest.TestCase): 
    """Test PersonalAccount specific features"""
    def setUp(self): # testing PersonalAccount specific features
        self.account = PersonalAccount("12345", "1111", 0) # taking account_id = 12345 an dpasscode = 1111 and initializing funds to 0
    
    def test_mobile_topup(self):
        """Test mobile top-up functionality"""
        self.account.deposit(200) 
        result = self.account.top_up_mobile(50) # calling top_up_mobile method with 50 as an argument (adding 50 to mobile balance)
        self.assertEqual(self.account.funds, 150) # check if the funds are 150 after the top-up
        self.assertEqual(self.account.mobile_balance, 50) # checks mobile balance for 50
        self.assertIn("Mobile topped up", result) #should give "Mobile topped up $50.00" or its an error
        
        with self.assertRaises(InsufficientFundsError):
            self.account.top_up_mobile(200) # should raise an error as initially only 150 in balance
        
        with self.assertRaises(InvalidAmountError):
            self.account.top_up_mobile(-10) # error check for negative amount in top-up

class TestBankingSystem(unittest.TestCase):
    """Test BankingSystem management functions"""
    
    def setUp(self): # 
        self.test_file = "test_system.txt"
        if os.path.exists(self.test_file):
            os.remove(self.test_file) # removing the test file if it exists to avoid conflicts
        
        self.bank = BankingSystem(self.test_file) # initilizing a new BankingSystem with the test file
        self.account = self.bank.create_account("Personal") # Testing with a Personal account
    
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file) # removing the test file after the tests are done
    
    def test_file_persistence(self):
        """Test accounts are saved/loaded correctly"""
        self.account.deposit(500)
        self.bank.save_accounts() # saving the accounts to the test file
        new_bank = BankingSystem(self.test_file) # creating a new BankingSystem instance to test loading
        loaded_account = new_bank.login(self.account.account_id, self.account.passcode) # loading the account from the test file
        self.assertEqual(loaded_account.funds, 500) # checking if the funds are 500 after loading
        self.assertEqual(loaded_account.account_type, "Personal") # testing if account type is till personal after loading
    
    def test_login(self):
        """Test authentication system"""
        account = self.bank.login(self.account.account_id, self.account.passcode) # logining in
        self.assertEqual(account, self.account) # checking if the logged in account is same as the created account
        
        with self.assertRaises(AuthenticationError):
            self.bank.login("99999", self.account.passcode) # loging with a non-existing account id should raise AuthenticationError
        
        with self.assertRaises(AuthenticationError):
            self.bank.login(self.account.account_id, "9999") # loging with a wrong passcode should also raise AuthenticationError
    
    def test_delete_account(self):
        """Test account deletion"""
        acc_id = self.account.account_id 
        self.bank.delete_account(acc_id)
        self.assertNotIn(acc_id, self.bank.accounts) # Testing if the account is deleted from the bank's accounts
        
        with self.assertRaises(AuthenticationError):
            self.bank.login(acc_id, self.account.passcode)

class TestEdgeCases(unittest.TestCase): # 
    """Test unusual scenarios and edge cases"""
    
    def setUp(self):
        self.test_file = "test_edge.txt"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        
        self.bank = BankingSystem(self.test_file)
        self.account = self.bank.create_account("Business")
        self.account.deposit(1000)
    
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_large_values(self):
        """Test handling of large amounts"""
        self.account.deposit(1_000_000)
        self.assertEqual(self.account.funds, 1_001_000) # Testing if large deposit works correctly
        
        acc2 = self.bank.create_account("Personal") # Creating another account for transfer testing
        self.account.transfer(500_000, acc2)
        self.assertEqual(acc2.funds, 500_000) # Testing if transfer of large amounts works correctly
    
    def test_precision_handling(self):
        """Test decimal precision handling"""
        self.account.deposit(0.01) # Testing deposit with small decimal value
        self.assertEqual(self.account.funds, 1000.01) # testing equality of Updated funds to be 1000.01 
        
        self.account.withdraw(0.01) # Testing withdrawl with small decimal value
        self.assertEqual(self.account.funds, 1000.00) 
        
        with self.assertRaises(InvalidAmountError):# 
            self.account.deposit(0.001) # Testing deposit with too decimal value more then 2 decimal place- should raise InvalidAmountError
    
    def test_concurrent_access(self):
        """Test file handling with multiple instances"""
        bank2 = BankingSystem(self.test_file) #again new instance for banking system created for concurrent access test
        acc2 = bank2.login(self.account.account_id, self.account.passcode) # logging in to the second instance
        
        self.account.deposit(500) # depositing 500 to the first instance
        self.bank.save_accounts()
        
        bank2.load_accounts() # loading accounts in the second instance
        acc2_reloaded = bank2.login(acc2.account_id, acc2.passcode) # logging in to the second instance again
        self.assertEqual(acc2_reloaded.funds, 1500)# testing if the funds are updated correctly in the second instance after saving and loading

if __name__ == "__main__":
    unittest.main()