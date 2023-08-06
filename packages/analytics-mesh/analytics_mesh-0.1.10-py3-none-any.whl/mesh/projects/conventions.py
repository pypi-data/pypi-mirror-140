import logging
from datetime import datetime
from abc import ABCMeta
import pandas as pd

log = logging.getLogger(__name__)




class PathConventions(metaclass=ABCMeta):

    def __init__(self, **kwargs):
        self.values = None

    def storage_id(self):
        """
        Provide a storage id formatted in a simple way

        Returns:
            a formatted string
        """
        return '_'.join(self.values).replace('.', '')

    def storage_path(self):
        """
        Provide a storage path formatted in a simple way

        Returns:
            a formatted string
        """
        return '/'.join(self.values).replace('.', '') + '/'


class SimplePath(PathConventions):
    """
    A simple class to define a default path structure. If you wish to change this behaviour in your pipelines,
    override the methods defined here and pass your own object to MeshContext.
    """

    def __init__(self,
                 customer=None,
                 usecase=None,
                 pipeline_type=None,
                 model_version=None,
                 pipeline_version=None,
                 identifier=None,
                 point_in_time: datetime=None):
        super().__init__()

        # todo - this should live here.
        if isinstance(point_in_time, datetime):
            # format it as simplepath wishes
            self.point_in_time = datetime.strftime(point_in_time, '%Y%m%d')
        elif point_in_time is None:
            self.point_in_time = datetime.strftime(datetime.utcnow(), '%Y%m%d')
        else:
            self.point_in_time = point_in_time
        # hack to deal with locals call below - make point_in_time not None if it was before.
        point_in_time = self.point_in_time
        local_vars = locals()
        # the order of our object
        self.keys = ['customer', 'usecase', 'pipeline_type', 'model_version', 'pipeline_version',
                     'point_in_time', 'identifier']
        self.__margs = {k: str(v) for k, v in local_vars.items() if v is not None}
        log.debug(f'filtered args: {set(local_vars.keys()).difference(set(self.__margs.keys()))}')
        self.values = [self.__margs[x] for x in self.keys if x in self.__margs.keys()]



class EgressConventions:
    """
    A holder for modifying in-memory data for egress
    Typically schema changes and adding columns and such
    """

    @staticmethod
    def apply(dataframe):
        EgressConventions.__pandas(dataframe)
        return dataframe

    @staticmethod
    def __pandas(dataframe):
        if isinstance(dataframe, pd.DataFrame):
            log.info(f'incoming egress dataframe size {dataframe.memory_usage().sum() / 1024 / 1024}')
            dataframe['_insert_time'] = datetime.utcnow()
            log.info(f'modified egress dataframe size {dataframe.memory_usage().sum() / 1024 / 1024}')
        return dataframe

