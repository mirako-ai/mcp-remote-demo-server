# Mirako MCP Server CloudRun Sample

## Setup
Below are required setup in CloudRun, other configurations depends on your use case
1. In CloudRun, click `Deploy Container` -> `Service`
2. Choose `Function`
3. Runtime: `Python 3.x`
4. Trigger: `Allow unauthenticated invocations`
5. `Containers`
    1. `Settings`
        1. `Container command`: `sh`
        2. `Container arguments`: `run.sh`
    2. `Variables and Secrets`
        1. `AUTH_TOKEN`
            * your Auth Token

