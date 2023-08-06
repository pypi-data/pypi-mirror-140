import os
from typing import Union, Type
from enum import Enum
from datetime import datetime
import logging
import yaml
from box import Box
import mesh
from mesh.projects import conventions
import mesh.pipeline
log = logging.getLogger(__name__)




class RandomSeedMixin:
    """
    a class to use in setting your numpy and standard random seeds
    """

    def set_seed(self):
        """
        set the numpy and random seeds
        """
        log.info('fixing numpy and random seeds')
        import random
        import numpy as np

        random.seed(101)
        np.random.seed(101)


class MeshContext:

    """
    Create a data analytics project. Simply it is a holder of basic
    attributes related to analytics applications.
    However, it may also be used to house more general configuration
    such as agreed to yml configurations
    """
    def __init__(self,
                 customer=None,
                 usecase=None,
                 model_version=None,
                 identifier=None,
                 point_in_time=None,
                 pipeline_version=None,
                 pipeline_type='default',
                 path_conventions=None,
                 egress_conventions=None,
                 config=None):
        """
        :param customer: a customer name (e.g. acme-industries)
        :param usecase: a use case name (e.g. propensity-to-blow)
        :param identifier: some way to identify model (e.g. a name like 'xgboost' or '22341b1')
          - if not provided, one will be generated for you
        :param model_version: version expression (e.g. 20171120.2) - this is to
          capture the 'logic' of the model
        :param model_store: what kind of store does this model project use)
        :param pipeline_version: a code version for your pipeline - if not provided it will
          use the application version
        :param pipeline_type: a pipeline may be {experiment, sample, challenger, default, ...}
        :param config: provide a config object and you need not provide the other args
        :param kwargs
        """
        self.config = None
        # try the config first
        if not self.add_config(config):
            # config was not provided, so use the kwargs
            # a helper function to encapsulate some of the default settings on the args
            self.__configure_pipeline(customer,
                                      usecase,
                                      model_version,
                                      identifier,
                                      pipeline_version,
                                      pipeline_type,
                                      point_in_time)
        else:
            self.point_in_time = point_in_time
        if path_conventions is not None:
            self.path_conventions = path_conventions
        else:
            self.path_conventions = conventions.SimplePath

        # if provided then add it to context (point in time run)
        # todo - this can't be initialised in here - makes it hard to add new kind of convention
        self.path_conventions = self.path_conventions(
            customer=self.customer,
            usecase=self.usecase,
            pipeline_type=self.pipeline_type,
            model_version=self.model_version,
            pipeline_version=self.pipeline_version,
            identifier=self.identifier,
            point_in_time=self.point_in_time
        )

        if  egress_conventions:
            self.egress_conventions = egress_conventions
        else:
            self.egress_conventions = conventions.EgressConventions()
        self.pipeline = mesh.pipeline.Pipeline(self) # omg



    def __configure_pipeline(self,
                            customer=None,
                            usecase=None,
                            model_version=None,
                            identifier=None,
                            pipeline_version=None,
                            pipeline_type=None,
                            point_in_time=None
    ):

        # be handled by the storage_paths object
        self.customer = customer
        self.usecase = usecase
        # also, this can just be the current time if nothing is provided. leaving out for now
        # self.model_version = '19790101' if not model_version else model_version
        self.model_version = model_version
        self.identifier = datetime.strftime(datetime.utcnow(), '%Y%m%d') if not identifier else identifier

        # we select the library version if a pipeline version is not provided -
        # this should be a code version in general
        # so we will ignore that for now.
        self.pipeline_version = pipeline_version
        #self.pipeline_version = f'mesh{mesh.__version__}'.replace('.','') if not
        # ...pipeline_version else pipeline_version
        self.pipeline_type = pipeline_type

        # this should be moved from storage path to here or vice-versa
        self.point_in_time = point_in_time


    def __str__(self):
        import inspect
        import pprint
        # attributes = inspect.getmembers(self, lambda a:not(inspect.isroutine(a) or inspect.isclass(a)))
        # pprint.pprint([a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))])
        return 'you got them context'


    def add_config(self, config: Union[Box, str, dict]):
        if isinstance(config, str):
            log.debug('configuration file provided')
            with open(config, 'r') as f:
                config = yaml.safe_load(f)
        elif isinstance(config, dict):
            log.debug('configuration dictionary provided')
        else:
            return None
        self.config = Box(config)
        self.__configure_pipeline(**self.config.pipeline)
        return self


class EdaContext(MeshContext, RandomSeedMixin):

    def __init__(self, **kwargs):
        super(EdaContext, self).__init__(**kwargs)
        """
        :param experiment_name: a name of your experiment (else is timestamp)
        """
        self.set_seed()
        self.pipeline_type = 'experiment'
