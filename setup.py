from setuptools import setup
from setuptools.dist import Distribution
import os

class BinaryDistribution(Distribution):
    def has_ext_modules(foo):
        return True

plat_name = os.environ.get('WHEEL_PLATFORM_NAME', 'any')

setup(
    distclass=BinaryDistribution,
    options={'bdist_wheel': {'plat_name': plat_name}}
)
