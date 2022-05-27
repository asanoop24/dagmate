# DAGmate

### Make your **dagster** deployment easier with **dagmate**.

<br>

**dagmate** allows you to deploy your data science project in the form of workflows and steps that can be executed on demand or on a pre-defined schedule. It also provides you with a UI to view/execute the runs and their statuses and logs. Behind the scenes, it uses [**dagster**](https://dagster.io/). The UI is also a part of the dagster deployment.

Using dagmate, you don't need to know or interact with dagster or write any workflow scripts. All you need to do is create a YAML configuration file which provides info around the workflows and steps that you want to deploy in a simple way and that's it. You're done.

<br>

# Instructions

To run the workflow with sample *config.yml* given in the repo, execute the following:

1. Install dagmate

    ```
    pip install dagmate
    ```

2. Write YAML config file for your project. This is a sample workflow containing 2 tasks *a* and *b* with parameter-based dependency.

    ```
    project: SampleProject
    workflows:
    - name: SampleWorkflow
      steps:
        - name: a
          module: ./src/training/a.py
          function: fn_a
          dependencies: null
          return:
            - x1
            - x2
        - name: b
          module: ./src/training/b.py
          function: step_fn
          dependencies:
            - type: param
              name: x1
              source:
                step: a
                param: x1
            - type: param
              name: x2
              source:
                step: a
                param: x2
          return:
          - x3
    ```

    For a more elaborate and commented YAML config, refer to the *config.yml* inside the *conf* folder.

3. Activate dagmate from your main script

    ```
    # main.py

    from dagmate.core import Dagmate
    config_file = "./conf/config.yml"
    
    mate = Dagmate(config_file)
    mate.activate()
    ```

4. Run the following command to start **dagit** which will load the workflow. You can then access the dagit UI by accessing the following url - [localhost:3000](http://127.0.0.1:3000)

    ```
    dagit -f main.py
    ```
5. [Optional] To use the scheduling feature, you'll need to run the **dagster-daemon** in parallel to dagit

    ```
    dagster-daemon run -f main.py
    ```

