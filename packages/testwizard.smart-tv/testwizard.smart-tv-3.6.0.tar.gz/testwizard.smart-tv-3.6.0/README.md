# Testwizard - Smart-Tv

> Python language support for testing Smart-Tv devices using testwizard

## Usage

* Import the [testwizard.test](https://pypi.org/project/testwizard.core/) and the testwizard.smart_tv packages
* Get a session and use it to create a Smart TV testobject.
* Use this object to execute commands.
* You can use the session to add results that will be reported to the robot when the script finishes or set results that will be posted immediately.

## Sample script

### Python (smart-tv.py)

```python
from testwizard.test import TestWizard
from testwizard.test import ResultCodes
from testwizard.smart_tv import SmartTv

with TestWizard() as TW:
    session = TW.session

    smartTv = SmartTv(session, "SmartTv")

    print("sendRCKey")
    result = smartTv.sendRCKey("menu")
    print(result.message)
    if not result.success:
        session.addFail(result.message)

    if not (session.hasFails or session.hasErrors):
        session.setResult(ResultCodes.PASS, "Test was successful")
```

### sidecar file (smart-tv.json)

```json
{
    "resources": [
        { 
            "category": "SMART_TV", 
            "name": "SmartTv", 
            "id": "TV Model 1"
        }
    ]
}
```

## Compatibility

The version is compatible with testwizard version 3.5

## License

[Testwizard licensing](https://www.eurofins-digitaltesting.com/testwizard/)