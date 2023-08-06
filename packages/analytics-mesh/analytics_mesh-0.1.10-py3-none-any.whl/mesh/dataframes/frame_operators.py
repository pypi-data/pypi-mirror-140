import json
import pandas as pd
import json
import logging

log = logging.getLogger(__name__)


class PandasSchema:

    filename_suffix = '-pandas-schema.json'

    @staticmethod
    def get(dataframe):
        return dataframe.dtypes.astype(str).to_dict()

    @staticmethod
    def write_local(dataframe: pd.DataFrame, frame_name):
        schema = PandasSchema.get(dataframe)
        with open(f'{frame_name}{PandasSchema.filename_suffix}', 'w') as f:
            json.dump(schema, f, indent=4, sort_keys=True)

    @staticmethod
    def read_local(dataframe_name):
        with open(f'{dataframe_name}{PandasSchema.filename_suffix}', 'r') as f:
            schema = json.load(f)
            return schema


    @staticmethod
    def to_string(dictionary):
        return ['%s: %s' % (k, v) for k, v in dictionary.items()]


    @staticmethod
    def verify(dataframe, schema):
        # there is an issue with this method - it casts the schema too and is not a
        # direct check in that sense... todo create a function to cast if that is what we want
        if len(set(dataframe.keys()).symmetric_difference(set(schema.keys()))) != 0:
            log.error('schema mismatch - nr of columns do not agree')
            raise ValueError(f'keys not matched: {set(dataframe.keys()).symmetric_difference(schema.keys())}')
        try:
            return dataframe.astype(schema)
        except (ValueError, KeyError) as e:
            log.error("failed to enforce schema: {}".format(e))
            log.error("Output of <dataframe> compared to provided <schema>")
            # now to provide something more useful
            log.error(
                set(PandasSchema.to_string(PandasSchema.get(dataframe))) \
                ^ set(PandasSchema.to_string(schema)))
            raise e
