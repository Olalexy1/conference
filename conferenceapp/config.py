class Config(object):
    DATABASE_URI="some random parameters"
    MERCHANT_ID="SAMPLE"

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI="mysql+mysqlconnector://root@127.0.0.1/confdb"
    SQLALCHEMY_TRACK_MODIFICATIONS=True

    MERCHANT_ID="T98765@0"

class TestConfig(Config):
    DATABASE_URI="Test connection parameters"