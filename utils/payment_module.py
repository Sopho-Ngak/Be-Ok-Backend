import requests
import uuid
import json
from django.conf import settings

LOGIN_URL = "https://payments.paypack.rw/api/auth/agents/authorize"
CASHIN_URL = url = "https://payments.paypack.rw/api/transactions/cashin?Idempotency-Key={idempotency_key}"
TRANSACTION_STATUS_URL = "https://payments.paypack.rw/api/events/transactions?ref={reference_key}&kind={kind}&client={client}"

class Payment:
    def __init__(self, amount:int = None, phone_number:str=None, reference_key=None, kind=None):
        self.amount = amount
        self.phone_number = phone_number
        self.reference_key = reference_key
        self.kind = kind

    def _authenticate(self) -> str:
        """Authenticate to get a token"""
        payload = json.dumps({
        "client_id": settings.PAYPACK_APP_ID,
        "client_secret": settings.PAYPACK_APP_SECRET
        })
        headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer {access_token}'
        }

        response = requests.request("POST", LOGIN_URL, headers=headers, data=payload)

        return response.json()["access"]

    def generate_idempotency_key(self) -> str:
        return str(uuid.uuid4()).replace('-', '')[:32]


    def _cashin(self) -> dict:
        payload = json.dumps({
            "amount": self.amount,
            "number": self.phone_number
        })

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self._authenticate()}'
        }
        url = CASHIN_URL.format(idempotency_key=self.generate_idempotency_key())
        response = requests.request("POST", url, headers=headers, data=payload)

        return response.json()
    
    def pay(self) -> dict:
        return self._cashin()

    def check_status(self) -> dict:
        """Check the status of a transaction"""
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self._authenticate()}'
        }
        payload = {}
        url = TRANSACTION_STATUS_URL.format(reference_key=self.reference_key, kind=self.kind.upper(), client=self.phone_number)
        response = requests.request("GET", url, headers=headers, data=payload)
        
        return response.json()