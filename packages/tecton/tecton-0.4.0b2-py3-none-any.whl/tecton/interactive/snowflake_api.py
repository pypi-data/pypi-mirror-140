from datetime import datetime
from typing import Dict
from typing import Optional
from typing import Union

import pandas
import pendulum

from tecton.interactive.data_frame import DataFrame
from tecton.interactive.run_api import validate_and_get_aggregation_level
from tecton.snowflake_context import SnowflakeContext
from tecton_spark import conf
from tecton_spark.feature_definition_wrapper import FeatureDefinitionWrapper as FeatureDefinition
from tecton_spark.feature_set_config import FeatureSetConfig
from tecton_spark.snowflake import sql_helper
from tecton_spark.snowflake.errors import TectonSnowflakeNotImplementedError


def get_historical_features(
    feature_set_config: FeatureSetConfig,
    spine: Optional[Union["snowflake.snowpark.DataFrame", pandas.DataFrame, DataFrame, str]] = None,
    timestamp_key: Optional[str] = None,
    include_feature_view_timestamp_columns: bool = False,
    from_source: bool = False,
    save: bool = False,
    save_as: Optional[str] = None,
    start_time: Optional[Union[pendulum.DateTime, datetime]] = None,
    end_time: Optional[Union[pendulum.DateTime, datetime]] = None,
    entities: Optional[Union["snowflake.snowpark.DataFrame", pandas.DataFrame, DataFrame]] = None,
) -> DataFrame:
    if spine is None:
        raise TectonSnowflakeNotImplementedError("spine is required for Snowflake")

    if timestamp_key is None:
        raise TectonSnowflakeNotImplementedError("timestamp_key must be specified with Snowflake")

    # TODO(TEC-6991): Dataset doesn't really work with snowflake as it has spark dependency.
    # Need to rewrite it with snowflake context or remove this param for snowflake.
    if save or save_as is not None:
        raise TectonSnowflakeNotImplementedError("save is not supported for Snowflake")

    # TODO(TEC-6996): Implement this
    if entities is not None:
        raise TectonSnowflakeNotImplementedError("entities is not supported for Snowflake")

    # TODO(TEC-7010): Implement this
    if start_time is not None or end_time is not None:
        raise TectonSnowflakeNotImplementedError("start_time and end_time are not supported for Snowflake")

    if conf.get_or_none("ALPHA_SNOWFLAKE_SNOWPARK_ENABLED"):
        return DataFrame._create_with_snowflake(
            sql_helper.get_historical_features_with_snowpark(
                spine=spine,
                session=SnowflakeContext.get_instance().get_session(),
                timestamp_key=timestamp_key,
                feature_set_config=feature_set_config,
                include_feature_view_timestamp_columns=include_feature_view_timestamp_columns,
            )
        )
    else:
        return DataFrame._create(
            sql_helper.get_historical_features(
                spine=spine,
                connection=SnowflakeContext.get_instance().get_connection(),
                timestamp_key=timestamp_key,
                feature_set_config=feature_set_config,
                include_feature_view_timestamp_columns=include_feature_view_timestamp_columns,
            )
        )


def run_batch(
    fd: FeatureDefinition,
    mock_inputs: Dict[str, Union[pandas.DataFrame, DataFrame]],
    feature_start_time: Union[pendulum.DateTime, datetime],
    feature_end_time: Union[pendulum.DateTime, datetime],
    aggregate_tiles: bool,
    aggregation_level: str,
) -> DataFrame:
    # TODO(TEC-7053): Implement this
    if len(mock_inputs) > 0:
        raise TectonSnowflakeNotImplementedError("mock_inputs is not supported for Snowflake")

    fv_proto = fd.feature_view_proto
    aggregation_level = validate_and_get_aggregation_level(fd, aggregate_tiles, aggregation_level)

    if fv_proto.HasField("temporal_aggregate"):
        for feature in fv_proto.temporal_aggregate.features:
            aggregate_function = sql_helper.AGGREGATION_PLANS[feature.function]
            if not aggregate_function:
                raise TectonSnowflakeNotImplementedError(
                    f"Unsupported aggregation function {feature.function} in snowflake pipeline"
                )
    sql_str = sql_helper.generate_run_batch_sql(
        feature_view=fv_proto,
        feature_start_time=feature_start_time,
        feature_end_time=feature_end_time,
        aggregation_level=aggregation_level,
    )
    if conf.get_or_none("ALPHA_SNOWFLAKE_SNOWPARK_ENABLED"):
        session = SnowflakeContext.get_instance().get_session()
        return DataFrame._create_with_snowflake(session.sql(sql_str))
    else:
        connection = SnowflakeContext.get_instance().get_connection()
        cur = connection.cursor()
        cur.execute(sql_str)
        return DataFrame._create(cur.fetch_pandas_all())
