
import logging
from abc import ABC, abstractmethod
from mesh.google.connectors import gcs

log = logging.getLogger(__name__)


class Store(ABC):
    """
    Store base class for storage/persistence objects
    """

    def __init__(self,
                context,
                connector,
                data_type,
                **kwargs):
        """
        :param context: an analytics project context containing a minimal description of project
        :param connector: a connector class implementing read and write methods
        :param data_type: the expected data type obtained when interacting with the store (e.g. pandas)
        """
        self.context = context
        self.connector = connector
        self.data_type = data_type


    @abstractmethod
    def read(self, **kwargs):
        pass

    @abstractmethod
    def write(self, data, **kwargs):
        pass



class SourceStore(Store):
    """
    A source store that is a read-only flavour
    """

    def __init__(self,
                 context,
                 connector,
                 data_type,
                 **kwargs):
        """

        :param name: the store name
        :param bucket_name: if dfs connector, provide a bucket name
        :param blob_name: if dfs connector, a blob name
        :param table_name: a table name (if db connector)
        :param dataset_name: a dataset/database name (if db connector)
        :param sql:
        """
        super().__init__(context, connector, data_type, **kwargs)


    def read(self, **kwargs):
        return self.connector.read(**kwargs)

    def write(self, data=None, **kwargs):
        raise NotImplementedError('sources are read-only --- you may not write to them')

    def describe(self):
        return f'{type(self.connector).__name__}-->{self.data_type}'


class FeatureStore(Store):
    """
    A feature store that will apply connector conventions - currently just wee
    shell.
    """

    def __init__(self,
                context,
                connector,
                data_type,
                **kwargs):
        """
        A feature store object that requires a context
        """
        super().__init__(context, connector, data_type, **kwargs)


    def write(self, data, **kwargs):
        """
        """
        return self.connector.write(data)


    def read(self):
        log.info('reading from feature store')
        # maybe add a list to the connector here.
        return self.connector.read()


# heavy duplication here. meh. create a run of the mill general store or o
# verride from the base store without 'abstract'
class RWStore(Store):

    def __init__(self,
                context,
                connector,
                data_type,
                **kwargs):
        """
        A feature store object that requires a context
        """
        super().__init__(context, connector, data_type, **kwargs)

    def write(self, data, **kwargs):
        """
        """
        return self.connector.write(self.context.egress_conventions.apply(data))


    def read(self, latest=False, point_in_time=None):
        log.info('reading from sink')
        # maybe add a list to the connector here.
        return self.connector.read()


class ModelStore(Store):

    def __init__(self,
                context,
                connector,
                data_type,
                **kwargs):
        super().__init__(context, connector, data_type, **kwargs)


    def write(self, data, metadata=None, **kwargs):
        """
        :param data: the file you wish to write
        :param metadata: any metadata objects you wish to write
        """
        # the convention is that metadata is currently written as string
        # ultimately, it should be its own class that simply gets executed here
        # that is, a DS can write their own custom metadata extractors and we can
        # also provide a generic one for most cases
        if metadata:
            if isinstance(metadata, str):
                if isinstance(self.connector, gcs.GcsConnector):
                    # mutate this baddie to take advantage of bucket paths
                    orig_blob_name = self.connector._GcsConnect__blob_name
                    orig_data_type = self.connector.data_type
                    self.connector.data_type = 'string'
                    self.connector.blob_name = 'metadata.txt'
                    self.connector.write(metadata)
                    log.info('wrote metadata to %s', self.connector.blob_name)
                    self.connector.data_type = orig_data_type
                    self.connector.blob_name = orig_blob_name
        self.connector.write(data, **kwargs)
   
    def read(self):
        log.info('reading from binary store')
        return self.connector.read()

    def read_metadata(self):
        """
        read metadata from store location
        """
        try:
            if isinstance(self.connector, gcs.GcsConnector):
                # mutate this baddie to take advantage of bucket paths
                orig_blob_name = self.connector._GcsConnect__blob_name
                orig_data_type = self.connector.data_type
                self.connector.data_type = 'string'
                self.connector.blob_name = 'metadata.txt'
                self.connector.read()
                self.connector.data_type = orig_data_type
                self.connector.blob_name = orig_blob_name
        except Exception as e:
            log.error('fix this nincompoop - no general exceptions allowed %s', e)


class BinaryStore(Store):

    def __init__(self,
                 context,
                 connector,
                 data_type,
                 **kwargs):
        super().__init__(context, connector, data_type, **kwargs)

    def write(self, data, name=None, **kwargs):
        """
        :param data: the file you wish to write
        :param name: a blob name with which to save this binary (include your extension - e.g. joblib)
        """
        if name is None:
            raise ValueError('name must actually be provided, either in call to binary store or in config')

        self.connector.blob_name = name
        self.connector.write(data, **kwargs)

    def read(self, name=None):
        raise NotImplementedError('the binary store is not a fully featured thing, load manually')

