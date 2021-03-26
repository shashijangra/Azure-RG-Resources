# Import the needed credential and management objects from the libraries.
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
import os

def resolve_resource_api(client, resource):
    """ This method retrieves the latest non-preview api version for
    the given resource (unless the preview version is the only available
    api version) """
    provider = client.providers.get(resource.id.split('/')[6])
    rt = next((t for t in provider.resource_types
               if t.resource_type == '/'.join(resource.type.split('/')[1:])), None)
    #print(rt)
    if rt and 'api_versions' in rt.__dict__:
        #api_version = [v for v in rt[0].api_versions if 'preview' not in v.lower()]
        #return npv[0] if npv else rt[0].api_versions[0]
        api_version = [v for v in rt.__dict__['api_versions'] if 'preview' not in v.lower()]
        return api_version[0] if api_version else rt.__dict__['api_versions'][0]


# Acquire a credential object using CLI-based authentication.
credential = AzureCliCredential()

subscription_id = 'f60d1ca0-3e98-4505-8d80-9d6782135e0f'

# Obtain the management object for resources.
resource_client = ResourceManagementClient(credential, subscription_id)

# Retrieve the list of resource groups
group_list = resource_client.resource_groups.list()

# Show the groups in formatted output
column_width = 40

for group in list(group_list):
    resource_list = resource_client.resources.list_by_resource_group(
        group.name,
        expand = "createdTime,changedTime"
    )
    # Show the resources in formatted output
    column_width = 36

    print("Resource".ljust(column_width) + "Type".ljust(column_width)
        + "Create date".ljust(column_width) + "Change date".ljust(column_width))
    print("-" * (column_width * 4))

    for resource in list(resource_list):
        print(f"{resource.name:<{column_width}}{resource.type:<{column_width}}"
        f"{str(resource.created_time):<{column_width}}{str(resource.changed_time):<{column_width}}"
        f"{str(resource.tags):<{column_width}}{str(resource.id):<{column_width}}")
        
        resource.tags['test'] = 'test1'

        resource_client.resources.begin_update_by_id(
            resource_id=resource.id,
            api_version=resolve_resource_api(resource_client, resource),
            parameters=resource
        )