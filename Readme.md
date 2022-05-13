# Dagger

<br>

This repo allows the user to run their ETL, ML workflows in `dagster` without actually needing to configure or even touch `dagster`. This code/framework will set up `dagster` in the background automatically. All user needs to do is provide a `config.yml` file in the specified format and maintain the file/folder structure accordingly. Details provided below.

<br>

# Prerequisites

- `docker`
- `docker-compose`

<br>

# Instructions

To run the sample workflow given in the repo, execute the following:

- `cd` into the root directory where you have the `docker-compose.yml`.
    ```
    cd PATH/TO/ROOT
    ```
- build the docker image using `docker-compose`
    ```
    docker-compose build
    ```
- start the containers once the images are downloaded and built
    ```
    docker-compose up -d
    ```
- check to see if the docker containers are running
    ```
    docker ps -a
    ```
    You should see the following 4 containers running:
```
CONTAINER ID   IMAGE                  COMMAND                  CREATED       STATUS       PORTS                    NAMES
ddcad72ae0ca   img_dagster_instance   "dagit -h 0.0.0.0 -p…"   2 hours ago   Up 2 hours   0.0.0.0:3000->3000/tcp   ctr_dagster_dagit
23e405c38f43   img_dagster_instance   "dagster-daemon run"     2 hours ago   Up 2 hours                            ctr_dagster_daemon
71d3214ac898   postgres:11            "docker-entrypoint.s…"   2 hours ago   Up 2 hours   5432/tcp                 ctr_postgresql
6f32bcf735bd   img_dagster_grpc       "dagster api grpc -h…"   2 hours ago   Up 2 hours   4000/tcp                 ctr_dagster_grpc
```


<br>

# Things to keep in mind

<br>

### **Wrap the body of each step inside `step_fn`**

<br>

Every `step` in the `workflow` must be a separate module/script with its body wrapped inside a function named `step_fn`. For example, for a step to treat missing values in the **preproecssing** workflow, the user will need to have a folder `preprocessing` in the `app` directory and inside that folder, a script with name such as `treat_missing_values.py` should be placed with the contents wrapped inside `step_fn` as given below:

<br>

```
def step_fn(df: pd.DataFrame) -> pd.DataFrame:
    ....
    ...
    function body here
    ..
    ...

    return df
```

<br>

### **Names for parameters, files, folders should be consistent with `config.yml`**

<br>

User will need to pass a `config.yml` in order to provide information around the various workflows, steps and their dependencies. Here's the structure/attributes of `config.yml`.

- **`project`** - Name of the ML/ETL project. Should be the same as folder name. (`app` in this case)

- **`workflows`** - Different workflows/pipelines in the project such as *`extraction`*, *`training`*,  *`preprocessing`*, *`inference`*

- **`steps`** - Different steps in a workflow. For example, in a *`training`* workflow, steps could be *`load_data`*, *`split_data`*, *`categorical_encoding`*, *`train_model`*, *`tune_model`*

    - **`input`** - Every step needs an *`input`* attribute. If a step as no input, then its value will be *`null`*. If the input parameters of a step depends on return value from another step, the mapping needs to be provided in config. In the sample config, steps `a` and `b` don't have any dependency on other steps and therefore `input` attribute is `null` for both of them. However, the input parameter for step `d` depends on the return value of step `c` i.e. input parameter `x5` of `d` is sourced from the output paramter `x4` of `c`. A step can have non-parameteric dependency on other steps as well such as order-based dependency. In the sample config, the start of step `c` depends on the completion of step `b`. This type of dependence is provided using the attribute `type: start` whereas a paramteric dependecy is provided using the attribute `type: var`.

    - **`output`** - Every step needs an *`output`* attribute. If a step as no output, then its value will be *`null`*. Multiple outputs should be provided in a list format.


- **`schedule`** - If there is a schedule at which the workflow needs to be executed, that needs to provided here. Note that this accepts the schedule in a cronjob format as given in the sample config.yml
