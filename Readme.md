# Dagger

<br>

`dagger` allows you to deploy your data science project in the form of workflows and steps that can be executed on demand or on a pre-defined schedule. It also provides you with a UI to view/execute the runs and their statuses and logs. Behind the scenes, it uses [**`dagster`**](https://dagster.io/). The UI is also a part of the dagster deployment.

Using `dagger`, you don't need to know or interact with `dagster` or write any workflow scripts. All you need to do is create a YAML configuration file which provides info around the workflows and steps that you want to deploy in a simple way and that's it. You're done.

<br>

# Instructions

To run the workflow with sample `config.yml` given in the repo, execute the following:

- Clone the repo in your local machine.
- Install the requirements given in `requirements.txt` preferably in a virtual environment.
- Run the following command

    ```
    dagit -f main.py
    ```



<br>

# Things to keep in mind

<br>

### **Wrap the body of each step inside `step_fn`**

<br>

### **Names for parameters, files, folders should be consistent with `config.yml`**

<br>

User will need to pass a `config.yml` in order to provide information around the various workflows, steps and their dependencies. Here's the structure/attributes of `config.yml`.

- **project** - Name of the ML/ETL project. Should be the same as folder name. (`app` in this case)

- **workflows** - Different workflows/pipelines in the project such as *extraction*, *training*,  *preprocessing*, *inference*

- **steps** - Different steps in a workflow. For example, in a *training* workflow, steps could be *load_data*, *split_data*, *categorical_encoding*, *train_model*, *tune_model*

    - **input** - Every step needs an *input* attribute. If a step as no input, then its value will be *null*. If the input parameters of a step depends on return value from another step, the mapping needs to be provided in config. In the sample config, steps `a` and `b` don't have any dependency on other steps and therefore `input` attribute is `null` for both of them. However, the input parameter for step `d` depends on the return value of step `c` i.e. input parameter `x5` of `d` is sourced from the output paramter `x4` of `c`. A step can have non-parameteric dependency on other steps as well such as order-based dependency. In the sample config, the start of step `c` depends on the completion of step `b`. This type of dependence is provided using the attribute `type: order` whereas a paramteric dependecy is provided using the attribute `type: param`.

    - **output** - Every step needs an *output* attribute. If a step as no output, then its value will be *null*. Multiple outputs should be provided in a list format.


- **schedule** - This is not applicable in the basic deployment.
