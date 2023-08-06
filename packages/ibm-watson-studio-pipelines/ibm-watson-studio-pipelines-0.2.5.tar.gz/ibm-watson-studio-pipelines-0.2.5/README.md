# IBM Watson Studio Pipelines Python Client

This package provides various utilities for working with IBM Watson
Studio Pipelines. Its primary usage is to enable users to store
artifact results of a notebook run.


## Usage

### Construction

`WSPipelines` client is constructed from IAM APIKEY, which can be provided
in a few ways:

* explicitly:

  ```python
  from ibm_watson_studio_pipelines import WSPipelines
  
  client = WSPipelines(apikey)
  # or
  client = WSPipelines.from_apikey(apikey)
  # or
  client = WSPipelines.from_token(token)
  ```

* implicitly:

  ```bash
  APIKEY=...
  export APIKEY
  ```
  or
  ```bash
  USER_ACCESS_TOKEN=...
  export USER_ACCESS_TOKEN
  ```

  ```python
  from ibm_watson_studio_pipelines import WSPipelines

  # use APIKEY
  client = WSPipelines.from_apikey()

  # use USER_ACCESS_TOKEN
  client = WSPipelines.from_token()

  # try APIKEY, if absent then USER_ACCESS_TOKEN:
  client = WSPipelines()
  # or
  client = WSPipelines.new_instance()
  ```

All of the above may also define `service_name` and `url`.

The exact procedure of deciding which authentication method to use:
1. If `from_apikey` or `from_token` is used, the method is forced.
2. If constructor is used but either `apikey` or `bearer_token` argument
  was provided, that method will be forced (if both are present,
  an overloading error will be raised). Note that providing a nameless
  argument is equivalent to providing `apikey`.
3. If constructor or `new_instance` is used, `APIKEY` env-var is used.
4. If constructor or `new_instance` is used, but `APIKEY` env-var is not
   present, `USER_ACCESS_TOKEN` env-var is used.
5. If none of the above matches, an error is returned.


### Usage in Python notebooks

Notebooks run in IBM Watson Studio Pipelines get inputs and expose
outputs as a node:

```
{
  "id": ...,
  "type": "execution_node",
  "op": "run_container",
  "app_data": {
    "pipeline_data": {
      "name": ...,
      "config": {
        "link": {
          "component_id_ref": "run-notebook"
        }
      },
      "inputs": [
        ...,
        {
          "name": "model_name",
          "group": "env_variables",
          "type": "String",
          "value_from": ...
        }
      ],
      "outputs": [
        {
          "name": "trained_model",
          "group": "output_variables",
          "type": {
            "CPDPath": {
              "path_type": "resource",
              "resource_type": "asset",
              "asset_type": "wml_model"
            }
          }
        }
      ]
    }
  },
  ...
}
```

Inside of the notebook, inputs are available as environmental
variables:

```python
model_name = os.environ['model_name']
```

Outputs are exposed using sdk method, `store_results`:

```python
client = WSPipelines.from_apikey(...)
client.store_results({
  "trained_model": ... // cpd path to the trained model
})
```


### Extracting credentials

On public cloud, this client provides a method for easy retrieval of WML
instance credentials and scope storage credentials:

```python
client.get_wml_credentials() # the scope passed in notebook
# or
client.get_wml_credentials("cpd:///projects/123456789")
```
```python
client.get_storage_credentials() # the scope passed in notebook
# or
client.get_storage_credentials("cpd:///projects/123456789")
```

Note how the result will vary depending on the authentication method
used to create the client.


### CPD-Path manipulation

CPD-Path parsing is manipulation is also supported:

```python
from ibm_watson_studio_pipelines import CpdScope, WSPipelines

client = WSPipelines.from_apikey()

scope = CpdScope.from_string("cpd:///projects/123456789")

assert scope.scope_type() == "projects"
assert scope.scope_id() == "123456789"

client.get_wml_credentials(scope)
```

Different kinds of CPD-Paths will have different properties, providing the same
interface across scopes, resource and file paths:

```python
from ibm_watson_studio_pipelines import CpdPath

scope_file_path = CpdPath.from_string("cpd:///projects/123456789/files/abc/def")
assert scope_file_path.scope_type() == "projects"
assert scope_file_path.scope_id() == "123456789"
assert scope_file_path.file_path() == "/abc/def"

connection_path = CpdPath.from_string("cpd:///projects/123456789/connections/3141592")
assert connection_path.scope_type() == "projects"
assert connection_path.scope_id() == "123456789"
assert connection_path.resource_type() == "connections"
assert connection_path.resource_id() == "3141592"

connection_file_path = CpdPath.from_string("cpd:///projects/123456789/connections/3141592/files/~/abc/def")
assert connection_file_path.scope_type() == "projects"
assert connection_file_path.scope_id() == "123456789"
assert connection_file_path.resource_type() == "connections"
assert connection_file_path.resource_id() == "3141592"
assert connection_file_path.bucket_name() == "~"
assert connection_file_path.file_path() == "/abc/def"
```

...additionally, for non-scope paths the scope can be extracted, if present:

```python
from ibm_watson_studio_pipelines import CpdPath

scope_path = CpdPath.from_string("cpd:///projects/123456789")
connection_path = CpdPath.from_string("cpd:///projects/123456789/connections/3141592")
assert connection_path.scope() == scope_path
```


## Contribution

See a separate [document on contribution](CONTRIBUTING.md).
