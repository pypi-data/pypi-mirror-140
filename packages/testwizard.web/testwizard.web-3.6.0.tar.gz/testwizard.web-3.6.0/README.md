# Testwizard - Web

> Python language support for testing websites, web-apps or webservices using testwizard

## Usage

* Import the [testwizard.test](https://pypi.org/project/testwizard.test/) and the testwizard.web packages.
* Get a session and use it to create a web testobject.
* Use this object to execute commands.
* You can use the session to add results that will be reported to the robot when the script finishes or set results that will be posted immediately.

## Sample script

### Python (website.js)

```Python
from testwizard.test import TestWizard
from testwizard.test import ResultCodes
from testwizard.web import Web

with TestWizard() as TW:
    session = TW.session

    website = Web(session, "TestwizardWebsite")

    print("startWebDriver")
    result = website.startWebDriver()
    print(result.message)
    if not result.success:
        session.addFail(result.message)
        exit()

    # Add your commands here

    print("quitDriver")
    result = website.quitDriver()
    print(result.message)
    if not result.success:
        session.addFail(result.message)

    if not (session.hasFails or session.hasErrors):
        session.setResult(ResultCodes.PASS, "Test was successful")
```

### sidecar file (website.json)

```json
{
    "resources": [
        { 
            "category": "WEB", 
            "name": "TestwizardWebsite", 
            "id": "Testwizard web site"
        }
    ]
}
```

## Compatibility

The version is compatible with testwizard version 3.5

## License

[Testwizard licensing](https://www.eurofins-digitaltesting.com/testwizard/)
