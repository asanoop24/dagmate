# DAGmate

### Make your **dagster** deployment easier with **dagmate**.

<br>

`dagmate` allows you to deploy your data science project in the form of workflows and steps that can be executed on demand or on a pre-defined schedule. It also provides you with a UI to view/execute the runs and their statuses and logs. Behind the scenes, it uses [**`dagster`**](https://dagster.io/). The UI is also a part of the dagster deployment.

Using `dagmate`, you don't need to know or interact with `dagster` or write any workflow scripts. All you need to do is create a YAML configuration file which provides info around the workflows and steps that you want to deploy in a simple way and that's it. You're done.

<br>

# Instructions

To run the workflow with sample `config.yml` given in the repo, execute the following:

- Clone the repo in your local machine.
- Install the requirements given in `requirements.txt` preferably in a virtual environment.
- Run the following command to start `dagit` which will load the workflow. You can then access the dagit UI by accessing the following url - [localhost:3000](http://127.0.0.1:3000)

    ```
    dagit -f main.py
    ```
- [Optional] To use the scheduling feature, you'll need to run the `dagster-daemon` in parallel to `dagit`

    ```
    dagster-daemon run -f main.py
    ```


<br>

# Things to keep in mind

<br>

- Every step in the workflow needs to wrapped inside a function and the name of that function needs to be provided in the YAML file under the attribute `function`

<br>

- All the names used need to be consistent with the attribute values provided in the YAML file. This includes the names of function parameters, functions and the modules in which functions reside.

<br>

- You'll only need to make changes to the following files/folders:
    - `conf` - Place all your YAML files here. Each YAML file will be loaded as a separate project in the setup.
    - `src` - Place all your code files here. You can follow any folder structure and names you want, as long as you provide the same names in the YAML file.
    - `requirements.txt` - Add any packages/modules that you'd require

<br>

- To understand the YAML file's structure and attributes, refer to the sample file `config.yml` inside the `conf` directory. It contains comments explaining the different attributes and their expected values.

<br>
