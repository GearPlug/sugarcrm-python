# sugarcrm-python
Sugar CRM API wrapper written in python.

## Installing
```
pip install sugarcrm-python
```

## Usage
```
from sugarcrm.client import Client

client = Client('SERVER_URL', 'USERNAME', 'PASSWORD', version='8.3')
```

Get leads
```
client.get_leads()
```

Create leads
```
client.create_lead()
```

## Requirements
- requests

## Tests
```
python tests/test_client.py
```

## TODO

## Contributing
We are always grateful for any kind of contribution including but not limited to bug reports, code enhancements, bug fixes, and even functionality suggestions.

#### You can report any bug you find or suggest new functionality with a new [issue](https://github.com/GearPlug/sugarcrm-python/issues).

#### If you want to add yourself some functionality to the wrapper:
1. Fork it ( https://github.com/GearPlug/sugarcrm-python )
2. Create your feature branch (git checkout -b my-new-feature)
3. Commit your changes (git commit -am 'Adds my new feature')
4. Push to the branch (git push origin my-new-feature)
5. Create a new Pull Request
