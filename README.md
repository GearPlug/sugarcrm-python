# sugarcrm-python
Sugar CRM API wrapper written in python.

## Installing
```
pip install git+git://github.com/GearPlug/sugarcrm-python.git
```

## Usage
```
from sugarcrm.client import Client

client = Client('SERVER_URL', 'USERNAME', 'PASSWORD')
```

Get available modules
```
client.get_available_modules('MODULE_NAME')
```

Get entries
```
client.get_entries('MODULE_NAME', ['ENTRY_ID'])
```

Get entries count
```
client.get_entries_count('MODULE_NAME')
```

Get entry
```
client.get_entries_count('MODULE_NAME', 'ENTRY_ID')
```

Get entry list
```
client.get_entry_list('MODULE_NAME')
```

Get module fields
```
client.get_module_fields('MODULE_NAME')
```

