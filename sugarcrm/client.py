import json
import hashlib
import requests
from sugarcrm import exception
from sugarcrm.decorator import valid_parameters
from sugarcrm.enumerator import ErrorEnum


class Client(object):
    def __init__(self, url, username, password, app='sugarcrm-python', lang='en_US', verify=True, session=None):
        if not url.endswith('/service/v4_1/rest.php'):
            if not url.endswith('/'):
                url += '/'
            url += 'service/v4_1/rest.php'
        self.url = url + '?'
        self.username = username
        self.password = password
        self.app = app
        self.lang = lang
        self.verify = verify
        self.session = session
        try:
            response = self._login()
        except requests.exceptions.InvalidSchema:
            raise exception.InvalidURL("Please check your url '{0}' has a valid schema: 'http://', 'https://'".format(response.url))
        self.session_id = response['id']

    def _login(self):
        params = [
            {
                'user_name': self.username,
                'password': hashlib.md5(self.password.encode('utf8')).hexdigest()
            },
            self.app,
            [{
                'name': "language",
                'value': self.lang
            }]
        ]
        return self._post('login', params=params)

    def _post(self, endpoint, params=None):
        data = {
            'method': endpoint,
            'input_type': 'JSON',
            'response_type': 'JSON',
            'rest_data': json.dumps(params)
        }
        if self.session:
            client = self.session
        else:
            client = requests
        return self._parse(client.post(self.url + endpoint, data=data, verify=True))

    def _parse(self, response):
        if 'application/json' in response.headers['Content-Type']:
            r = response.json()
        else:
            try:
                r = response.json() # Una version anterior de SugarCRM no utiliza los headers adecuadamente.
            except Exception:
                r = response.text

        if 'name' in r and 'description' in r and 'number' in r:
            code = r['number']
            message = r['description']

            try:
                error_enum = ErrorEnum(code)
            except Exception:
                raise exception.UnknownError('Error: {}. Message {}'.format(code, message))
            if error_enum == ErrorEnum.InvalidLogin:
                raise exception.InvalidLogin(message)
        return r

    def get_available_modules(self, filter='default'):
        """Retrieves a list of available modules in the system.

        Args:
            filter: String to filter the modules with. Possible values are 'default', 'mobile', 'all'.

        Returns:
            A dict.

        """
        data = [self.session_id, filter]
        return self._post('get_available_modules', data)

    @valid_parameters
    def get_entries(self, module_name, ids, *, select_fields=[], link_name_to_fields_array={}, track_view=False):
        """Retrieves a list of beans based on specified record IDs.

        Args:
            module_name: The name of the module from which to retrieve records. Note: This is the modules key which may not be the same as the modules display name.
            ids: The list of record IDs to retrieve.
            select_fields: The list of fields to be returned in the results. Specifying an empty array will return all fields.
            link_name_to_fields_array: A list of link names and the fields to be returned for each link.
            track_view: Flag the record as a recently viewed item.

        Returns:
            A dict.

        """
        if isinstance(ids, str):
            ids = [ids]
        if link_name_to_fields_array:
            link_name_to_fields_array = [{'name': k.lower(), 'value': v} for k, v in link_name_to_fields_array.items()]
        data = [self.session_id, module_name, ids, select_fields, link_name_to_fields_array, track_view]
        return self._post('get_entries', data)

    @valid_parameters
    def get_entries_count(self, module_name, *, query="", deleted=False):
        """Retrieves a list of beans based on query specifications.

        Args:
            module_name: The name of the module from which to retrieve records. Note: This is the modules key which may not be the same as the modules display name.
            query: The SQL WHERE clause without the word "where".
            deleted: If deleted records should be included in the results.

        Returns:
            A dict.

        """
        data = [self.session_id, module_name, query, int(deleted)]
        return self._post('get_entries_count', data)

    @valid_parameters
    def get_entry(self, module_name, id, *, select_fields=[], link_name_to_fields_array={}, track_view=False):
        """Retrieves a single bean based on record ID.

        Args:
            module_name: The name of the module from which to retrieve records. Note: This is the modules key which may not be the same as the modules display name.
            id: The ID of the record to retrieve.
            select_fields: The list of fields to be returned in the results. Specifying an empty array will return all fields.
            link_name_to_fields_array: A list of link names and the fields to be returned for each link.
            track_view: Flag the record as a recently viewed item.

        Returns:
            A dict.

        """
        if link_name_to_fields_array:
            link_name_to_fields_array = [{'name': k.lower(), 'value': v} for k, v in link_name_to_fields_array.items()]
        data = [self.session_id, module_name, id, select_fields, link_name_to_fields_array, track_view]
        return self._post('get_entry', data)

    @valid_parameters
    def get_entry_list(self, module_name, *, query="", order_by="", offset=0, select_fields=[],
                       link_name_to_fields_array={}, max_results=0, deleted=False, favorites=False):
        """Retrieves a list of beans based on query specifications.

        Args:
            module_name: The name of the module from which to retrieve records. Note: This is the modules key which may not be the same as the modules display name.
            query: The SQL WHERE clause without the word "where". You should remember to specify the table name for the fields to avoid any ambiguous column errors.
            order_by: The SQL ORDER BY clause without the phrase "order by".
            offset: The record offset from which to start.
            select_fields: The list of fields to be returned in the results. Specifying an empty array will return all fields.
            link_name_to_fields_array: A list of link names and the fields to be returned for each link.
            max_results: The maximum number of results to return.
            deleted: If deleted records should be included in the results.
            favorites: 	If only records marked as favorites should be returned.

        Returns:
            A dict.

        """
        if link_name_to_fields_array:
            link_name_to_fields_array = [{'name': k.lower(), 'value': v} for k, v in link_name_to_fields_array.items()]
        data = [self.session_id, module_name, query, order_by, offset, select_fields, link_name_to_fields_array,
                max_results, int(deleted), favorites]
        return self._post('get_entry_list', data)

    @valid_parameters
    def get_module_fields(self, module_name, *, fields=[]):
        """Retrieves the list of field vardefs for a specific module.

        Args:
            module_name: The name of the module from which to retrieve records. Note: This is the modules key which may not be the same as the modules display name.
            fields: The list of fields to retrieve. An empty parameter will return all.

        Returns:
            A dict.

        """
        data = [self.session_id, module_name, fields]
        return self._post('get_module_fields', data)

    def set_entries(self, module_name, name_value_lists):
        """Create or update a list of records.

        Args:
            module_name: The name of the module from which to retrieve records. Note: This is the modules key which may not be the same as the modules display name.
            name_value_lists: The an array of name/value lists containing the record attributes.

        Returns:
            A dict.

        """
        _dict = [{'name': k.lower(), 'value': v} for k, v in name_value_lists.items()]
        data = [self.session_id, module_name, _dict]
        return self._post('set_entries', data)

    def set_entry(self, module_name, name_value_list):
        """Creates or updates a specific record.

        Args:
            module_name: The name of the module from which to retrieve records. Note: This is the modules key which may not be the same as the modules display name.
            name_value_list: The name/value list of the record attributes.

        Returns:
            A dict.

        """
        _dict = [{'name': k.lower(), 'value': v} for k, v in name_value_list.items()]
        data = [self.session_id, module_name, _dict]
        return self._post('set_entry', data)

    def get_document_revision(self):
        raise NotImplementedError

    def get_language_definition(self):
        raise NotImplementedError

    def get_last_viewed(self):
        raise NotImplementedError

    def get_modified_relationships(self):
        raise NotImplementedError

    def get_module_fields_md5(self):
        raise NotImplementedError

    def get_module_layout(self):
        raise NotImplementedError

    def get_module_layout_md5(self):
        raise NotImplementedError

    def get_note_attachment(self):
        raise NotImplementedError

    def get_quotes_pdf(self):
        raise NotImplementedError

    def get_relationships(self):
        raise NotImplementedError

    def get_report_entries(self):
        raise NotImplementedError

    def get_report_pdf(self):
        raise NotImplementedError

    def get_server_info(self):
        raise NotImplementedError

    def get_upcoming_activities(self):
        raise NotImplementedError

    def get_user_id(self):
        raise NotImplementedError

    def get_user_team_id(self):
        raise NotImplementedError

    def job_queue_cycle(self):
        raise NotImplementedError

    def job_queue_next(self):
        raise NotImplementedError

    def job_queue_run(self):
        raise NotImplementedError

    def logout(self):
        raise NotImplementedError

    def oauth_access(self):
        raise NotImplementedError

    def seamless_login(self):
        raise NotImplementedError

    def search_by_module(self):
        raise NotImplementedError

    def set_campaign_merge(self):
        raise NotImplementedError

    def set_document_revision(self):
        raise NotImplementedError

    def set_note_attachment(self):
        raise NotImplementedError

    def set_relationship(self):
        raise NotImplementedError

    def set_relationships(self):
        raise NotImplementedError

    def snip_import_emails(self):
        raise NotImplementedError

    def snip_update_contacts(self):
        raise NotImplementedError
