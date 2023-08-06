
import logging
import io
import functools
from google.cloud.storage import bucket
import joblib
from google.cloud import storage
import google.cloud.bigquery
import google.cloud.storage.blob
from  google.api_core.exceptions import Forbidden
import pandas as pd
# import tensorflow as tf
# from tensorflow.python.lib.io import file_io
from mesh.connectors.base import GoogleConnector
from mesh.google.connectors import bigquery


log = logging.getLogger(__name__)


class GcsConnector(GoogleConnector):
    """
    a wee wrapper of the googl client
    """
    def __init__(self, project, **kwargs):
        """
        :param service_key_filename - if not provided, the assumption is already provided
        :param context: (optional) provide a mesh context for
        """
        super().__init__(project)
        self.client_gcsfs=None
        try:
            self.service_key_file = kwargs['service_key_filename']
            log.debug(f'connecting to gcs with keyfile {self.service_key_file}')
            self.client = storage.Client.from_service_account_json(self.service_key_file)
        except (KeyError, TypeError) as e:
            self.client = storage.Client.create_anonymous_client()
            log.info('Please provide a valid service key file and project if you require a non-anonymous connection')
            log.info('creating anonymous key created')

    @property
    def client_gcsfs(self):  #todo is this still relevant
        self._client_gcsfs = gcsfs.GCSFileSystem(
            project=self.project,
            token=self.service_key_file
        )

    @client_gcsfs.setter
    def client_gcsfs(self, value):
        self._client_gcsfs = value


    def read_blob(self, bucket_name: str, blob_path: str) -> io.BytesIO:
        """
        Trivial wrapper to read a blob at a path from cloud storage
        This binary is kept in memory and a BytesIO buffer is returned
        :param bucket_name: a gcs bucket name
        :param path: path within the bucket for gcs
        :return: a blob object buffer
        """
        log.info(f'Reading from gs://{bucket_name}/{blob_path}')
        bucket = self.client.get_bucket('{}'.format(bucket_name))
        gcs_object = bucket.blob(blob_path)
        buffer = io.BytesIO()
        gcs_object.download_to_file(buffer)
        # now that the buffer is populated, get cursor back to start
        buffer.seek(0)
        return buffer
    


    def read_joblib(self, bucket_name: str, blob_path: str):
        """
        Trivial wrapper to read an object serialised with joblib
        and located at <bucket_name>/<path> from cloud storage.
        :param bucket_name: a gcs bucket name
        :param path: path within the bucket for gcs
        :return: a blob object
        """
        log.debug(f'Reading from gs://{bucket_name}/{blob_path}')
        buffer = self.read_blob(bucket_name, blob_path)
        # now, deserialise it using joblib
        obj = joblib.load(buffer)
        return obj


    def _read_pandas_dataframe(self,
                               bucket_name,
                               blob_path,
                               delimiter=',',
                               parse_dates=None) -> pd.DataFrame:
        """
        Read a csv file into a pandas dataframe
        :param filename: the filename (may include full path) of the csv file
        :param delimiter: a character delimiter for the csv file
        :param parse_dates: pass through to the pandas api
        :return: a pandas dataframe
        """
        log.info(f'Reading from gs://{bucket_name}/{blob_path}')
        bytes_object = self.read_blob(bucket_name=bucket_name, blob_path=blob_path)
        if parse_dates is None:
            return pd.read_csv(bytes_object, delimiter=delimiter)
        return pd.read_csv(bytes_object, parse_dates=parse_dates, delimiter=delimiter)


    def read_pandas_dataframe(self,
                              bucket_name,
                              blob_path,
                              delimiter=',',
                              parse_dates=None):
        """
        Read a pandas dataframe - we are using a simple approach to list the possible files in the event that they
        are sharded - this is brittle and we should likely do some regex as a next step
        """
        blobs = self.client.list_blobs(bucket_name, prefix=blob_path)
        appended_df = []
        blob_names = []

        # strip '*' for shardy guys
        try:
            for blob in blobs:
                blob_names.append(blob.name)
        except google.api_core.exceptions.Forbidden as e:
            # todo not ideal - we might want to make it explicit in the config but serves purposes at moment
            log.debug('unable to list on this bucket, assuming is just a single file')
            log.info('list operation not possible on this key - attempting file directly')
            blob_names.append(blob_path)

        for blob_name in blob_names:
            appended_df.append(self._read_pandas_dataframe(bucket_name, blob_name, delimiter, parse_dates))

        if not appended_df:
            log.warning(f'no data read for pandas dataframe gs://{bucket_name}/{blob_path}')
            return None
        return pd.concat(appended_df)


    def read_string(self, bucket_name: str, blob_path: str):
        """
        read a string encoded as utf-8 in a bucket
        :param bucket_name: the name of the bucket in gcs
        :param blob_path: the full path of the blob in gcs (including filename)
        """
        log.info(f'Reading from gs://{bucket_name}/{blob_path}')
        bucket = self.client.bucket(bucket_name)
        return bucket.blob(blob_path).download_as_string().decode('utf-8')


    def write_string(self, bucket_name: str, blob_path: str, a_string: str):
        """
        write a string to gcs
        :param bucket_name: the name of a bucket in gcs
        :param blob_path: the path to (and including) the blob in gcs
        :param a_string: a string
        """
        bucket = self.client.bucket(bucket_name)
        string_buffer = io.StringIO(a_string)
        bucket.blob(blob_path).upload_from_string(string_buffer.read(), content_type="text/plain")
        string_buffer.close()

    def write_blob(self, bucket_name: str, blob_path: str,  obj: object):
        """
        :param obj:
        :param bucket_name:
        :param path:
        :return:
        """
        log.info(f'persisting to gs:\\{bucket_name}/{blob_path}')
        buffer = io.BytesIO()
        joblib.dump(obj, buffer)
        # rewind to the start of the bugger
        buffer.seek(0)

        # get bucket via the client
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        blob.upload_from_file(buffer)


    def write_local_file(self, bucket_name: str, blob_path: str, file: str):
        """
        Uploads a local file to the provided bucket
        :param bucket_name: a gcs bucket
        :param file: the location of the file in the local directory (including name)
        :param path: the desired location of the file in the provided gcs bucket
        """
        log.info(f'persisting to gs:\\{bucket_name}/{blob_path}')
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(file)


    def write_pandas_dataframe(self, bucket_name: str,
                               blob_path: str,
                               data: pd.DataFrame,
                               delimiter=',',
                               file_type: str = 'csv'):
        """
        :param bucket_name: the bucket name in cloud storage
        :param blob_path: the blob path within storage
        :param data: the data frame that will be written
        :param delimiter: the element separator if csv file
        :param file_type: the file_type (at the moment we only support csv, alternatives are parquet)
        """

        log.info(f'Writing to gs://{bucket_name}/{blob_path}')
        bucket = self.client.get_bucket('{}'.format(bucket_name))
        if file_type == 'csv':
            bucket.blob(blob_path).upload_from_string(data.to_csv(index=False, sep=delimiter), file_type)
        else:
            raise NotImplementedException()



    def write_joblib(self, bucket_name: str, blob_path: str, obj: object, chunk_size_mb=None):
        """
        :param obj: an object in memory to write with joblib serialisation to a bucket
        :param bucket_name: a gcs bucket
        :param blob_path: the desired location of the file in the provided gcs bucket
        """
        log.info(f'persisting to gcs: {bucket_name}/{blob_path}')
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        if chunk_size_mb:
            blob.chunk_size = chunk_size_mb * 1024 * 1024 # 5 MB is good for local; default is 100MB

        buffer = io.BytesIO()
        joblib.dump(obj, buffer)
        buffer.seek(0)

        blob.upload_from_file(buffer)


class GcsConnect(GcsConnector):

    """
    fix a connection to a specific bucket_name and blob_name pair, whilst specifying
    how you would like it read into memory too. So, connect it specifically.
    """
    def __init__(self,
                project,
                service_key_filename,
                bucket_name,
                blob_name,
                data_type,
                path_conventions=None):
        super().__init__(project=project,
                         service_key_filename=service_key_filename)
        self.bucket_name = bucket_name
        self.__blob_name = blob_name
        self.data_type = data_type
        self.path_conventions = path_conventions


    @property
    def read(self):
        """
        Read the data from the connection.
        """
        return self._accessor()



    @property
    def write(self):
        """
        Write data to the connection.
        :param data: some data (e.g. pandas dataframe or object)
        """
        return self._accessor(write=True)



    @property
    def blob_name(self):
        if self.path_conventions:
            return f'{self.path_conventions.storage_path()}{self.__blob_name}'
        return self.__blob_name


    @blob_name.setter
    def blob_name(self, blob_name):
        self.__blob_name = blob_name


    def _accessor(self, write=False, **kwargs):
        """
        get a callable to the functions in this object that are linked to the
        data_type you would like to read and write to (e.g. gcs -> pandas and pandas -> gcs)
        :param kwargs: there to ignore all that is irrelevant
        """
        if self.data_type == 'pandas':
            func = self.write_pandas_dataframe if write else self.read_pandas_dataframe
        elif self.data_type == 'joblib':
            func = self.write_joblib if write else self.read_joblib
        elif self.data_type == 'string':
            func = self.write_string if write else self.read_string
        else:
            raise ValueError(f'no such datatype: "{self.data_type}"')
        return functools.partial(func, self.bucket_name, self.blob_name)

    
