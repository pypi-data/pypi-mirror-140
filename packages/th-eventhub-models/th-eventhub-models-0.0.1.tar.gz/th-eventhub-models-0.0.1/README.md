# th-eventhub-models

This Repo Contains The Object Models For The Transform Health Event Hub Operations.

### To Publish Changes

1. Make changes to the models
2. Update the version number in `setup.py`
3. Install dist tools by using
   `python -m pip install --user --upgrade setuptools wheel`
4. Run `python setup.py sdist bdist_wheel`
5. Test locally by running `pip install -e .`
6. Install twine by `python -m pip install --user --upgrade twine`
7. After creating an account in testPy upload it in testPy by `python -m twine upload - repository testpypi dist/*`
8. Test if it works as expected by uninstalling the local version and installing the testPy version by <br> 
   `pip uninstall th-eventhub-models --yes-i-know-what-i-am-doing` <br> 
    and then <br>
   `pip install -i https://test.pypi.org/th-eventhub-models/th-eventhub-models==<version-number>`
9. Upload to PyPI Repository by running
   `twine upload dist/*`
10. Install in any repository of your choice by using `pip install th-eventhub-models` and import by using
    `from transformHealthEventHubModels.insertOne import DSEventHubInsertOneObject`