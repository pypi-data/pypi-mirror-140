# Resistant documents client

This library provides a Python client for a [Resistant.ai document forgery analysis service](https://resistant.ai/products/documents/).
For a detailed description of the API please see [API reference docs](https://pdf.resistant.ai/docs/v1.html).

## Prerequisites

During the customer onboarding process, you should be provided with the following:

- API_KEY : str

## Basic usage

Submit a document for analysis with default pipeline configuration.

```python
from bp_pdf_forgery_client.client import BpPdfForgeryClient

client = BpPdfForgeryClient(api_key="API_KEY")
with open("local_file.pdf", "rb") as fp:
    report = client.analyze(fp.read(), query_id="local_file.pdf")

print(report)
``` 

## Customized usage

Submit a document for analysis with customized process parameters or select a different type of analysis. 

### Step 1: Create a client with your credentials

```python
client = BpPdfForgeryClient(api_key="API_KEY")
```

### Step 2: Create submission with pipeline setup

```python
with open("local_file.pdf", "rb") as fp:
    my_submission_id = client.submit(fp.read(), query_id="local_file.pdf", pipeline_configuration="CONTENT_AFTER_FRAUD_AFTER_QUALITY")
```

Possible pipeline configurations are listed in [REST API docs](https://pdf.resistant.ai/docs/v1.html#operation/createSubmission)

### Step 3: Retrieve analysis result
You can retrieve only those types of analysis which were requested in the previous step as `pipeline_configuration` option.

```python
result_fraud = client.results(submission_id=my_submission_id)
result_content = client.content(submission_id=my_submission_id)
result_quality = client.quality(submission_id=my_submission_id)

print(result_content)
print(result_fraud)
print(result_quality)
```
These methods also accept `max_num_retries`, which represents how many times the client will poll the server before failing (because the communication is asynchronous). It might be customized but has a default
value. Other parameters correspond to the ones in the REST API docs.

### Step 4: Pre-signed url [Optional]
This method lets you generate a link for anybody else to access the analysis result.

```python
data = client.presign(submission_id=my_submission_id, expiration=600)
presigned_url = data["presigned_url"]
```
Parameters:
- `expiration`- specifies a validity duration (in seconds) of the generated link, min: `1`,  max: `604800` seconds (one week).
