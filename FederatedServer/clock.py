from apscheduler.schedulers.blocking import BlockingScheduler
import flask
import firebase_admin
from firebase_admin import credentials, storage, db
import io
import os, random
import pickle
import tensorflow as tf
import numpy as np
import binascii, struct
import logging
from server import cvt_bytetofloat
import zipfile
import math
from datetime import datetime

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

cred = {
  }

certi = firebase_admin.credentials.Certificate(cred)
fireapp = firebase_admin.initialize_app(certi, {'storageBucket': ,'databaseURL': }, 'globalModelChecker')

sched = BlockingScheduler()
def delete_blob(blob_name):
  bucket = storage.bucket(app = fireapp)
  blob = bucket.blob(blob_name)
  blob.delete()
@sched.scheduled_job('interval', hours=1, id = 'UpdateGlobalModel')
def scheduled_job():
  ref = db.reference('/')
  z = ref.get()
  ref.update({'isUpdated': 'True'})
  ctr1 = z['num']
  modelctr = z['modelctr']
  # print("Checking number of files")
  if ctr1 == -1:                          ######CHANGE THIS TO RUN THE SCRIPT
    memWeights = []
    blob_ls = []
    bucket = storage.bucket(app = fireapp)
    blobs = bucket.list_blobs()
    ctr = 0
    # print("Getting Firebase storage items")
    for blob in blobs:
      if 'weight' in blob.name:
        print(blob.name)
        blob_ls.append(blob.name)
        blob.download_to_filename(str(ctr) + '.bin')
        ctr += 1
    for i in range(ctr):
      ctr = 0
      with open(str(i) + '.bin', 'rb') as f:
        flag = 0
        x = pickle.load(f)
        for i in range(np.shape(x)[0]):
          x[i] = np.asarray(x[i], dtype = np.float32)
          if np.isinf(x[i]).any() == False and np.isnan(x[i]).any() == False:
            flag = 1
        if flag == 1:
          memWeights.append(x)
          ctr += 1
          print("Append")
    bucket = storage.bucket(app = fireapp)
    blobs = bucket.list_blobs()
    for blob in blobs:
      if blob.name == "checkpoint":
        blob.download_to_filename('checkpoint')
        print(blob.name)
    bucket = storage.bucket(app = fireapp)
    blobs = bucket.list_blobs()
    for blob in blobs:
      if 'FINAL_GRAPH' in blob.name:
        blob.download_to_filename(blob.name)
        print(blob.name)
    #Average the weights
    w1 = []
    h1 = []
    w2 = []
    h2 = []
    w3 = []
    h3 = []
    n_w = np.shape(memWeights)[0]
    print(np.shape(memWeights)) # (n_bins = 5, n_weights = 5)
    w1 = np.ones((150, ))
    w1 = memWeights[0][0].flatten()
    for i in range(1, n_w):
      w1 = np.add(w1, memWeights[i][0].flatten())
    w1 /= n_w
    w1 = np.reshape(w1, (10, 15))
    print("W1: ")
    print(w1)


    h1 = np.ones((15, ))
    for i in range(np.shape(memWeights)[0]):
      h1 += ((memWeights[i][1]).flatten())
    h1 /= np.shape(memWeights)[0]
    h1 = np.reshape(h1, (15,))
    print("H1: ")
    print(h1)


    w2 = np.ones((375,))
    for i in range(1, np.shape(memWeights)[0]):
      w2 = np.add(w2, memWeights[i][2].flatten())
    w2 /= (np.shape(memWeights)[0])
    w2 = np.reshape(w2, (15, 25))
    print("W2: ")
    print(w2)

    h2 = np.ones((25,))
    for i in range(np.shape(memWeights)[0]):
      h2 += ((memWeights[i][3]).flatten())
    h2 /= (np.shape(memWeights)[0])
    h2 = np.reshape(h2, (25, ))
    print("H2: ")
    print(h2)


    w3 = np.ones((25,))
    for i in range(np.shape(memWeights)[0]):
      w3 += ((memWeights[i][4]).flatten())
    w3 /= (np.shape(memWeights)[0])
    w3 = np.reshape(w3, (25, 1))
    print("W3: ")
    print(w3)


    h3 = np.ones((1,))
    for i in range(np.shape(memWeights)[0]):
      h3 += ((memWeights[i][5]).flatten())
    h3 /= (np.shape(memWeights)[0])
    h3 = np.reshape(h3, (1, ))
    print("H3: ")
    print(h3)

    model_weights = [w1, h1, w2, h2, w3, h3]
    model = tf.keras.models.Sequential([tf.keras.layers.Dense(15, activation=tf.keras.activations.relu, input_shape=(10, )),
    tf.keras.layers.Dense(25, activation=tf.keras.activations.relu),
    tf.keras.layers.Dense(1, activation=tf.keras.activations.relu)])
    model.compile(optimizer=tf.keras.optimizers.Adam(), loss=tf.keras.losses.mean_squared_error)
    print(model_weights)
    model.set_weights(model_weights)
    saver = tf.train.Saver()
    sess = tf.keras.backend.get_session()
    save_path = saver.save(sess, "FINAL_GRAPH.ckpt")
    with open("checkpoint", "rb") as f:
        blob = bucket.blob('checkpoint')
        blob.upload_from_file(f)
    with open("FINAL_GRAPH.ckpt.data-00000-of-00001", "rb") as f:
        blob = bucket.blob('FINAL_GRAPH.ckpt.data-00000-of-00001')
        blob.upload_from_file(f)
    with open("FINAL_GRAPH.ckpt.index", "rb") as f:
        blob = bucket.blob('FINAL_GRAPH.ckpt.index')
        blob.upload_from_file(f)
    with open("FINAL_GRAPH.ckpt.meta", "rb") as f:
        blob = bucket.blob('FINAL_GRAPH.ckpt.meta')
        blob.upload_from_file(f)
    print("Files Uploaded")
    print("Global Model Updated")
    zipf = zipfile.ZipFile('model' + str(modelctr) + '.zip','w', zipfile.ZIP_DEFLATED)
    bucket = storage.bucket(app = fireapp)
    blobs = bucket.list_blobs()
    for blob in blobs:
      if blob.name == 'checkpoint' or 'FINAL_GRAPH' in blob.name:
        blob.download_to_filename(blob.name)
        zipf.write(blob.name)
    blob = bucket.blob('checkpoint')
    with open('model' + str(modelctr) + '.zip', 'rb') as f:
      blob.upload_from_file(f)
    ref.update({'isUpdated': 'True'})
    ref.update({'modelctr': (modelctr + 1)})
    with open('x_test.bin', 'rb') as f:
      x_test = pickle.load(f)
    print(np.shape(x_test))
    print(np.shape(x_test[0]))
    with open('y_test.bin', 'rb') as f:
      y_test = pickle.load(f)
    x_test = np.asarray(x_test, dtype = np.float32)
    y_test = np.asarray(y_test, dtype = np.float32)
    print((y_test.shape))
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
    pred = model.predict(np.array(x_test))
    print(pred)
    print(np.isnan(y_test).any())
    print(np.isnan(pred).any())
    from sklearn.metrics import mean_squared_error
    mse = mean_squared_error(pred, y_test)
    print(mse)
    rmse = (mse**0.5)
    print(rmse)
    lossref = db.reference("/Losses")
    lossref.push({dt_string: rmse})
    for blob in blob_ls:
      delete_blob(blob)
    ref.update({'num': 0})
    print("Weights Deleted")
    return "Global Model Updated\n"
scheduled_job()
sched.start()
