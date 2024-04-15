import requests
import uuid
import json
from django.conf import settings

from settings.models import BlackListedTransaction

LOGIN_URL = "https://payments.paypack.rw/api/auth/agents/authorize"
CASHIN_URL = url = "https://payments.paypack.rw/api/transactions/cashin?Idempotency-Key={idempotency_key}"
TRANSACTION_STATUS_URL = "https://payments.paypack.rw/api/events/transactions?ref={reference_key}&kind={kind}&client={client}"
FIND_TRANSACTION_URL = "https://payments.paypack.rw/api/transactions/find/{referenceKey}"


class Payment:
    def __init__(self, amount: str = '', phone_number: str = '', reference_key: str = '', kind: str = ''):
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

        response = requests.request(
            "POST", LOGIN_URL, headers=headers, data=payload)

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
        url = CASHIN_URL.format(
            idempotency_key=self.generate_idempotency_key())
        response = requests.request("POST", url, headers=headers, data=payload)

        return response.json()

    def pay(self) -> dict:
        return self._cashin()

    def find_transaction(self, ref: str) -> dict:
        """Find a transaction"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self._authenticate()}'
        }
        url = FIND_TRANSACTION_URL.format(referenceKey=ref)
        response = requests.request("GET", url, headers=headers)
        data = response.json()
        data['status_code'] = response.status_code
        return data

    def blacklist_transaction(self, transaction_ref, **kwargs) -> BlackListedTransaction:
        """Blacklist a transaction"""
        instance = BlackListedTransaction.objects.create(reference_key=transaction_ref,
                                                         transaction_date=kwargs['timestamp'],
                                                         amount=kwargs['amount'],
                                                         fee=kwargs['fee'],
                                                         provider=kwargs['provider'],
                                                         client_id=kwargs['client'],
                                                         )
        return instance

    def check_status(self) -> dict:
        """Check the status of a transaction"""
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self._authenticate()}'
        }
        payload = {}
        url = TRANSACTION_STATUS_URL.format(
            reference_key=self.reference_key, kind=self.kind.upper(), client=self.phone_number)
        response = requests.request("GET", url, headers=headers, data=payload)

        return response.json()
