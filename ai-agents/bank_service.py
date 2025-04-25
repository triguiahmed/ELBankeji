import requests
from datetime import datetime
from typing import List, Optional, Dict, Any


class BankAPIClient:
    """A client service for interacting with the Bank API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the Bank API client.
        
        Args:
            base_url: The base URL of the Bank API service
        """
        self.base_url = base_url.rstrip('/')
    
    def request_loan(self, user: str, amount: float, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Request a loan through the API.
        
        Args:
            user: Username of the loan requester
            amount: Amount of money to borrow
            date: Date of the loan request (defaults to current time)
            
        Returns:
            Dictionary containing the response data
        """
        if date is None:
            date = datetime.utcnow()
        
        payload = {
            "user": user,
            "amount": amount,
            "date": date.isoformat()
        }
        
        response = requests.post(f"{self.base_url}/request-loan", json=payload)
        response.raise_for_status()
        return response.json()
    
    def send_money(self, emitter: str, receiver: str, amount: float, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Send money from one account to another.
        
        Args:
            emitter: Sender's username
            receiver: Receiver's username
            amount: Amount of money to send
            date: Date of the transaction (defaults to current time)
            
        Returns:
            Dictionary containing the response data
        """
        if date is None:
            date = datetime.utcnow()
        
        payload = {
            "emitter": emitter,
            "receiver": receiver,
            "amount": amount,
            "date": date.isoformat()
        }
        
        response = requests.post(f"{self.base_url}/send-money", json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_balance(self, account: str) -> Dict[str, float]:
        """
        Get the balance of an account.
        
        Args:
            account: Username of the account owner
            
        Returns:
            Dictionary containing the balance information
        """
        headers = {"account": account}
        response = requests.get(f"{self.base_url}/balance", headers=headers)
        response.raise_for_status()
        return response.json()
    
    def get_transactions_history(self, emitter: str, receiver: str, date: datetime) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get transaction history between emitter and receiver on a specific date.
        
        Args:
            emitter: Sender's username
            receiver: Receiver's username
            date: Date of the transactions
            
        Returns:
            Dictionary containing the list of transactions
        """
        headers = {
            "emitter": emitter,
            "receiver": receiver,
            "date": date.isoformat()
        }
        
        response = requests.get(f"{self.base_url}/transactions-history", headers=headers)
        response.raise_for_status()
        return response.json()


# Example usage
if __name__ == "__main__":
    client = BankAPIClient("http://localhost:8000")
    
    # Example: Request a loan
    loan_response = client.request_loan(
        user="john_doe",
        amount=5000.0
    )
    print(f"Loan request response: {loan_response}")
    
    # Example: Send money
    transfer_response = client.send_money(
        emitter="john_doe",
        receiver="jane_smith",
        amount=150.50
    )
    print(f"Money transfer response: {transfer_response}")
    
    # Example: Check balance
    balance = client.get_balance("john_doe")
    print(f"Account balance: {balance}")
    
    # Example: Get transaction history
    specific_date = datetime(2025, 4, 25, 12, 0, 0)
    transactions = client.get_transactions_history(
        emitter="john_doe",
        receiver="jane_smith", 
        date=specific_date
    )
    print(f"Transaction history: {transactions}")