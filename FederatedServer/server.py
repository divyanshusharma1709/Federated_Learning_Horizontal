import flask
import firebase_admin
from firebase_admin import credentials, storage, db
import io
import pickle
import os, random
import numpy as np
import binascii, struct
import zipfile
from datetime import datetime

app = flask.Flask(__name__)

def cvt_bytetofloat(byte):
  a = list(byte)
  num = []
  for i in range(0,len(byte),4):
    b = [byte[i+3],byte[i+2],byte[i+1],byte[i]]
    x = bytearray(b)
    temp = struct.unpack('<f', x)
    num.append(temp)
  return num
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

@app.route("/upload", methods = ['POST'])
def upload():
  ref = db.reference('/')
  z = ref.get()
  ctr = z['num']
  print(flask.request)
  if flask.request.method == "POST":
    print("Uploading File")
    if flask.request.files["file"]:
      print("Reading input")
      weights = flask.request.files["file"].read()
      print("Input Read")
      weights_stream = io.BytesIO(weights)
      bucket = storage.bucket()
      blob = bucket.blob('weight' + str(ctr + 1))
      print("Saving at Server")
      with open("delta.bin", "wb") as f:
        f.write(weights_stream.read())
      print("Starting upload to Firebase")
      with open("delta.bin", "rb") as upload:
        byte_w = upload.read()
        x = np.array(cvt_bytetofloat(byte_w))
        print(len(x), np.shape(x))
        print(x)
        w1 = x[0:150]
        print(len(w1))
        w1 = np.reshape(np.array(w1), (10, 15))
        h1 = x[150:165]
        print(len(h1))
        h1 = np.reshape(np.array(h1), (15,))
        w2 = x[165:540]
        print(len(w2))
        w2 = np.reshape(np.array(w2), (15, 25))
        h2 = x[540:565]
        print(len(h2))
        h2 = np.reshape(np.array(h2), (25,))
        w3 = x[550:575]
        w3 = np.reshape(np.array(w3), (25, 1))
        h3 = x[575]
        print(len(h3))
        h3 = np.reshape(np.array(h3), (1,))
        print(len(x))
        weights = [w1, h1, w2, h2, w3, h3]
        with open("Weights.bin", "wb") as f:
          pickle.dump(weights, f)
      with open("Weights.bin", "rb") as f:
        blob = bucket.blob('weight' + str(ctr + 1))
        blob.upload_from_file(f)
        print("File Successfully Uploaded to Firebase")
        ref.update({'num': ctr + 1})
        return "File Uploaded\n"
    else:
      print("File not found")

@app.route("/getGlobalModel", methods = ['GET'])
def returnGlobalModel():
  if flask.request.method == "GET":
  #Get difference of weights file from firebase, make model file and average
    bucket = storage.bucket(app = fireapp)
    blobs = bucket.list_blobs()
    print("Downloading Global Model")
    zipf = zipfile.ZipFile('checkpoint.zip','w', zipfile.ZIP_DEFLATED)
    for blob in blobs:
      if blob.name == 'checkpoint' or 'FINAL_GRAPH' in blob.name:
        blob.download_to_filename(blob.name)
        zipf.write(blob.name)
        print(blob.name + " sent")
    zipf.close()
  return flask.send_file("checkpoint.zip",mimetype = 'zip',attachment_filename= 'checkpoint.zip', as_attachment = True)
if __name__ == "__main__":
  app.run(debug = True, port = int(os.environ.get("PORT", 5000)))
@app.route("/isModelUpdated", methods = ['GET'])
def isModelUpdated():
  ref = db.reference('/')
  z = ref.get()
  update = z['isUpdated']
  return update
@app.route("/uploadLoss", methods = ['POST'])
def uploadLoss():
  print(flask.request)
  if flask.request.method == "POST":
    print("Uploading File")
  if flask.request.files["file"]:
    print("Reading input")
    loss = flask.request.files["file"].read()
    print("Loss Read")
    loss_stream = io.BytesIO(loss)
    lossStr = str(loss_stream.getvalue(), 'utf-8')
    lossStr = float(lossStr)
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
    ref = db.reference('/DeviceLosses')
    ref.push({dt_string: lossStr})
    print("Loss pushed to FireBase")
  return "Loss Upload Successful"
@app.route("/setPrefFlag", methods = ['POST'])
def setFlag():
  print(flask.request)
  if flask.request.method == "POST":
    print("Uploading File")
  if flask.request.files["file"]:
    print("Reading input")
    loss = flask.request.files["file"].read()
    print("Loss Read")
    loss_stream = io.BytesIO(loss)
    lossStr = str(loss_stream.getvalue(), 'utf-8')
    ref = db.reference('/FedUsers')
    z = ref.get()
    if lossStr == "True":
      ref.update({"n_Users": z['n_Users'] + 1})
    elif lossStr == "False":
      ref.update({"n_Users": z['n_Users'] - 1})
    print("Count Updated")
  return "Count Updated"