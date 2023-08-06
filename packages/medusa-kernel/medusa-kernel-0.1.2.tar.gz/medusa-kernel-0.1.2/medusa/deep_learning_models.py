# Built-in imports
import warnings
import os
# External imports
import tensorflow as tf
from tensorflow.keras.layers import Activation, Input, Flatten
from tensorflow.keras.layers import Dropout, BatchNormalization
from tensorflow.keras.layers import Conv2D, AveragePooling2D, DepthwiseConv2D
from tensorflow.keras.layers import Dense, SpatialDropout2D, SeparableConv2D
from tensorflow.keras.constraints import max_norm
from tensorflow.keras.callbacks import EarlyStopping
import tensorflow.keras as keras
import sklearn.utils as sk_utils
import numpy as np

# Medusa imports
from medusa import components
from medusa import classification_utils
from medusa import tensorflow_integration


class EEGInceptionv1(components.ProcessingMethod):
    """EEG-Inception as described in Santamaría-Vázquez et al. 2020 [1]. This
    model is specifically designed for EEG classification tasks.

    References
    ----------
    [1] Santamaría-Vázquez, E., Martínez-Cagigal, V., Vaquerizo-Villar, F., &
    Hornero, R. (2020). EEG-Inception: A Novel Deep Convolutional Neural Network
    for Assistive ERP-based Brain-Computer Interfaces. IEEE Transactions on
    Neural Systems and Rehabilitation Engineering.
    """
    def __init__(self, input_time=1000, fs=128, n_cha=8, filters_per_branch=8,
                 scales_time=(500, 250, 125), dropout_rate=0.25,
                 activation='elu', n_classes=2, learning_rate=0.001,
                 gpu_acceleration=None):
        # Super call
        super().__init__(fit=[], predict_proba=['y_pred'])

        # Tensorflow config
        if gpu_acceleration is None:
            tensorflow_integration.check_tf_config(autoconfig=True)
        else:
            tensorflow_integration.config_tensorflow(gpu_acceleration)
        if tensorflow_integration.check_gpu_acceleration():
            os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
        tf.keras.backend.set_image_data_format('channels_last')

        # Parameters
        self.input_time = input_time
        self.fs = fs
        self.n_cha = n_cha
        self.filters_per_branch = filters_per_branch
        self.scales_time = scales_time
        self.dropout_rate = dropout_rate
        self.activation = activation
        self.n_classes = n_classes
        self.learning_rate = learning_rate

        # Useful variables
        self.input_samples = int(input_time * fs / 1000)
        self.scales_samples = [int(s * fs / 1000) for s in scales_time]

        # Create model
        self.model = self.__keras_model()
        # Create training callbacks
        self.training_callbacks = list()
        self.training_callbacks.append(
            EarlyStopping(monitor='val_loss',
                          min_delta=0.001,
                          mode='min',
                          patience=20,
                          verbose=1,
                          restore_best_weights=True)
        )
        # Create fine-tuning callbacks
        self.fine_tuning_callbacks = list()
        self.fine_tuning_callbacks.append(
            EarlyStopping(monitor='val_loss',
                          min_delta=0.0001,
                          mode='min',
                          patience=10,
                          verbose=1,
                          restore_best_weights=True)
        )

    def __keras_model(self):
        # ============================= INPUT ================================ #
        input_layer = Input((self.input_samples, self.n_cha, 1))
        # ================ BLOCK 1: SINGLE-CHANNEL ANALYSIS ================== #
        b1_units = list()
        for i in range(len(self.scales_samples)):
            unit = Conv2D(filters=self.filters_per_branch,
                          kernel_size=(self.scales_samples[i], 1),
                          kernel_initializer='he_normal',
                          padding='same')(input_layer)
            unit = BatchNormalization()(unit)
            unit = Activation(self.activation)(unit)
            unit = Dropout(self.dropout_rate)(unit)

            b1_units.append(unit)

        # Concatenation
        b1_out = keras.layers.concatenate(b1_units, axis=3)
        b1_out = AveragePooling2D((2, 1))(b1_out)

        # ================= BLOCK 2: SPATIAL FILTERING ======================= #
        b2_unit = DepthwiseConv2D((1, self.n_cha),
                                  use_bias=False,
                                  depth_multiplier=2,
                                  depthwise_constraint=max_norm(1.))(b1_out)
        b2_unit = BatchNormalization()(b2_unit)
        b2_unit = Activation(self.activation)(b2_unit)
        b2_unit = Dropout(self.dropout_rate)(b2_unit)
        b2_out = AveragePooling2D((2, 1))(b2_unit)

        # ================ BLOCK 3: MULTI-CHANNEL ANALYSIS =================== #
        b3_units = list()
        for i in range(len(self.scales_samples)):
            unit = Conv2D(filters=self.filters_per_branch,
                          kernel_size=(int(self.scales_samples[i] / 4), 1),
                          kernel_initializer='he_normal',
                          use_bias=False,
                          padding='same')(b2_out)
            unit = BatchNormalization()(unit)
            unit = Activation(self.activation)(unit)
            unit = Dropout(self.dropout_rate)(unit)

            b3_units.append(unit)

        # Concatenate + Average pooling
        b3_out = keras.layers.concatenate(b3_units, axis=3)
        b3_out = AveragePooling2D((2, 1))(b3_out)

        # ==================== BLOCK 4: OUTPUT-BLOCK ========================= #
        b4_u1 = Conv2D(filters=int(self.filters_per_branch *
                                   len(self.scales_samples) / 2),
                       kernel_size=(8, 1),
                       kernel_initializer='he_normal',
                       use_bias=False,
                       padding='same')(b3_out)
        b4_u1 = BatchNormalization()(b4_u1)
        b4_u1 = Activation(self.activation)(b4_u1)
        b4_u1 = AveragePooling2D((2, 1))(b4_u1)
        b4_u1 = Dropout(self.dropout_rate)(b4_u1)

        b4_u2 = Conv2D(filters=int(self.filters_per_branch *
                                   len(self.scales_samples) / 4),
                       kernel_size=(4, 1),
                       kernel_initializer='he_normal',
                       use_bias=False,
                       padding='same')(b4_u1)
        b4_u2 = BatchNormalization()(b4_u2)
        b4_u2 = Activation(self.activation)(b4_u2)
        b4_u2 = AveragePooling2D((2, 1))(b4_u2)
        b4_out = Dropout(self.dropout_rate)(b4_u2)

        # =========================== OUTPUT ================================= #
        # Output layer
        output_layer = Flatten()(b4_out)
        output_layer = Dense(self.n_classes, activation='softmax')(output_layer)
        # ============================ MODEL ================================= #
        # Optimizer
        optimizer = keras.optimizers.Adam(learning_rate=self.learning_rate,
                                          beta_1=0.9, beta_2=0.999,
                                          amsgrad=False)
        # Create and compile model
        model = keras.models.Model(inputs=input_layer,
                                   outputs=output_layer)
        model.compile(loss='categorical_crossentropy',
                      optimizer=optimizer,
                      metrics=['accuracy'])

        return model

    @staticmethod
    def transform_data(X, y=None):
        """Transforms input data to the correct dimensions for EEG-Inception

        Parameters
        ----------
        X: np.ndarray
            Feature matrix. If shape is [n_observ x n_samples x n_channels],
            this matrix will be adapted to the input dimensions of EEG-Inception
            [n_observ x n_samples x n_channels x 1]
        y: np.ndarray
            Labels array. If labels are in categorical format, they will be
            converted to one-hot encoding.
        """
        if len(X.shape) == 3 or X.shape[-1] != 1:
            X = X.reshape((X.shape[0], X.shape[1], X.shape[2], 1))
        if y is None:
            return X
        else:
            if len(y.shape) == 1 or y.shape[-1] == 1:
                y = classification_utils.one_hot_labels(y)
            return X, y

    def fit(self, X, y, fine_tuning=False, shuffle_before_fit=False, **kwargs):
        """Fit the model. All additional keras parameters of class
        tensorflow.keras.Model will pass through. See keras documentation to
        know what can you do: https://keras.io/api/models/model_training_apis/.

        If no parameters are specified, some default options are set [1]:

            - Epochs: 100 if fine_tuning else 500
            - Batch size: 32 if fine_tuning else 1024
            - Callbacks: self.fine_tuning_callbacks if fine_tuning else
                self.training_callbacks

        Parameters
        ----------
        X: np.ndarray
            Feature matrix. If shape is [n_observ x n_samples x n_channels],
            this matrix will be adapted to the input dimensions of EEG-Inception
            [n_observ x n_samples x n_channels x 1]
        y: np.ndarray
            Feature matrix. If shape is [n_observ x n_samples x n_channels],
            this matrix will be adapted to the input dimensions of EEG-Inception
            [n_observ x n_samples x n_channels x 1]
        fine_tuning: bool
            Set to True to use the default training parameters for fine
            tuning. False by default.
        shuffle_before_fit: bool
            If True, the data will be shuffled before training just once. Note
            that if you use the keras native argument 'shuffle', the data is
            shuffled each epoch.
        kwargs:
            Key-value arguments will be passed to the fit function of the model.
            This way, you can set your own training parameters using keras API.
            See https://www.tensorflow.org/api_docs/python/tf/keras/Model#fit
        """
        # Check numpy arrays
        X = np.array(X)
        y = np.array(y)
        # Check GPU
        if not tensorflow_integration.check_gpu_acceleration():
            warnings.warn('GPU acceleration is not available. The training '
                          'time is drastically reduced with GPU.')
        # Shuffle the data before fitting
        if shuffle_before_fit:
            X, y = sk_utils.shuffle(X, y)
        # Training parameters
        if not fine_tuning:
            # Rewrite default values
            kwargs['epochs'] = kwargs['epochs'] if \
                'epochs' in kwargs else 500
            kwargs['batch_size'] = kwargs['batch_size'] if \
                'batch_size' in kwargs else 1024
            kwargs['callbacks'] = kwargs['callbacks'] if \
                'callbacks' in kwargs else self.training_callbacks
        else:
            kwargs['epochs'] = kwargs['epochs'] if \
                'epochs' in kwargs else 100
            kwargs['batch_size'] = kwargs['batch_size'] if \
                'batch_size' in kwargs else 32
            kwargs['callbacks'] = kwargs['callbacks'] if \
                'callbacks' in kwargs else self.fine_tuning_callbacks

        # Transform data if necessary
        X, y = self.transform_data(X, y)
        # Fit
        with tf.device(tensorflow_integration.get_tf_device_name()):
            return self.model.fit(X, y, **kwargs)

    def predict_proba(self, X):
        """Model prediction scores for the given features.

        Parameters
        ----------
        X: np.ndarray
            Feature matrix. If shape is [n_observ x n_samples x n_channels],
            this matrix will be adapted to the input dimensions of EEG-Inception
            [n_observ x n_samples x n_channels x 1]
        """
        # Check numpy arrays
        X = np.array(X)
        # Transform data if necessary
        X = self.transform_data(X)
        # Predict
        with tf.device(tensorflow_integration.get_tf_device_name()):
            return self.model.predict(X)

    def to_pickleable_obj(self):
        # Parameters
        kwargs = {
            'input_time': self.input_time,
            'fs': self.fs,
            'n_cha': self.n_cha,
            'filters_per_branch': self.filters_per_branch,
            'scales_time': self.scales_time,
            'dropout_rate': self.dropout_rate,
            'activation': self.activation,
            'n_classes': self.n_classes,
            'learning_rate': self.learning_rate,
        }
        weights = self.model.get_weights()
        # Pickleable object
        pickleable_obj = {
            'kwargs': kwargs,
            'weights': weights
        }
        return pickleable_obj

    @classmethod
    def from_pickleable_obj(cls, pickleable_obj):
        model = cls(**pickleable_obj['kwargs'])
        model.model.set_weights(pickleable_obj['weights'])
        return model

    def set_weights(self, weights):
        return self.model.set_weights(weights)

    def get_weights(self):
        return self.model.get_weights()

    def save_weights(self, path):
        return self.model.save_weights(path)

    def load_weights(self, weights_path):
        return self.model.load_weights(weights_path)


class EEGNet(components.ProcessingMethod):
    """EEG-Inception as described in Lawhern et al. 2018 [1]. This model is
    specifically designed for EEG classification tasks.

    Original source https://github.com/vlawhern/arl-eegmodels

    References
    ----------
    [1] Lawhern, V. J., Solon, A. J., Waytowich, N. R., Gordon, S. M., Hung,
    C. P., & Lance, B. J. (2018). EEGNet: a compact convolutional neural network
    for EEG-based brain–computer interfaces. Journal of neural engineering,
    15(5), 056013.
    """
    def __init__(self, nb_classes, n_cha=64, samples=128, dropout_rate=0.5,
                 kern_length=64, F1=8, D=2, F2=16, norm_rate=0.25,
                 dropout_type='Dropout', learning_rate=0.001,
                 gpu_acceleration=None):

        # Super call
        super().__init__(fit=[], predict_proba=['y_pred'])

        # Tensorflow config
        if gpu_acceleration is None:
            tensorflow_integration.check_tf_config(autoconfig=True)
        else:
            tensorflow_integration.config_tensorflow(gpu_acceleration)
        if tensorflow_integration.check_gpu_acceleration():
            os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
        tf.keras.backend.set_image_data_format('channels_last')

        # Parameters
        self.nb_classes = nb_classes
        self.n_cha = n_cha
        self.samples = samples
        self.dropout_rate = dropout_rate
        self.kern_length = kern_length
        self.F1 = F1
        self.D = D
        self.F2 = F2
        self.norm_rate = norm_rate
        self.dropout_type = dropout_type
        self.learning_rate = learning_rate

        # Create model
        self.model = self.__keras_model()

        # Create training callbacks
        self.training_callbacks = list()
        self.training_callbacks.append(
            EarlyStopping(monitor='val_loss',
                          min_delta=0.001,
                          mode='min',
                          patience=20,
                          verbose=1,
                          restore_best_weights=True)
        )
        # Create fine-tuning callbacks
        self.fine_tuning_callbacks = list()
        self.fine_tuning_callbacks.append(
            EarlyStopping(monitor='val_loss',
                          min_delta=0.0001,
                          mode='min',
                          patience=10,
                          verbose=1,
                          restore_best_weights=True)
        )

    def __keras_model(self):
        """ Keras Implementation of EEGNet
        http://iopscience.iop.org/article/10.1088/1741-2552/aace8c/meta
        Note that this implements the newest version of EEGNet and NOT the
        earlier version (version v1 and v2 on arxiv). We strongly recommend
        using this architecture as it performs much better and has nicer
        properties than our earlier version. For example:

            1. Depthwise Convolutions to learn spatial filters within a
            temporal convolution. The use of the depth_multiplier option maps
            exactly to the number of spatial filters learned within a temporal
            filter. This matches the setup of algorithms like FBCSP which learn
            spatial filters within each filter in a filter-bank. This also
            limits the number of free parameters to fit when compared to a
            fully-connected convolution.

            2. Separable Convolutions to learn how to optimally combine spatial
            filters across temporal bands. Separable Convolutions are Depthwise
            Convolutions followed by (1x1) Pointwise Convolutions.


        While the original paper used Dropout, we found that SpatialDropout2D
        sometimes produced slightly better results for classification of ERP
        signals. However, SpatialDropout2D significantly reduced performance
        on the Oscillatory dataset (SMR, BCI-IV Dataset 2A). We recommend using
        the default Dropout in most cases.

        Assumes the input signal is sampled at 128Hz. If you want to use this
        model for any other sampling rate you will need to modify the lengths of
        temporal kernels and average pooling size in blocks 1 and 2 as needed
        (double the kernel lengths for double the sampling rate, etc). Note
        that we haven't tested the model performance with this rule so this
        may not work well.

        The model with default parameters gives the EEGNet-8,2 model as
        discussed in the paper. This model should do pretty well in general,
        although it is advised to do some model searching to get optimal
        performance on your particular dataset.

        We set F2 = F1 * D (number of input filters = number of output filters)
        for the SeparableConv2D layer. We haven't extensively tested other
        values of this parameter (say, F2 < F1 * D for compressed learning,
        and F2 > F1 * D for overcomplete). We believe the main parameters to
        focus on are F1 and D.

        Inputs:

          nb_classes      : int, number of classes to classify
          Chans, Samples  : number of channels and time points in the EEG data
          dropoutRate     : dropout fraction
          kernLength      : length of temporal convolution in first layer. We
                            found that setting this to be half the sampling
                            rate worked well in practice. For the SMR dataset in
                            particular since the data was high-passed at 4Hz
                            we used a kernel length of 32.
          F1, F2          : number of temporal filters (F1) and number of
                            pointwise filters (F2) to learn. Default: F1 = 8,
                            F2 = F1 * D.
          D               : number of spatial filters to learn within each
                            temporal convolution. Default: D = 2
          dropoutType     : Either SpatialDropout2D or Dropout, passed as a
                            string.
        """

        if self.dropout_type == 'SpatialDropout2D':
            self.dropout_type = SpatialDropout2D
        elif self.dropout_type == 'Dropout':
            self.dropout_type = Dropout
        else:
            raise ValueError('dropoutType must be one of SpatialDropout2D '
                             'or Dropout, passed as a string.')

        input1 = Input(shape=(self.n_cha, self.samples, 1))

        ##################################################################
        block1 = Conv2D(self.F1, (1, self.kern_length), padding='same',
                        input_shape=(self.n_cha, self.samples, 1),
                        use_bias=False)(input1)
        block1 = BatchNormalization()(block1)
        block1 = DepthwiseConv2D((self.n_cha, 1), use_bias=False,
                                 depth_multiplier=self.D,
                                 depthwise_constraint=max_norm(1.))(block1)
        block1 = BatchNormalization()(block1)
        block1 = Activation('elu')(block1)
        block1 = AveragePooling2D((1, 4))(block1)
        block1 = self.dropout_type(self.dropout_rate)(block1)

        block2 = SeparableConv2D(self.F2, (1, 16),
                                 use_bias=False, padding='same')(block1)
        block2 = BatchNormalization()(block2)
        block2 = Activation('elu')(block2)
        block2 = AveragePooling2D((1, 8))(block2)
        block2 = self.dropout_type(self.dropout_rate)(block2)

        flatten = Flatten(name='flatten')(block2)

        dense = Dense(self.nb_classes, name='dense',
                      kernel_constraint=max_norm(self.norm_rate))(flatten)
        softmax = Activation('softmax', name='softmax')(dense)

        # Create and compile model
        model = keras.models.Model(inputs=input1, outputs=softmax)
        optimizer = keras.optimizers.Adam(learning_rate=self.learning_rate,
                                          beta_1=0.9, beta_2=0.999,
                                          amsgrad=False)
        model.compile(loss='categorical_crossentropy',
                      optimizer=optimizer,
                      metrics=['accuracy'])

        return model

    @staticmethod
    def transform_data(X, y=None):
        """Transforms input data to the correct dimensions for EEG-Inception

        Parameters
        ----------
        X: np.ndarray
            Feature matrix. If shape is [n_observ x n_samples x n_channels],
            this matrix will be adapted to the input dimensions of EEG-Inception
            [n_observ x n_samples x n_channels x 1]
        y: np.ndarray
            Labels array. If labels are in categorical format, they will be
            converted to one-hot encoding.
        """
        if len(X.shape) == 3 or X.shape[-1] != 1:
            X = X.reshape((X.shape[0], X.shape[1], X.shape[2], 1))
            X = np.swapaxes(X, 1, 2)
        if y is None:
            return X
        else:
            if len(y.shape) == 1 or y.shape[-1] == 1:
                y = classification_utils.one_hot_labels(y)
            return X, y

    def fit(self, X, y, fine_tuning=False, shuffle_before_fit=False, **kwargs):
        """Fit the model. All additional keras parameters of class
        tensorflow.keras.Model will pass through. See keras documentation to
        know what can you do: https://keras.io/api/models/model_training_apis/.

        If no parameters are specified, some default options are set [1]:

            - Epochs: 100 if fine_tuning else 500
            - Batch size: 32 if fine_tuning else 1024
            - Callbacks: self.fine_tuning_callbacks if fine_tuning else
                self.training_callbacks

        Parameters
        ----------
        X: np.ndarray
            Feature matrix. If shape is [n_observ x n_samples x n_channels],
            this matrix will be adapted to the input dimensions of EEG-Inception
            [n_observ x n_samples x n_channels x 1]
        y: np.ndarray
            Feature matrix. If shape is [n_observ x n_samples x n_channels],
            this matrix will be adapted to the input dimensions of EEG-Inception
            [n_observ x n_samples x n_channels x 1]
        fine_tuning: bool
            Set to True to use the default training parameters for fine
            tuning. False by default.
        shuffle_before_fit: bool
            If True, the data will be shuffled before training.
        kwargs:
            Key-value arguments will be passed to the fit function of the model.
            This way, you can set your own training parameters for keras.
            See https://www.tensorflow.org/api_docs/python/tf/keras/Model#fit
        """
        # Check numpy arrays
        X = np.array(X)
        y = np.array(y)
        # Check GPU
        if not tensorflow_integration.check_gpu_acceleration():
            warnings.warn('GPU acceleration is not available. The training '
                          'time is drastically reduced with GPU.')

        # Shuffle the data before fitting
        if shuffle_before_fit:
            X, y = sk_utils.shuffle(X, y)

        # Training parameters
        if not fine_tuning:
            # Rewrite default values
            kwargs['epochs'] = kwargs['epochs'] if \
                'epochs' in kwargs else 500
            kwargs['batch_size'] = kwargs['batch_size'] if \
                'batch_size' in kwargs else 1024
            kwargs['callbacks'] = kwargs['callbacks'] if \
                'callbacks' in kwargs else self.training_callbacks
        else:
            kwargs['epochs'] = kwargs['epochs'] if \
                'epochs' in kwargs else 100
            kwargs['batch_size'] = kwargs['batch_size'] if \
                'batch_size' in kwargs else 32
            kwargs['callbacks'] = kwargs['callbacks'] if \
                'callbacks' in kwargs else self.fine_tuning_callbacks

        # Transform data if necessary
        X, y = self.transform_data(X, y)
        # Fit
        with tf.device(tensorflow_integration.get_tf_device_name()):
            return self.model.fit(X, y, **kwargs)

    def predict_proba(self, X):
        """Model prediction scores for the given features.

        Parameters
        ----------
        X: np.ndarray
            Feature matrix. If shape is [n_observ x n_samples x n_channels],
            this matrix will be adapted to the input dimensions of EEG-Inception
            [n_observ x n_samples x n_channels x 1]
        """
        # Check numpy arrays
        X = np.array(X)
        # Transform data if necessary
        X = self.transform_data(X)
        # Predict
        with tf.device(tensorflow_integration.get_tf_device_name()):
            return self.model.predict(X)

    def to_pickleable_obj(self):
        # Key data
        kwargs = {
            'nb_classes': self.nb_classes,
            'n_cha': self.n_cha,
            'samples': self.samples,
            'dropout_rate': self.dropout_rate,
            'kern_length': self.kern_length,
            'F1': self.F1,
            'D': self.D,
            'F2': self.F2,
            'norm_rate': self.norm_rate,
            'dropout_type': self.dropout_type,
            'learning_rate': self.learning_rate
        }
        weights = self.model.get_weights()
        # Pickleable object
        pickleable_obj = {
            'kwargs': kwargs,
            'weights': weights
        }
        return pickleable_obj

    @classmethod
    def from_pickleable_obj(cls, pickleable_obj):
        model = cls(**pickleable_obj['kwargs'])
        model.model.set_weights(pickleable_obj['weights'])
        return model

    def set_weights(self, weights):
        return self.model.set_weights(weights)

    def get_weights(self):
        return self.model.get_weights()

    def save_weights(self, path):
        return self.model.save_weights(path)

    def load_weights(self, weights_path):
        return self.model.load_weights(weights_path)
