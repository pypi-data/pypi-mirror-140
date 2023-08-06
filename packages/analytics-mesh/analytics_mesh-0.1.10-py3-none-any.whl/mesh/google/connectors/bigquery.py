import logging
import functools
import re
import time
import pandas as pd
import google.cloud.bigquery
from google.oauth2.service_account import Credentials
import google.cloud.bigquery.job
from google.cloud.exceptions import NotFound, BadRequest
from mesh.connectors.base import GoogleConnector


log = logging.getLogger(__name__)


class BqConnector(GoogleConnector):
    """
    a wee wrapper of the google client
    """
    def __init__(self, project, **kwargs):
        """
        :param optional - service_key_filename:
        :param project: a project object
        """
        super().__init__(project)
        self.scopes = (
                'https://www.googleapis.com/auth/bigquery',
                'https://www.googleapis.com/auth/cloud-platform',
                'https://www.googleapis.com/auth/drive'
            )
        try:
            log.debug('connecting to bq')
            self.service_key_filename = kwargs['service_key_filename']
            credentials = Credentials.from_service_account_file(
                self.service_key_filename
            ).with_scopes(self.scopes)
            self.client = google.cloud.bigquery.Client(credentials=credentials,
                                                       project=self.project)
        except (KeyError, TypeError) as e:
            self.client = google.cloud.bigquery.Client()
            log.info('inferred from environment')


    def read_pandas_dataframe(self,  sql: str = None) -> pd.DataFrame:
        """
        :param sql: run the sql on big query and produce a dataframe
        :return dataframe: a pandas dataframe
        """
        log.info(f'bigquery: executing custom sql to populate pandas df: {self.__sql_extract(sql)}...)')
        return self.client.query(sql).to_dataframe()


    def __get_dataset(self, dataset_id):
        """
        Get or create a big query dataset
        :param dataset_id: given a dataset name, get use the big query client
        to get the dataset, or create it if it doesn't exist.
        """
        try:
            dataset = self.client.get_dataset(dataset_id)
        except NotFound as e:
            dataset = google.cloud.bigquery.Dataset(f'{self.client.project}.{dataset_id}')
            dataset.location = "EU"
            dataset = self.client.create_dataset(dataset, timeout=30)
            log.info("Create: bq dataset {}.{} ".format(self.client.project, dataset.dataset_id))
        return dataset

    def __sql_extract(self, sql):
        """
        get sql lines that match certain statements (e.g. CREATE... SELECT FROM...)
        :param sql: a sql string
        :return a list lines that match the specified terms
        """
        return list(filter(None,
                    [x for tupl in re.findall(r"(CREATE.*TABLE.*)|(SELECT.*FROM [`\w+\.\_-]*)",
                                              sql,
                                              re.IGNORECASE) for x in tupl]
                    )
             )

    def write_pandas_dataframe(self, dataset: str,
                               tablename: str,
                               overwrite: bool,
                               data: pd.DataFrame):
        """
        A wrapper function that overwrites or creates a table in BigQuery from a data frame
        :param dataset: the dataset name (or database name)
        :param tablename: the table name (or collection name)
        :param overwrite: the mode being overwrite or not, this currently works with suffixes only
        :param data: the data frame containing the final feature store
        :return:
        """
        log.info('writing to {}.{}'.format(dataset, tablename))
        dataset_ref = self.__get_dataset(dataset)
        table_ref = dataset_ref.table(tablename)
        if overwrite is False:
            raise NotImplementedError('This code is presently only able to truncate/overwrite a table')
        # set up the write disposition
        jconf = google.cloud.bigquery.job.LoadJobConfig(
            write_disposition=google.cloud.bigquery.job.WriteDisposition.WRITE_TRUNCATE,
            create_disposition=google.cloud.bigquery.job.CreateDisposition.CREATE_IF_NEEDED)
        job = self.client.load_table_from_dataframe(data, table_ref, job_config=jconf)
        job.result()  # waits for query to complete


    def write_sql(self, sql:str = None) -> google.cloud.bigquery.job:
        """
        :param file_name: the name or path to the sql file to be passed in
          eg. /sql_files/fs_train.sql
        :param table_name: the name of the table that is to be created
        :param dataset: a dataset on the gcp
        :param parameters: a dictionary from the config file of specific
          paramaters to be substituted in at execution time
        :return: a dataframe
        """
        log.info(f'bigquery: executing sql to bq: {self.__sql_extract(sql)}...)')
        self.client.query(sql).result()  # wait for job to finish
        return sql[0:64]


    def dry_run(self, sql:str = None):
        """
        Perform a dry run of this sql against the big query api - courtesy of
        https://cloud.google.com/bigquery/docs/dry-run-queries#python
        :param sql: a complete sql string to be passed to big query
        """
        job_config = google.cloud.bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)

        # Start the query, passing in the extra configuration.
        query_job = self.client.query(
            (
               sql
            ),
            job_config=job_config,
        )
        bytes_processed = query_job.total_bytes_processed
        log.info("COST: This query will process {:.4f} TiB.".format(bytes_processed/1024**4))
        return bytes_processed
    
    
    

    def get_table(self, table_id:str=None):
        """
        table_id: 'your-project.your_dataset.your_table' to check for
        """
        try:
            table = self.client.get_table(table_id)  # Make an API request.
            log.info(f'Table {table.table_id} found')
        except NotFound as e:
            log.info(e)
            table=None

        return table

    

    def poll_table(self, project=None, dataset=None, table=None, time_out=7200,timer=10):
        """
        param: timeout: a timeout for when to exit the loop default = 2hrs
        param: time: time in sec to sleep for between table checks
        param: project: the gcp project name
        param: dataset: the gcp dataset name
        param: table: the gcp table to check against
        """

        table_id = f'{project}.{dataset}.{table}'
        table_ref=None
        poll_time = 0
        while ((table_ref == None) & (poll_time <= time_out)):
            log.warning(f'sql polling for {poll_time} of {time_out} seconds') 
            table_ref = self.get_table(table_id=table_id)  # Make an API request.  
            time.sleep(timer)
            poll_time += timer

        if table_ref == None:
            raise NotFound(message='BQ polling timed out')
        else: 
            return self


    def write_gcs(self, project: str,
                dataset_name: str,
                table_name: str,
                bucket_name: str,
                blob_name: str,
                columns='*',
                destination_format=google.cloud.bigquery.DestinationFormat.CSV,
                destination_delimiter=','):
        """
        Creates a job to export a bigquery table to a gcs bucket
        :param bucket_name: The name of the bucket to export the table to
        :param blob_name: The name of the file in the specified bucket
        :param project: The project in which the biq query table is
        :param dataset_name: The dataset from which to export the table
        :param table_name: The table to be exported
        :param columns: The columns to export

        Presently, the credentials of the Big Query connection are used to access
        the big query and to write to Google Cloud Storage. This read and write
        (BQ --> GCS) happens within the same project.
        """
        columns = [columns] if isinstance(columns, str) else columns
        bq_name = '{project}.{dataset}.{table}'.format(project=project,
                                                       dataset=dataset_name,
                                                       table=table_name)
        log.info('loading data (bq: {}) into gcp storage bucket: {}'.format(
            bq_name,
            bucket_name)
        )

        # create query
        query = self.client.query(r"""SELECT {columns} FROM `{name}`""".format(
            name=bq_name,
            columns=', '.join(columns)))
        log.info('bq query job_id: {}'.format(query.job_id))
        query.result()

        # create job config object
        job_config = google.cloud.bigquery.job.ExtractJobConfig()
        job_config.destination_format = (destination_format)
        job_config.field_delimiter = destination_delimiter

        destination_uri = "gs://{}/{}".format(bucket_name, blob_name)
        log.info('writing to: {}'.format(destination_uri))

        # dataset_ref = self.client.dataset(dataset_name, project=self.project)
        # table_ref = dataset_ref.table(table_name)

        extract_job = self.client.extract_table(
            query.destination,
            destination_uri,
            location="EU",
            job_config=job_config
        )
        log.info('extract job_id: {}'.format(query.job_id))
        extract_job.result()
        log.info("Exported {}.{}.{} to {}".format(project, dataset_name, table_name, destination_uri))


class BqConnect(BqConnector):

    """
    This doesn't make enough sense :)
    ...
    """
    def __init__(self,
                project,
                service_key_filename,
                data_type,
                dataset_name=None,
                table_name=None,
                bucket_name=None,
                blob_name=None,
                sql=None,
                sql_file=None,
                path_conventions=None,
                overwrite=None):
        super().__init__(project=project,
                         service_key_filename=service_key_filename)
        log.debug('Bq connect args {locals()}')
        self.data_type = data_type
        self.__table_name = table_name
        self.dataset_name = dataset_name
        self.path_conventions = path_conventions
        self.overwrite = overwrite
        self.sql = sql  # this guy is operated on
        if sql_file:
            if sql:
                log.warning('you should not provide sql and a sql file... is that your intention?')
                raise ValueError("sql and sql file provided - untenable")
            with open(sql_file) as f:
                self.sql = f.read()
                # have a first pass at mutating it - this is a common usage pattern where just project, dataset
                # and tablename are set
                try:
                    self.mutate_sql()
                except KeyError:
                    log.warning('the provided sql needs to be mutated - see .mutate_sql()')
        # these should not be here - for another day when we redesign this thing
        self.bucket_name = bucket_name
        self.__blob_name = blob_name


    def mutate_sql(self, **kwargs):
        """
        Given key-value pairs, search the sql and replace those keys within curly braces with
        the corresponding values. By default, it will attempt to parameterize project, dataset_name and
        table_name (from the object attributes). #todo consider making this more explicit
        :param kwargs: key-value pairs
        :return: the object itself
        """
        if bool(re.search('\{.*\}', self.sql)):
            log.debug('BQ sql file requires parameterization')
            # update it to do parameterization
            self.sql = self.sql.format(
                project=self.project,
                dataset=self.dataset_name,
                table_name=self.table_name(),
                **kwargs
            )
        return self


    def tibibytes_processed(self):
        """
        return the number of tibibytes processed by the resident sql
        """
        return self.dry_run(self.sql)/1024**4



    @property
    def read(self, **kwargs):
        """
        if kwargs are provided then handle them accordingly - the assumption at the moment
        is that the only optional 'read-time' parameters are parameters. We can make a more complex structure
        later or break out sql specific stores
        """
        return self._accessor()


    @property
    def write(self, **kwargs):
        """
        Write data to the connection. Provide kwargs to communicate directly with the
        underlying BqConnector methods
        """
        return  self._accessor(write=True)


    def table_name(self, apply_path=False):
        if apply_path and self.path_conventions:
            return f'{self.path_conventions.storage_id()}' #/{self.__table_name}' for discussion
        else:
            log.warning('no path_conventions provided')
        return self.__table_name


    def blob_name(self, apply_path=False):
        """
        dev-notes: this is a duplicate of the function in gcs connector
        """
        if apply_path and self.path_conventions:
            return f'{self.path_conventions.storage_path()}{self.__blob_name}'
        return self.__blob_name


    def _accessor(self, write=False, **kwargs):
        """
        get a callable to the functions in this object that are linked to the
        data_type you would like to read and write to (e.g. gcs -> pandas and pandas -> gcs)
        :param kwargs: there to ignore all that is irrelevant
        """
            
        if self.data_type == 'pandas':
            if write:
                return functools.partial(self.write_pandas_dataframe,
                                        self.dataset_name,
                                        self.table_name(),
                                        self.overwrite)
            f = functools.partial(self.read_pandas_dataframe, self.sql)
            return f
        if self.data_type == 'bq':
            log.warning('you are only able to write with this configuration... writing')
            return functools.partial(self.write_sql, self.sql)
        if self.data_type == 'gcs':
            return functools.partial(self.write_gcs,
                self.project,
                self.dataset_name,
                self.table_name(),
                self.bucket_name,
                self.blob_name(apply_path=True))


        raise ValueError(f'no such datatype: "{self.data_type}"')


