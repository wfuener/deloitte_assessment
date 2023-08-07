##  Consulting Soft Skills - Section 1
Section 1's response is the `deloitte answer.doc` file. It was created in libreoffice and not
MS word so please let me know if there are any issues with the formatting if opening in MS Word.  

---
## Database & Python ETL - Section 2
Section 2's response is in the etl directory

### Requirements
Docker/Docker-compose was added for an easy database setup. You can install it following the 
directions here if you don't have it. https://docs.docker.com/compose/install/ . Although
if you don't want to install it you could change the environment variables in the .env
file to point to another database and just run the script inside flyway to create the neccessary DDL.

Python 3.X (was developed on 3.10)

A virtual environment is always a good idea when running python locally. 

`python3 -m venv venv; source venv/bin/activate'`

Install requirements in requirements.txt.
`pip install -r requirements.txt`

### Running
Inside the etl directory, Run/Build the database via docker-compose; `docker-compose build; docker-compose up`
Then invoke the main script when the database is ready `python main.py`

-----

## ML API - Section 3
Section 3's response is in the model_serving directory.

Deploy a pretrained model to AWS Sagemaker using python, boto3, huggingface, and pytorch.

### Requirements
Python 3.X (was developed on 3.10)

A virtual environment is always a good idea when running python locally. 

`python3 -m venv venv; source venv/bin/activate`

Install requirements in requirements.txt. The transformers library and pytorch may have dependencies 
not installed on your machine so if you have issues you will need to consult their documentation
`pip install -r requirements.txt`

https://pytorch.org/get-started/locally/
https://huggingface.co/docs/transformers/installation

An active aws account and the aws command line is also need to deploy this script.

### Running
Just run the deploy script inside the model_serving directory `python deploy.py`

There is a test run at the bottom of the deploy script to invoke the endpoint
but you can execute the `test.py` script too. 
