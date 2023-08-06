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
        self.session = aiohttp.ClientSession(
            base_url=self.base_url,
            raise_for_status=True,
            timeout=aiohttp.ClientTimeout(total=60)
        )
        self.auth_headers = {'Authorization': f'Token {self.token}'}

    @staticmethod
    def _clean_params(params):
        if params is None:
            return {}
        return {k: v for k, v in params.items() if v is not None}

    async def _request(self, path, method, headers=None, params=None, data=None):
        url = path
        headers = {**self.auth_headers, **(headers or {})}
        params = self._clean_params(params)
        async with self.session.request(method, url, headers=headers, params=params, json=data) as response:
            if response.status == 204:
                return None
            return await response.json()

    async def _fetch(self, path, headers=None, params=None):
        return await self._request(path, 'GET', headers=headers, params=params)

    async def _post(self, path, headers=None, params=None, data=None):
        return await self._request(path, 'POST', headers=headers, params=params, data=data)

    async def _patch(self, path, headers=None, params=None, data=None):
        return await self._request(path, 'PATCH', headers=headers, params=params, data=data)

    async def _delete(self, path, headers=None, params=None):
        return await self._request(path, 'DELETE', headers=headers, params=params)

    def _get_deployment_volume_url(self, deployment_type, deployment_volume_id=None):
        url = self.base_url
        if deployment_type == 'service':
            url += f'/operations/service-volumes/'
        elif deployment_type == 'database':
            url += f'/operations/database-volumes/'
        else:
            raise ValueError('Invalid deployment type')

        if deployment_volume_id:
            url += f'{deployment_volume_id}/'
        return url

    @api_exception_wrapper
    async def fetch_project(self, project_id):
        url = f'/operations/projects/{project_id}/'
        return await self._fetch(url)

    @api_exception_wrapper
    async def fetch_service(self, service_id):
        url = f'/operations/services/{service_id}/'
        return await self._fetch(url)

    @api_exception_wrapper
    async def fetch_database(self, database_id):
        url = f'/operations/database-instances/{database_id}/'
        return await self._fetch(url)

    @api_exception_wrapper
    async def fetch_image(self, image_id):
        url = f'/operations/images/{image_id}/'
        return await self._fetch(url)

    @api_exception_wrapper
    async def fetch_volume(self, volume_id):
        url = f'/operations/volumes/{volume_id}/'
        return await self._fetch(url)

    @api_exception_wrapper
    async def fetch_deployment_volume(self, deployment_volume_id, deployment_type):
        url = self._get_deployment_volume_url(deployment_type, deployment_volume_id)
        return await self._fetch(url)

    @api_exception_wrapper
    async def fetch_database_type(self, database_type_id):
        url = f'/operations/database-types/{database_type_id}/'
        return await self._fetch(url)

    @api_exception_wrapper
    async def patch_service(self, service_id, image_id):
        url = f'/operations/services/{service_id}/'
        data = {
            'image_id': image_id
        }
        return await self._patch(url, data=data)

    @api_exception_wrapper
    async def create_image(self, tag, previous_image, base_image_id=None, branch=None):
        url = f'/operations/images/'
        data = {
            'title': previous_image['title'],
            'project_id': previous_image['project_id'],
            'preset_id': previous_image['preset']['id'],
            'tag': tag,
            'git_url': previous_image['git_url'],
            'git_branch': branch or previous_image['git_branch'],
            'build_envs': previous_image['build_envs'],
            'init_command': previous_image['init_command'],
            'startup_command': previous_image['startup_command'],
            'daemon_command': previous_image['daemon_command'],
        }
        if base_image_id:
            data['base_image_id'] = base_image_id
        return await self._post(url, data=data)

    @api_exception_wrapper
    async def create_service(self,
                             project_id,
                             name,
                             type_id,
                             image_id,
                             quota_id,
                             env_vars=None,
                             domain_ids=None,
                             test_domain=None, ):
        url = f'/operations/services/'
        data = {
            'project_id': project_id,
            'name': name,
            'type_id': type_id,
            'image_id': image_id,
            'quota_id': quota_id,
            'envs': env_vars or {},
            'domains_id': domain_ids or [],
            'test_domain': test_domain
        }
        return await self._post(url, data=data)

    @api_exception_wrapper
    async def create_pipeline(self, project_id, services, images, base_image_id=None):
        url = f'/operations/pipelines/'
        data = {
            'project_id': project_id,
            'services': services,
            'images': images
        }
        if base_image_id:
            data['base_image_id'] = base_image_id
        return await self._post(url, data=data)

    @api_exception_wrapper
    async def create_database(self, project_id, name, type_id, image_id, quota_id):
        url = f'/operations/database-instances/'
        data = {
            'project_id': project_id,
            'name': name,
            'initial_db_name': name,
            'type_id': type_id,
            'image_id': image_id,
            'quota_id': quota_id
        }
        return await self._post(url, data=data)

    @api_exception_wrapper
    async def create_volume(self, project_id, name, capacity=None):
        url = f'/operations/volumes/'
        data = {
            'project_id': project_id,
            'name': name
        }
        if capacity:
            data['capacity'] = capacity
        return await self._post(url, data=data)

    @api_exception_wrapper
    async def create_deployment_volume(self, volume_id, deployment_id, mount_path, size, deployment_type):
        url = self._get_deployment_volume_url(deployment_type)
        data = {
            'volume_id': volume_id,
            f"{deployment_type}_id": deployment_id,
            'target': mount_path,
            'capacity': size
        }
        return await self._post(url, data=data)

    @api_exception_wrapper
    async def create_domain(self, service_id, base, https_active=True, https_redirect_code=None):
        url = f'/operations/domains/'
        data = {
            'service_id': service_id,
            'base': base,
            'https_active': https_active,
            'https_redirect': https_redirect_code
        }
        return await self._post(url, data=data)

    @api_exception_wrapper
    async def commit_image(self, image_id):
        url = f'/operations/images/{image_id}/commit/'
        return await self._post(url)

    @api_exception_wrapper
    async def commit_database(self, database_id):
        url = f'/operations/database-instances/{database_id}/commit/'
        return await self._post(url)

    @api_exception_wrapper
    async def list_services(self, project_id=None, type_id=None, search=None, limit=20, offset=0):
        url = '/operations/services/'
        params = {
            'project': project_id,
            'type': type_id,
            'search': search,
            'limit': limit,
            'offset': offset
        }
        return await self._fetch(url, params=params)

    @api_exception_wrapper
    async def list_databases(self, project_id=None, type_id=None, search=None, limit=20, offset=0):
        url = '/operations/database-instances/'
        params = {
            'project': project_id,
            'type': type_id,
            'search': search,
            'limit': limit,
            'offset': offset
        }
        return await self._fetch(url, params=params)

    @api_exception_wrapper
    async def list_organizations(self, search=None, limit=20, offset=0):
        url = f'/auth/organizations/'
        params = {
            'search': search,
            'limit': limit,
            'offset': offset
        }
        return await self._fetch(url, params=params)

    @api_exception_wrapper
    async def list_projects(self, organization_id=None, search=None, limit=20, offset=0):
        url = f'/operations/projects/'
        params = {
            'organization': organization_id,
            'search': search,
            'limit': limit,
            'offset': offset
        }
        return await self._fetch(url, params=params)

    @api_exception_wrapper
    async def list_volumes(self, project_id, search=None, limit=20, offset=0):
        url = f'/operations/volumes/'
        params = {
            'project': project_id,
            'search': search,
            'limit': limit,
            'offset': offset
        }
        return await self._fetch(url, params=params)

    @api_exception_wrapper
    async def list_deployment_volumes(self, deployment_id, deployment_type, search=None, limit=20, offset=0):
        url = self._get_deployment_volume_url(deployment_type)
        params = {
            f"{deployment_type}": deployment_id,
            'search': search,
            'limit': limit,
            'offset': offset
        }
        return await self._fetch(url, params=params)

    @api_exception_wrapper
    async def list_defaults(self,
                            content_type_name=None,
                            field_name=None,
                            service_type_codename=None,
                            type_preset=None,
                            search=None,
                            limit=None,
                            offset=None):
        url = '/operations/defaults/'
        params = {
            'content_type_name': content_type_name,
            'field_name': field_name,
            'service_type': service_type_codename,
            'type_preset': type_preset,
            'search': search,
            'limit': limit,
            'offset': offset
        }
        return await self._fetch(url, params=params)

    @api_exception_wrapper
    async def delete_service(self, service_id):
        url = f'/operations/services/{service_id}/'
        return await self._delete(url)
