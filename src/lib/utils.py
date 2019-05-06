class DotDict(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except Exception as e:
            raise AttributeError


def set_gpu_memory_grow():
    import keras.backend.tensorflow_backend as KTF
    import tensorflow as tf
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    session = tf.Session(config=config)
    KTF.set_session(session)
