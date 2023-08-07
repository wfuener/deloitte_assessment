"""This script can deploy a pretrained model to AWS Sagemaker"""
import json
import os
import sys
import tarfile
import time
from datetime import datetime
import boto3
from transformers import BertTokenizer, BertModel
import sagemaker
from botocore.exceptions import ClientError
from sagemaker.pytorch import PyTorchModel

# This setup_default_session was needed when running locally but shouldn't be needed if running in the cloud
boto3.setup_default_session(profile_name='personal', region_name='us-east-2')
sagemaker_session = sagemaker.Session(boto3.session.Session(region_name='us-east-2'))

# set out constants variables
ROLE_NAME = "sagemaker-endpoint"
MODEL_PATH = "model/"
CODE_PATH = "code/"
ZIPPED_MODEL_PATH = os.path.join(MODEL_PATH, "model.tar.gz")
# Endpoint names must be unique in all of AWS
ENDPOINT_NAME = "bert-base-" + time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())


def main():
    """Main method which will control the logic flow"""
    create_iam_role()
    get_model_artifacts()
    package_model()
    deploy()
    predict()


def create_iam_role():
    """Create role for our new sagemaker endpoint using boto3. Normally this
    would be done with a tool like terraform but for demo purposes boto3 works great."""
    client = boto3.client('iam')

    assume_role_policy = {  # AssumeRolePolicyDocument is required for all roles
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {
                    "Service": "sagemaker.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    # first create the role
    try:
        client.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy),
            Description='Role for creating sagemaker inference endpoints',
        )
    except ClientError as exc:
        if exc.response['Error']['Code'] == 'EntityAlreadyExists':
            print("SageMaker role already created")
        else:
            print(f"Something went wrong while creating sagemaker role {exc}")

    except Exception as exc:
        print(f"something went wrong while creating sagemaker role. Exiting. {exc}")
        sys.exit()

    else:
        print(f"Successfully created sagemaker role {ROLE_NAME}")

    # then attach the sagemaker policy. AmazonSageMakerFullAccess is a builtin role made by AWS
    # attach won't through an error if already attached
    client.attach_role_policy(
        RoleName=ROLE_NAME, PolicyArn='arn:aws:iam::aws:policy/AmazonSageMakerFullAccess')

    print(f"Successfully attached sagemaker policy to {ROLE_NAME}")


def get_model_artifacts():
    """ Retrieve Model Artifacts from Hugging face using the transformers' library. We
    will be demoing with the Bert Model. Place downloaded files in the specified MODEL PATH
    """
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model = BertModel.from_pretrained("bert-base-uncased")

    if not os.path.exists(MODEL_PATH):
        os.mkdir(MODEL_PATH)

    model.save_pretrained(save_directory=MODEL_PATH)
    tokenizer.save_pretrained(save_directory=MODEL_PATH)


def package_model():
    """Package the Model to SageMaker specifications the package.
    It needs all files to be packaged in a tar archive named “model.tar.gz” with gzip compression.
    The model files need to be in the root directory and code directory should have files: inference.py
    and requirements.txt
    """
    print("Packaging and compressing model file")

    with tarfile.open(ZIPPED_MODEL_PATH, "w:gz") as tar:
        tar.add(CODE_PATH)
        # add the contents of the model directory to the root level
        for fn in os.listdir(MODEL_PATH):
            path = os.path.join(MODEL_PATH, fn)
            tar.add(path, arcname=fn)

    print("Finished packaging")


def deploy():
    """Use the SageMaker Python SDK to deploy our API endpoint
    Specify PyTorch version and Python version when creating the PyTorchModel object.
    The SageMaker SDK uses these parameters to determine which PyTorch container to use.
    Also, The role created earlier is used here.
   """

    model = PyTorchModel(
        entry_point="inference.py",
        model_data=ZIPPED_MODEL_PATH,
        role=ROLE_NAME,
        framework_version="1.5",
        py_version="py3"
    )

    print("Deploying model...")

    model.deploy(
        initial_instance_count=1, instance_type="ml.t2.medium", endpoint_name=ENDPOINT_NAME
    )
    print(f"Model Finished deployment at: {datetime.now()}")
    print(f"Model Endpoint name: {ENDPOINT_NAME}")


def predict():
    """Get Predictions from the new endpoint. Send it text to get predictions from our BERT model.
    You can use the SageMaker SDK or the InvokeEndpoint method of the SageMaker Runtime API to invoke the endpoint.
    """
    sm = sagemaker.Session().sagemaker_runtime_client

    prompt = "Amazon Sagemaker is great!"

    response = sm.invoke_endpoint(
        EndpointName=ENDPOINT_NAME, Body=prompt.encode(encoding="UTF-8"), ContentType="text/csv"
    )

    res_body = response["Body"].read()
    print(f"response received\n{res_body}")


if __name__ == '__main__':
    main()
