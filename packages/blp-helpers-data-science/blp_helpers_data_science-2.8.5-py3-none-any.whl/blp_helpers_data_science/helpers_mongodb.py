import pymongo
from pymongo.errors import OperationFailure
from pymongo.uri_parser import parse_uri
import logging
import os


def get_mongo_collection(environment_name, collection_name=False):
    logger = logging.getLogger(__name__)

    env_vars_available = False
    mongodb_connected = False
    db_available = False
    mongo_collection = False

    try:
        mongodb_uri = os.environ['{}_MONGODB_DB_URI'.format(environment_name)]
        mongodb_connect_params = parse_uri(
            mongodb_uri
            , validate=True
            , warn=False
            , normalize=True
            , connect_timeout=None
        )
        mongodb_db_name = mongodb_connect_params.get('database')

        if (mongodb_connect_params.get('collection')) and collection_name:
            logger.error('collection twice available, once in connection string and once passed in')
            return mongo_collection

        if mongodb_connect_params.get('collection'):
            mongodb_collection_name = mongodb_connect_params.get('collection')
            logger.info("loaded mongodb_collection_name from env")
        else:
            mongodb_collection_name = collection_name
            logger.info("loaded mongodb_collection_name from passed in value")
        env_vars_available = True
        logger.info("env_vars_available available")
    except KeyError as e:
        logger.error('issues at os.environ {}'.format(e))

    if env_vars_available:
        try:
            mongo_client = pymongo.MongoClient(mongodb_uri)
            mongodb_connected = True
            logger.info("mongodb_connected")
        except ValueError as e:
            logger.error('issues at mongo_client {}'.format(e))

    if mongodb_connected:
        try:
            mongo_client.list_database_names().index(mongodb_db_name)
            db_available = True
            logger.info("list_database_names available")
        except ValueError as e:
            logger.error('The DB: {} is not available. Error Msg.: {}'.format(mongodb_db_name, e))
        except OperationFailure as e:
            logger.error('cannot authenticate to db'.format(mongodb_db_name, e))

    if db_available:
        # no error handling necessary
        mongo_db = mongo_client[mongodb_db_name]
        mongo_collection = mongo_db[mongodb_collection_name]
        logger.info("opened collection")

    return mongo_collection
