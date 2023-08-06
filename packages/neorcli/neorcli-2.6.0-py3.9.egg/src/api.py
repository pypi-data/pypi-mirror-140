from functools import wraps

import aiohttp

BACKEND_URL = 'https://api.neorcloud.com'


def api_exception_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except aiohttp.ClientResponseError as e:
            print(func.__name__, e.status, e.message)
            exit(1)

    return wrapper


class APIClient:
    def __init__(self, token, base_url=BACKEND_URL):
        self.token = token
        self.base_url = base_url
        # self.session = aiohttp.ClientSession(
        #     base_url=self.base_url,
        #     raise_for_status=True,
        #     timeout=aiohttp.ClientTimeout(total=60)
        # )

    # def _get_deployment_volume_url(self, deployment_type, deployment_volume_id=None):
    #     url = self.base_url
    #     if deployment_type == 'service':
    #         url += f'/operations/service-volumes/'
    #     elif deployment_type == 'database':
    #         url += f'/operations/database-volumes/'
    #     else:
    #         raise ValueError('Invalid deployment type')
    #
    #     if deployment_volume_id:
    #         url += f'{deployment_volume_id}/'
    #     return url
    #
    # @api_exception_wrapper
    # def fetch_service(self, service_id):
    #     url = f'{BACKEND_URL}/operations/services/{service_id}/'
    #     headers = {'Authorization': f'Token {self.token}'}
    #     response = requests.get(url, headers=headers)
    #     response.raise_for_status()
    #     return response.json()
    #
    # @api_exception_wrapper
    # def fetch_database(self, database_id):
    #     url = f'{BACKEND_URL}/operations/database-instances/{database_id}/'
    #     headers = {'Authorization': f'Token {self.token}'}
    #     response = requests.get(url, headers=headers)
    #     response.raise_for_status()
    #     return response.json()
    #
    # @api_exception_wrapper
    # def fetch_image(self, image_id):
    #     url = f'{BACKEND_URL}/operations/images/{image_id}/'
    #     headers = {'Authorization': f'Token {self.token}'}
    #     response = requests.get(url, headers=headers)
    #     response.raise_for_status()
    #     return response.json()
    #
    # @api_exception_wrapper
    # def fetch_volume(self, volume_id):
    #     url = f'{BACKEND_URL}/operations/volumes/{volume_id}/'
    #     headers = {'Authorization': f'Token {self.token}'}
    #     response = requests.get(url, headers=headers)
    #     response.raise_for_status()
    #     return response.json()
    #
    # @api_exception_wrapper
    # def fetch_deployment_volume(self, deployment_volume_id, deployment_type):
    #     url = self._get_deployment_volume_url(deployment_type, deployment_volume_id)
    #     headers = {'Authorization': f'Token {self.token}'}
    #     response = requests.get(url, headers=headers)
    #     response.raise_for_status()
    #     return response.json()
    #
    # @api_exception_wrapper
    # def fetch_database_type(self, database_type_id):
    #     url = f'{BACKEND_URL}/operations/database-types/{database_type_id}/'
    #     headers = {'Authorization': f'Token {self.token}'}
    #     response = requests.get(url, headers=headers)
    #     response.raise_for_status()
    #     return response.json()
    #
    # @api_exception_wrapper
    # def patch_service(self, service_id, image_id):
    #     url = f'{BACKEND_URL}/operations/services/{service_id}/'
    #     headers = {'Authorization': f'Token {self.token}'}
    #     data = {
    #         'image_id': image_id
    #     }
    #     response = requests.patch(url, headers=headers, json=data)
    #     response.raise_for_status()
    #     return response.json()
    #
    # @api_exception_wrapper
    # def create_image(self, tag, previous_image, base_image_id=None, branch=None):
    #     url = f'{BACKEND_URL}/operations/images/'
    #     headers = {'Authorization': f'Token {self.token}'}
    #     data = {
    #         'title': previous_image['title'],
    #         'project_id': previous_image['project_id'],
    #         'preset_id': previous_image['preset']['id'],
    #         'tag': tag,
    #         'git_url': previous_image['git_url'],
    #         'git_branch': branch or previous_image['git_branch'],
    #         'build_envs': previous_image['build_envs'],
    #         'init_command': previous_image['init_command'],
    #         'startup_command': previous_image['startup_command'],
    #         'daemon_command': previous_image['daemon_command'],
    #     }
    #     if base_image_id:
    #         data['base_image_id'] = base_image_id
    #     response = requests.post(url, headers=headers, json=data)
    #     response.raise_for_status()
    #     return response.json()
    #
    # @api_exception_wrapper
    # def create_service(self,
    #                    project_id,
    #                    name,
    #                    type_id,
    #                    image_id,
    #                    quota_id,
    #                    env_vars=None,
    #                    domain_ids=None,
    #                    test_domain=None, ):
    #     url = f'{BACKEND_URL}/operations/services/'
    #     headers = {'Authorization': f'Token {self.token}'}
    #     data = {
    #         'project_id': project_id,
    #         'name': name,
    #         'type_id': type_id,
    #         'image_id': image_id,
    #         'quota_id': quota_id,
    #         'envs': env_vars or {},
    #         'domains_id': domain_ids or [],
    #         'test_domain': test_domain
    #     }
    #     response = requests.post(url, headers=headers, json=data)
    #     response.raise_for_status()
    #     return response.json()
    #
    # @api_exception_wrapper
    # def create_pipeline(self, project_id, services, images, base_image_id=None):
    #     url = f'{BACKEND_URL}/operations/pipelines/'
    #     headers = {'Authorization': f'Token {self.token}'}
    #     data = {
    #         'project_id': project_id,
    #         'services': services,
    #         'images': images
    #     }
    #     if base_image_id:
    #         data['base_image_id'] = base_image_id
    #     response = requests.post(url, headers=headers, json=data)
    #     response.raise_for_status()
    #     return response.json()
    #
    # @api_exception_wrapper
    # def create_database(self, project_id, name, type_id, image_id, quota_id):
    #     url = f'{BACKEND_URL}/operations/database-instances/'
    #     headers = {'Authorization': f'Token {self.token}'}
    #     data = {
    #         'project_id': project_id,
    #         'name': name,
    #         'initial_db_name': name,
    #         'type_id': type_id,
    #         'image_id': image_id,
    #         'quota_id': quota_id
    #     }
    #     response = requests.post(url, headers=headers, json=data)
    #     response.raise_for_status()
    #     return response.json()
    #
    # @api_exception_wrapper
    # def create_volume(self, project_id, name, capacity=None):
    #     url = f'{BACKEND_URL}/operations/volumes/'
    #     headers = {'Authorization': f'Token {self.token}'}
    #     data = {
    #         'project_id': project_id,
    #         'name': name
    #     }
    #     if capacity:
    #         data['capacity'] = capacity
    #     response = requests.post(url, headers=headers, json=data)
    #     response.raise_for_status()
    #     return response.json()
    #
    # @api_exception_wrapper
    # def create_deployment_volume(self, volume_id, deployment_id, mount_path, size, deployment_type):
    #     url = self._get_deployment_volume_url(deployment_type)
    #     headers = {'Authorization': f'Token {self.token}'}
    #
    #     data = {
    #         'volume_id': volume_id,
    #         f"{deployment_type}_id": deployment_id,
    #         'target': mount_path,
    #         'capacity': size
    #     }
    #     response = requests.post(url, headers=headers, json=data)
    #     response.raise_for_status()
    #     return response.json()
    #
    # @api_exception_wrapper
    # def create_domain(self, service_id, base, https_active=True, https_redirect_code=None):
    #     url = f'{BACKEND_URL}/operations/domains/'
    #     headers = {'Authorization': f'Token {self.token}'}
    #     data = {
    #         'service_id': service_id,
    #         'base': base,
    #         'https_active': https_active,
    #         'https_redirect': https_redirect_code
    #     }
    #     response = requests.post(url, headers=headers, json=data)
    #     response.raise_for_status()
    #     return response.json()
    #
    # @api_exception_wrapper
    # def commit_image(self, image_id):
    #     url = f'{BACKEND_URL}/operations/images/{image_id}/commit/'
    #     headers = {'Authorization': f'Token {self.token}'}
    #     response = requests.post(url, headers=headers)
    #     response.raise_for_status()
    #     return response.json()
    #
    # @api_exception_wrapper
    # def commit_database(self, database_id):
    #     url = f'{BACKEND_URL}/operations/database-instances/{database_id}/commit/'
    #     headers = {'Authorization': f'Token {self.token}'}
    #     response = requests.post(url, headers=headers)
    #     response.raise_for_status()
    #     return response.json()
    #
    @api_exception_wrapper
    async def list_services(self, project_id, type_id=None, search=None, limit=20, offset=0):
        url = '/operations/services/'
        headers = {'Authorization': f'Token {self.token}'}
        params = {
            'project': project_id,
            'type': type_id,
            'search': search,
            'limit': limit,
            'offset': offset
        }
        async with aiohttp.ClientSession(base_url=BACKEND_URL) as session:
            async with session.get(url, headers=headers, params=params) as response:
                return await response.json()
    #
    # @api_exception_wrapper
    # def list_organizations(self, search=None, limit=20, offset=0):
    #     url = f'{BACKEND_URL}/auth/organizations/'
    #     headers = {'Authorization': f'Token {self.token}'}
    #     params = {
    #         'search': search,
    #         'limit': limit,
    #         'offset': offset
    #     }
    #     response = requests.get(url, headers=headers, params=params)
    #     response.raise_for_status()
    #     return response.json()
    #
    # @api_exception_wrapper
    # def list_projects(self, organization_id, search=None, limit=20, offset=0):
    #     url = f'{BACKEND_URL}/operations/projects/'
    #     headers = {'Authorization': f'Token {self.token}'}
    #     params = {
    #         'organization': organization_id,
    #         'search': search,
    #         'limit': limit,
    #         'offset': offset
    #     }
    #     response = requests.get(url, headers=headers, params=params)
    #     response.raise_for_status()
    #     return response.json()
    #
    # @api_exception_wrapper
    # def list_volumes(self, project_id, search=None, limit=20, offset=0):
    #     url = f'{BACKEND_URL}/operations/volumes/'
    #     headers = {'Authorization': f'Token {self.token}'}
    #     params = {
    #         'project': project_id,
    #         'search': search,
    #         'limit': limit,
    #         'offset': offset
    #     }
    #     response = requests.get(url, headers=headers, params=params)
    #     response.raise_for_status()
    #     return response.json()
    #
    # @api_exception_wrapper
    # def list_deployment_volumes(self, deployment_id, deployment_type, search=None, limit=20, offset=0):
    #     url = self._get_deployment_volume_url(deployment_type)
    #     headers = {'Authorization': f'Token {self.token}'}
    #     params = {
    #         f"{deployment_type}": deployment_id,
    #         'search': search,
    #         'limit': limit,
    #         'offset': offset
    #     }
    #     response = requests.get(url, headers=headers, params=params)
    #     response.raise_for_status()
    #     return response.json()
    #
    # @api_exception_wrapper
    # def list_defaults(self,
    #                   content_type_name=None,
    #                   field_name=None,
    #                   service_type_codename=None,
    #                   type_preset=None,
    #                   search=None,
    #                   limit=None,
    #                   offset=None):
    #     url = f'{BACKEND_URL}/operations/defaults/'
    #     headers = {'Authorization': f'Token {self.token}'}
    #     params = {
    #         'content_type_name': content_type_name,
    #         'field_name': field_name,
    #         'service_type': service_type_codename,
    #         'type_preset': type_preset,
    #         'search': search,
    #         'limit': limit,
    #         'offset': offset
    #     }
    #     response = requests.get(url, headers=headers, params=params)
    #     response.raise_for_status()
    #     return response.json()
