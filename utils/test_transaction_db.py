import time
from utils.transaction_db import TransactionDB

def test_insert_transaction():
    db = TransactionDB(db_path='test_transactions.db')
    timestamp = str(time.time())
    device_id = 'AA:BB:CC:DD:EE:FF'
    data = '{"name": "TestDevice", "last_rssi": -50, "last_seen": %s, "manufacturer": "TestCorp", "services": "TestService", "tx_power": 4, "connectable": true}' % timestamp
    db.add_transaction(timestamp, device_id, data)
    db.close()
    print('Test transaction inserted.')

if __name__ == "__main__":
    test_insert_transaction()
