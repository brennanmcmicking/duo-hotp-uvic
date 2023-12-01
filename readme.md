# Duo HOTP

Duo can authenticate using HOTP - _Hash(message authentication code)-based One-Time Password_.

But it has some proprietary covers over the OATH (Initiative for Open Authentication) standard.

[simonseo/nyuad-spammer](https://github.com/simonseo/nyuad-spammer/tree/master/spammer/duo) has code to work around this.
`duo.py` is largely copied from there

## Usage

also see `duo.py -h` or the doc string of [duo.py](duo.py)

1. generate a new duo QR code for an android tablet within your institution's device management portal
2. copy the url of the QR code image <img src="img/copy_qr_code.png?raw=True" width=100>. it should look like `https://api-e4c9863e.duosecurity.com/frame/qr?value=c53Xoof7cFSOHGxtm69f-YXBpLWU0Yzk4NjNlLmR1b3NlY3VyaXR5LmNvbQ`
3. `./duo.py "https://URL-OF-IMAGE" -o "PATH/TO/OUTPUT/QR/CODE.png` to register
4. push continue in the browser
5. scan the QR code from your preferred authenticator app (I have only tested using Google Authenticator)

## Install

```
pip install -r requirements.txt # pyotp docopt requests
./duo.py -h
```
