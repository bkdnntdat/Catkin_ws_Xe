#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright @ 2019 Liming Liu     HuNan University
#


"""predict the model"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
from tf_bisenet.models.bisenet import BiseNet
from tf_bisenet import configuration
import cv2
import numpy as np
import time
import rospkg
rospack = rospkg.RosPack()
cur_dir = rospack.get_path('team503')

colors = np.array([[0,0,0],
[128,64,128],
[0,0,142],
[220,220,0],
[70,130,180]], dtype=np.float32)


class BiseNet_Loader(object):
    def __init__(self):

        model_config = configuration.MODEL_CONFIG
        train_config = configuration.TRAIN_CONFIG
        infer_size = (320, 320)

        self.input_image = tf.placeholder(shape=[None, None, 3], dtype=tf.float32)
        g = tf.Graph()
        # with g.as_default():
        # Build the test model
        self.model = BiseNet(model_config, None, 5, 'inference')
        self.model.build(self.input_image)
        self.response = self.model.response

        self.saver = tf.train.Saver()
        # Dynamically allocate GPU memory
        gpu_options = tf.GPUOptions(allow_growth=True)
        sess_config = tf.ConfigProto(gpu_options=gpu_options)

        self.sess = tf.Session(config=sess_config)
        # model_path = tf.train.latest_checkpoint(train_config['train_dir'])

        # global_variables_init_op = tf.global_variables_initializer()
        # local_variables_init_op = tf.local_variables_initializer()

        # sess.run(local_variables_init_op)
        self.saver1 = tf.train.Saver(var_list=tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope='Bisenet'))
        self.saver1.restore(self.sess, cur_dir + "/scripts/tf_bisenet/Logs/bisenet-v2/hsv_210000/model.ckpt-210000")
        img = np.ones((320, 320, 3))
        self.transform = tf.reshape(tf.matmul(tf.reshape(tf.one_hot(tf.argmax(self.response, -1), 5), [-1, 5]), colors),
                            [-1, infer_size[0], infer_size[1], 3])
        _ = self.sess.run(self.transform, feed_dict={self.input_image: img})

        print("Model loaded!")

    def predict(self, img):
        img = cv2.resize(img, (320, 320))
        img = img/255.

        predict = self.sess.run(self.transform, feed_dict={self.input_image: img})
        predict = cv2.cvtColor(predict[0], cv2.COLOR_RGB2BGR)
        return predict

