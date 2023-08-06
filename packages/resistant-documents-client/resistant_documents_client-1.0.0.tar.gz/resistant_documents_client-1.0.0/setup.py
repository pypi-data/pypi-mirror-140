# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['resistant_documents_client', 'resistant_documents_client.tests']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22.0,<3.0.0']

setup_kwargs = {
    'name': 'resistant-documents-client',
    'version': '1.0.0',
    'description': 'Resistant.ai document forjerry python client for convenient integration with REST API service.',
    'long_description': '# Resistant documents client\n\nThis library provides a Python client for a [Resistant.ai document forgery analysis service](https://resistant.ai/products/documents/).\nFor a detailed description of the API please see [API reference docs](https://pdf.resistant.ai/docs/v1.html).\n\n## Prerequisites\n\nDuring the customer onboarding process, you should be provided with the following:\n\n- API_KEY : str\n\n## Basic usage\n\nSubmit a document for analysis with default pipeline configuration.\n\n```python\nfrom bp_pdf_forgery_client.client import BpPdfForgeryClient\n\nclient = BpPdfForgeryClient(api_key="API_KEY")\nwith open("local_file.pdf", "rb") as fp:\n    report = client.analyze(fp.read(), query_id="local_file.pdf")\n\nprint(report)\n``` \n\n## Customized usage\n\nSubmit a document for analysis with customized process parameters or select a different type of analysis. \n\n### Step 1: Create a client with your credentials\n\n```python\nclient = BpPdfForgeryClient(api_key="API_KEY")\n```\n\n### Step 2: Create submission with pipeline setup\n\n```python\nwith open("local_file.pdf", "rb") as fp:\n    my_submission_id = client.submit(fp.read(), query_id="local_file.pdf", pipeline_configuration="CONTENT_AFTER_FRAUD_AFTER_QUALITY")\n```\n\nPossible pipeline configurations are listed in [REST API docs](https://pdf.resistant.ai/docs/v1.html#operation/createSubmission)\n\n### Step 3: Retrieve analysis result\nYou can retrieve only those types of analysis which were requested in the previous step as `pipeline_configuration` option.\n\n```python\nresult_fraud = client.results(submission_id=my_submission_id)\nresult_content = client.content(submission_id=my_submission_id)\nresult_quality = client.quality(submission_id=my_submission_id)\n\nprint(result_content)\nprint(result_fraud)\nprint(result_quality)\n```\nThese methods also accept `max_num_retries`, which represents how many times the client will poll the server before failing (because the communication is asynchronous). It might be customized but has a default\nvalue. Other parameters correspond to the ones in the REST API docs.\n\n### Step 4: Pre-signed url [Optional]\nThis method lets you generate a link for anybody else to access the analysis result.\n\n```python\ndata = client.presign(submission_id=my_submission_id, expiration=600)\npresigned_url = data["presigned_url"]\n```\nParameters:\n- `expiration`- specifies a validity duration (in seconds) of the generated link, min: `1`,  max: `604800` seconds (one week).\n',
    'author': 'Resistant.ai',
    'author_email': 'sales@resistant.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
