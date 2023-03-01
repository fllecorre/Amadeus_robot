SERVER = 'bkgv0700.os.amadeus.net'    
PORT = '9092'
cluster = 'bkts32' 
topics = {
    'unprocessed':'aps.appevent.unprocessed',
    'raw':'aps.appevent.raw',
    'rich': 'aps.appevent.rich', 
    'recovery': 'aps.appevent_recovery.rich'
}            