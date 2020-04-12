import firebase_admin
from firebase_admin import credentials, storage, db

cred = {
}
certi = firebase_admin.credentials.Certificate(cred)
fireapp = firebase_admin.initialize_app(certi, {'storageBucket': ,'databaseURL': })

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
