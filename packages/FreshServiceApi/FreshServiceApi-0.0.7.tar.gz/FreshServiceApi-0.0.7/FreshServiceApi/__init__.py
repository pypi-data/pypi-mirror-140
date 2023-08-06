import base64
import requests
from json.decoder import JSONDecodeError
import csv


class FreshServiceApi:
    def __init__(self, apikey, base_uri):
        self.apikey = apikey
        self.base_uri = base_uri

    def encode_apikey_for_fs(self):
        """Returns base64 encoded string w/ dummy password per FS documentation"""
        authorization = "%s:x" % self.apikey
        apikey_ascii = authorization.encode('ascii')
        base64_encoded = base64.b64encode(apikey_ascii)
        return base64_encoded.decode("ascii")

    def call_api(self, method, resource, version=1, params=None, payload=None, return_response_headers=False):
        request_headers = {"Authorization": "Basic %s" % self.encode_apikey_for_fs(), "content-type": "application/json"}
        param_string = ''
        if params:
            param_string += '?'
            for key, value in params.items():
                param_string += f"{key}={value}&"

        endpoint_url = f"{self.base_uri}{resource}{param_string}"

        response = None
        if method == 'get':
            response = requests.get(endpoint_url, headers=request_headers)
        elif method == 'post':
            response = requests.post(endpoint_url, headers=request_headers, json=payload)
        elif method == 'put':
            response = requests.put(endpoint_url, headers=request_headers, json=payload)
        elif method == 'delete':
            response = requests.delete(endpoint_url, headers=request_headers, json=payload)

        if return_response_headers:
            return {'headers': response.headers, 'body': response.json()}

        try:
            return response.json()
        except JSONDecodeError:
            return response

    # Agents #
    def get_all_agents(self):
        """Returns the first 100 agent first & last names and their ID in an array of dicts"""
        agents_call = self.call_api('get', 'agents', params={'per_page': 100})
        agents = []
        for agent in agents_call['agents']:
            agents.append({
                'first_name' : agent['first_name'],
                'last_name': agent['last_name'],
                'agent_id': agent['id']
            })

        return agents

    def get_all_group_ids(self):
        """Returns all agent groups as list of dicts"""
        groups_call = self.call_api('get', 'groups')
        groups = []
        for group in groups_call['groups']:
            groups.append({
                'group_name': group['name'],
                'group_id': group['id']
            })

        return groups

    # Requesters #
    def get_single_requester_by_email(self, email_address):
        requester = self.call_api('get', 'requesters', params={'email': email_address})
        if not requester['requesters']:
            requester = [{'error': 'Requestor not found'}]
            return requester
        else:
            return requester['requesters']

    # Assets #
    def get_all_products(self):
        """returns all products in list of dicts"""
        products = self.call_api('get', 'products')
        return products['products']

    def get_product_by_id(self, product_id):
        try:
            product = self.call_api('get', f"products/{product_id}")
        except JSONDecodeError:
            return 'Product not found'
        else:
            return product['product']

    # Software #
    def get_all_software(self):
        """Return all software in array of dicts"""
        application_call = self.call_api('get', 'applications')
        applications = []
        for application in application_call['applications']:
            applications.append({
                'application_name': application['name'],
                'application_id': application['id']
            })

        return applications

    def post_bulk_users_to_software(self, csv_filename, index_of_email_column, fs_software_id, headers=True):
        """Uses csv column w/ emails to post to FS software group. Assumes csv has column headers. Wont work w/agents"""
        with open(csv_filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            if headers:
                next(csv_reader)

            current_row = 0
            for line in csv_reader:
                requester_email = line[index_of_email_column]
                try:
                    get_user = self.get_single_requester_by_email(requester_email)
                    user_id = get_user[0]['id']
                    payload = {'application_users': [{'user_id': user_id}]}
                    call = self.call_api('post', f"applications/{fs_software_id}/users", payload=payload)

                    print(f"Row: {current_row} - ADDED: {requester_email} successfully.")
                    current_row += 1

                except KeyError:
                    row_status = f"Row: {current_row} - FAILED: {requester_email}"
                    error_report = open('api_failed_uploads.txt', "a")
                    error_report.write(row_status + "\n")
                    print(row_status)
                    current_row += 1

            print('Complete.')

    # Tickets #
    def create_ticket(self, requester_email, status=2, priority=1, source=1, agent_id=None, group_id=None, subject=None,
                      description=None):
        """Creates an Low priority open ticket with a source of email, by default. Returns response"""
        payload = {
             'email': requester_email,
             'description': description,
             'subject': subject,
             'responder_id': agent_id,
             'status': status,
             'priority': priority,
             'source': source,
             'group_id': group_id
        }
        return self.call_api('post', 'tickets', payload=payload)

    def get_single_ticket_by_id(self, ticket_id):
        """Returns a ticket with specified id"""
        try:
            ticket = self.call_api('get', f"tickets/{ticket_id}")
        except JSONDecodeError:
            return {'error': 'ticket not found'}
        except SyntaxError:
            return {'error': "syntax error"}
        else:
            return ticket['ticket']

    def get_ticket_requested_items(self, ticket_id):
        """Return the requested items of a service request"""
        try:
            requested_items = self.call_api('get', f"tickets/{ticket_id}/requested_items")
        except JSONDecodeError:
            return {'error': 'ticket not found'}
        except SyntaxError:
            return {'error': "syntax error"}
        else:
            return requested_items['requested_items']

    def get_service_item(self, service_id):
        """Gets a service item by display id"""
        try:
            service_item = self.call_api('get', f'service_catalog/items/{service_id}')
        except JSONDecodeError:
            return {'error': 'ticket not found'}
        except SyntaxError:
            return {'error': "syntax error"}
        else:
            return service_item

    def post_bulk_offboard_service_requests(self, csv_filename, index_of_email_column, requester_email, headers=True):
        """Uses csv column w/ emails to post offboard SRs. Column headers by default Wont work w/agents"""
        # Assumes most custom fields are 'No'
        with open(csv_filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            if headers:
                next(csv_reader)
            ticket_numbers = []
            for line in csv_reader:
                user = self.get_single_requester_by_email(line[index_of_email_column])
                user_id = user[0]['id']
                payload = {
                    'email': requester_email,
                    'custom_fields': {
                        'employee_being_terminated': user_id,
                        'job_title': 'Other',
                        'is_this_termination_temporary_or_permanent': 'Permanent',
                        'does_the_user_have_a_revflow_account_that_needs_to_be_disabled': 'No',
                        'does_the_employee_need_emails_forwarded_to_someone': 'No',
                        'do_we_need_to_grant_access_to_the_employee_s_one_drive_files': 'No'}}
                call = self.call_api('post', 'service_catalog/items/95/place_request', payload=payload)
                ticket_numbers.append(call['service_request']['id'])
            # Creates a report of created ticket numbers.
            tickets_txt = open('created_ticket_numbers.txt', "a")
            for ticket in ticket_numbers:
                tickets_txt.write(str(ticket) + "\n")
            tickets_txt.close()

            return ticket_numbers

