import firebase_admin
from firebase_admin import credentials, storage, db

cred = {
  "type": "service_account",
  "project_id": "fedserver-3766d",
  "private_key_id": "9f04161b3ee31a2c88ac335c093f93f33b31253a",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCkwIE5hMM7hrQJ\nLkLz3c3bxJI530kA+Xbhwqe/msu4ziI2IcD4DnKVEeelcUuyH6mNeLEBRPL/GGra\nTZJLo5E0r4R9QkSjjuxpTvy49uAYvkKNKPlzXu6EedZimT+YpOIyDT6TojGmc+e8\nig3Pq1gNZXAsftGVy+JVcy2UoPxymjYPHPQTdj36L+C0zs3awSZhXI3EHPKbu/GB\n+OqVFN/efG+WgnZHkTTZUySlYtR5DfkyAwa1AhPNu9ASCpZpCGu3rTRET1H7pQ1i\nixNlB0OJIkLeXsTWLK5FSQ+0Df3YYa3MWepFgnygj//cjibDUPcOL5ITwspVVivT\nRYsV6mOjAgMBAAECggEAFx5S7oD8aw2eP9eNBO7FT1HIecnPqGJZK0Qxs90DOf3l\npmuayh7aN07ZjvP/UjxyghaYh/wROSNHreB1Z0XJlMy4WQyugwuwOErMLcxUFUTF\neUzG9vMwTHNTARJOGUZciKIme3hRYpvLE0AwFfRjmRBN6wB/ZSIaCDGZs3cvqt5S\nUErd6QmDy1LCZzQ7m4Dp5FFW2B34k3nqAVmSs5xx8fem7eH0LoSAftIbdUNgdaHV\ntkIpQAhbvCQ2NKksziq/86Y5ep6naLNFQtlr2wEzIq9u5GMnlkpNmsr++MmMchYa\ndkVB3cYxbfDQneKe659z2RFuoJ+FseD6oTnQ0BwrmQKBgQDiNqmqyqTaT5pdrwv+\nDIY7YCKDzxyfjPSfYlnOqy6b5zpCzFL/KWIe4wjYUprhD32ms5racXEAWpXHaJGF\nFN3aZcUODUkhyFIsZxaDvhDnm2dcyJU+qPggi3LaibDyOu3AunUP68h8NHVl6SpP\n99LpnfqimgANLF2vUtC+/I2JjQKBgQC6cg9mm+QLgE/Qq7MDxpHXremyP3iLEB6k\nVCJZw0RD9FGnwnMuneQjceE7nFmcqYQhFucMxlHO+/hE5VvQ/y62S5B3xd8hxV3U\nRp/iTreJNFGQu2YI5ZoRyGgeQJKDnNy8gI34Iqm4cz3yxzvOKJjuG2NsOMZ4Mji/\ni+wKmHod7wKBgCaGOqTcd/C558cWnYs5ZM7N03LxHaXKYoqWPEcm/fwNB+4CUAwm\nZxBth78Xakrz0WlHYxLaiO0PgDyCgW3RnOqptEJtXswDCoOHVt0+zDA1VggGHOyb\n6A3a0ceH9Xt7L6xH1NHOTMliQbAGYm9V/DRO9DUm1uVnbdkC2Iv+BLitAoGBAKyB\nbih1IllV3gNnadmbd0NEQU7QFRstzfwjcCj3V4k8W/TJIENIiVYWPtwlvHAMFBl9\nlEeokvbdAYfVYs+L28+FOOTo6pvXfgozUilUxdIn2zP7f9vJfHTppRQgkK8/iqjK\nlRC6Gah00CN6HaaQv3bHVoVCPrflV8Y6kyn2jD53AoGADXzuAtCFSBfPlYUnLjeK\nL43P0rk2lcEJ6WNAWmJffi5PqcmDvYNumVzoXi+8DAYZ87sBWkIaYXzeunZyX/wx\nOilJzIU0DrYj3vq2KC+35uiDVsl/XLp1uL769pvh+hAD5B+1AZTA41eRr9pX0DoH\npqSqXcnh9cbqSMW7CWUQOag=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-60hpn@fedserver-3766d.iam.gserviceaccount.com",
  "client_id": "113317434999205960444",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-60hpn%40fedserver-3766d.iam.gserviceaccount.com"
}
certi = firebase_admin.credentials.Certificate(cred)
fireapp = firebase_admin.initialize_app(certi, {'storageBucket': 'fedserver-3766d.appspot.com','databaseURL': 'https://fedserver-3766d.firebaseio.com/'})

ref = db.reference('/DeviceLosses')
ls = ref.get()
keys = list(ls.keys())
print(keys)
losses = []
for key in keys:
  print(ls[key])
  losses.append(ls[key])
print(np.shape(losses))
print(losses)