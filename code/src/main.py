import os
import json

from process_transaction import process_transaction

def process():
    sample_transaction = {
        "Transaction ID": "TXN001",
        "Payer Name": "Acme Corp",
        "Receiver Name": "SovCo Capital Partners",
        "Transaction Details": "Payment for services rendered",
        "Amount": "$500,000",
        "Receiver Country": "USA"
    }

    extraction_result = process_transaction(sample_transaction)
#     {
#   "Transaction ID": "TXN001",
#   "Extracted Entity": [
#     "Acme Corp",
#     "SovCo Capital Partners"
#   ],
#   "Entity Type": [
#     "Corporation",
#     "Corporation"
#   ],
#   "Supporting Evidence": [
#     null,
#     null
#   ],
#   "Confidence Score": 0.72,
#   "Countries": [
#     "United States of America (the)",
#     "Netherlands (the)"
#   ]
# }

























if __name__ == "__main__":
    process()

