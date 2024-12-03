from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlalchemy import pool
from alembic import context

# Import model yang berisi MetaData
from myapp.models import Base  # Gantilah 'myapp.models' sesuai struktur proyek Anda.

# this is the Alembic Config object, which provides access to the configuration
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata  # 'Base' adalah kelas dasar dari model Anda, biasanya didefinisikan dalam 'models.py'

# other setup code...
