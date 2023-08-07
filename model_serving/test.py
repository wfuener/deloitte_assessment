"""This simple script can be used to re invoke the endpoint"""
import sagemaker
import boto3
import json

boto3.setup_default_session(profile_name='personal', region_name='us-east-2')
sm = sagemaker.Session().sagemaker_runtime_client
endpoint_name = "bert-base-2023-08-06-Aug-08-1691374313"

prompt = "Let's test our model deployment"
print("invoking...")

# # This setup_default_session was needed when running locally but shouldn't be needed if running in the cloud
# test the content type as text
try:
    response = sm.invoke_endpoint(
        EndpointName=endpoint_name, Body=prompt.encode(encoding="UTF-8"), ContentType="text/csv",
    )
except Exception as ex:
    print(ex)
else:
    r = response["Body"].read()
    print("response recived")
    print(r)


# test content type as json
try:
    response = sm.invoke_endpoint(
        EndpointName=endpoint_name, Body=json.dumps(prompt), ContentType="application/json",
        Accept='application/json; verbose=True'
    )
except Exception as ex:
    print(ex)
else:
    r = response["Body"].read()
    print("response recived")
    print(r)

