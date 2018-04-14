'''This script goes along the blog post
"Building powerful image classification models using very little data"
from blog.keras.io.
It uses data that can be downloaded at:
https://www.kaggle.com/c/dogs-vs-cats/data

'''

from keras.preprocessing.image import ImageDataGenerator
from keras import backend as K
from keras import metrics
from keras_squeezenet import SqueezeNet
import functools

# dimensions of our images.
img_width, img_height = 140, 140

class_number=4


train_data_dir = 'data_EE_2F/4class_v2/train'
validation_data_dir = 'data_EE_2F/4class_v2/validation'
nb_train_samples = 4200
nb_validation_samples = 1450

epochs = 15
batch_size = 50


if K.image_data_format() == 'channels_first':
    input_shape = (3, img_width, img_height)
else:
    input_shape = (img_width, img_height, 3)

model=SqueezeNet(load_weight=False,weights=None,input_shape=input_shape,classes=class_number)

top2_acc = functools.partial(metrics.top_k_categorical_accuracy, k=2)
top2_acc.__name__ = 'top2_acc'

model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy', top2_acc])

# this is the augmentation configuration we will use for training
train_datagen = ImageDataGenerator(rescale=1. / 255)

# this is the augmentation configuration we will use for testing:
# only rescaling
test_datagen = ImageDataGenerator(rescale=1. / 255)

train_generator = train_datagen.flow_from_directory(
    train_data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='categorical')

validation_generator = test_datagen.flow_from_directory(
    validation_data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='categorical')

train_history=model.fit_generator(
    train_generator,
    steps_per_epoch=nb_train_samples/batch_size,
    epochs=epochs,
    validation_data=validation_generator,
    validation_steps=nb_validation_samples//batch_size)
    

model.save_weights('navigation_cnn_squeezenet_EE_2F_4class_v2_140x140.h5')
    
#view gradient descent    
import matplotlib.pyplot as plt
def show_train_history(train_history,train,validation):
	plt.plot(train_history.history[train])
	plt.plot(train_history.history[validation])
	plt.title('Train History')
	plt.ylabel(train)
	plt.xlabel('Epoch')
	plt.legend(['train', 'validation'], loc='upper left')
	plt.show()
						
show_train_history(train_history,'acc','val_acc')
show_train_history(train_history,'loss','val_loss')

#building confusion matrix
import numpy as np

evaluation_datagen = ImageDataGenerator(rescale=1. / 255)
evaluation_generator = evaluation_datagen.flow_from_directory(
    validation_data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='categorical',
    shuffle=False)

prediction=model.predict_generator(evaluation_generator,nb_validation_samples//batch_size)
prediction = np.argmax(prediction, axis=1)
        
import pandas as pd
pd.crosstab(evaluation_generator.classes,prediction,
            rownames=['label'],colnames=['predict'])
print(evaluation_generator.class_indices)
