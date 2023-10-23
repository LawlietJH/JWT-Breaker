import base64
import json
import time
import jwt


encoded_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXIifQ.p5LogGsW6l9h-xwx_QD8u61gpRTJnnQQvLl1dOVGQWQ"

padding_b64 = lambda b64str: b64str + '=' * (-len(b64str) % 4)
decode_b64 = lambda b64str: json.loads(base64.b64decode(padding_b64(b64str)).decode())

header_b64, payload_b64, signature_b64 = encoded_jwt.split('.')
header = decode_b64(header_b64)
payload = decode_b64(payload_b64)
print('\n Header:   ', header_b64)
print('  - Decode:', header)
print(' Payload:  ', payload_b64)
print('  - Decode:', payload)
print(' Signature:', signature_b64)
algorithm = header.get('alg', '')

filename = 'common_secrets.txt'

with open(filename, 'r') as file:
    secrets = file.readlines()

last_secret = ''
print()

for secret in secrets:
    time.sleep(.1)
    if secret.endswith('\n'):
        secret = secret[:-1]
    try:
        decoded_jwt = jwt.decode(encoded_jwt, secret, algorithms=['RS256', 'HS256', algorithm])
        print('\r Secret:', secret, end=' '*len(last_secret)+'\n')
        break
    except Exception as error:
        print('\r Secret:', secret, end=' '*len(last_secret))
    last_secret = secret
