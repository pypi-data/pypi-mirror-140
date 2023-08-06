# Testwizard - Mobile

> Python language support for testing Mobile devices using testwizard

## Usage

* Import the [testwizard.test](https://pypi.org/project/testwizard.test/) and the testwizard.mobile packages.
* Get a session and use it to create a mobile testobject.
* Use this object to execute commands.
* You can use the session to add results that will be reported to the robot when the script finishes or set results that will be posted immediately.

## Sample

### Python (mobile.py)

```Python
from testwizard.test import TestWizard
from testwizard.test import ResultCodes
from testwizard.mobile import Mobile

with TestWizard() as TW:
    session = TW.session

    mobile = Mobile(session, "Mobile")

    print("InitDriver")
    result = mobile.initDriver()
    print(result.message)
    if not result.success:
        session.addFail(result.message)
        exit()

    # Add your commands here

    print("QuitDriver")
    result = mobile.quitDriver()
    print(result.message)
    if not result.success:
        session.addFail(result.message)

    if not (session.hasFails or session.hasErrors):
        session.setResult(ResultCodes.PASS, "Test was successful")
```

### sidecar file (mobile.json)

```json
{
    "resources": [
        { 
            "category": "MOBILE", 
            "name": "Mobile", 
            "id": "Mobile 1"
        }
    ]
}
```

## Compatibility

The version is compatible with testwizard version 3.5

## License

[Testwizard licensing](https://www.eurofins-digitaltesting.com/testwizard/)