# INFO

## usb device
Wenn der Lärmmessgerät an RPI mit USB verbunden ist kann sich in zwei unterschiedliche Moden befinden:

- **mass storage** name='XL2_SD-Card', id=0003: Der lärmessgerät verhält sich wie ein Speicher. 
- **seriale verbindung**, name='XL2_Remote', id=0004  : Der lärmessgerät bietet eine seriale Schnittstelle. den device ist unten ttyACM zu finden

In Beide fälle ist den gerät erkennbar durch ID_VENDOR=NTiAudio, ID_VENDOR_ENC=NTiAudio, ID_VENDOR_ID=1a2b


