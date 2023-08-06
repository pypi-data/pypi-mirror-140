from typing import Dict
import logging
import box
from mesh import stores


log = logging.getLogger(__name__)


"""
A module only for interpreting and reading config yml files in the
mesh flavour
"""


class Pipeline:

    def __init__(self, context):
        self.context = context
        if not hasattr(self.context, 'config'):
            log.warning('It is expected that a context has a config attached - beware')


    def __keyfile(self, config_stage, platform='google'):
        try:
            return config_stage['credentials']['keyfile']
        except box.BoxKeyError:
            log.debug('no credentials object provided')
        try:
            # use the 'global' config object here to get the defaults
            return self.context.config.defaults[platform]['keyfile']
        except box.BoxKeyError:
            log.debug('no default credentials provided')
        return None


    def __project(self, config_stage, platform='google'):
        """
        this likely only applies to google stuffs presently
        """
        project = config_stage.get('project', None)
        if project is None:
            try:
                return self.context.config.defaults[platform]['project']
            except box.BoxKeyError as e:
                log.error('Project must be provided')
                raise e
        return project


    def get_connection(self, config_stage):
        """
        Nasty little method to return the connection objects.
        """
        # todo - spaghetti madness - context has path but connect uses context...
        path_conventions = self.context.path_conventions
        if config_stage.types.input in {'gcs', 'bq'}:
            keyfile = self.__keyfile(config_stage)
            project = self.__project(config_stage)
            log.debug(f'current project: {project}, current credentials: {keyfile}')
            if  config_stage.types.input == 'gcs':
                log.info('getting gcs connector')
                filename = config_stage.get('filename', None)
                if filename is None:
                    log.warning('this gcs connector is not initialise with a filename')
                from mesh.google.connectors import gcs
                return gcs.GcsConnect(
                    project=project,
                    service_key_filename=keyfile,
                    bucket_name=config_stage.bucket_name,
                    blob_name=filename,
                    data_type=config_stage.types.output,
                    path_conventions=path_conventions
                    )
            elif 'bq' == config_stage.types.input:
                log.info('getting bq connector')
                from mesh.google.connectors import bigquery
                # handle optional config separately for better error reporting (raising now)
                sql = config_stage.get('sql', None)
                sql_file = config_stage.get('sql_file', None)
                overwrite = None if 'overwrite' not in config_stage.types.keys() else config_stage.types.overwrite
                table_name = config_stage.get('table_name', None)
                bucket_name = config_stage.get('bucket_name', None)
                filename = config_stage.get('filename', None)
                try:
                    return bigquery.BqConnect(
                        project=project,
                        service_key_filename=keyfile,
                        data_type=config_stage.types.output,
                        dataset_name=config_stage.dataset,
                        table_name=table_name,
                        sql=sql,
                        sql_file=sql_file,
                        path_conventions=path_conventions,
                        overwrite=overwrite,
                        bucket_name=bucket_name,
                        blob_name=filename)
                except box.BoxKeyError as e:
                    log.error(e)
                    raise KeyError('Big query configuration broken') from e
        else:
            raise NotImplementedError(f'The requested connection, {config_stage.types.input}, is not handled')


    def write_features(self, name:str, data=None):
        """
        A function to use during development where you care not about
        getting the feature store pointer and so on...
        Just provide that data and the feature store name and you are good to go
        :param name: the name of the stage were the feature store is relevant
        :param data: data may be none in the even that the writing is occurring
        independently of the run-time
        """
        self.get_feature_store(name).write(data)

    def get_features(self, name:str):
        """
        Simple wrapper to extract feature store using the name key in the config.
        """
        o = self.get_feature_store(name)
        return o.read()


    def write_model(self, model_pipeline_obj, metadata=None):
        """
        :param model_pipeline_obj: python class/object
        :param metadata: a string containing training info
        """
        o = self.get_model_store()
        o.write(model_pipeline_obj, metadata)


    def get_model(self):
        o = self.get_model_store()
        return o.read()

    def write_results(self, data):
        """
        :param data: provide a data object containing results (e.g. dataframe)
        """
        self.get_result_store().write(data)

    def get_results(self):
        o = self.get_result_store()
        return o.read()



    def get_feature_stores(self, box_config) -> Dict[str, stores.FeatureStore]:
        """
        returns a list of named feature stores (key'd by name).
        """
        feature_store_kv = dict()
        for elem in box_config:
            fs = self.get_feature_store(self.context, box_config[elem])
            if fs:
                feature_store_kv[elem] = fs

        return feature_store_kv


    def get_feature_store(self, name: str) -> stores.FeatureStore:
        """
        :param context: an analytics project object
        :param name: the name of the stage where the feature store is
        """
        config_stage = self.context.config[name]
        try:
            if ('stage' in config_stage.keys()) and (config_stage.stage == 'features'):
                conn = self.get_connection(config_stage.output)
                fs = stores.FeatureStore(self.context,
                                    conn,
                                    config_stage.output.types.output,
                                    **config_stage.output)
                return fs
            else:
                raise RuntimeError('"stage" is not labelled as "features"')
        except AttributeError as e:
            log.error(f'could not create feature store:  error caught: {e}')
            return None

    def __get_source(self, config_part, name, read=False) -> Dict[str, stores.SourceStore]:

        try:
            config_stage=config_part[name]
        except KeyError as e :
            log.error('%s is invalid considering the config in context\n%s', name, self.context.config.datastores.sources)
            raise e

        conn = self.get_connection(config_stage)
        store = stores.SourceStore(self.context,
                                   conn,
                                   config_stage.types.output,
                                   **config_stage)

        if read:
            # materialise
            return store.read()
        # lazy load
        return store


    def get_sources_history(self, read=False, describe=False):
        """
        High-level api for getting historical data from sources - this is
        what you might train/fit your model on.
        """
        return self.__get_sources(self.context.config.datastores.sources_history, read, describe)

    def get_sources(self, read=False, describe=False):
        """
        High-level api for getting sources (recent) that might be used for online scoring.
        :param read: boolean saying if source must be read/materialised in the call
        :param describe: boolean flag indicating if the source should print info about
          itself.
        """
        return self.__get_sources(self.context.config.datastores.sources, read, describe)


    def __get_sources(self, config_part, read=False, describe=False) -> stores.FeatureStore:
        """
        returns a list of named data sources (key'd by name)
        """
        sources_kv = dict()
        for elem in  config_part.keys():
            log.info(f'getting source {elem}')
            source = self.__get_source(config_part, elem, read)
            if describe is True:
                log.debug('describing sources only')
                sources_kv[elem] = source.describe()
            else:
                sources_kv[elem] = source

        return sources_kv


    def get_model_store(self, read=False) -> stores.ModelStore:
        """
        :param read: if False then return point to the read function, else materialise it.
        """
        config_stage = self.context.config.datastores.model
        store = stores.ModelStore(self.context,
                        self.get_connection(config_stage),
                        config_stage.types.output,
                        **config_stage)

        if read is True:
            return store.read()
        return store

    def get_binary_store(self, read=False) -> stores.BinaryStore:
        """
        :param read: if False then return point to the read function, else materialise it.
        """
        config_stage = self.context.config.datastores.binaries
        store = stores.BinaryStore(self.context,
                                  self.get_connection(config_stage),
                                  config_stage.types.output,
                                  **config_stage)

        if read is True:
            return store.read()
        return store

    # same as get_model_store -
    def get_result_store(self, read=False):
        """
        Get the data resulting from a model scoring/ranking/etc.
        :param read: a boolean for materialising the data
        """
        config_stage = self.context.config.datastores.results
        store = stores.RWStore(self.context,
                               self.get_connection(config_stage),
                               config_stage.types.output,
                               **config_stage)

        # store.set_defaults()
        if read is True:
            return store.read()
        return store
