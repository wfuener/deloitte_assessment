"""
Inference script is required by sagemaker

The script will run inside a PyTorch container. The PyTorch container provides
default implementations for generating a prediction and input/output processing.
"""

import os
import json
from transformers import BertTokenizer, BertModel
import sys
import logging


# create logger
logger = logging.getLogger('model')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
handler = logging.StreamHandler(stream=sys.stdout)
handler.setLevel(logging.DEBUG)

# add formatter to ch
handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

# add ch to logger
logger.addHandler(handler)

logger.info("loading model into sagemaker...")


def model_fn(model_dir):
    """Load the model for inference. Required by Sagemaker.
    """
    logger.info("loading modeling")
    model_path = os.getcwd()

    # Load BERT tokenizer from disk.
    tokenizer = BertTokenizer.from_pretrained(model_path)

    # Load BERT model from disk.
    model = BertModel.from_pretrained(model_path)

    model_dict = {'model': model, 'tokenizer': tokenizer}
    logger.info("finished loading")
    return model_dict


def predict_fn(input_data, model):
    """Apply model to the incoming request. Overrides default Sagemaker function.
    """
    logger.debug(f"predicting: {input_data}")
    tokenizer = model['tokenizer']
    bert_model = model['model']

    encoded_input = tokenizer(input_data, return_tensors='pt')
    logger.debug(f"encoded_input: {encoded_input}")

    return bert_model(**encoded_input)


def input_fn(request_body, request_content_type):
    """Deserialize and prepare the prediction input. Overrides default Sagemaker function.
    """
    if request_content_type == "application/json":
        return json.loads(request_body)
    else:
        return request_body


def output_fn(prediction, response_content_type):
    """Serialize and prepare the prediction output. Overrides default Sagemaker function.
    """
    return str(prediction)

