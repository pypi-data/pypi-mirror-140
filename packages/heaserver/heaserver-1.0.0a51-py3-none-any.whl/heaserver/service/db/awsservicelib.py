"""
Functions for interacting with Amazon Web Services.

This module supports management of AWS accounts, S3 buckets, and objects in S3 buckets. It uses Amazon's boto3 library
behind the scenes.

In order for HEA to access AWS accounts, buckets, and objects, there must be a volume accessible to the user through
the volumes microservice with an AWSFileSystem for its file system. Additionally, credentials must either be stored
in the keychain microservice and associated with the volume through the volume's credential_id attribute,
or stored on the server's file system in a location searched by the AWS boto3 library. Users can only see the
accounts, buckets, and objects to which the provided AWS credentials allow access, and HEA may additionally restrict
the returned objects as documented in the functions below. The purpose of volumes in this case is to supply credentials
to AWS service calls. Support for boto3's built-in file system search for credentials is only provided for testing and
should not be used in a production setting. This module is designed to pass the current user's credentials to AWS3, not
to have application-wide credentials that everyone uses.

The request argument to these functions is expected to have a OIDC_CLAIM_sub header containing the user id for
permissions checking. No results will be returned if this header is not provided or is empty.

In general, there are two flavors of functions for getting accounts, buckets, and objects. The first expects the id
of a volume as described above. The second expects the id of an account, bucket, or bucket and object. The latter
attempts to match the request up to any volumes with an AWSFileSystem that the user has access to for the purpose of
determine what AWS credentials to use. They perform the
same except when the user has access to multiple such volumes, in which case supplying the volume id avoids a search
through the user's volumes.
"""
import logging
import boto3
from botocore.exceptions import ClientError
import os
from aiohttp import web
from .. import response, client
from .servicelib import get_file_system_and_credentials_from_volume
from ..heaobjectsupport import type_to_resource_url
from ..oidcclaimhdrs import SUB
from typing import Any, Optional, List
from aiohttp.web import Response
from aiohttp.web import Request
from heaobject.volume import AWSFileSystem, Volume
from heaobject.user import NONE_USER
from heaobject.bucket import AWSBucket
from heaobject.root import DesktopObjectDict
from yarl import URL
from asyncio import gather

"""
Available functions
AWS object
- get

- change_storage_class            TODO
- copy_object
- delete_bucket_objects
- delete_bucket
- delete_folder
- delete_object
- download_object
- download_archive_object         TODO
- generate_presigned_url
- get_object_meta
- get_object_content
- get_all_buckets
- get all
- opener                          TODO -> return file format -> returning metadata containing list of links following collection + json format
-                                         need to pass back collection - json format with link with content type, so one or more links, most likely
- post_bucket
- post_folder
- post_object
- post_object_archive             TODO
- put_bucket
- put_folder
- put_object
- put_object_archive              TODO
- transfer_object_within_account
- transfer_object_between_account TODO
- rename_object
- update_bucket_policy            TODO

TO DO
- accounts?
"""


async def get_account(request: Request, volume_id: str):
    """
    Gets the AWS account associated with the provided volume id.

    Only get since you can't delete or put id information
    currently being accessed. If organizations get included, then the delete, put, and post will be added for name,
    phone, email, ,etc.
    NOTE: maybe get email from the login portion of the application?

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :return: account object with
        account id
        account name
        full name
        phone number
        alternate contact name
        alternate email address
        alternate phone number
        charge account?
    FIXME: a bad volume_id should result in a 400 status code; currently has status code 500.
    """
    aws_object_dict = await _get_account(request, volume_id)
    return await response.get(request, aws_object_dict)


async def get_account_by_id(request: web.Request) -> Optional[DesktopObjectDict]:
    """
    Gets an account by its id. The id is expected to be the request object's match_info mapping, with key 'id'.

    :param request: an aiohttp Request object (required).
    :return: an AWSAccount dict.
    """
    headers = {SUB: request.headers.get(SUB)} if SUB in request.headers else None
    volume_url = await type_to_resource_url(request, Volume)
    if volume_url is None:
        raise ValueError('No Volume service registered')
    get_volumes_url = URL(volume_url) / 'byfilesystemtype' / AWSFileSystem.get_type_name()

    async def get_one(request, volume_id):
        return await _get_account(request, volume_id)

    return next((a for a in await gather(
        *[get_one(request, v.id) async for v in client.get_all(request.app, get_volumes_url, Volume, headers=headers)])
                 if
                 a['id'] == request.match_info['id']), None)


async def get_volume_id_for_account_id(request: web.Request) -> Optional[str]:
    """
    Gets the id of the volume associated with an AWS account. The account id is expected to be in the request object's
    match_info mapping, with key 'id'.

    :param request: an aiohttp Request object (required).
    :return: a volume id string, or None if no volume was found associated with the AWS account.
    """
    headers = {SUB: request.headers.get(SUB)} if SUB in request.headers else None
    volume_url = await type_to_resource_url(request, Volume)
    if volume_url is None:
        raise ValueError('No Volume service registered')
    get_volumes_url = URL(volume_url) / 'byfilesystemtype' / AWSFileSystem.get_type_name()

    async def get_one(request, volume_id):
        return volume_id, await _get_account(request, volume_id)

    return next((volume_id for (volume_id, a) in await gather(
        *[get_one(request, v.id) async for v in client.get_all(request.app, get_volumes_url, Volume, headers=headers)])
                 if
                 a['id'] == request.match_info['id']), None)


async def get_all_accounts(request: web.Request) -> List[DesktopObjectDict]:
    """
    Gets all AWS accounts for the current user.

    In order for HEA to access an AWS account, there must be a volume accessible to the user through the volumes
    microservice with an AWSFileSystem for its file system, and credentials must either be stored in the keychain
    microservice and associated with the volume, or stored on the server's file system in a location searched by the
    AWS boto3 library.

    :param request: an aiohttp Request object (required).
    :return: a list of AWSAccount objects, or the empty list of the current user has no accounts.
    """
    headers = {SUB: request.headers.get(SUB)} if SUB in request.headers else None
    volume_url = await type_to_resource_url(request, Volume)
    if volume_url is None:
        raise ValueError('No Volume service registered')
    get_volumes_url = URL(volume_url) / 'byfilesystemtype' / AWSFileSystem.get_type_name()

    async def get_one(request, volume_id):
        return await _get_account(request, volume_id)

    return [a for a in await gather(
        *[get_one(request, v.id) async for v in client.get_all(request.app, get_volumes_url, Volume, headers=headers)])]


async def post_account(request: Request, volume_id: str):
    """
    Placeholder for when this may get implemented in the future.
    """
    return response.status_not_found()


async def put_account(request: Request, volume_id: str):
    """
    Placeholder for when this may get implemented in the future.
    """
    return response.status_not_found()


async def delete_account(request: Request, volume_id: str):
    """
    Placeholder for when this may get implemented in the future.
    """
    return response.status_not_found()


def change_storage_class():
    """
    change storage class (Archive, un-archive) (copy and delete old)

    S3 to archive -> https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/glacier.html#Glacier.Client.upload_archive
        save archive id for future access?
        archived gets charged minimum 90 days
        buckets = vault?
        delete bucket
    archive to S3
        create vault? link vault to account as attribute?
        delete vault
    """


async def copy_object(request: Request, volume_id: str, source_path: str, destination_path: str):
    """
    copy/paste (duplicate), throws error if destination exists, this so an overwrite isn't done
    throws another error is source doesn't exist
    https://medium.com/plusteam/move-and-rename-objects-within-an-s3-bucket-using-boto-3-58b164790b78
    https://stackoverflow.com/questions/47468148/how-to-copy-s3-object-from-one-bucket-to-another-using-python-boto3

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param source_path: (str) s3 path of object, includes bucket and key values together
    :param destination_path: (str) s3 path of object, includes bucket and key values together
    """
    # Copy object A as object B
    s3_resource = await _get_resource(request, 's3', volume_id)
    source_bucket_name = source_path.partition("/")[0]
    source_key_name = source_path.partition("/")[2]
    copy_source = {'Bucket': source_bucket_name, 'Key': source_key_name}
    destination_bucket_name = destination_path.partition("/")[0]
    destination_key_name = destination_path.partition("/")[2]
    try:
        s3_client = await _get_client(request, 's3', volume_id)
        s3_client.head_object(Bucket=destination_bucket_name,
                              Key=destination_key_name)  # check if destination object exists, if doesn't throws an exception
        return web.HTTPBadRequest()
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':  # object doesn't exist
            try:
                s3_client = await _get_client(request, 's3', volume_id)
                s3_client.head_object(Bucket=source_bucket_name,
                                      Key=source_key_name)  # check if source object exists, if not throws an exception
                s3_resource.meta.client.copy(copy_source, destination_path.partition("/")[0],
                                             destination_path.partition("/")[2])
                logging.info(e)
                return web.HTTPCreated()
            except ClientError as e_:
                logging.error(e_)
                return web.HTTPBadRequest()
        else:
            logging.info(e)
            return web.HTTPBadRequest()


async def delete_bucket_objects(request: Request, volume_id: str, bucket_name: str):
    """
    Deletes all objects inside a bucket

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param bucket_name: Bucket to delete
    """
    try:
        s3_resource = await _get_resource(request, 's3', volume_id)
        s3_client = await _get_client(request, 's3', volume_id)
        s3_client.head_bucket(Bucket=bucket_name)
        s3_bucket = s3_resource.Bucket(bucket_name)
        bucket_versioning = s3_resource.BucketVersioning(bucket_name)
        if bucket_versioning.status == 'Enabled':
            del_obj_all_result = s3_bucket.object_versions.delete()
            logging.info(del_obj_all_result)
        else:
            del_obj_all_result = s3_bucket.objects.all().delete()
            logging.info(del_obj_all_result)
        return web.HTTPNoContent()
    except ClientError as e:
        logging.error(e)
        return web.HTTPNotFound()


async def delete_bucket(request: Request, volume_id: str):
    """
    Deletes bucket and all contents

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param bucket_name: Bucket to delete
    """
    s3_client = await _get_client(request, 's3', volume_id)
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        delete_bucket_objects(request, volume_id, bucket_name)
        del_bucket_result = s3_client.delete_bucket(Bucket=bucket_name)
        logging.info(del_bucket_result)
        return web.HTTPNoContent()
    except ClientError as e:
        logging.error(e)
        return web.HTTPNotFound()


async def delete_folder(request: Request, volume_id: str, path_name: str):
    """
    Deletes folder and all contents

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param path_name: path to delete folder, split into bucket and folder for function

    https://izziswift.com/amazon-s3-boto-how-to-delete-folder/
    """
    # TODO: bucket.object_versions.filter(Prefix="myprefix/").delete()     add versioning option like in the delete bucket?
    # TODO: throws error if bucket doesn't exist, should this be desired effect?
    bucket_name = path_name.partition("/")[0]
    folder_name = path_name.partition("/")[2]
    s3_client = await _get_client(request, 's3', volume_id)
    try:
        s3_client.head_object(Bucket=bucket_name,
                              Key=(folder_name + '/'))  # check if folder exists, if not throws an exception
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_name + '/', MaxKeys=10000000)
        for object_f in response['Contents']:
            s3_client.delete_object(Bucket=bucket_name, Key=object_f['Key'])
        delete_folder_result = s3_client.delete_object(Bucket=bucket_name, Key=folder_name + '/')
        logging.info(delete_folder_result)
        return web.HTTPNoContent()
    except ClientError as e:
        logging.error(e)
        return web.HTTPNotFound()


async def delete_object(request: Request, volume_id: str, path_name: str):
    """
    Deletes a single object, checks if object exists before deleting, throws error if it doesn't

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param path_name: path to the object to delete

    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_object
    """
    s3_client = await _get_client(request, 's3', volume_id)
    bucket_name = path_name.partition("/")[0]
    key_name = path_name.partition("/")[2]
    try:
        # TODO: when last object is deleted the folder is also deleted. Should this be saved?
        s3_client.head_object(Bucket=bucket_name, Key=key_name)  # check if object exists, if not throws an exception
        delete_response = s3_client.delete_object(Bucket=bucket_name, Key=key_name)
        logging.info(delete_response)
        return web.HTTPNoContent()
    except ClientError as e:
        logging.error(e)
        return web.HTTPBadRequest()


async def download_object(request: Request, volume_id: str, object_path: str, save_path: str):
    r"""
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.download_file

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param object_path: path to the object to download
    :param save_path: path of where object is to be saved, note, needs to include the name of the file to save to
        ex: r'C:\Users\...\Desktop\README.md'  not  r'C:\Users\...\Desktop\'
    """
    try:
        s3_resource = await _get_resource(request, 's3', volume_id)
        bucket_name = object_path.partition("/")[0]
        folder_name = object_path.partition("/")[2]
        s3_resource.meta.client.download_file(bucket_name, folder_name, save_path)
    except ClientError as e:
        logging.error(e)


def download_archive_object(length=1):
    """

    """


def get_archive():
    """
    Don't think it is worth it to have a temporary view of data, expensive and very slow
    """


async def account_opener(request: Request, volume_id: str) -> Response:
    """
    Gets choices for opening an account object.

    :param request: the HTTP request. Required. If an Accepts header is provided, MIME types that do not support links
    will be ignored.
    :param volume_id: the id string of the volume containing the requested HEA object. If None, the root volume is
    assumed.
    :return: a Response object with status code 300, and a body containing the HEA desktop object and links
    representing possible choices for opening the HEA desktop object; or Not Found.
    """
    result = await _get_account(request, volume_id)
    if result is None:
        return response.status_not_found()
    return await response.get_multiple_choices(request, result)


async def account_opener_by_id(request: web.Request) -> web.Response:
    """
    Gets choices for opening an account object, using the 'id' value in the match_info attribute of the request.

    :param request: the HTTP request, must contain an id value in its match_info attribute. Required. If an Accepts
    header is provided, MIME types that do not support links will be ignored.
    :return: a Response object with status code 300, and a body containing the HEA desktop object and links
    representing possible choices for opening the HEA desktop object; or Not Found.
    """
    result = await get_account_by_id(request)
    if result is None:
        return response.status_not_found()
    return await response.get_multiple_choices(request, result)


async def generate_presigned_url(request: Request, volume_id: str, path_name: str, expiration: int = 3600):
    """Generate a presigned URL to share an S3 object

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param path_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.

    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
    """
    # Generate a presigned URL for the S3 object
    try:
        s3_client = await _get_client(request, 's3', volume_id)
        bucket_name = path_name.partition("/")[0]
        folder_name = path_name.partition("/")[2]
        response = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': folder_name},
                                                    ExpiresIn=expiration)
        logging.info(response)
    except ClientError as e:
        logging.error(e)
        return None
    # The response contains the presigned URL
    return response


async def get_object_meta(request: Request, volume_id: str, path_name: str):
    """
    preview object in object explorer

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param path_name: path to the object to get, includes both bucket and key values
    """
    try:
        s3_client = await _get_client(request, 's3', volume_id)
        bucket_name = path_name.partition("/")[0]
        folder_name = path_name.partition("/")[2]
        response = s3_client.get_object(Bucket=bucket_name, Key=folder_name)
        logging.info(response["ResponseMetadata"])
        return response["ResponseMetadata"]  # .read(amt=1024)
        # return response  # ["Body"] .read()   .read(amt=chunk_size)
    except ClientError as e:
        logging.error(e)


async def get_object_content(request: Request, volume_id: str, path_name: str):
    """
    preview object in object explorer

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param path_name: path to the object to get, includes both bucket and key values
    """
    try:
        s3_client = await _get_client(request, 's3', volume_id)
        bucket_name = path_name.partition("/")[0]
        folder_name = path_name.partition("/")[2]
        response = s3_client.get_object(Bucket=bucket_name, Key=folder_name)
        logging.info(response["ResponseMetadata"])
        return response["Body"]  # .read(amt=1024)
        # return response  # ["Body"] .read()   .read(amt=chunk_size)
    except ClientError as e:
        logging.error(e)


async def get_bucket(request: Request, volume_id: str, bucket: Optional[dict] = None,
                     bucket_name: Optional[str] = None):
    """
    List a single bucket's attributes

    :param bucket_name: the name of the bucket representing the user's AWS Bucket
    :param bucket:  the retrieved bucket dict from our db, if id is provided we will attempt to retrieve it
    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :return:  return the single bucket object requested or None
    """
    if bucket is None and bucket_name is None:
        return web.HTTPBadRequest()
    bucket_name = bucket["name"] if bucket is not None else bucket_name
    try:
        b = AWSBucket()
        if bucket is not None:  # I expect this will never be None
            b.from_dict(bucket)
        s3_client = await _get_client(request, 's3', volume_id)
        s3_resource = await _get_resource(request, 's3', volume_id)
        resp = s3_resource.Bucket(bucket_name)
        b.created = resp.creation_date
        bucket_versioning = s3_resource.BucketVersioning(bucket_name)
        b.is_versioned = bucket_versioning.status == 'Enabled'
        b.s3_uri = "s3://" + bucket_name + "/"
        b.region = s3_client.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
        # todo how to find partition dynamically. The format is arn:PARTITION:s3:::NAME-OF-YOUR-BUCKET
        # b.arn = "arn:"+"aws:"+":s3:::"
        try:
            b.tags = s3_client.get_bucket_tagging(Bucket=bucket_name)
        except ClientError as ce:
            if ce.response['Error']['Code'] != 'NoSuchTagSet':
                logging.error(ce)
        try:
            encrypt = s3_client.get_bucket_encryption(Bucket=bucket_name)
            rules: list = encrypt['ServerSideEncryptionConfiguration']['Rules']
            b.is_encrypted = len(rules) > 0
        except ClientError as e:
            if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                b.is_encrypted = False
        if bucket["object_count"] and bucket["size"] and bucket["modified"]:
            b.object_count = bucket["object_count"]
            b.size = bucket["size"]
        else:
            total_size = 0
            obj_count = 0
            mod_date = bucket["modified"]
            s3bucket = s3_resource.Bucket(bucket_name)
            for obj in s3bucket.objects.all():
                total_size += obj.size
                obj_count += 1
                mod_date = obj.last_modified if mod_date is None or obj.last_modified > mod_date else mod_date
            b.size = total_size
            b.object_count = obj_count
            b.modified = mod_date

    except ClientError as e:
        logging.error(e)
        return web.HTTPNotFound()
    return await response.get(request, b.to_dict())


async def get_all_buckets(request: Request, volume_id: str) -> List[DesktopObjectDict]:
    """
    List available buckets by name

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :return: (list) list of available buckets
    """
    try:
        s3_client = await _get_client(request, 's3', volume_id)
        resp = s3_client.list_buckets()
        bucket_dict = {}
        bucket_list = []
        for bucket in resp['Buckets']:
            bucket_list.append(f'{bucket["Name"]}')
        bucket_dict['buckets'] = bucket_list
    except ClientError as e:
        logging.error(e)
        return response.status_bad_request()
    return await response.get(request, bucket_dict)


async def get_all(request: Request, volume_id: str, bucket_name: str, max_keys: int = 1000):
    """
    List all objects in entire bucket. This includes folder names.

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param bucket_name: (str) name of bucket to list objects in
    :param max_keys: (int) max number of objects to list, list_objects_v2 defualts to 1000
    """
    try:
        object_list = []
        s3_client = await _get_client(request, 's3', volume_id)
        response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=max_keys)
        logging.info(response)
        for val in response["Contents"]:
            object_list.append(val["Key"])
        return object_list
    except ClientError as e:
        logging.error(e)


async def post_bucket(request: Request, volume_id: str, bucket_name: str, region: Optional[str] = None):
    """
    Create an S3 bucket in a specified region, checks that it is the first, if already exists errors are thrown
    If a region is not specified, the bucket is created in the S3 default region (us-east-1).

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    """
    s3_client = await _get_client(request, 's3', volume_id)
    try:
        response = s3_client.head_bucket(Bucket=bucket_name)  # check if bucket exists, if not throws an exception
        logging.info(response)
        return web.HTTPBadRequest(body="bucket already exists")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':  # bucket doesn't exist
            if region is None:
                create_bucket_result = s3_client.create_bucket(Bucket=bucket_name)
                logging.info(create_bucket_result)
                return web.HTTPCreated()
                # return response.put(create_bucket_result["ResponseMetadata"]["HTTPStatusCode"])
            else:
                create_bucket_result = s3_client.create_bucket(Bucket=bucket_name,
                                                               CreateBucketConfiguration={'LocationConstraint': region})
                logging.info(create_bucket_result)
                return web.HTTPCreated()
        elif error_code == '403':  # already exists
            logging.error(e)
            return web.HTTPBadRequest(body="bucket exists, no permission to access")
        else:
            logging.error(e)
            return web.HTTPBadRequest()


async def post_folder(request: Request, volume_id: str, path_name: str):
    """
    Adds a folder to bucket given in parameter, checks that it is the first, if already exists errors are thrown

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param path_name: (str) path to delete folder, split into bucket and folder for function, input as bucket and key values together
    """
    bucket_name = path_name.partition("/")[0]
    folder_name = path_name.partition("/")[2]
    s3_client = await _get_client(request, 's3', volume_id)
    try:
        response = s3_client.head_object(Bucket=bucket_name,
                                         Key=(folder_name + '/'))  # check if folder exists, if not throws an exception
        logging.info(response)
        return web.HTTPBadRequest(body="folder already exists")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':  # folder doesn't exist
            add_folder_result = s3_client.put_object(Bucket=bucket_name, Key=(folder_name + '/'))
            logging.info(add_folder_result)
            return web.HTTPCreated()
        else:
            logging.error(e)
            return web.HTTPBadRequest()


async def post_object(request: Request, volume_id: str, path_name: str, file_path: str,
                      object_name: Optional[str] = None):
    """Upload a file to an S3 bucket, checks that it is the first, if already exists errors are thrown

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param file_path: Path to the file to upload
    :param path_name: path to the location of object
    :param object_name: S3 object name. If not specified then file_name is used

    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(
            (os.path.normpath(file_path)))  # only gets the last part of the path so identifiable info not included

    s3_client = await _get_client(request, 's3', volume_id)
    bucket_name = path_name.partition("/")[0]
    key_name = path_name.partition("/")[2]
    try:
        upload_response = s3_client.head_object(Bucket=bucket_name,
                                                Key=key_name + object_name)  # check if folder exists, if not throws an exception
        logging.info(upload_response)
        return web.HTTPBadRequest(body="object already exists")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':  # folder doesn't exist
            upload_response = s3_client.upload_file(file_path, bucket_name, key_name + object_name)
            logging.info(upload_response)
            return web.HTTPCreated()
        else:
            logging.info(e)
            return web.HTTPBadRequest()


def post_object_archive():
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/glacier.html
    """


async def put_bucket(request: Request, volume_id: str, bucket_name: str, region: Optional[str] = None):
    """
    Create an S3 bucket in a specified region, if it doesn't exist an error will be thrown
    If a region is not specified, the bucket is created in the S3 default region (us-east-1).

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    """
    s3_client = await _get_client(request, 's3', volume_id)
    try:
        s3_client.head_bucket(Bucket=bucket_name)  # check if bucket exists, if not throws an exception
        if region is None:
            create_bucket_result = s3_client.create_bucket(Bucket=bucket_name)
            logging.info(create_bucket_result)
            return web.HTTPCreated()
        else:
            create_bucket_result = s3_client.create_bucket(Bucket=bucket_name,
                                                           CreateBucketConfiguration={'LocationConstraint': region})
            logging.info(create_bucket_result)
            return web.HTTPCreated()
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            logging.error(e)
            return web.HTTPBadRequest(body="bucket doesn't exist")
        elif error_code == '403':
            logging.error(e)
            return web.HTTPBadRequest(body="bucket exists, no permission to access")
        else:
            logging.error(e)
            return web.HTTPBadRequest()


async def put_folder(request: Request, volume_id: str, path_name: str):
    """
    Adds a folder to bucket given in parameter, if it doesn't exist, throws error

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param path_name: (str) path to delete folder, split into bucket and folder for function, input as bucket and key values together
    """
    bucket_name = path_name.partition("/")[0]
    folder_name = path_name.partition("/")[2]
    s3_client = await _get_client(request, 's3', volume_id)
    try:
        s3_client.head_object(Bucket=bucket_name,
                              Key=(folder_name + '/'))  # check if folder exists, if not throws an exception
        add_folder_result = s3_client.put_object(Bucket=bucket_name, Key=(folder_name + '/'))
        logging.info(add_folder_result)
        return web.HTTPCreated()
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':  # folder doesn't exist
            logging.error(e)
            return web.HTTPBadRequest()
        else:
            logging.error(e)
            return web.HTTPBadRequest()


async def put_object(request: Request, volume_id: str, path_name: str, file_path: str,
                     object_name: Optional[str] = None):
    """Upload a file to an S3 bucket, if doesn't exist, throws error

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param file_path: Path to the file to upload
    :param path_name: path to the location of object
    :param object_name: S3 object name. If not specified then file_name is used

    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(
            (os.path.normpath(file_path)))  # only gets the last part of the path so identifiable info not included

    s3_client = await _get_client(request, 's3', volume_id)
    bucket_name = path_name.partition("/")[0]
    folder_name = path_name.partition("/")[2]
    try:
        s3_client.head_object(Bucket=bucket_name,
                              Key=folder_name + object_name)  # check if folder exists, if not throws an exception
        upload_response = s3_client.upload_file(file_path, bucket_name, folder_name + object_name)
        logging.info(upload_response)
        return web.HTTPCreated()
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':  # folder doesn't exist
            logging.error(e)
            return web.HTTPBadRequest()
        else:
            logging.error(e)
            return web.HTTPBadRequest()


def put_object_archive():
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/glacier.html
    """


async def transfer_object_within_account(request: Request, volume_id: str, object_path, new_path):
    """
    same as copy_object, but also deletes the object

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param object_path (str) gives the old location of the object, input as the bucket and key together
    :param new_path: (str) gives the new location to put the object
    """
    await copy_object(request, volume_id, object_path, new_path)
    await delete_object(request, volume_id, object_path)


def transfer_object_between_account():
    """
    https://markgituma.medium.com/copy-s3-bucket-objects-across-separate-aws-accounts-programmatically-323862d857ed
    """
    # TODO: use update_bucket_policy to set up "source" bucket policy correctly
    """
    {
    "Version": "2012-10-17",
    "Id": "Policy1546558291129",
    "Statement": [
        {
            "Sid": "Stmt1546558287955",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::<AWS_IAM_USER>"
            },
            "Action": [
              "s3:ListBucket",
              "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::<SOURCE_BUCKET>/",
            "Resource": "arn:aws:s3:::<SOURCE_BUCKET>/*"
        }
    ]
    }
    """
    # TODO: use update_bucket_policy to set up aws "destination" bucket policy
    """
    {
    "Version": "2012-10-17",
    "Id": "Policy22222222222",
    "Statement": [
        {
            "Sid": "Stmt22222222222",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                  "arn:aws:iam::<AWS_IAM_DESTINATION_USER>",
                  "arn:aws:iam::<AWS_IAM_LAMBDA_ROLE>:role/
                ]
            },
            "Action": [
                "s3:ListBucket",
                "s3:PutObject",
                "s3:PutObjectAcl"
            ],
            "Resource": "arn:aws:s3:::<DESTINATION_BUCKET>/",
            "Resource": "arn:aws:s3:::<DESTINATION_BUCKET>/*"
        }
    ]
    }
    """
    # TODO: code
    source_client = boto3.client('s3', "SOURCE_AWS_ACCESS_KEY_ID", "SOURCE_AWS_SECRET_ACCESS_KEY")
    source_response = source_client.get_object(Bucket="SOURCE_BUCKET", Key="OBJECT_KEY")
    destination_client = boto3.client('s3', "DESTINATION_AWS_ACCESS_KEY_ID", "DESTINATION_AWS_SECRET_ACCESS_KEY")
    destination_client.upload_fileobj(source_response['Body'], "DESTINATION_BUCKET",
                                      "FOLDER_LOCATION_IN_DESTINATION_BUCKET")


async def rename_object(request: Request, volume_id: str, object_path: str, new_name: str):
    """
    BOTO3, the copy and rename is the same
    https://medium.com/plusteam/move-and-rename-objects-within-an-s3-bucket-using-boto-3-58b164790b78
    https://stackoverflow.com/questions/47468148/how-to-copy-s3-object-from-one-bucket-to-another-using-python-boto3

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param object_path: (str) path to object, includes both bucket and key values
    :param new_name: (str) value to rename the object as, will only replace the name not the path. Use transfer object for that
    """
    # TODO: check if ACL stays the same and check existence
    try:
        s3_resource = await _get_resource(request, 's3', volume_id)
        copy_source = {'Bucket': object_path.partition("/")[0], 'Key': object_path.partition("/")[2]}
        bucket_name = object_path.partition("/")[0]
        old_name = object_path.rpartition("/")[2]
        s3_resource.meta.client.copy(copy_source, bucket_name,
                                     object_path.partition("/")[2].replace(old_name, new_name))
    except ClientError as e:
        logging.error(e)


def update_bucket_policy():
    """

    """


async def _get_client(request: Request, service_name: str, volume_id: str) -> Any:
    """
    Gets an AWS service client.  If the volume has no credentials, it uses the boto3 library to try and find them.

    :param request: the HTTP request (required).
    :param service_name: AWS service name (required).
    :param volume_id: the id string of a volume (required).
    :return: a Mongo client for the file system specified by the volume's file_system_name attribute. If no volume_id
    was provided, the return value will be the "default" Mongo client for the microservice found in the HEA_DB
    application-level property.
    :raise ValueError: if there is no volume with the provided volume id, the volume's file system does not exist,
    the volume's credentials were not found, or a necessary service is not registered.
    """

    if volume_id is not None:
        file_system, credentials = await get_file_system_and_credentials_from_volume(request, volume_id, AWSFileSystem)
        if credentials is None:
            return boto3.client(service_name)
        else:
            return boto3.client(service_name, aws_access_key_id=credentials.account,
                                aws_secret_access_key=credentials.password)
    else:
        raise ValueError('volume_id is required')


async def _get_resource(request: Request, service_name: str, volume_id: str) -> Any:
    """
    Gets an AWS resource. If the volume has no credentials, it uses the boto3 library to try and find them.

    :param request: the HTTP request (required).
    :param service_name: AWS service name (required).
    :param volume_id: the id string of a volume (required).
    :return: a Mongo client for the file system specified by the volume's file_system_name attribute. If no volume_id
    was provided, the return value will be the "default" Mongo client for the microservice found in the HEA_DB
    application-level property.
    :raise ValueError: if there is no volume with the provided volume id, the volume's file system does not exist,
    the volume's credentials were not found, or a necessary service is not registered.
    """

    if volume_id is not None:
        file_system, credentials = await get_file_system_and_credentials_from_volume(request, volume_id, AWSFileSystem)
        if credentials is None:
            return boto3.resource(service_name)
        else:
            return boto3.resource(service_name, aws_access_key_id=credentials.account,
                                  aws_secret_access_key=credentials.password)
    else:
        raise ValueError('volume_id is required')


async def _get_account(request: Request, volume_id: str) -> Optional[DesktopObjectDict]:
    """
    Gets the current user's AWS account dict associated with the provided volume_id.

    :param request: the HTTP request object (required).
    :param volume_id: the volume id (required).
    :return: the AWS account dict, or None if not found.
    """
    aws_object_dict = {}
    sts_client = await _get_client(request, 'sts', volume_id)
    iam_client = await _get_client(request, 'iam', volume_id)

    aws_object_dict['account_id'] = sts_client.get_caller_identity().get('Account')
    # aws_object_dict['alias'] = next(iam_client.list_account_aliases()['AccountAliases'], None)  # Only exists for IAM accounts.
    user = iam_client.get_user()['User']
    # aws_object_dict['account_name'] = user.get('UserName')  # Only exists for IAM accounts.
    aws_object_dict['id'] = user['UserId']
    aws_object_dict['owner'] = request.headers.get(SUB, NONE_USER)
    aws_object_dict['created'] = user['CreateDate']
    return aws_object_dict

# if __name__ == "__main__":
# print(get_account())
# print(post_bucket('richardmtest'))
# print(put_bucket("richardmtest"))
# print(get_all_buckets())
# print(get_all("richardmtest"))
# print(post_folder('richardmtest/temp'))
# print(put_folder("richardmtest/temp"))
# print(post_object(r'richardmtest/temp/', r'C:\Users\u0933981\IdeaProjects\heaserver\README.md'))
# print(put_object(r'richardmtest/temp/', r'C:\Users\u0933981\IdeaProjects\heaserver\README.md'))
# download_object(r'richardmtest/temp/README.md', r'C:\Users\u0933981\Desktop\README.md')
# rename_object(r'richardmtest/README.md', 'readme2.md')
# print(copy_object(r'richardmtest/temp/README.md', r'richardmtest/temp/README.md'))
# print(transfer_object_within_account(r'richardmtest/temp/readme2.md', r'timmtest/temp/README.md'))
# print(generate_presigned_url(r'richardmtest/temp/'))
# print(get_object_content(r'richardmtest/temp/README.md'))  # ["Body"].read())
# print(delete_object('richardmtest/temp/README.md'))
# print(delete_folder('richardmtest/temp'))
# print(delete_bucket_objects("richardmtest"))
# print(delete_bucket('richardmtest'))
# print("done")
