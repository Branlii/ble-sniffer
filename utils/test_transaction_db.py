from datetime import datetime
from utils.transaction_db import TransactionDB

def test_insert_transaction():
    db = TransactionDB(db_path='test_transactions.db')
    timestamp = datetime.now().isoformat()
    device_id = 'AA:BB:CC:DD:EE:FF'
    device_info = {
        'name': 'TestDevice',
        'last_rssi': -50,
        'last_seen': timestamp,
        'manufacturer': 'TestCorp',
        'services': ['TestService'],
        'tx_power': 4,
        'connectable': True
    }
    db.add_transaction(timestamp, device_id, device_info)
    db.close()
    print('Test transaction inserted.')

if __name__ == "__main__":
    test_insert_transaction()
