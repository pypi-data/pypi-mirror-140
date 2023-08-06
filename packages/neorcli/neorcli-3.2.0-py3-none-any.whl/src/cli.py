"""
Cli interface to update services

Usage:
    neor-cli.py [options] update <service_id> --tag <tag> [--branch <branch>]
    neor-cli.py [options] update-mass <base_service_id> <services> [<services>...] --tag <tag> [--branch <branch>]

Options:
    -h --help     Show this screen.
    -t --token    Token to use for authentication.
    -v --version  Show version.
"""
import argparse
import asyncio
import json
import uuid
from datetime import datetime
from time import sleep

import humanize
import pkg_resources
from tabulate import tabulate

from src.api import APIClient

VERSION = pkg_resources.get_distribution("neorcli").version

parser = argparse.ArgumentParser(description='Neor CLI')
subparsers = parser.add_subparsers(dest='command', help='sub-command help')

parser.add_argument('-t', '--token', help='Token to use for authentication.')
parser.add_argument('-v', '--version', action='version', version=f'%(prog)s v{VERSION}')

update_parser = subparsers.add_parser('update', help='Update a service')

update_parser.add_argument('service_id', help='Service ID to update', type=int)
update_parser.add_argument('--tag', help='Tag to update')
update_parser.add_argument('--branch', help='Branch to update. use tag if no branch is selected', required=False)

mass_update_parser = subparsers.add_parser('update-mass', help='Update a mass of services')

mass_update_parser.add_argument('base_service_id', help='Service to use as base for mass update', type=int)
mass_update_parser.add_argument('services', nargs='+', help='Services to update', type=int)
mass_update_parser.add_argument('--tag', help='Tag to update')
mass_update_parser.add_argument('--branch', help='Branch to update. use tag if no branch is selected', required=False)

create_parser = subparsers.add_parser('create', help='Create a service')
create_subparsers = create_parser.add_subparsers(dest='create_type', help='sub-command help')

create_service_parser = create_subparsers.add_parser('service', help='Create a service')

create_service_parser.add_argument('project_id', help='Project ID to create service in', type=int)
create_service_parser.add_argument('service_name', help='Name of service to create')
create_service_parser.add_argument('--base_service_id', help='Base service ID to use for service creation', type=int)
create_service_parser.add_argument('--test-domain', help='Test domain to use for service creation', required=False)
create_service_parser.add_argument('--domains', nargs='+', help='Domains to use for service creation', required=False)
create_service_parser.add_argument(
    '--domains-ssl-redirect-code',
    help='SSL redirect code to use for all domains. leave empty to disable SSL redirect',
    required=False,
    type=int,
    choices=[301, 302, 307]
)
create_service_parser.add_argument(
    '--envs-file',
    help='File containing environment variables to use for service creation',
    required=False
)
create_service_parser.add_argument(
    '--no-new-image',
    help='Do not create a new image',
    action='store_true',
    default=False
)
create_service_parser.add_argument('--no-deploy', help='Do not deploy service', action='store_true', default=False)
create_service_parser.add_argument(
    '--share-storage',
    help='Share storage with base service',
    action='store_true',
    default=False
)
create_service_parser.add_argument(
    '--volumes-capacity',
    help='Capacity of all volumes in Byte',
    required=False,
    type=int
)

create_db_parser = create_subparsers.add_parser('db', help='Create a database')

create_db_parser.add_argument('project_id', help='Project ID to create database in', type=int)
create_db_parser.add_argument('db_name', help='Name of database to create')
create_db_parser.add_argument('--type-id', help='Type ID of database to create', type=int)
create_db_parser.add_argument('--image-id', help='Image ID of database to create', type=int)
create_db_parser.add_argument('--quota-id', help='Quota ID of database to create', type=int)

list_parser = subparsers.add_parser('list', help='List resources')
list_subparsers = list_parser.add_subparsers(dest='list_type', help='sub-command help')

list_service_parser = list_subparsers.add_parser('services', help='List services')
list_service_parser.add_argument('--project-id', help='Project ID to list services in', type=int, required=False)
list_service_parser.add_argument(
    '--limit',
    help='Limit number of services to list',
    type=int,
    required=False,
    default=50
)
list_service_parser.add_argument(
    '--offset',
    help='Offset to start listing services from',
    type=int,
    required=False,
    default=0
)

token = None
client: APIClient = None


async def handle_update(args):
    service = await client.fetch_service(args.service_id)
    image = await client.fetch_image(service['image_id'])
    image_id = await client.create_image(args.tag, image, branch=args.branch or args.tag)['id']
    await client.patch_service(args.service_id, image_id)
    await client.create_pipeline(service['project_id'], [args.service_id], [image_id])
    print(f"{service['name']} service begins to update")


async def handle_mass_update(args):
    base_service = await client.fetch_service(args.base_service_id)
    base_image = await client.fetch_image(base_service['image_id'])
    new_base_image_id = await client.create_image(args.tag, base_image, branch=args.branch or args.tag)['id']
    await client.patch_service(args.base_service_id, new_base_image_id)
    services = [
        base_service['id']
    ]
    images = []
    for service_id in args.services:
        service = await client.fetch_service(service_id)
        image = await client.fetch_image(service['image_id'])
        if image['id'] == base_image['id']:
            new_image_id = new_base_image_id
        else:
            new_image_id = await client.create_image(
                args.tag,
                image,
                base_image_id=new_base_image_id,
                branch=args.branch or args.tag
            )['id']
            images.append(new_image_id)
        await client.patch_service(service_id, new_image_id)
        services.append(service_id)
    await client.create_pipeline(base_service['project_id'], services, images, base_image_id=new_base_image_id)
    print(f"{len(services)} services begins to update")


def handle_create(args):
    if args.create_type == 'service':
        handle_create_service(args)
    elif args.create_type == 'db':
        handle_create_db(args)
    else:
        raise Exception("Unknown create type")


def handle_create_service(args):
    base_service = client.fetch_service(args.base_service_id)

    if base_service['project_id'] != args.project_id:
        raise Exception("Base service is not in the same project")

    base_image = client.fetch_image(base_service['image_id'])
    if args.no_new_image is True:
        image_id = base_service['image_id']
    else:
        image_id = client.create_image(
            base_image['tag'],
            base_image,
            base_image_id=base_image['id'],
            branch=base_image['git_branch']
        )['id']

    test_domain = args.test_domain or f"{args.service_name}-{str(uuid.uuid4().int)[:6]}"

    envs = {}
    if args.envs_file:
        with open(args.envs_file, 'r') as f:
            envs = json.load(f)

    service = client.create_service(
        args.project_id,
        args.service_name,
        type_id=base_service['type']['id'],
        image_id=image_id,
        quota_id=base_service['quota']['id'],
        env_vars={**base_service['envs'], **envs},
        test_domain=test_domain
    )
    print(f"{service['name']} service has been created with ID {service['id']}")

    if base_service['volumes']:
        volume_relations = client.list_deployment_volumes(
            base_service['id'], deployment_type='service'
        )['results']

        if args.share_storage is False:
            print(f"Creating {len(volume_relations)} volumes")
            sleep(1)
            for volume_relation in volume_relations:
                capacity = args.volumes_capacity or volume_relation['volume'].get('capacity')
                volume_relation['volume'] = client.create_volume(
                    project_id=args.project_id,
                    name=f"{args.service_name}-vol-{str(uuid.uuid4().int)[:6]}",
                    capacity=capacity,
                )
            print("Volumes created")

        for volume_relation in volume_relations:
            print(f"Attaching volume {volume_relation['volume']['name']} to {service['name']}")
            client.create_deployment_volume(
                volume_id=volume_relation['volume']['id'],
                deployment_id=service['id'],
                deployment_type='service',
                mount_path=volume_relation['target'],
                size=volume_relation['volume'].get('capacity', None)
            )
            print(f"Volume {volume_relation['volume']['name']} attached")

    if args.domains:
        for domain in args.domains:
            client.create_domain(
                service_id=service['id'],
                base=domain,
                https_redirect_code=args.domains_ssl_redirect_code,
            )

    if args.no_deploy is False:
        if image_id == base_service['image_id']:
            images = []
        else:
            images = [image_id]
        client.create_pipeline(args.project_id, [service['id']], images)
        print(f"{service['name']} service begins to deploy")
    elif args.no_deploy is True and args.no_new_image is False:
        client.commit_image(image_id)
        print(f"{service['name']} service image begins to create but no deploy is scheduled")


def handle_create_db(args):
    args.db_name = args.db_name.replace('_', '-')
    type_ = client.fetch_database_type(args.type_id)
    volumes = client.list_defaults(
        content_type_name='databaseinstance',
        field_name='volumes',
        service_type_codename=type_['code_name']
    )['results'] or []
    db = client.create_database(
        project_id=args.project_id,
        name=args.db_name,
        type_id=args.type_id,
        image_id=args.image_id,
        quota_id=args.quota_id
    )
    print(f"{db['initial_db_name']} database has been created with ID {db['id']}")
    if volumes:
        print(f"Creating {len(volumes)} volumes")
    for volume in volumes:
        volume = json.loads(volume['value'])
        volume_obj = client.create_volume(
            args.project_id,
            f"{db['initial_db_name']}-{volume['name']}-{str(uuid.uuid4().int)[:6]}"
        )
        print(f"Attaching volume {volume_obj['name']} to {db['initial_db_name']}")
        client.create_deployment_volume(
            volume_id=volume_obj['id'],
            deployment_id=db['id'],
            deployment_type='database',
            mount_path=volume['target'],
            size=volume.get('capacity', None)
        )
        print(f"Volume {volume_obj['name']} attached")

    client.commit_database(db['id'])
    print(f"{db['initial_db_name']} database image begins to deploy")

    sleep(1)
    db = client.fetch_database(db['id'])

    print(f"hostname: {db['host']}")


async def handle_list(args):
    if args.list_type == 'services':
        services = await client.list_services(args.project_id, limit=args.limit, offset=args.offset)
        services = services['results']
        services = [
            {
                'id': service['id'],
                'name': service['name'],
                'type': service['type']['name'],
                'build_status': service.get('image_status', 'without image'),
                'deploy_status': service['creation_status'],
                # show dates in relative format
                'created_at': humanize.naturaltime(
                    datetime.strptime(service['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z'),
                    when=datetime.now(datetime.strptime(service['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z').tzinfo)
                ),
                'updated_at': humanize.naturaltime(
                    datetime.strptime(service['updated_at'], '%Y-%m-%dT%H:%M:%S.%f%z'),
                    when=datetime.now(datetime.strptime(service['updated_at'], '%Y-%m-%dT%H:%M:%S.%f%z').tzinfo)
                ),
            }
            for service in sorted(services, key=lambda x: x['id'])
        ]
        table = tabulate(services, headers='keys', numalign='left')
        print(table)


handlers = {
    'update': handle_update,
    'update-mass': handle_mass_update,
    'create': handle_create,
    'list': handle_list,
}


async def main():
    args = parser.parse_args()

    global token
    token = args.token

    global client
    client = APIClient(token)

    if args.token is None:
        print('You must provide a token')
        return

    handler = handlers[args.command]
    await handler(args)
    await client.session.close()


def run():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


if __name__ == '__main__':
    run()
