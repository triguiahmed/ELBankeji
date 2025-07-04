import requests
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any


class BankAPIClient:
    """A client service for interacting with the Bank API with comprehensive logging."""
    
    def __init__(self, base_url: str = "http://host.docker.internal:8000", log_level=logging.INFO):
        """
        Initialize the Bank API client.
        
        Args:
            base_url: The base URL of the Bank API service
            log_level: Logging level (default: INFO)
        """
        self.base_url = base_url.rstrip('/')
        
        # Set up logging
        self.logger = logging.getLogger('BankAPIClient')
        self.logger.setLevel(log_level)
        
        # Create console handler if no handlers exist
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            
            # Create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            
            # Add handler to logger
            self.logger.addHandler(console_handler)
        
        self.logger.info(f"Bank API Client initialized with base URL: http://host.docker.internal:8000")
    
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
        
        self.logger.info(f"Requesting loan for user '{user}' with amount {amount}")
        self.logger.debug(f"Request payload: {payload}")
        
        try:
            response = requests.post(f"http://host.docker.internal:8000/request-loan", json=payload)
            
            response_data = response.json()
            response.raise_for_status()
            
            self.logger.info(f"Loan request successful: loan_id={response_data.get('loan_id')}")
            self.logger.debug(f"Response data: {response_data}")
            
            return response_data
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error in loan request: {e}")
            self.logger.debug(f"Response status: {e.response.status_code}, content: {e.response.text}")
            return response_data
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error in loan request: {e}")
            return response_data
        except Exception as e:
            self.logger.error(f"Unexpected error in loan request: {e}")
            return response_data
    
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
        
        self.logger.info(f"Sending {amount} from '{emitter}' to '{receiver}'")
        self.logger.debug(f"Request payload: {payload}")
        
        try:
            response = requests.post(f"http://host.docker.internal:8000/send-money", json=payload)
            response_data = response.json()
            response.raise_for_status()
            
            
            self.logger.info(f"Money transfer successful: transaction_id={response_data.get('transaction_id')}")
            self.logger.debug(f"Response data: {response_data}")
            
            return response_data
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error in money transfer: {e}, {response_data}")
            self.logger.debug(f"Response status: {e.response.status_code}, content: {e.response}")
            return response_data
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error in money transfer: {e}")
            return response_data
        except Exception as e:
            self.logger.error(f"Unexpected error in money transfer: {e}")
            return response_data
    
    def get_balance(self, account: str) -> Dict[str, float]:
        """
        Get the balance of an account.
        
        Args:
            account: Username of the account owner
            
        Returns:
            Dictionary containing the balance information
        """
        headers = {"account": account}
        
        self.logger.info(f"Getting balance for account '{account}'")
        self.logger.debug(f"Request headers: {headers}")
        
        try:
            response = requests.get(f"http://host.docker.internal:8000/balance", headers=headers)
            response_data = response.json()
            response.raise_for_status()
            
            
            self.logger.info(f"Balance retrieved successfully: {response_data.get('balance')}")
            self.logger.debug(f"Response data: {response_data}")
            
            return response_data
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error in balance check: {e}")
            self.logger.debug(f"Response status: {e.response.status_code}, content: {e.response.text}")
            return response_data
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error in balance check: {e}")
            return response_data
        except Exception as e:
            self.logger.error(f"Unexpected error in balance check: {e}")
            return response_data
    
    def get_transactions_history(self, emitter: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get transaction history of a specific user.
        
        Args:
            emitter: connected user's username

            
        Returns:
            Dictionary containing the list of transactions
        """
        headers = {
            "emitter": emitter,
        }
        
        self.logger.info(f"Getting transaction history for '{emitter}'")
        self.logger.debug(f"Request headers: {headers}")
        
        try:
            response = requests.get(f"http://host.docker.internal:8000/transactions-history", headers=headers)
            response_data = response.json()
            response.raise_for_status()
            
            num_transactions = len(response_data.get("transactions", []))
            self.logger.info(f"Retrieved {num_transactions} transactions")
            self.logger.debug(f"Response data: {response_data}")
            
            return response_data
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error in transaction history retrieval: {e}")
            self.logger.debug(f"Response status: {e.response.status_code}, content: {e.response.text}")
            return response_data
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error in transaction history retrieval: {e}")
            return response_data
        except Exception as e:
            self.logger.error(f"Unexpected error in transaction history retrieval: {e}")
            return response_data



# Example usage with logging configuration
if __name__ == "__main__":
    # Configure logging for the entire application
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='bank_api_client.log'  # Optionally log to file
    )
    
    # Create client with DEBUG logging level
    client = BankAPIClient("http://host.docker.internal:8000", log_level=logging.DEBUG)
    
    try:
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
        transactions = client.get_transactions_history(
            emitter="john_doe",
      
        )
        print(f"Transaction history: {transactions}")
    except Exception as e:
        logging.error(f"Error in example usage: {e}")