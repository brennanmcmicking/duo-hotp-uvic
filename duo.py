#!/usr/bin/env python3
"""Duo HOTP

Usage:
    duo_hotp <qr_url> -o <output_path>
    duo_hotp -h | --help

Options:
    -h --help     Show this screen.
    -s PATH       provide PATH of secret.json file

Large parts of code copied from
 https://github.com/simonseo/nyuad-spammer/tree/master/spammer/duo
"""
import base64
import inspect
import json
import os
import pyotp
import requests
from Crypto.PublicKey import RSA
from docopt import docopt
from os.path import dirname, join, abspath, isfile
from urllib import parse
import qrcode


def b32_encode(key):
    return base64.b32encode(key.encode("utf-8"))


def find_secret(path=None, must_exist=True):
    """use input, env, or script directory
    >>> os.path.basename(find_secret(must_exist=False)) # default
    'secrets.json'
    >>> os.environ["DUO_SECRETFILE"] = "a/b"
    >>> find_secret(must_exist=False)                   # env
    'a/b'
    >>> find_secret("foobar", False)                    # explicit
    'foobar'
    """
    if path is None and os.environ.get("DUO_SECRETFILE", None) is not None:
        path = os.environ["DUO_SECRETFILE"]

    if path is None:
        bin_dir = dirname(abspath(inspect.stack()[0][1]))
        path = join(bin_dir, "secrets.json")

    if not isfile(path) and must_exist:
        print(f"'{path}' does not exist!")
        raise Exception("Cannot find secret json file")

    return path


def qr_url_to_activation_url(qr_url):
    "Create request URL"
    # get ?value=XXX
    data = parse.unquote(qr_url.split("?value=")[1])
    # first half of value is the activation code
    code = data.split("-")[0].replace("duo://", "")
    # second half of value is the hostname in base64
    hostb64 = data.split("-")[1]
    # Same as "api-e4c9863e.duosecurity.com"
    host = base64.b64decode(hostb64 + "=" * (-len(hostb64) % 4))
    # this api is not publicly known
    activation_url = "https://{host}/push/v2/activation/{code}".format(
        host=host.decode("utf-8"), code=code
    )
    print(activation_url)
    return activation_url


def activate_device(activation_url):
    """Activates through activation url and returns HOTP key """
    # --- Get response which will be a JSON of secret keys, customer names, etc
    # --- Expected Response:
    #     {'response': {'hotp_secret': 'blahblah123', ...}, 'stat': 'OK'}
    # --- Expected Error:
    #     {'code': 40403, 'message': 'Unknown activation code', 'stat': 'FAIL'}
    params = {"pkpush": "rsa-sha512",
              "pubkey": RSA.generate(2048).public_key().export_key("PEM").decode(),
              "manufacturer": "Apple",
              "model": "iPhone 4S"}
    response = requests.post(activation_url, params=params)
    response_dict = json.loads(response.text)
    if response_dict["stat"] == "FAIL":
        raise Exception("Activation failed! Try a new QR/Activation URL")
    print(response_dict)

    hotp_secret = response_dict["response"]["hotp_secret"]
    return hotp_secret


def mknew(qr_url, output_path):
    """load QR code, send activation request, generate first code"""

    activation_url = qr_url_to_activation_url(qr_url)
    hotp_secret = activate_device(activation_url)

    encoded = hotp_secret[:-4]
    qr = qrcode.make(f"otpauth://hotp/Duo?secret={encoded}&issuer=Duo&counter=1")
    qr.save(output_path)
    print(f"Saved to {output_path}, go scan it from your app such as Google Authenticator!")


if __name__ == "__main__":
    args = docopt(__doc__)

    mknew(args["<qr_url>", args["<output_path>"]])
