
# Step Function Validator (AWS)

An issue we have is that we are quite human and we often make mistakes in the YAML "code". 
These could be syntactical errors (for example, an incorrect indent), but also semantical (for example, forgetting to add a required parameter to a step). 
We only find out about these errors in the last step of the CI/CD, when the step function fails to deploy to AWS. This makes troubleshooting very.. slow...

So we came up with this little tool. 

## Authors

- [@b0tting](https://github.com/b0tting)
- [@NileshDebix](https://github.com/NileshDebix)


## Installation

1. create virtual environment in python and activate this one in Terminal or CMD

```python
  python3 -m venv env
  
  Windows: 
    
    env\Script\activate.bat

  Mac/Linux:

    source env/bin/activate
```

2. install requirement.txt file

```python
    ####################### [ NOTE !!! ] ############################################################
    #    you NEED to see in your command line the env before your prompt
    #    so you know that you are in your virtual environment:
    #
    #    example: (env) nilesh@Mac%
    ################################################################################################

    if above is clear then:

    pip install -r requirement.txt # to install the required libraries

```

3. More steps comming soon.
