import traceback
from tensorflow.python.saved_model import builder as saved_model_builder, tag_constants
from tensorflow.python.saved_model.signature_def_utils_impl import predict_signature_def

from neural_net import build_and_train
from utils import save_json_result
import tensorflow as tf
import keras.backend as K
from hyperopt import STATUS_FAIL


def optimize_cnn(hype_space):
    """Build a convolutional neural network and train it."""
    tf.logging.debug("Hyperspace: ", hype_space)
    tf.logging.debug("\n")
    try:
        model, model_name, result, _ = build_and_train(hype_space)

        tf.logging.info("Training ended with success:")
        tf.logging.info("Model name: ", model_name)

        # Save training results to disks with unique filenames
        # TODO do we need this? this save to json on disc not to mongo. Not sure if we want always save to disc

        save_json_result(model_name, result)

        # Export Model
        #K.set_learning_phase(0)
        #saved_model = model.save('results/model.h5')
        builder = saved_model_builder.SavedModelBuilder('results')

        # TODO FIX THIS
        signature = predict_signature_def(inputs={'images': model.input},
                                          outputs={'scores': model.output})
        with K.get_session() as sess:
            builder.add_meta_graph_and_variables(sess=sess,
                                                 tags=[tag_constants.SERVING],
                                                 signature_def_map={'predict': signature})
            builder.save()
        K.clear_session()
        del model
        tf.logging.info('before return result')
        return result

    except Exception as err:
        try:
            K.clear_session()
        except:
            pass
        err_str = str(err)
        tf.logging.error(err_str)
        traceback_str = str(traceback.format_exc())
        tf.logging.error(traceback_str)
        return {
            'status': STATUS_FAIL,
            'err': err_str,
            'traceback': traceback_str
        }
