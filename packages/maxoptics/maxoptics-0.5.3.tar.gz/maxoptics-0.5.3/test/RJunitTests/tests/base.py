import unittest
from pathlib import Path
# import logging
from pprint import pprint
import maxoptics

maxoptics.__CONFIGPATH__ = Path(__file__).parent / "maxoptics.conf"


class Base:
    cl = maxoptics.MosLibrary()
    pr = cl.create_project_as("UnitTest")



