#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 13:39:58 2021

@author: mike
"""
import os
import numpy as np
import xarray as xr
import pandas as pd
import tethys_utils as tu
from tethysts.utils import s3_client, get_object_s3, read_json_zstd, b2_public_key_pattern, read_pkl_zstd
import tethys_data_models as tdm
from typing import List, Optional, Dict, Union
# import boto3
# import botocore
from botocore import exceptions as bc_exceptions
import requests
import uuid
from cryptography.fernet import Fernet
import pandas as pd
from pydantic import HttpUrl
import concurrent.futures
import copy
from shapely import wkb, wkt, geometry
import pathlib
import stat
import dask
from hashlib import blake2b
import glob
from datetime import date, datetime
import multiprocessing as mp
import pyproj

##############################################
### Parameters

b2_dl_by_id = 'https://b2.tethys-ts.xyz/b2api/v1/b2_download_file_by_id?fileId={obj_id}'


preprocessed_dir = 'preprocessed_data'
previous_dir = 'previous_results'
final_dir = 'final_results'

preprocessed_file_str = '{ds_id}_{file_id}.nc.zst'
interim_file_str = '{ds_id}_{stn_id}_{date}.nc'

base_encoding = {'lon': {'dtype': 'int32', '_FillValue': -999999, 'scale_factor': 1e-07},
'lat': {'dtype': 'int32', '_FillValue': -999999, 'scale_factor': 1e-07},
'altitude': {'dtype': 'int32', '_FillValue': -9999, 'scale_factor': 0.001},
'time': {'_FillValue': -99999999, 'units': 'days since 1970-01-01 00:00:00'},
'height': {'dtype': 'int16', '_FillValue': -9999}}

dask.config.set(**{'array.slicing.split_large_chunks': False})

###############################################
### Helper functions



def save_chunks(chunks_list, output_path):
    """

    """
    for c in chunks_list:
        chunk_json = tdm.dataset.ChunkID(height=int(c.height.values[0] * 1000), start_date=int(c.attrs['start_date'])).json(exclude_none=True).encode('utf-8')
        chunk_id = blake2b(chunk_json, digest_size=12).hexdigest()
        stn_id = str(c.station_id.values[0])
        file_path = os.path.join(output_path, stn_id + '_' + chunk_id + '.nc.zst')

        b = c.copy().load()

        obj1 = tu.misc.write_pkl_zstd(b.to_netcdf(), file_path)

        b.close()
        del b
        del obj1


def multi_save_dataset_stations(nc_paths, block_length, block_length_factor: int = 10, compression='zstd', remove_station_data=True, max_workers=3):
    """

    """
    if isinstance(nc_paths, str):
        nc_paths1 = glob.glob(nc_paths)
    elif isinstance(nc_paths, list):
        nc_paths1 = nc_paths

    ## Iterate through files
    if max_workers <= 1:

        nc_paths = []
        for nc_path in nc_paths1:
            new_paths0 = tu.processing.save_dataset_stations(nc_path, block_length * block_length_factor, compression=compression, remove_station_data=remove_station_data)
            nc_paths.append(new_paths0)
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
            futures = []
            for nc_path in nc_paths1:
                f = executor.submit(tu.processing.save_dataset_stations, nc_path, block_length * block_length_factor, compression=compression, remove_station_data=remove_station_data)
                futures.append(f)
            runs = concurrent.futures.wait(futures)

        new_paths = [r.result() for r in runs[0]]

    ## process output
    new_paths1 = []
    for new_path in new_paths:
        new_paths1.extend(new_path)

    new_paths1.sort()

    return new_paths1


def estimate_time_interval_accurate(data, block_length, null_grid=None, max_mb=2):
    """

    """
    ## Get the dimension data
    dims = dict(data.dims)

    ## Test requested block_length
    chunks_list = tu.processing.chunk_data(data, block_length=block_length, time_interval=None, null_grid=null_grid)

    dim_sizes = np.array([np.prod(list(c.dims.values())) for c in chunks_list])
    max_dim_index = np.argsort(dim_sizes)[-10:]
    sum_dim_objs = np.sum(dim_sizes[max_dim_index])

    sum_chunks = 0
    for i in max_dim_index:
        chunk = chunks_list[i].copy().load()
        obj_len = len(tu.misc.write_pkl_zstd(chunk.to_netcdf()))

        sum_chunks += obj_len

        chunk.close()
        del chunk

    dim_per_mb = int(sum_dim_objs/(sum_chunks * 0.000001))

    if 'geometry' in dims:
        geo_sizes = np.array([c.dims['geometry'] for c in chunks_list])
    else:
        geo_sizes = np.array([c.dims['lon'] * c.dims['lat'] for c in chunks_list])

    max_geo_size = np.max(geo_sizes)

    times_per_mb = (dim_per_mb/max_geo_size)

    ## Calc time_interval
    times1 = pd.to_datetime(data['time'].values)
    days = times1.floor('D').drop_duplicates()
    times_per_day = len(times1)/len(days)

    days_per_mb = times_per_mb/times_per_day

    days_per_chunk = int(days_per_mb * max_mb)

    ## Test final parameters
    chunks_list = tu.processing.chunk_data(data, block_length=block_length, time_interval=days_per_chunk, null_grid=null_grid)

    n_chunks = len(chunks_list)

    _ = [c.close() for c in chunks_list]
    del chunks_list

    output_dict = {'time_interval': days_per_chunk,
                   'n_geometries_per_station': max_geo_size,
                   'n_chunks': n_chunks,
                   'values_per_mb': dim_per_mb
                   }

    return output_dict


def bulk_estimate_time_interval(data, block_lengths, null_grid=None, max_mb=2):
    """

    """
    block_length_dict = {}
    for b in block_lengths:
        print(b)
        o1 = estimate_time_interval_accurate(data, b, null_grid, max_mb)
        block_length_dict[b] = o1

    return block_length_dict


def estimate_time_interval_rough(data_grid_length, time_freq, block_lengths, max_mb=2, values_per_mb=550000):
    """

    """
    t1 = pd.date_range('2000-01-01', '2000-01-08', freq = time_freq)[:-1]
    val_per_day = len(t1)/7

    total_val_per_file = max_mb * values_per_mb

    res_list = []
    for bl in block_lengths:
        n_stns = int(np.ceil((bl**2)/(data_grid_length**2)))
        days_per_chunk = int(total_val_per_file/n_stns/val_per_day)
        dict1 = {'time_interval': days_per_chunk,
                 'n_geometries_per_station': n_stns}
        res_list.append(dict1)

    res_dict = {bl: res_list[i] for i, bl in enumerate(block_lengths)}

    return res_dict


def decompress_path(glob_path, compression_type='gzip', max_workers=4, **kwargs):
    """

    """
    if isinstance(glob_path, str):
        files1 = glob.glob(glob_path)
    elif isinstance(glob_path, list):
        files1 = glob_path
    new_files = tu.data_io.decompress_files_remove(files1, max_workers=max_workers)

    return new_files


def file_format_conversion(glob_path, file_format='grib', max_workers=4, **kwargs):
    """
    Function to convert data files to netcdf files.
    This also should add in the time coordinate when converting TIF files. It should parse the time from the file name.
    """
    if isinstance(glob_path, str):
        files1 = glob.glob(glob_path)
    elif isinstance(glob_path, list):
        files1 = glob_path
    new_files = tu.data_io.convert_gribs_remove(files1, max_workers=max_workers)

    return new_files


def get_obj_list(glob_path, date_format=None, freq=None, from_date=None, to_date=None, connection_config=None, bucket=None):
    """

    """
    glob_path2 = glob_path

    if isinstance(connection_config, dict) and isinstance(bucket, str):
        if glob_path2.startswith('/'):
            glob_path2 = glob_path2[1:]
        glob_path3, glob_ext = os.path.split(glob_path2)
        if not glob_path3.endswith('/'):
            glob_path3 = glob_path3 + '/'
        s3 = s3_client(connection_config)
        obj_list = tu.s3.list_objects_s3(s3, bucket, glob_path3, delimiter='/', date_format=date_format)
        obj_list1 = obj_list.rename(columns={'Key': 'path', 'Size': 'size', 'KeyDate': 'date'}).drop(['LastModified', 'ETag'], axis=1).copy()
        # obj_list1['remote_type'] = 's3'
    else:
        files1 = glob.glob(glob_path)
        sizes = [os.path.getsize(f) for f in files1]
        obj_list1 = pd.DataFrame(zip(files1, sizes), columns=['path', 'size'])
        # obj_list1['remote_type'] = 'local'

        if isinstance(date_format, str):
            dates1 = tu.misc.filter_data_paths(obj_list1.path, date_format, return_dates=True)
            obj_list1 = pd.merge(obj_list1, dates1, on='path')

    filter1 = [pathlib.Path(p).match(glob_path2) for p in obj_list1.path.values]
    obj_list2 = obj_list1.iloc[filter1]

    if isinstance(date_format, str):
        if isinstance(from_date, (str, pd.Timestamp, date, datetime)):
            obj_list2 = obj_list2[obj_list2['date'] >= pd.Timestamp(from_date)].copy()
        if isinstance(to_date, (str, pd.Timestamp, date, datetime)):
            obj_list2 = obj_list2[obj_list2['date'] < pd.Timestamp(to_date)].copy()

    if isinstance(freq, str):
        grp1 = obj_list2.groupby(pd.Grouper(key='date', freq=freq, origin='start'))

        obj_list3 = [v for k, v in grp1]
    else:
        obj_list3 = obj_list2

    return obj_list3


def copy_source_objs(source_paths, dest_path, bucket=None, connection_config=None, public_url=None, compression=None, threads=None, max_workers=None):
    """

    """
    objs = source_paths

    if isinstance(connection_config, (dict, str)) and isinstance(bucket, str):
        s3 = s3_client(connection_config, threads)

        if isinstance(max_workers, int):

            with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
                futures = []
                for obj in objs:
                    f = executor.submit(tu.data_io.copy_s3_file, source_path=obj, dest_path=dest_path, connection_config=connection_config, bucket=bucket, public_url=public_url, compression=compression)
                    futures.append(f)
                runs = concurrent.futures.wait(futures)

            new_paths = [r.result() for r in runs[0]]

        else:
            if threads is None:
                threads = 4

            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
                futures = []
                for obj in objs:
                    f = executor.submit(tu.data_io.copy_s3_file, source_path=obj, dest_path=dest_path, s3=s3, connection_config=connection_config, bucket=bucket, public_url=public_url, compression=compression)
                    futures.append(f)
                runs = concurrent.futures.wait(futures)

            new_paths = [r.result() for r in runs[0]]

    else:
        new_paths = []
        for obj in objs:
            path1 = tu.data_io.copy_file(source_path=obj, dest_path=dest_path, compression=compression)
            new_paths.append(path1)

    new_paths.sort()

    return new_paths


def copy_interim_objs(source_paths, dest_path, bucket, connection_config=None, public_url=None, threads=10):
    """

    """
    s3 = s3_client(connection_config, threads)

    path1 = pathlib.Path(dest_path)
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for source_path in source_paths:
            p_list = source_path.split('/')
            ds_id = p_list[4]
            stn_id, date, nc, z = p_list[5].split('.')

            file_name = interim_file_str.format(ds_id=ds_id, stn_id=stn_id, date=date)
            dest_path1 = str(path1.joinpath(file_name))

            f = executor.submit(tu.data_io.copy_s3_file, source_path, dest_path1, bucket, s3=s3, public_url=public_url, compression='zstd')
            futures.append(f)
        runs = concurrent.futures.wait(futures)

    new_paths = [r.result() for r in runs[0]]

    new_paths.sort()

    return new_paths


def variable_processing(nc_paths, time_name, x_name, y_name, variables, time_index_bool=None, projected_coordinates=True, nc_source='normal', max_workers=4):
    """
    The variable processing function does three things:
        - select only the specific variables that should be exported,
        - restructure (transpose in xarray) the coordinates so that they are ordered by time, y, x, height,
        - remove duplicate overlapping timestamps between files.

    The restructuring of the coordinates must make sure that the time coordinate is called "time", but the x and y coordinates do not necessarily need to be modified. They just need to be in the correct order. If they are actually longitude and latitude, changing them to lon and lat will make things easier in the future.
    This process will iterate over all of the nc files rather than trying to open them and process them using Dask and xarray. They will initially be opened in Dask to determine the overlapping times only.

    Parameters
    ----------
    nc_paths : list of str or glob str
        The paths to the nc files to be processed.
    variables : list of str
        The variables that should be extracted from the nc files.
    time_index_bool : list of bool
        The boolean time index in case only one file is pulled down to be processed. Normally this should not be needed as there will be multiple files to determine the overlapping times.

    """
    if isinstance(nc_paths, str):
        nc_paths1 = glob.glob(nc_paths)
    elif isinstance(nc_paths, list):
        nc_paths1 = nc_paths

    ## Determine duplicate times
    xr1 = xr.open_mfdataset(nc_paths1)

    time_bool = xr1.get_index(time_name).duplicated(keep='first')

    xr1.close()
    del xr1

    if time_bool.any():
        xr1 = xr.open_dataset(nc_paths1[0])
        nc_time_len = len(xr1[time_name])
        time_index_bool = ~time_bool[:nc_time_len]
        xr1.close()
        del xr1

    ## Iterate through files
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
        futures = []
        for nc_path in nc_paths1:
            f = executor.submit(tu.processing.preprocess_data_structure, nc_path, time_name, x_name, y_name, variables, time_index_bool, projected_coordinates)
            futures.append(f)
        runs = concurrent.futures.wait(futures)

    ## process output
    new_paths = [r.result() for r in runs[0]]
    new_paths1 = []
    for new_path in new_paths:
        new_paths1.extend(new_path)

    new_paths1.sort()

    return new_paths1


def resample_to_wgs84_grids(nc_paths, proj4_crs, order=2, min_val=None, max_val=None, bbox=None, time_name='time', x_name='x', y_name='y', max_workers=4):
    """

    """
    if isinstance(nc_paths, str):
        nc_paths1 = glob.glob(nc_paths)
    elif isinstance(nc_paths, list):
        nc_paths1 = nc_paths

    xr1 = xr.open_dataset(nc_paths1[0])

    ## Get approximate grid resolution
    x1 = xr1[x_name].values
    half_x = len(x1)//2
    x = x1[half_x:(half_x+10)]

    y1 = xr1[y_name].values
    half_y = len(y1)//2
    y = y1[half_y:(half_y+10)]

    xr1.close()
    del xr1

    wgs84 = pyproj.Proj(proj='latlong', datum='WGS84')

    trans = pyproj.Transformer.from_proj(proj4_crs, wgs84)

    lon, lat = trans.transform(x, y)

    grid_res_lat = np.quantile(np.abs(np.diff(lat.T)), 0.5)
    grid_res_lon = np.quantile(np.abs(np.diff(lon.T)), 0.5)
    grid_res = round((grid_res_lon + grid_res_lat)/2, 5)

    ## Iterate through files
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
        futures = []
        for nc_path in nc_paths1:
            f = executor.submit(tu.processing.resample_to_wgs84_grid, nc_path, proj4_crs, grid_res, order, min_val, max_val, bbox)
            futures.append(f)
        runs = concurrent.futures.wait(futures)

    ## process output
    print('grid resolution/length is: ' + str(grid_res))
    new_paths = [r.result() for r in runs[0]]
    new_paths.sort()

    return new_paths


# def calc_new_parameters():
#     """

#     """
#     dates1 = tu.misc.filter_data_paths(obj_list1.path, date_format, return_dates=True)



def combine_metadata(project, dataset):
    """

    """
    datasets = []
    for d in dataset:
        d1 = copy.deepcopy(d)
        d1.update(project)
        datasets.append(d1)

    return datasets


def multi_calc_new_variables(nc_paths, datasets, func_dict):
    """

    """
    dates1 = tu.misc.filter_data_paths(nc_paths, '%Y%m%d%H%M%S', return_dates=True)
    dates1['variable'] = dates1.path.apply(lambda x: pathlib.Path(x).stem.split('_wgs84_')[0])

    ## Iterate through files
    # if max_workers <=1:
    new_paths_list = []
    for i, g in dates1.groupby('date'):
        # print(g)
        p = tu.processing.calc_new_variables(g['path'].tolist(), datasets, func_dict)
        new_paths_list.append(p)

    # elif max_workers > 1:
    #     with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
    #         futures = []
    #         for i, g in dates1.groupby('date'):
    #             # print(g)
    #             f = executor.submit(tu.processing.calc_new_variables, g['path'].tolist(), datasets, func_dict)
    #             futures.append(f)
    #         runs = concurrent.futures.wait(futures)

    #     # process output
    #     new_paths_list = [r.result() for r in runs[0]]

    new_paths1 = []
    for new_path in new_paths_list:
        new_paths1.extend(new_path)

    new_paths1.sort()

    return new_paths1


def multi_mergetime_nc_remove(source_paths, by, max_workers=3):
    """

    """
    source_paths_dict = {}
    if by == 'dataset':
        for p in source_paths:
            path1 = pathlib.Path(p)
            ds_id = path1.stem.split('_')[0]
            if ds_id in source_paths_dict:
                source_paths_dict[ds_id].append(p)
            else:
                source_paths_dict[ds_id] = [p]
    elif by == 'station':
        for p in source_paths:
            path1 = pathlib.Path(p)
            ds_id, stn_id, date = path1.stem.split('_')
            key = (ds_id, stn_id)
            if key in source_paths_dict:
                source_paths_dict[key].append(p)
            else:
                source_paths_dict[key] = [p]
    else:
        raise ValueError('by must be either dataset or station.')

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
        futures = []
        for ds_id, paths in source_paths_dict.items():
            f = executor.submit(tu.data_io.mergetime_nc_remove, paths, by)
            futures.append(f)
        runs = concurrent.futures.wait(futures)

    new_paths = [r.result() for r in runs[0]]
    new_paths.sort()

    return new_paths







###############################################
### Class


class Titan(object):
    """

    """

    def __init__(self, temp_path: pathlib.Path, run_id: str = None, key: str = None, diagnostics_url: HttpUrl = None ):
        """

        """
        ## Check temp path
        os.makedirs(temp_path, exist_ok=True)

        if not os.access(temp_path, os.W_OK):
            raise OSError('{} has no write access.'.format(temp_path))

        ## Add in the additional paths
        preprocessed_path = os.path.join(temp_path, preprocessed_dir)
        # previous_path = os.path.join(temp_path, previous_dir)
        # final_path = os.path.join(temp_path, final_dir)
        os.makedirs(preprocessed_path, exist_ok=True)
        # os.makedirs(previous_path, exist_ok=True)
        # os.makedirs(final_path, exist_ok=True)

        self.preprocessed_path = preprocessed_path
        # self.previous_path = previous_path
        # self.final_path = final_path

        ## Test for the run_id and key
        need_dgn = True

        if isinstance(key, str) and (diagnostics_url is not None):
            # Attempt to read the diagnostics file
            try:
                resp = requests.get(diagnostics_url)
                f = Fernet(key)
                dgn = read_json_zstd(f.decrypt(resp.content))
                run_id = dgn['run_id']
                need_dgn = False

                _ = [setattr(self, k, v) for k, v in dgn['attributes'].items()]
                print('Diagnostics file has loaded sucessfully.')
            except:
                print('Reading diagnostics file failed. Check the URL link. If you continue, the diagnostics file will be overwritten.')

        if (not isinstance(key, str)):
            key = Fernet.generate_key().decode()
            print('A new encryption key has been generated. Keep it safe and secret:')
            print(key)

        if isinstance(run_id, str):
            if len(run_id) != 14:
                print('The run_id provided is not correct, setting a new one.')
                run_id = uuid.uuid4().hex[:14]
                print('A new run_id has been generated:')
                print(run_id)
        else:
            run_id = uuid.uuid4().hex[:14]
            print('A new run_id has been generated:')
            print(run_id)

        self.key = key
        self.run_id = run_id
        self.temp_path = temp_path

        ## Set up diagnostics dict
        if need_dgn:
            run_date1 = tu.misc.make_run_date_key()
            dgn = {'attributes': {},
                   'run_id': run_id,
                   'run_date': run_date1,
                   'key': key
                   }

        self.diagnostics = dgn

        pass


    @staticmethod
    def process_sparse_stations_from_df(stns, dataset_id=None, connection_config=None, bucket=None, system_version=4):
        """
        Function that takes a stns dataframe of station data and converts it to an Xarray Dataset for Tethys. This is ultimately meant to be combined with the time series data for futher processing. If a geometry column is provided, it must be as a geojson-type dict (not a geopandas column).

        """
        stns = tu.processing.process_sparse_stations_from_df(stns, dataset_id, connection_config=connection_config, bucket=bucket, system_version=system_version)

        return stns


    @staticmethod
    def combine_dataset_metadata(project, dataset):
        """

        """
        datasets = []
        for d in dataset:
            d1 = copy.deepcopy(d)
            d1.update(project)
            datasets.append(d1)

        return datasets


    # def init_results_dict(self):
    #     """

    #     """
    #     results_dict = {d: [] for d in self.datasets}
    #     setattr(self, 'results_dict', results_dict)


    def status_checks(self, connection_config: tdm.base.ConnectionConfig, bucket: str, public_url: str = None, system_version: int = 4, load_diagnostics: bool = False):
        """

        """
        ## Test S3 connection
        _ = tdm.base.Remote(**{'connection_config': connection_config, 'bucket': bucket})
        s3 = s3_client(connection_config)

        # Read permissions
        try:
            _ = s3.head_bucket(Bucket=bucket)
        except Exception as err:
            response_code = err.response['Error']['Code']
            if response_code == '403':
                raise requests.exceptions.ConnectionError('403 error. The connection_config is probably wrong.')
            elif response_code == '404':
                raise requests.exceptions.ConnectionError('404 error. The bucket was not found.')

        # Write permissions
        test1 = b'write test'
        test_key = 'tethys/testing/test_write.txt'

        try:
            _ = tu.s3.put_object_s3(s3, bucket, test_key, test1, {}, '', retries=1)
        except bc_exceptions.ConnectionClosedError:
            raise ValueError('Account does not have write permissions.')

        # Public URL read test
        if isinstance(public_url, str):
            try:
                _ = tdm.base.Remote(**{'public_url': public_url, 'bucket': bucket})
                _ = get_object_s3(test_key, public_url=public_url, bucket=bucket, counter=1)
            except:
                raise ValueError('public_url does not work.')

        ## Check that the S3 version is valid
        if not system_version in tdm.key_patterns:
            raise ValueError('S3 version must be one of {}.'.format(list(tdm.key_patterns.keys())))

        ## Check if there is an existing Tethys S3 version
        # Version 3+ check
        objs1 = tu.s3.list_objects_s3(s3, bucket, 'tethys/', delimiter='/')
        if not objs1.empty:
            exist_version = int(objs1.iloc[0].Key.split('/')[1].split('.')[0][1:])
        else:
        # Version 2 check
            objs2 = tu.s3.list_objects_s3(s3, bucket, 'tethys/v2/', delimiter='/')
            if objs2.empty:
                exist_version = None
            else:
                exist_version = 2

        if isinstance(exist_version, int):
            if exist_version != system_version:
                raise ValueError('The bucket already has Tethys data and is version {}. Either change the requested version to the existing version or use a different bucket.'.format(exist_version))

        print('All checks passed!')

        ## Save parameters
        setattr(self, 'connection_config', connection_config)
        setattr(self, 'bucket', bucket)
        setattr(self, 'public_url', public_url)
        setattr(self, 'system_version', system_version)

        ## Loading diagnostic log if it exists
        if load_diagnostics:
            dgn_key_pattern = tdm.key_patterns[self.system_version]['diagnostics']
            dgn_key = dgn_key_pattern.format(run_id=self.run_id)

            try:
                resp = get_object_s3(dgn_key, bucket, s3, public_url=public_url, counter=0)
                f = Fernet(self.key)
                dgn = read_json_zstd(f.decrypt(resp))
                self.diagnostics = dgn
                _ = [setattr(self, k, v) for k, v in dgn['attributes'].items()]
                print('Diagnostics log found and loaded.')
            except:
                ## diagnostic log
                self.diagnostics['status_checks'] = {'pass': True}
                self.diagnostics['attributes'].update({'connection_config': connection_config, 'bucket': bucket, 'public_url': public_url, 'system_version': system_version})
        else:
            ## diagnostic log
            self.diagnostics['status_checks'] = {'pass': True}
            self.diagnostics['attributes'].update({'connection_config': connection_config, 'bucket': bucket, 'public_url': public_url, 'system_version': system_version})


    def save_diagnostics(self):
        """

        """
        tu.misc.diagnostic_check(self.diagnostics, 'status_checks')

        f = Fernet(self.key)
        dgn_obj = f.encrypt(tu.misc.write_json_zstd(copy.deepcopy(self.diagnostics)))

        dgn_key_pattern = tdm.key_patterns[self.system_version]['diagnostics']
        dgn_key = dgn_key_pattern.format(run_id=self.run_id)

        s3 = s3_client(self.connection_config)
        run_date1 = tu.misc.make_run_date_key()

        obj_resp = tu.s3.put_object_s3(s3, self.bucket, dgn_key, dgn_obj, {'run_date': run_date1}, 'application/json')

        self.diagnostics['diagnostic_s3_obj_id'] = obj_resp['VersionId']

        if isinstance(self.public_url, str):
            dgn_url = b2_public_key_pattern.format(base_url=self.public_url, bucket=self.bucket, obj_key=dgn_key)
        else:
            dgn_url = ''

        return dgn_url


    def load_dataset_metadata(self, datasets: Union[dict, list]):
        """

        """
        tu.misc.diagnostic_check(self.diagnostics, 'status_checks')

        dataset_list = tu.processing.process_datasets(datasets)

        # TODO: Check for existing datasets in other S3 buckets

        ds_dict = {ds['dataset_id']: ds for ds in dataset_list}

        setattr(self, 'dataset_list', dataset_list)
        setattr(self, 'datasets', ds_dict)

        ## Check if the chunking parameters are in the datasets
        chunk_params_bool_list = []
        for ds in dataset_list:
            if 'chunk_parameters' in ds:
                _ = tdm.dataset.ChunkParams(**ds['chunk_parameters'])
                chunk_params_bool_list.extend([True])
            else:
                chunk_params_bool_list.extend([True])

        if all(chunk_params_bool_list):
            self.diagnostics['set_chunking_parameters'] = {'pass': True}

        ## diagnostic log
        self.diagnostics['load_dataset_metadata'] = {'pass': True}
        self.diagnostics['attributes'].update({'dataset_list': dataset_list, 'datasets': ds_dict})


    def set_chunking_parameters(self, geometry_count=1, time_interval=None, height_interval=None):
        """

        """
        tu.misc.diagnostic_check(self.diagnostics, 'load_dataset_metadata')

        chunk_params = tdm.dataset.ChunkParams(geometry_count=geometry_count, time_interval=time_interval, height_interval=height_interval).dict(exclude_none=True)

        datasets = []
        for ds in self.dataset_list:
            ds['chunk_parameters'] = chunk_params
            datasets.append(ds)

        self.load_dataset_metadata(datasets)


    def process_versions(self, version_data: dict = None):
        """

        """
        tu.misc.diagnostic_check(self.diagnostics, 'load_dataset_metadata')

        if isinstance(self.public_url, str):
            conn_config = self.public_url
        else:
            conn_config = self.connection_config

        version_dict = tu.s3.process_results_versions(self.dataset_list, bucket=self.bucket, connection_config=self.connection_config, public_url=self.public_url, version_data=version_data, system_version=self.system_version)
        max_version_date_key = tu.misc.make_run_date_key(max(list([d['version_date'] for d in version_dict.values()])))

        # setattr(self, 'processing_code', processing_code)
        setattr(self, 'version_dict', version_dict)
        setattr(self, 'max_version_date_key', max_version_date_key)

        ## diagnostic log
        self.diagnostics['process_versions'] = {'pass': True}
        self.diagnostics['attributes'].update({'version_dict': version_dict, 'max_version_date_key': max_version_date_key})

        return version_dict


    def save_preprocessed_results(self, dataset_id: str, data: Union[List[xr.Dataset], xr.Dataset]):
        """
        Method to save preprocessed results xarray datasets to netcdf files in the temp_path. The results must have the standard dimensions, geometry caclulated, appropriate parameter names, and station data.
        """
        ## All the checks...
        tu.misc.diagnostic_check(self.diagnostics, 'load_dataset_metadata')

        dataset1 = self.datasets[dataset_id]
        result_type = dataset1['result_type']
        param = dataset1['parameter']
        data_model = tdm.dataset.result_type_dict[result_type]
        dims = set(data_model.schema()['properties'].keys())

        if isinstance(data, xr.Dataset):
            data_list = [data]
        else:
            data_list = data

        _ = [data_model(**d.dims) for d in data_list]

        for d in data_list:
            if not param in d:
                raise ValueError('The {param} valiable should be in the data if {ds_id} is the dataset_id.'.format(param=param, ds_id=dataset_id))

            d_dims = set(d[param].dims)
            if d_dims != dims:
                raise ValueError('The {param} valiable should contain the dims: {dims}.'.format(param=param, dims=dims))

        ## Save the data
        file_list = []
        for d in data_list:
            file_id = uuid.uuid4().hex[:14]
            file_path = os.path.join(self.preprocessed_path, preprocessed_file_str.format(ds_id=dataset_id, file_id=file_id))
            _ = tu.misc.write_pkl_zstd(d.to_netcdf(), file_path)
            file_list.append(file_path)

        return file_list


    def get_obj_list(self, glob_path, date_format=None, freq=None, from_date=None, to_date=None, source_connection_config=None, source_bucket=None, source_public_url=None):
        """

        """
        obj_list = get_obj_list(glob_path, date_format=date_format, freq=freq, from_date=from_date, to_date=to_date, connection_config=source_connection_config, bucket=source_bucket)

        # self.obj_list = obj_list.path.tolist()
        self.source_connection_config = source_connection_config
        self.source_bucket = source_bucket
        self.source_public_url = source_public_url

        ## diagnostic log
        self.diagnostics['get_obj_list'] = {'pass': True}
        self.diagnostics['attributes'].update({'source_connection_config': source_connection_config, 'source_bucket': source_bucket, 'source_public_url': source_public_url})

        return obj_list


    def copy_source_objs(self, source_paths, compression=None, threads=None, max_workers=None):
        """

        """
        tu.misc.diagnostic_check(self.diagnostics, 'get_obj_list')

        new_paths = copy_source_objs(source_paths, self.preprocessed_path, threads=threads, compression=compression, connection_config=self.source_connection_config, bucket=self.source_bucket, public_url=self.source_public_url, max_workers=max_workers)

        return new_paths


    # def decompress_files(self, source_paths, compression_type='gzip', max_workers=4):
    #     """

    #     """
    #     new_paths1 = decompress_path(source_paths, compression_type=compression_type, max_workers=max_workers)

    #     return new_paths1


    def file_format_conversion(self, source_paths, file_format='grib', max_workers=4):
        """

        """
        new_paths2 = file_format_conversion(source_paths, file_format=file_format, max_workers=max_workers)

        return new_paths2


    def variable_processing(self, source_paths, time_name, x_name, y_name, variables, time_index_bool=None, projected_coordinates=True, nc_source='normal', max_workers=4):
        """

        """
        new_paths2 = variable_processing(source_paths, time_name, x_name, y_name, variables, time_index_bool=time_index_bool, projected_coordinates=projected_coordinates, max_workers=max_workers)

        return new_paths2


    def resample_to_wgs84(self, source_paths, proj4_crs, order=2, bbox=None, max_workers=4):
        """

        """
        new_paths2 = resample_to_wgs84_grids(source_paths, proj4_crs, order=order, bbox=bbox, max_workers=max_workers)

        return new_paths2


    def calc_new_variables(self, source_paths, func_dict):
        """

        """
        new_paths2 = multi_calc_new_variables(source_paths, self.dataset_list, func_dict)

        return new_paths2


    def merge_time_nc_files(self, source_paths, by, max_workers=4):
        """

        """
        if by == 'station':
            tu.misc.diagnostic_check(self.diagnostics, 'copy_interim_objs')

        new_paths = multi_mergetime_nc_remove(source_paths, by=by, max_workers=max_workers)

        if by == 'station':
            ## diagnostic log
            self.diagnostics['merge_nc_files'] = {'pass': True}

        return new_paths


    def save_dataset_stations(self, source_paths, block_length, block_length_factor=10, compression='zstd', max_workers=4):
        """

        """
        new_paths = multi_save_dataset_stations(source_paths, block_length, block_length_factor=block_length_factor, compression=compression, max_workers=max_workers)

        return new_paths


    def upload_interim_results(self, source_paths, threads=10):
        """

        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            s3 = s3_client(self.connection_config, max_pool_connections=threads)
            futures = []
            for path in source_paths:
                f = executor.submit(tu.s3.put_interim_results_s3, s3, self.bucket, path, self.run_id, system_version=self.system_version)
                futures.append(f)
            runs = concurrent.futures.wait(futures)

        keys = [r.result() for r in runs[0]]

        self.interim_keys = keys

        ## Remove source files
        for path in source_paths:
            os.remove(path)

        ## diagnostic log
        # self.diagnostics['upload_interim_results'] = {'pass': True}
        # self.diagnostics['attributes'].update({'interim_keys': keys})

        return keys


    def get_interim_results_list(self, max_size_gb=0.1):
        """

        """
        tu.misc.diagnostic_check(self.diagnostics, 'status_checks')

        key_pattern = tdm.key_patterns[self.system_version]['interim_results'].split('{dataset_id}')[0]
        key = key_pattern.format(run_id=self.run_id)

        s3 = s3_client(self.connection_config)
        obj_list1 = tu.s3.list_objects_s3(s3, self.bucket, key)
        obj_list1 = obj_list1[['Key', 'Size']].rename(columns={'Key': 'key', 'Size': 'size'})

        obj_keys1 = obj_list1['key'].tolist()
        ds_keys2 = [k.split('/')[4] for k in obj_keys1]
        stn_keys2 = [k.split('/')[5].split('.')[0] for k in obj_keys1]

        obj_list1['dataset_id'] = ds_keys2
        obj_list1['station_id'] = stn_keys2

        # ds_sizes = obj_list1.groupby('dataset_id')['size'].sum().reset_index()
        ds_stn_sizes = obj_list1.groupby(['dataset_id', 'station_id'])['size'].sum().reset_index()
        ds_stn_sizes = ds_stn_sizes.sample(frac=1, ignore_index=True)

        # self.ds_sizes = ds_sizes
        # self.ds_stn_sizes = ds_stn_sizes
        # self.interim_objects = obj_list1

        max_size = max_size_gb * 1000000000

        ds_stn_sum = ds_stn_sizes['size'].sum()
        mean_size = ds_stn_sum/len(ds_stn_sizes)
        group_len = int(max_size//mean_size)
        df_len = len(ds_stn_sizes)

        grouper = np.repeat(np.arange((df_len//group_len)+1), group_len)

        grp1 = ds_stn_sizes.groupby(grouper[:df_len])
        ds_stn_groups = [v for k, v in grp1]

        interim_groups = []
        for df in ds_stn_groups:
            ig = pd.merge(df.drop('size', axis=1), obj_list1, on=['dataset_id', 'station_id'])
            interim_groups.append(ig)

        ## diagnostic log
        self.diagnostics['get_interim_results_list'] = {'pass': True}
        # self.diagnostics['attributes'].update({'interim_objects': obj_list1, 'ds_stn_sizes': ds_stn_sizes, 'ds_sizes': ds_sizes})

        return interim_groups


    def copy_interim_objs(self, source_paths, threads=10):
        """

        """
        tu.misc.diagnostic_check(self.diagnostics, 'get_interim_results_list')

        new_paths = copy_interim_objs(source_paths, self.preprocessed_path, threads=threads, connection_config=self.connection_config, bucket=self.bucket, public_url=self.public_url)

        ## diagnostic log
        self.diagnostics['copy_interim_objs'] = {'pass': True}

        return new_paths


    def save_final_results(self, source_paths, max_workers=4):
        """

        """
        tu.misc.diagnostic_check(self.diagnostics, 'merge_nc_files')
        tu.misc.diagnostic_check(self.diagnostics, 'process_versions')

        ## Iterate through files
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, mp_context=mp.get_context("spawn")) as executor:
            futures = []
            for source_path in source_paths:
                ds_id = source_path.split('/')[-1].split('_')[0]
                metadata = self.datasets[ds_id]
                f = executor.submit(tu.processing.save_final_results, source_path, metadata, self.max_version_date_key, self.system_version)
                futures.append(f)
            runs = concurrent.futures.wait(futures)

        ## process output
        results_new_paths1 = []
        stn_new_paths1 = []

        new_paths = [r.result() for r in runs[0]]

        for paths_list in new_paths:
            r1, s1 = paths_list
            results_new_paths1.extend(r1)
            stn_new_paths1.extend(s1)

        results_new_paths1.sort()
        stn_new_paths1.sort()

        ## diagnostic log
        self.diagnostics['save_final_results'] = {'pass': True}

        return results_new_paths1, stn_new_paths1


    def upload_final_results(self, results_paths, threads=20):
        """

        """
        tu.misc.diagnostic_check(self.diagnostics, 'save_final_results')

        ## Determine which chunks need to uploaded
        if isinstance(self.public_url, str):
            remote1 = {'bucket': self.bucket, 'public_url': self.public_url, 'version': self.system_version}
        else:
            remote1 = {'bucket': self.bucket, 'connection_config': self.connection_config, 'version': self.system_version}

        r_chunks = tu.s3.determine_results_chunks_diffs(results_paths, remote1)

        if not r_chunks.empty:
            results_paths1 = r_chunks['file_path'].tolist()

            ## Make sure all of the station files exist
            stn_paths = []
            for path in results_paths1:
                ds_id, version_date1, stn_id, chunk_id, hash_id, _ = os.path.split(path)[1].split('_')

                stn_file_name = tu.processing.ds_stn_json_str.format(ds_id=ds_id, stn_id=stn_id)
                stn_file_path = os.path.join(os.path.split(path)[0], stn_file_name)

                if os.path.exists(stn_file_path):
                    stn_paths.append(stn_file_path)
                else:
                    raise FileNotFoundError('station file not found: ' + stn_file_path)

            ## Iterate through the results and stations
            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
                s3 = s3_client(self.connection_config, max_pool_connections=threads)
                futures = []

                for path in results_paths1:
                    f = executor.submit(tu.s3.put_result, s3, self.bucket, path, system_version=self.system_version)
                    futures.append(f)

                for path in set(stn_paths):
                    # Add the station file
                    f = executor.submit(tu.s3.put_station, s3, self.bucket, path, system_version=self.system_version)
                    futures.append(f)

                runs = concurrent.futures.wait(futures)

            keys = [r.result() for r in runs[0]]
            keys.sort()

            stn_keys = [key for key in keys if 'station' in key]
            results_keys = [key for key in keys if 'results' in key]
        else:
            stn_keys = []
            results_keys = []
            print('No chunks have changed, so no files have been uploaded.')

        ## Remove source files
        path1 = pathlib.Path(os.path.split(results_paths[0])[0])
        for path in path1.glob('*_results.nc.zst'):
            os.remove(path)
        for path in path1.glob('*_station.json.zst'):
            os.remove(path)

        return results_keys, stn_keys


    def update_aggregates(self, threads=50):
        """

        """
        ## Update the datasets and station jsons
        s3 = s3_client(self.connection_config, threads)

        for ds in self.dataset_list:
            # print(ds['dataset_id'])
            stn_list, results_chunks = tu.s3.put_remote_agg_stations(self.version_dict[ds['dataset_id']], ds['dataset_id'], self.bucket, self.connection_config, self.public_url, threads, system_version=self.system_version)
            if stn_list is not None:
                ds_new = tu.s3.put_remote_dataset(ds, self.bucket, s3=s3, public_url=self.public_url, system_version=self.system_version)

        # Aggregate all datasets for the bucket
        ds_all = tu.s3.put_remote_agg_datasets(self.bucket, self.connection_config, self.public_url, threads, system_version=self.system_version)

        return ds_all


    def clear_interim_results(self):
        """

        """
        prefix = tdm.utils.key_patterns[self.system_version]['interim_results'].split('{dataset_id}')[0].format(run_id=self.run_id)

        s3 = s3_client(self.connection_config)

        obj_list = tu.s3.list_object_versions_s3(s3, self.bucket, prefix)

        rem_keys = []
        for i, row in obj_list.iterrows():
            rem_keys.extend([{'Key': row['Key'], 'VersionId': row['VersionId']}])

        if len(rem_keys) > 0:
            ## Split them into 1000 key chunks
            rem_keys_chunks = np.array_split(rem_keys, int(np.ceil(len(rem_keys)/1000)))

            ## Run through and delete the objects...
            for keys in rem_keys_chunks:
                _ = s3.delete_objects(Bucket=self.bucket, Delete={'Objects': keys.tolist(), 'Quiet': True})

        print(str(len(rem_keys)) + ' objects removed')












################################
### Testing


   # def init_ray(self, num_cpus=1, include_dashboard=False, configure_logging=False, **kwargs):
    #     """

    #     """
    #     if ray.is_initialized():
    #         ray.shutdown()

    #     ray.init(num_cpus=num_cpus, include_dashboard=include_dashboard, configure_logging=configure_logging, **kwargs)

    #     @ray.remote
    #     def _load_result(dataset, result, run_date_key, other_attrs, discrete, other_closed, sum_closed, other_encoding):
    #         """

    #         """
    #         out1 = tu.processing.prepare_results_v02(dataset, result, run_date_key, sum_closed=sum_closed, other_closed=other_closed, discrete=discrete, other_attrs=other_attrs, other_encoding=other_encoding)

    #         return out1

    #     self._load_result = _load_result
    #     self._obj_refs = []


    # def shutdown_ray(self):
    #     ray.shutdown()


    # def load_results(self, results, sum_closed='right', other_closed='left', discrete=True, other_attrs=None, other_encoding=None, run_date=None):
    #     """

    #     """
    #     ## Dataset checks
    #     # ds_ids = list(results.keys())

    #     if isinstance(run_date, str):
    #         run_date_key = tu.misc.make_run_date_key(run_date)
    #     else:
    #         run_date_key = self.max_run_date_key

    #     r1 = [self._load_result.remote(self.datasets[r['dataset_id']], r['result'], run_date_key, other_attrs, discrete, other_closed, sum_closed, other_encoding) for r in results]
    #     # r2 = ray.get(r1)

    #     self._obj_refs.extend(r1)
