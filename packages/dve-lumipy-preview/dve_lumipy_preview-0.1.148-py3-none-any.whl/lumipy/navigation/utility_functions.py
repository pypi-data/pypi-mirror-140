from lumipy.navigation.atlas import Atlas
from lumipy.navigation.field_metadata import FieldMetadata
from lumipy.navigation.provider_metadata import ProviderMetadata
from lumipy.navigation.metadata_class_factory import _MetadataClassFactory
from lumipy.client import Client
from typing import Optional, List
from lumipy.common.string_utils import random_globe
from pandas import DataFrame


def query_provider_metadata(client: Client) -> DataFrame:
    """Query luminesce for metadata on the available providers.

    Args:
        client (Client): lumipy client to query with.

    Returns:
        DataFrame: pandas dataframe containing query result.
    """

    return client.query_and_fetch("""
        select
          svc.[MqUserName], svc.[Description], svc.[Type], 
          svc.[Category], svc.[Client], 
          svc.[DocumentationLink], svc.[LastPingAt], svc.[LicenceCode], fld.[FieldName], fld.[TableName], 
          fld.[Source], fld.[DataType], fld.[FieldType], fld.[Description] as [Description_fld], fld.[IsMain], 
          fld.[IsPrimaryKey], fld.[ParamDefaultValue], fld.[TableParamColumns] 
        from
          Sys.Field as fld 
        left join
          Sys.Registration as svc
         on
          ((svc.[Name] = fld.[TableName]) 
          and (svc.[Type] = 'DataProvider')) 
          and (fld.[FieldName] is not null)          
    """)


def build_provider_metadata_objects(df: DataFrame, client: Client) -> List[ProviderMetadata]:
    """Build a list of provider metadata objects from the queried metadata rows.

    Args:
        df (DataFrame): dataframe containing the queried luminesce provider metadata.
        client (Client): the client to attach to the provider metadata objects.

    Returns:
        List[ProviderMetadata]: list of provider metadata objects to build the atlas with.
    """

    provider_descriptions = []
    for p, p_df in df.groupby('TableName'):

        p_df = p_df.drop_duplicates(subset='FieldName')
        fields = [FieldMetadata.from_row(row) for _, row in p_df.iterrows()]

        p_row = p_df.iloc[0]
        provider_metadata_cls = _MetadataClassFactory(
            table_name=p_row.TableName,
            description=p_row.Description,
            provider_type=p_row.Type,
            category=p_row.Category,
            last_ping_at=p_row.LastPingAt,
            documentation=p_row.DocumentationLink,
            fields=fields,
            client=client
        )
        provider_metadata = provider_metadata_cls()

        provider_descriptions.append(provider_metadata)

    return provider_descriptions


def get_atlas(**kwargs) -> Atlas:
    """Get luminesce data provider atlas instance by passing any of the following: a token, api_url and app_name; a path to a secrets file
       via api_secrets_filename; or by passing in proxy information. If none of these are provided then lumipy will try
       to find the credentials information as environment variables.

    Keyword Args:
        token (str): Bearer token used to initialise the API
        api_secrets_filename (str): Name of secrets file (including full path)
        api_url (str): luminesce API url
        app_name (str): Application name (optional)
        certificate_filename (str): Name of the certificate file (.pem, .cer or .crt)
        proxy_url (str): The url of the proxy to use including the port e.g. http://myproxy.com:8888
        proxy_username (str): The username for the proxy to use
        proxy_password (str): The password for the proxy to use
        correlation_id (str): Correlation id for all calls made from the returned finbournesdkclient API instances

    Returns:
        Atlas: the atlas instance.
    """

    print("Building atlas... ", end='')

    client = Client(**kwargs)
    at_df = query_provider_metadata(client)
    provider_meta = build_provider_metadata_objects(at_df, client)

    atlas = Atlas(
        provider_meta,
        atlas_type='All available data providers'
    )
    globe = random_globe()

    print(f'done!{globe}')

    return atlas
