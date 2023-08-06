#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  1 13:30:43 2021

@author: mike
"""
import os
import numpy as np
import zstandard as zstd
import pandas as pd
import xarray as xr
import orjson
from tethys_data_models.dataset import Dataset, Station
# from data_models import Geometry, Dataset, DatasetBase, S3ObjectKey
import tethys_data_models as tdm
from tethysts.utils import get_object_s3, s3_client, read_json_zstd, read_pkl_zstd, chunk_filters
from tethys_utils.misc import make_run_date_key, write_json_zstd, path_date_parser
# from misc import make_run_date_key, write_json_zstd, write_pkl_zstd
from tethys_utils.processing import compare_xrs, process_station_summ, stats_for_dataset_metadata
# from processing import compare_xrs, process_station_summ, stats_for_dataset_metadata
from datetime import date, datetime
from tethysts import Tethys
from botocore import exceptions as bc_exceptions
from time import sleep
import pathlib
import concurrent.futures
import multiprocessing as mp

############################################
### Parameters



############################################
### Functions


def put_object_s3(s3, bucket, key, obj, metadata, content_type, retries=5):
    """

    """
    counter = retries
    while counter > 0:
        try:
            obj2 = s3.put_object(Bucket=bucket, Key=key, Body=obj, Metadata=metadata, ContentType=content_type)
            break
        except bc_exceptions.ConnectionClosedError as err:
            print(err)
            counter = counter - 1
            if counter == 0:
                raise err
            print('...trying again...')
            sleep(5)
        except bc_exceptions.ConnectTimeoutError as err:
            print(err)
            counter = counter - 1
            if counter == 0:
                raise err
            print('...trying again...')
            sleep(5)

    return obj2


def put_file_s3(s3, bucket, key, file_path, metadata, content_type, retries=5):
    """

    """
    with open(file_path, 'rb') as f:
        obj_out = put_object_s3(s3, bucket, key, f.read(), metadata, content_type, retries=retries)

    return obj_out


def put_interim_results_s3(s3, bucket, file_path, run_id, system_version=4, retries=5):
    """

    """
    path1 = pathlib.Path(file_path)
    ds_id, stn_id, start_date = path1.stem.split('.')[0].split('_')
    key = tdm.utils.key_patterns[system_version]['interim_results'].format(run_id=run_id, dataset_id=ds_id, station_id=stn_id, start_date=start_date)

    stats = os.stat(file_path)
    run_date = pd.Timestamp(round(stats.st_mtime), unit='s')
    run_date_key = make_run_date_key(run_date)

    _ = put_file_s3(s3, bucket, key, file_path, {'run_date': run_date_key}, 'application/zstd', retries=retries)

    return key


def list_objects_s3(s3, bucket, prefix, start_after='', delimiter='', continuation_token='', date_format=None):
    """
    Wrapper S3 function around the list_objects_v2 base function with a Pandas DataFrame output.

    Parameters
    ----------
    s3_client : boto3.client
        A boto3 client object
    bucket : str
        The S3 bucket.
    prefix : str
        Limits the response to keys that begin with the specified prefix.
    start_after : str
        The S3 key to start after.
    delimiter : str
        A delimiter is a character you use to group keys.
    continuation_token : str
        ContinuationToken indicates to S3 that the list is being continued on this bucket with a token.

    Returns
    -------
    DataFrame
    """
    if s3._endpoint.host == 'https://vault.revera.co.nz':
        js = []
        while True:
            js1 = s3.list_objects(Bucket=bucket, Prefix=prefix, Marker=start_after, Delimiter=delimiter)

            if 'Contents' in js1:
                js.extend(js1['Contents'])
                if 'NextMarker' in js1:
                    start_after = js1['NextMarker']
                else:
                    break
            else:
                break

    else:
        js = []
        while True:
            js1 = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, StartAfter=start_after, Delimiter=delimiter, ContinuationToken=continuation_token)

            if 'Contents' in js1:
                js.extend(js1['Contents'])
                if 'NextContinuationToken' in js1:
                    continuation_token = js1['NextContinuationToken']
                else:
                    break
            else:
                break

    if js:
        f_df1 = pd.DataFrame(js)[['Key', 'LastModified', 'ETag', 'Size']].copy()
        if isinstance(date_format, str):
            f_df1['KeyDate'] = pd.to_datetime(f_df1.Key.apply(lambda x: path_date_parser(x, date_format)), utc=True, errors='coerce').dt.tz_localize(None)
        f_df1['ETag'] = f_df1['ETag'].str.replace('"', '')
        f_df1['LastModified'] = pd.to_datetime(f_df1['LastModified']).dt.tz_localize(None)
    else:
        if isinstance(date_format, str):
            f_df1 = pd.DataFrame(columns=['Key', 'LastModified', 'ETag', 'Size', 'KeyDate'])
        else:
            f_df1 = pd.DataFrame(columns=['Key', 'LastModified', 'ETag', 'Size'])

    return f_df1


def list_object_versions_s3(s3_client, bucket, prefix, start_after='', delimiter=None, date_format=None):
    """
    Wrapper S3 function around the list_object_versions base function with a Pandas DataFrame output.

    Parameters
    ----------
    s3_client : boto3.client
        A boto3 client object
    bucket : str
        The S3 bucket.
    prefix : str
        Limits the response to keys that begin with the specified prefix.
    start_after : str
        The S3 key to start at.
    delimiter : str or None
        A delimiter is a character you use to group keys.

    Returns
    -------
    DataFrame
    """
    js = []
    while True:
        if isinstance(delimiter, str):
            js1 = s3_client.list_object_versions(Bucket=bucket, Prefix=prefix, KeyMarker=start_after, Delimiter=delimiter)
        else:
            js1 = s3_client.list_object_versions(Bucket=bucket, Prefix=prefix, KeyMarker=start_after)

        if 'Versions' in js1:
            js.extend(js1['Versions'])
            if 'NextKeyMarker' in js1:
                start_after = js1['NextKeyMarker']
            else:
                break
        else:
            break

    if js:
        f_df1 = pd.DataFrame(js)[['Key', 'VersionId', 'IsLatest', 'LastModified', 'ETag', 'Size']].copy()
        if isinstance(date_format, str):
            f_df1['KeyDate'] = pd.to_datetime(f_df1.Key.apply(lambda x: path_date_parser(x, date_format)), utc=True, errors='coerce').dt.tz_localize(None)
        f_df1['ETag'] = f_df1['ETag'].str.replace('"', '')
        f_df1['LastModified'] = pd.to_datetime(f_df1['LastModified']).dt.tz_localize(None)
    else:
        if isinstance(date_format, str):
            f_df1 = pd.DataFrame(columns=['Key', 'VersionId', 'IsLatest', 'LastModified', 'ETag', 'Size', 'KeyDate'])
        else:
            f_df1 = pd.DataFrame(columns=['Key', 'VersionId', 'IsLatest', 'LastModified', 'ETag', 'Size'])

    return f_df1


def put_remote_dataset(dataset, bucket, s3=None, connection_config=None, public_url=None, system_version=4):
    """

    """
    run_date_key = make_run_date_key()

    dataset_id = dataset['dataset_id']

    ## Get the stations agg
    stns_key = tdm.utils.key_patterns[system_version]['stations'].format(dataset_id=dataset_id)

    obj1 = get_object_s3(stns_key, bucket, s3, connection_config, public_url)
    stns = read_json_zstd(obj1)

    ## generate stats for the dataset metadata
    ds_stats = stats_for_dataset_metadata(stns)

    if dataset['result_type'] == 'time_series':
        if 'spatial_resolution' in ds_stats:
            ds_stats.pop('spatial_resolution')

    dataset.update(ds_stats)

    ## Add version number
    dataset.update({'system_version': system_version})

    ## Check and create dataset metadata
    ds4 = tdm.dataset.Dataset(**dataset)

    ds5 = orjson.loads(ds4.json(exclude_none=True))

    ## Write the object
    ds_obj = write_json_zstd(ds5)

    ds_key = tdm.utils.key_patterns[system_version]['dataset'].format(dataset_id=dataset_id)

    _ = put_object_s3(s3, bucket, ds_key, ds_obj, {'run_date': run_date_key}, 'application/json')

    return ds5


def get_remote_dataset(bucket, s3=None, connection_config=None, public_url=None, dataset_id=None, key=None, system_version=4):
    """

    """
    if isinstance(dataset_id, str):
        key = tdm.utils.key_patterns[system_version]['dataset'].format(dataset_id=dataset_id)
    elif not isinstance(key, str):
        raise ValueError('dataset_id must be passed or key must be passed.')

    try:
        obj1 = get_object_s3(key, bucket, s3, connection_config, public_url)
        rem_ds = read_json_zstd(obj1)
    except:
        rem_ds = None

    return rem_ds


def get_remote_station(bucket, s3=None, connection_config=None, public_url=None, dataset_id=None, station_id=None, key=None, system_version=4):
    """

    """
    if isinstance(dataset_id, str) and isinstance(station_id, str):
        key = tdm.utils.key_patterns[system_version]['station'].format(dataset_id=dataset_id, station_id=station_id)
    elif not isinstance(key, str):
        raise ValueError('dataset_id and station_id must be passed or key must be passed.')

    try:
        obj1 = get_object_s3(key, bucket, s3, connection_config, public_url)
        rem_stn = read_json_zstd(obj1)
    except:
        rem_stn = None

    return rem_stn


def get_remote_results_chunks(bucket, s3=None, connection_config=None, public_url=None, dataset_id=None, key=None, system_version=4):
    """

    """
    if isinstance(dataset_id, str):
        key = tdm.utils.key_patterns[system_version]['results_chunks'].format(dataset_id=dataset_id)
    elif not isinstance(key, str):
        raise ValueError('dataset_id must be passed or key must be passed.')

    try:
        obj1 = get_object_s3(key, bucket, s3, connection_config, public_url)
        rem_ds = read_json_zstd(obj1)
    except:
        rem_ds = None

    return rem_ds



# def put_remote_station(s3, bucket, station, run_date=None, system_version=4):
#     """

#     """
#     run_date_key = make_run_date_key(run_date)

#     dataset_id = station['dataset_id']
#     station_id = station['station_id']

#     stn4 = Station(**station)

#     stn5 = orjson.loads(stn4.json(exclude_none=True))

#     stn_obj = write_json_zstd(stn5)

#     stn_key = tdm.utils.key_patterns[system_version]['station'].format(dataset_id=dataset_id, station_id=station_id)

#     _ = put_object_s3(s3, bucket, stn_key, stn_obj, {'run_date': run_date_key}, 'application/json')

#     return stn5


def put_remote_agg_stations(version_dict, dataset_id, bucket, connection_config, public_url=None, threads=30, system_version=4):
    """

    """
    stn_key = tdm.utils.key_patterns[system_version]['station']
    stn_prefix = stn_key.split('{station_id}')[0].format(dataset_id=dataset_id)

    s3 = s3_client(connection_config, max_pool_connections=threads)

    if system_version == 2:
        list1 = list_objects_s3(s3, bucket, stn_prefix)
    elif system_version >= 3:
        list1 = list_objects_s3(s3, bucket, stn_prefix, delimiter='/')
    else:
        raise ValueError('Wrong object structure version.')

    list2 = list1[list1.Key.str.contains('station.json.zst')].copy()

    if not list2.empty:

        ## Get all of the result chunks from the individual stations
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []

            for key in list2['Key'].tolist():
                f = executor.submit(get_remote_station, s3=s3, bucket=bucket, key=key, system_version=system_version)
                futures.append(f)

            runs = concurrent.futures.wait(futures)

        stn_list = [r.result() for r in runs[0]]

        ## Separate the results chunks from the stations
        results_chunks = []
        _ = [results_chunks.extend(s.pop('results_chunks')) for s in stn_list]

        ## Get the versions
        rv_key = tdm.utils.key_patterns[system_version]['results_versions'].format(dataset_id=dataset_id)

        v_obj1 = get_object_s3(rv_key, bucket, s3=s3, public_url=public_url, counter=1)

        if v_obj1 is not None:
            v1 = read_json_zstd(v_obj1)
            v2 = v1['results_versions']

            version_list = []
            for v in v2:
                if version_dict['version_date'] == v['version_date']:
                    version_list.append(version_dict)
                else:
                    version_list.append(v)
        else:
            version_list = [version_dict]

        ## Combine version data with chunks
        rv_model = tdm.dataset.ResultVersionGroup(results_versions=version_list, results_chunks=results_chunks)
        rv_dict = rv_model.dict(exclude_none=True)

        ## Save files
        # Stations
        stns_obj = write_json_zstd(stn_list)

        run_date_key = make_run_date_key()

        agg_stn_key = tdm.utils.key_patterns[system_version]['stations']

        stns_key = agg_stn_key.format(dataset_id=dataset_id)

        _ = put_object_s3(s3, bucket, stns_key, stns_obj, {'run_date': run_date_key}, 'application/json')

        # Results object keys
        rv_obj = write_json_zstd(rv_dict)

        _ = put_object_s3(s3, bucket, rv_key, rv_obj, {'run_date': run_date_key}, 'application/json')

        return stn_list, results_chunks
    else:
        print('There are no stations files in the database.')
        return None, None


def put_remote_agg_datasets(bucket, connection_config, public_url=None, threads=30, system_version=4):
    """

    """
    ds_key = tdm.utils.key_patterns[system_version]['dataset']

    ds_prefix = ds_key.split('{dataset_id}')[0]

    s3 = s3_client(connection_config, max_pool_connections=threads)

    if system_version == 2:
        list1 = list_objects_s3(s3, bucket, ds_prefix)
    elif system_version >= 3:
        list1 = list_objects_s3(s3, bucket, ds_prefix, delimiter='/')
    else:
        raise ValueError('Wrong object structure version.')

    list2 = list1[list1.Key.str.contains('dataset.json.zst')].copy()

    if not list2.empty:

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []

            for key in list2['Key'].tolist():
                f = executor.submit(get_remote_dataset, s3=s3, bucket=bucket, public_url=public_url, key=key, system_version=system_version)
                futures.append(f)

            runs = concurrent.futures.wait(futures)

        ds_list = [r.result() for r in runs[0]]

        dss_obj = write_json_zstd(ds_list)

        run_date_key = make_run_date_key()
        dss_key = tdm.utils.key_patterns[system_version]['datasets']

        _ = put_object_s3(s3, bucket, dss_key, dss_obj, {'run_date': run_date_key}, 'application/json')

    return ds_list


def compare_datasets_from_s3(connection_config, bucket, new_data, add_old=False, last_run_date_key=None, public_url=None, version=3):
    """
    Parameters
    ----------
    connection_config : dict
        A dictionary of the connection info necessary to establish an S3 connection.
    bucket : str
        The S3 bucket.
    new_data : xr.Dataset
        The new data that should be compared to existing data in S3.
    add_old : bool
        Should the data in the S3 be added to the output?
    last_run_date_key : str
        Specify the last run key instead of having the function figure it out. The function will do a check to make sure that the key exists.
    public_url : str
        Optional if there is a public URL to the object instead of using the S3 API directly.

    Returns
    -------
    xr.Dataset
        Of the data that should be updated.
    """
    ## Determine the parameter, station_id, and dataset_id
    vars1 = list(new_data.variables)
    dataset = [new_data[v].attrs for v in vars1 if 'dataset_id' in new_data[v].attrs][0]
    dataset_id = dataset['dataset_id']
    # result_type = dataset['result_type']
    station_id = str(new_data.squeeze()['station_id'].values)

    key_dict = {'dataset_id': dataset_id, 'station_id': station_id}

    base_key_pattern = tdm.utils.key_patterns[version]['results']

    ## Get list of keys
    if isinstance(last_run_date_key, str):
        key_dict.update({'run_date': last_run_date_key})
        last_key = base_key_pattern.format(**key_dict)
    else:
        last_key = None

    ## Get previous data and compare
    if isinstance(public_url, str):
        conn_config = public_url
    else:
        conn_config = connection_config

    if isinstance(last_key, str):
        # last_key = last_key1.iloc[0]['Key']
        p_old_one = get_object_s3(last_key, conn_config, bucket, 'zstd')
        xr_old_one = xr.load_dataset(p_old_one)

        up1 = compare_xrs(xr_old_one, new_data, add_old=add_old)
    else:
        # print('No prior data found in S3. All data will be returned.')
        up1 = new_data.copy()

    return up1


# def update_results_s3(processing_code, data_dict, run_date_dict, remote, threads=30, public_url=None, version=3):
#     """
#     Parameters
#     ----------
#     processing_code : int
#         The processing code to determine how the input data should be processed.
#     data_dict : dict of lists
#         A dictionary with the keys as the dataset_ids and teh values as lists of zstd compressed xr.Datasets.
#     remote : dict
#         Dict of a connection_config and bucket:
#         conn_config : dict
#             A dictionary of the connection info necessary to establish an S3 connection.
#         bucket : str
#             The S3 bucket.
#     threads : int
#         The number of threads to use to process the data.
#     public_url : str
#         Optional if there is a public URL to the object instead of using the S3 API directly.

#     Returns
#     -------
#     None

#     """
#     ### Parameters
#     conn_config = remote['connection_config']
#     bucket = remote['bucket']

#     if processing_code in [2, 3, 6]:
#         add_old = True
#     elif processing_code in [1, 4, 5]:
#         add_old = False
#     else:
#         raise ValueError('processing_code does not exist.')

#     if processing_code in [4, 5]:
#         no_comparison = True
#     else:
#         no_comparison = False

#     ### Run update

#     s3 = s3_client(conn_config, threads)

#     for ds_id, results in data_dict.items():
#         print('--dataset_id: ' + ds_id)

#         if len(results) > 0:

#             run_date_key = run_date_dict[ds_id]

#             # Create the Key info dict
#             prefix = tdm.utils.key_patterns[version]['results'].split('{station_id}')[0].format(dataset_id=ds_id)

#             keys1 = list_objects_s3(s3, bucket, prefix)
#             obj_df1 = keys1[keys1.Key.str.contains('results.nc')].copy()
#             # obj_df1['dataset_id'] = obj_df1['Key'].apply(lambda x: x.split('/')[2])
#             obj_df1['station_id'] = obj_df1['Key'].apply(lambda x: x.split('/')[3])

#             last_date1 = obj_df1.groupby(['station_id'])['KeyDate'].last().reset_index()


#             def update_result(result):
#                 """

#                 """
#                 ## Process data
#                 try:
#                     new1 = xr.load_dataset(read_pkl_zstd(result, False))
#                 except:
#                     print('Data could not be opened')
#                     return None

#                 stn_id = str(new1.squeeze()['station_id'].values)
#                 # print('station_id: ' + stn_id)

#                 vars1 = list(new1.variables)
#                 parameter = [v for v in vars1 if 'dataset_id' in new1[v].attrs][0]
#                 result_attrs = new1[parameter].attrs.copy()

#                 ds_id = result_attrs['dataset_id']
#                 mod_date_key = new1.attrs['history'].split(':')[0]

#                 if no_comparison:
#                     up1 = new1
#                 else:
#                     last_date_key_df = last_date1[last_date1['station_id'] == stn_id]
#                     if last_date_key_df.empty:
#                         last_date_key = None
#                     else:
#                         last_date_key = make_run_date_key(last_date_key_df['KeyDate'].iloc[0])

#                     up1 = compare_datasets_from_s3(conn_config, bucket, new1, add_old=add_old, last_run_date_key=last_date_key, public_url=public_url, version=version)

#                 ## Save results
#                 if isinstance(up1, xr.Dataset) and (len(up1[parameter].time) > 0):

#                     # print('Save results')
#                     key_dict = {'dataset_id': ds_id, 'station_id': stn_id, 'run_date': run_date_key}

#                     new_key = tdm.utils.key_patterns[version]['results'].format(**key_dict)

#                     cctx = zstd.ZstdCompressor(level=1)
#                     c_obj = cctx.compress(up1.to_netcdf())

#                     obj_resp = put_object_s3(s3, bucket, new_key, c_obj, {'run_date': mod_date_key}, 'application/zstd')

#                     ## Process stn data
#                     # print('Save station data')

#                     ## Process object key infos
#                     stn_obj_df1 = obj_df1[obj_df1['station_id'] == stn_id].drop(['LastModified', 'station_id'], axis=1).copy()
#                     keys = stn_obj_df1['Key'].unique()
#                     new_key_info = [new_key, obj_resp['ResponseMetadata']['HTTPHeaders']['etag'].replace('"', ''), len(c_obj), pd.Timestamp(run_date_key).tz_localize(None)]

#                     if new_key in keys:
#                         stn_obj_df1[stn_obj_df1['Key'] == new_key] = new_key_info
#                     else:
#                         stn_obj_df1.loc[len(stn_obj_df1)] = new_key_info

#                     info1 = [S3ObjectKey(key=row['Key'], bucket=bucket, content_length=row['Size'], etag=row['ETag'], run_date=row['KeyDate']) for i, row in stn_obj_df1.iterrows()]

#                     ## Final station processing and saving
#                     stn_m = process_station_summ(up1, info1, mod_date=mod_date_key)

#                     up_stns = put_remote_station(s3, bucket, stn_m, run_date=mod_date_key, version=version)

#                 else:
#                     print('No new data to update')

#                 ## Get rid of big objects
#                 new1 = None
#                 up1 = None


#             ## Run the threadpool
#             # output = ThreadPool(threads).imap_unordered(update_result, results)
#             with ThreadPool(threads) as pool:
#                 output = pool.map(update_result, results)
#                 pool.close()
#                 pool.join()


def put_result(s3, bucket, results_path, system_version=4):
    """

    """
    file_name = os.path.split(results_path)[1]
    ds_id, version_date_key, stn_id, chunk_id, hash1, _ = file_name.split('_')

    key_name = tdm.utils.key_patterns[system_version]['results'].format(dataset_id=ds_id, version_date=version_date_key, station_id=stn_id, chunk_id=chunk_id)

    metadata = {'chunk_hash': hash1}

    _ = put_file_s3(s3, bucket, key_name, results_path, metadata, 'application/zstd', retries=5)

    return key_name


def put_station(s3, bucket, stn_path, system_version=4):
    """

    """
    file_name = os.path.split(stn_path)[1]
    ds_id, stn_id, _ = file_name.split('_')

    key_name = tdm.utils.key_patterns[system_version]['station'].format(dataset_id=ds_id, station_id=stn_id)

    metadata = {}

    _ = put_file_s3(s3, bucket, key_name, stn_path, metadata, 'application/zstd', retries=5)

    return key_name


def delete_result_objects_s3(conn_config, bucket, dataset_ids=None, keep_last=10, threads=50, version=3):
    """
    Function to delete Tethys result objects including all object versions.

    Parameters
    ----------
    conn_config : dict
        A dictionary of the connection info necessary to establish an S3 connection.
    bucket : str
        The s3 bucket.
    dataset_ids : list, str, or None
        The specific datasets that should have the results objects removed. None will remove results objects from all datasets in the bucket.
    keep_last : int
        That last number of runs that should be kept. E.g. a value of 4 will kepp the last 4 runs and remove all prior runs.
    threads : int
        The number of concurrent threads to use when aggregating the stations and datasets.

    Returns
    -------
    list of keys deleted
    """
    s3 = s3_client(conn_config, threads)

    if isinstance(dataset_ids, str):
        dataset_ids = [dataset_ids]

    prefix = tdm.utils.key_patterns[version]['results'].split('{dataset_id}')[0]

    obj_list = list_object_versions_s3(s3, bucket, prefix)

    obj_list1 = obj_list[obj_list.KeyDate.notnull()].copy()
    key_split = obj_list1['Key'].str.split('/')
    obj_list1['dataset_id'] = key_split.apply(lambda x: x[2])
    obj_list1['station_id'] = key_split.apply(lambda x: x[3])

    if isinstance(dataset_ids, list):
        obj_list1 = obj_list1[obj_list1['dataset_id'].isin(dataset_ids)].copy()

    ## Get the keys to the objects that should be removed
    obj_list2 = obj_list1.groupby(['dataset_id', 'station_id'])

    rem_keys = []
    for i, row in obj_list2:
        rem1 = row.sort_values('KeyDate', ascending=False).iloc[keep_last:]
        for i2, row2 in rem1.iterrows():
            rem_keys.extend([{'Key': row2['Key'], 'VersionId': row2['VersionId']}])

    if len(rem_keys) > 0:
        ## Split them into 1000 key chunks
        rem_keys_chunks = np.array_split(rem_keys, int(np.ceil(len(rem_keys)/1000)))

        ## Run through and delete the objects...
        for keys in rem_keys_chunks:
            resp = s3.delete_objects(Bucket=bucket, Delete={'Objects': keys.tolist(), 'Quiet': True})

    print(str(len(rem_keys)) + ' objects removed')
    print('Updating stations and dataset json files...')

    dataset_list = obj_list1['dataset_id'].unique().tolist()

    for ds in dataset_list:
        ds_stations = put_remote_agg_stations(s3, bucket, ds, threads)

    ### Aggregate all datasets for the bucket
    ds_all = put_remote_agg_datasets(s3, bucket, threads)

    return rem_keys


# def process_results_versions(dataset_list, connection_config, bucket, version=4, version_date=None, version_data=None):
#     """
#     Function to process the run date keys for all datasets for the extraction. These are specific to each processing_code.

#     Parameters
#     ----------
#     processing_code : int
#         The processing code to determine how the input data should be processed.
#     dataset_list : list of dict
#         The list of datasets, which is the output of the process_datasets function.
#     remote : dict
#         Dict of a connection_config and bucket:
#         conn_config : dict
#             A dictionary of the connection info necessary to establish an S3 connection.
#         bucket : str
#             The S3 bucket.
#     run_date : str, datetime, date, pd.Timestamp, or None
#         The run_date to use for processing. If None, then the run_date will be generated.
#     save_interval_hours : int
#         The frequency by which the datasets should have run dates saved as in Tethys. Essentially the question is, how frequently do you want to keep a record of the data changes? This value is in hours and the default is 2 weeks. This does not effect datasets with processing_code 3 as the run_date always stays the same. A processing_code of 4 oe 5 always creates a new run_date.

#     Returns
#     -------
#     run_date_dict : dict of str
#     """
#     if isinstance(version_date, (str, datetime, date, pd.Timestamp)):
#         run_date1 = pd.Timestamp(version_date)
#     else:
#         run_date1 = pd.Timestamp.today(tz='utc').tz_localize(None).round('s')

#     run_date_dict = {}
#     for ds in dataset_list:
#         dataset_id = ds['dataset_id']

#         ## Get last result dates
#         try:
#             key1 = tdm.utils.key_patterns[version]['stations'].format(dataset_id=dataset_id)
#             obj1 = get_object_s3(key1, connection_config, bucket, counter=0)
#             rok1 = read_json_zstd(obj1)
#             if version <= 3:
#                 rok1b = [r['results_object_key'] if isinstance(r['results_object_key'], dict) else r['results_object_key'][-1] for r in rok1]
#                 rok2 = pd.DataFrame(rok1b)
#                 rok2['run_date'] = pd.to_datetime(rok2['run_date'])
#                 obj_list = rok2.dropna(subset=['run_date'])
#                 last_run_date = obj_list['run_date'].max()
#             else:
#                 rok1b = [r['result_versions'] for r in rok1]
#                 rok2 = pd.DataFrame(rok1b)
#                 rok2['version_date'] = pd.to_datetime(rok2['version_date'])
#                 obj_list = rok2.dropna(subset=['version_date'])
#                 last_run_date = obj_list['version_date'].max()
#         except:
#             last_run_date = run_date1

#         if processing_code in [3]:
#             last_run_date_key = last_run_date.strftime('%Y%m%dT%H%M%SZ')
#         elif processing_code in [4, 5]:
#             last_run_date_key = run_date1.strftime('%Y%m%dT%H%M%SZ')
#         elif processing_code in [1, 2, 6]:
#             if last_run_date < (run_date1 - pd.DateOffset(hours=save_interval_hours) + pd.DateOffset(minutes=5)):
#                 last_run_date_key = run_date1.strftime('%Y%m%dT%H%M%SZ')
#             else:
#                 last_run_date_key = last_run_date.strftime('%Y%m%dT%H%M%SZ')
#         else:
#             raise ValueError('processing_code does not exist.')

#         run_date_dict.update({dataset_id: last_run_date_key})

#     return run_date_dict


def process_results_versions(dataset_list, bucket, s3=None, connection_config=None, public_url=None, version_data=None, system_version=4):
    """
    Function to process the run date keys for all datasets for the extraction. These are specific to each processing_code.

    Parameters
    ----------
    processing_code : int
        The processing code to determine how the input data should be processed.
    dataset_list : list of dict
        The list of datasets, which is the output of the process_datasets function.
    remote : dict
        Dict of a connection_config and bucket:
        conn_config : dict
            A dictionary of the connection info necessary to establish an S3 connection.
        bucket : str
            The S3 bucket.
    run_date : str, datetime, date, pd.Timestamp, or None
        The run_date to use for processing. If None, then the run_date will be generated.


    Returns
    -------
    run_date_dict : dict of str
    """
    mod_date = pd.Timestamp.today(tz='utc').tz_localize(None).round('s')

    if isinstance(version_data, dict):
        if isinstance(version_data['version_date'], str):
            version_data['version_date'] = pd.Timestamp(version_data['version_date'])

        version_data['modified_date'] = mod_date

        version_dict = {}
        for ds in dataset_list:
            dataset_id = ds['dataset_id']
            vd = version_data.copy()
            vd['dataset_id'] = dataset_id
            version_m = tdm.dataset.ResultVersion(**vd)
            version_dict[dataset_id] = orjson.loads(version_m.json(exclude_none=True))

    else:
        version_dict = {'modified_date': mod_date}
        for ds in dataset_list:
            dataset_id = ds['dataset_id']
            vd = {'dataset_id': dataset_id}

            ## Get last result dates
            ## I probably need to make variants for versions 2 and 3
            if system_version == 4:
                try:
                    key1 = tdm.utils.key_patterns[system_version]['results_versions'].format(dataset_id=dataset_id)
                    obj1 = get_object_s3(key1, bucket, s3, connection_config, public_url, counter=1)
                    rok1 = read_json_zstd(obj1)

                    version_date = rok1[-1]['version_date']
                    vd['version_date'] = version_date
                    version_m = tdm.dataset.ResultVersion(**vd)
                    version_dict[dataset_id] = orjson.loads(version_m.json(exclude_none=True))
                except:
                    run_date1 = pd.Timestamp.today(tz='utc').tz_localize(None).round('s')
                    vd['version_date'] = run_date1
                    version_m = tdm.dataset.ResultVersion(**vd)
                    version_dict[dataset_id] = orjson.loads(version_m.json(exclude_none=True))
            else:
                raise NotImplementedError('I need to make variants for versions 2 and 3.')

    return version_dict


# def reprocess_datasets(dataset, conn_config, bucket, public_url, threads=20):
#     """

#     """
#     dataset_id = dataset['dataset_id']
#     tethys = Tethys([{'connection_config': public_url, 'bucket': bucket, 'version': 2}])

#     stns = tethys.get_stations(dataset_id, results_object_keys=True)

#     bad_stns = [s for s in stns if 'time_range' not in s]

#     prefix = tdm.utils.key_patterns[2]['results'].split('{station_id}')[0].format(dataset_id=dataset_id)

#     s3 = s3_client(conn_config)
#     keys1 = list_objects_s3(s3, bucket, prefix)
#     obj_df1 = keys1[keys1.Key.str.contains('results.nc')].copy()
#     obj_df1['station_id'] = obj_df1['Key'].apply(lambda x: x.split('/')[3])


#     def reprocess_dataset(stn):
#         """

#         """
#         stn_id = stn['station_id']
#         run_dates = tethys.get_run_dates(dataset_id, stn['station_id'])

#         for run_date in run_dates:

#         # run_date = stn['results_object_key']['run_date']
#             run_date_key = make_run_date_key(run_date)
#             mod_date_key = make_run_date_key()
#             up1 = tethys.get_results(dataset_id, stn_id, run_date=run_date, output='Dataset')

#             key_dict = {'dataset_id': dataset_id, 'station_id': stn_id, 'run_date': run_date_key}

#             new_key = tdm.utils.key_patterns[2]['results'].format(**key_dict)

#             cctx = zstd.ZstdCompressor(level=1)
#             c_obj = cctx.compress(up1.to_netcdf())

#             obj_resp = put_object_s3(s3, bucket, new_key, c_obj, {'run_date': mod_date_key}, 'application/zstd')

#             ## Process stn data
#             # print('Save station data')

#         ## Process object key infos
#         stn_obj_df1 = obj_df1[obj_df1['station_id'] == stn_id].drop(['LastModified', 'station_id'], axis=1).copy()
#         keys = stn_obj_df1['Key'].unique()
#         new_key_info = [new_key, obj_resp['ResponseMetadata']['HTTPHeaders']['etag'].replace('"', ''), len(c_obj), pd.Timestamp(run_date_key).tz_localize(None)]

#         if new_key in keys:
#             stn_obj_df1[stn_obj_df1['Key'] == new_key] = new_key_info
#         else:
#             stn_obj_df1.loc[len(stn_obj_df1)] = new_key_info

#         info1 = [S3ObjectKey(key=row['Key'], bucket=bucket, content_length=row['Size'], etag=row['ETag'], run_date=row['KeyDate']) for i, row in stn_obj_df1.iterrows()]

#         ## Final station processing and saving
#         stn_m = process_station_summ(up1, info1, mod_date=mod_date_key)

#         up_stns = put_remote_station(s3, bucket, stn_m, run_date=mod_date_key, version=2)


#     if len(bad_stns) > 0:
#         print('Updating results and stations...')
#         output = ThreadPool(threads).map(reprocess_dataset, bad_stns)

#         print('Updating aggregates...')

#         ds_stations = put_remote_agg_stations(s3, bucket, dataset_id, threads*2, version=2)
#         if ds_stations is not None:
#             ds_new = put_remote_dataset(s3, bucket, dataset, ds_stations, version=2)

#         # Aggregate all datasets for the bucket
#         ds_all = put_remote_agg_datasets(s3, bucket, threads*2, version=2)

#     else:
#         print('Nothing to update.')

#     print('Finished')


def determine_results_chunks_diffs(source_paths, remote):
    """

    """
    paths1 = []
    for p in source_paths:
        ds_id, version_date1, stn_id, chunk_id, hash_id, _ = os.path.split(p)[1].split('_')
        paths1.append([p, ds_id, version_date1, stn_id, chunk_id, hash_id])

    paths2 = pd.DataFrame(paths1, columns=['file_path', 'dataset_id', 'version_date', 'station_id', 'chunk_id', 'chunk_hash'])
    paths2['version_date'] = pd.to_datetime(paths2['version_date']).dt.tz_localize(None)

    tethys = Tethys([remote])
    datasets = tethys._datasets

    diffs_list = []
    for ds_id, g in paths2.groupby('dataset_id'):
        # print(ds_id)
        if ds_id in datasets:
            _ = tethys.get_versions(ds_id)
            vd_max = g.version_date.max()

            chunks1 = []
            for stn_id, c in tethys._results_chunks[ds_id].items():
                # print(stn_id)
                chunks2 = chunk_filters(c, version_date=vd_max)
                chunks1.extend(chunks2)

            chunks_df = pd.DataFrame(chunks1).drop(['version_date', 'content_length', 'height', 'chunk_day'], axis=1).rename(columns={'chunk_hash': 'original_chunk_hash'})

            combo1 = pd.merge(g, chunks_df, on=['dataset_id', 'station_id', 'chunk_id'], indicator=True, how='outer')
            combo1 = combo1[combo1['_merge'].isin(['both', 'left_only'])]
            combo1 = combo1[combo1['chunk_hash'] != combo1['original_chunk_hash']].copy()

            diffs_list.append(combo1.drop(['key', 'original_chunk_hash', '_merge'], axis=1))
        else:
            diffs_list.append(g)

    combo2 = pd.concat(diffs_list)

    return combo2








# for ds in titan.dataset_list:
#     reprocess_datasets(ds['dataset_id'], conn_config, bucket, public_url, threads=20)





# for result in results[2500:]:
#     new1 = xr.load_dataset(read_pkl_zstd(result, False))
#
#     stn_id = str(new1.squeeze()['station_id'].values)
#     print('station_id: ' + stn_id)
#
#     vars1 = list(new1.variables)
#     parameter = [v for v in vars1 if 'dataset_id' in new1[v].attrs][0]
#     result_attrs = new1[parameter].attrs.copy()
#
#     ds_id = result_attrs['dataset_id']
#     mod_date_key = new1.attrs['history'].split(':')[0]
#
#     if no_comparison:
#         up1 = new1
#     else:
#         last_date_key_df = last_date1[last_date1['station_id'] == stn_id]
#         if last_date_key_df.empty:
#             last_date_key = None
#         else:
#             last_date_key = make_run_date_key(last_date_key_df['KeyDate'].iloc[0])
#
#         up1 = compare_datasets_from_s3(conn_config, bucket, new1, add_old=add_old, last_run_date_key=last_date_key, public_url=public_url)
#
#     ## Save results
#     if isinstance(up1, xr.Dataset) and (len(up1[parameter].time) > 0):
#
#         # print('Save results')
#         key_dict = {'dataset_id': ds_id, 'station_id': stn_id, 'run_date': run_date_key}
#
#         new_key = tdm.utils.key_patterns['results'].format(**key_dict)
#
#         cctx = zstd.ZstdCompressor(level=1)
#         c_obj = cctx.compress(up1.to_netcdf())
#
#         obj_resp = s3.put_object(Body=c_obj, Bucket=bucket, Key=new_key, ContentType='application/zstd', Metadata={'run_date': mod_date_key})
#
#         ## Process stn data
#         # print('Save station data')
#
#         ## Process object key infos
#         stn_obj_df1 = obj_df1[obj_df1['station_id'] == stn_id].drop(['LastModified', 'station_id'], axis=1).copy()
#         keys = stn_obj_df1['Key'].unique()
#         new_key_info = [new_key, obj_resp['ResponseMetadata']['HTTPHeaders']['etag'].replace('"', ''), len(c_obj), pd.Timestamp(run_date_key).tz_localize(None)]
#
#         if new_key in keys:
#             stn_obj_df1[stn_obj_df1['Key'] == new_key] = new_key_info
#         else:
#             stn_obj_df1.loc[len(stn_obj_df1)] = new_key_info
#
#         info1 = [S3ObjectKey(key=row['Key'], bucket=bucket, content_length=row['Size'], etag=row['ETag'], run_date=row['KeyDate']) for i, row in stn_obj_df1.iterrows()]
#
#         ## Final station processing and saving
#         stn_m = process_station_summ(ds_id, stn_id, up1, info1, mod_date=mod_date_key)
#
#         up_stns = put_remote_station(s3, bucket, stn_m, run_date=mod_date_key)
#
#     else:
#         print('No new data to update')
#
#     ## Get rid of big objects
#     new1 = None
#     up1 = None
