# TODO: this needs to be done in a different way, this is just a quick hack
USE_TEST_DB = False

DB_TYPE = 'sqlite'
DB_FILE_NAME = 'locmess.sqlite'

PBKDF2_ITERATIONS = 1000  # number of pbkdf2 iterations

KEY_PATH = 'keys/server.key'  # path of server's symmetric key

# Testing Options
TEST_DB_NAME = 'locmess_test.sqlite'
TEST_PATH = '../tests/'
TEST_DB_FILE_NAME = TEST_PATH + TEST_DB_NAME

if USE_TEST_DB:
    DB_FILE_NAME = TEST_DB_FILE_NAME
