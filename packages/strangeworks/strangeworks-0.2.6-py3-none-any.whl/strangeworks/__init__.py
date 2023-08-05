"""Strangeworks SDK"""

from strangeworks.annealing.annealing import Annealing
from .auth import auth

from .client import Client
import importlib.metadata

__version__ = importlib.metadata.version("strangeworks")

client = Client()  # instantiate a client on import by default

# strangeworks.(public method)
authenticate = client.authenticate
login = auth.Login
annealing = client.annealing
rest_client = client.rest_client
circuit_runner = client.circuit_runner
