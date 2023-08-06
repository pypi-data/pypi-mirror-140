# flake8: noqa

import pkg_resources


__version__ = pkg_resources.get_distribution('fed').version


from fed.distance import WeightedFeatureEditDistance

from ._core import __doc__
from ._core import edit_distance
from ._core import weighted_feature_edit_distance
