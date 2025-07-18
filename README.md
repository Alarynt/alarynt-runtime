# Alarynt Secure Python Runtime

This is a secure, sandboxed Python Lambda runtime for Alarynt, a multi-tenant rule evaluation platform.

## Features

- **Secure Sandboxing**: Executes user-defined Python code in a restricted environment using `RestrictedPython`.
- **Resource Limiting**: Enforces strict timeouts on code execution to prevent abuse.
- **Structured I/O**: Accepts JSON payloads and returns structured JSON output.
- **Detailed Logging**: Logs execution traces, including timing and outcomes.

## Getting Started

### Prerequisites

- Python 3.9+
- An AWS account to deploy the Lambda function.

### Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd alarynt-runtime
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Local Testing

To test the Lambda function locally, you can use the AWS SAM CLI or invoke the `lambda_handler` directly in a Python script.

**Example `event.json`:**

```json
{
  "rule_logic": "result = event['user']['age'] > 30 and event['user']['plan'] == 'premium'",
  "payload": {
    "user": {
      "name": "John Doe",
      "age": 35,
      "plan": "premium"
    },
    "transaction": {
      "amount": 100,
      "currency": "USD"
    }
  }
}
```

**Running the handler:**

```python
import json
from app import lambda_handler

with open('event.json', 'r') as f:
    event = json.load(f)

# The 'context' object is often None in local testing
response = lambda_handler(event, None)
print(response)
```

## How It Works

The core of the runtime is the `app.py` file, which contains the `lambda_handler`.

1.  **Event Input**: The handler receives a JSON event from API Gateway or a direct invoke. This event must contain two keys:
    - `rule_logic`: A string containing the Python code to execute.
    - `payload`: A JSON object that will be available to the user's code inside the `event` variable.

2.  **Sandboxing**: The `rule_logic` is executed using `RestrictedPython`. This library prevents access to unsafe modules, built-ins, and attributes. Only a limited, safe subset of the Python language is available.

3.  **Execution and Timeouts**: The code is run in a separate thread with a hard-coded timeout (`EXECUTION_TIMEOUT`). If the code takes too long, the execution is aborted, and a timeout error is returned.

4.  **Output**: The Lambda returns a JSON object with the following structure:
    - `matched`: A boolean indicating whether the `result` of the script was truthy.
    - `result`: The value assigned to the `result` variable in the user's code.
    - `trace`: An object containing execution metadata, like `execution_time_ms`.

## User-Defined Code Guide

When writing `rule_logic`, you must adhere to the following:

-   The code **must** be a valid Python script.
-   The script **must** assign its final output to a variable named `result`.
-   You have access to the `event` variable, which contains the `payload` from the input.
-   You are restricted to safe Python operations. You cannot import modules, open files, or access the network. #   a l a r y n t - r u n t i m e  
 