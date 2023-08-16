from keras_preprocessing import image
from keras.models import load_model
from keras.applications.vgg16 import preprocess_input
import numpy as np

model=load_model('chest_xray.h5')
img=image.load_img('D:\primary-atypical-pneumonia.jpg',target_size=(224,224))
x=image.img_to_array(img)
x=np.expand_dims(x, axis=0)
img_data=preprocess_input(x)
classes=model.predict(img_data)
print(classes)
result=int(classes[0][0])
print(result)
if result == 0:
    print("Person is Affected By PNEUMONIA")
else:
    print("Result is Normal")