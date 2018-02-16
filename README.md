# sugarcrm-python
Sugar CRM API wrapper written in python.

## Installing
```
pip install sugarcrm-python
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

## Requirements
- requests

## Tests
```
python tests/test_client.py
```

## TODO
- get_document_revision
- get_language_definition
- get_last_viewed
- get_modified_relationships
- get_module_fields_md5
- get_module_layout
- get_module_layout_md5
- get_note_attachment
- get_quotes_pdf
- get_relationships
- get_report_entries
- get_report_pdf
- get_server_info
- get_upcoming_activities
- get_user_id
- get_user_team_id
- job_queue_cycle
- job_queue_next
- job_queue_run
- logout
- oauth_access
- seamless_login
- search_by_module
- set_campaign_merge
- set_document_revision
- set_note_attachment
- set_relationship
- set_relationships
- snip_import_emails
- snip_update_contacts
