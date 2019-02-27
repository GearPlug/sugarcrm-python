import json
import hashlib
import requests
from sugarcrm import exception
from sugarcrm.decorator import valid_parameters
from sugarcrm.enumerator import ErrorEnum


class Client(object):
    def __init__(self, url, username, password, app='sugarcrm-python', lang='en_US', verify=True, requests_session=None, requests_hooks=None):
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
        self.requests_session = requests_session
        if requests_hooks and not isinstance(requests_hooks, dict):
            raise Exception('requests_hooks must be a dict. e.g. {"response": func}. http://docs.python-requests.org/en/master/user/advanced/#event-hooks')
        self.requests_hooks = requests_hooks
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

    def _post(self, endpoint, params=None, **kwargs):
        data = {
            'method': endpoint,
            'input_type': 'JSON',
            'response_type': 'JSON',
            'rest_data': json.dumps(params)
        }
        if self.requests_session:
            client = self.requests_session
        else:
            client = requests
        if self.requests_hooks:
            kwargs.update({'hooks': self.requests_hooks})
        return self._parse(client.post(self.url + endpoint, data=data, verify=True, **kwargs))

    def _parse(self, response):
        if 'application/json' in response.headers['Content-Type']:
            r = response.json()
        else:
            try:
                r = response.json()  # Una version anterior de SugarCRM no utiliza los headers adecuadamente.
            except Exception:
                return response.text

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

    def get_relationships(
        self,
        module_name,
        module_id,
        link_field_name,
        related_module_query,
        related_fields,
        related_module_link_name_to_fields_array,
        deleted=False,
        order_by="",
        offset=0,
        limit=False,
    ):
        """Retrieve a collection of beans that are related to the specified
        bean and optionally return relationship data for those related beans.

        Args:
            module_name: The name of the module that the primary record is
                from. This name should be the name the module was developed
                under (changing a tab name is studio does not affect the name
                that should be passed into this method)..
            module_id: The ID of the bean in the specified module
            link_field_name: The name of the link field to return records from.
                This name should be the name the relationship.
            related_module_query: A portion of the where clause of the SQL
                statement to find the related items.  The SQL query will
                already be filtered to only include the beans that are related
                to the specified bean.
            related_fields - Array of related bean fields to be returned.
            related_module_link_name_to_fields_array - For every related bean
                returrned, specify link fields name to fields info for that
                bean to be returned. For ex.'link_name_to_fields_array' =>
                array(array('name' =>  'email_addresses', 'value' =>
                array('id', 'email_address', 'opt_out', 'primary_address'))).
            deleted: false if deleted records should not be include, true if
                deleted records should be included.
            order_by: field to order the result sets by
            offset: where to start in the return
            limit: number of results to return (defaults to all)

        Returns:
            A dict.
        """

        data = [
            self.session_id,
            module_name,
            module_id,
            link_field_name,
            related_module_query,
            related_fields,
            related_module_link_name_to_fields_array,
            int(deleted),
            order_by,
            offset,
            limit,
        ]
        return self._post("get_relationships", data)

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

    @valid_parameters
    def search_by_module(
        self,
        search_string,
        modules,
        offset=0,
        max_results=0,
        assigned_user_id="",
        select_fields=[],
        unified_search_only=False,
        favorites=False,
    ):
        """Given a list of modules to search and a search string, return the
        id, module_name, along with the fields. Supports Accounts, Bugs, Cases,
        Contacts, Leads, Opportunities, Project, ProjectTask, Quotes.
     
        Args:
            search_string: string to search
            modules: array of modules to query
            offset: a specified offset in the query
            max_results: max number of records to return
            assigned_user_id: a user id to filter all records by, leave empty
                to exclude the filter
            select_fields: An array of fields to return. If empty the default
                return fields will be from the active list view defs.
            unified_search_only: A boolean indicating if we should only search
                against those modules participating in the unified search.
            favorites: A boolean indicating if we should only search against
                records marked as favorites.

        Returns:
            A dict.
        """
        data = [
            self.session_id,
            search_string,
            modules,
            offset,
            max_results,
            assigned_user_id,
            select_fields,
            unified_search_only,
            favorites,
        ]
        return self._post("search_by_module", data)

    def set_campaign_merge(self):
        raise NotImplementedError

    def set_document_revision(self):
        raise NotImplementedError

    def set_note_attachment(
        self,
        noteid,
        filename,
        filecontent,
        related_module_id=None,
        related_module_name=None,
    ):
        """Add or replace the attachment on a Note. Optionally you can set the
        relationship of this note to Accounts/Contacts and so on by setting
        related_module_id, related_module_name

        Args:
            noteid: The ID of the Note containing the attachment
            filename: The file name of the attachment
            filecontent: The binary contents of the file.
            related_module_id: module id to which this note to related to
            related_module_name: module name to which this note to related to

        Returns:
            A dict.
        """
        data = [
            self.session_id,
            {
                "id": noteid,
                "filename": filename,
                "file": filecontent,
                "related_module_id": related_module_id,
                "related_module_name": related_module_name,
            },
        ]

        return self._post("set_note_attachment", data)


    @valid_parameters
    def set_relationship(
        self,
        module_name,
        module_id,
        link_field_name,
        related_ids,
        name_value_list=[],
        delete=0,
    ):
        """Set a single relationship between two beans. The items are related
        by module name and id.

        Args:
            module_name: name of the module that the primary record is from.
                This name should be the name the module was developed under
                (changing a tab name is studio does not affect the name that
                should be passed into this method)..
            module_id: The ID of the bean in the specified module_name
            link_field_name: name of the link field which relates to the other
                module for which the relationship needs to be generated.
            related_ids: array of related record ids for which relationships
                needs to be generated
            name_value_list: The keys of the array are the SugarBean
                attributes, the values of the array are the values the
                attributes should have.
            delete: Optional, if the value 0 or nothing is passed then it will
                add the relationship for related_ids and if 1 is passed, it
                will delete this relationship for related_ids

        Returns:
            A dict.
        """
        data = [
            self.session_id,
            module_name,
            module_id,
            link_field_name,
            related_ids,
            name_value_list,
            delete,
        ]
        return self._post("set_relationship", data)

    def set_relationships(self):
        raise NotImplementedError

    def snip_import_emails(self):
        raise NotImplementedError

    def snip_update_contacts(self):
        raise NotImplementedError
