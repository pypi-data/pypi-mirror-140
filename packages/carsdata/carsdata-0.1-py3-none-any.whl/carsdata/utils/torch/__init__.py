from carsdata import OPTIONAL_PACKAGES, NN_LIB
from carsdata.utils.errors import PackageRequiredError


if not OPTIONAL_PACKAGES[NN_LIB]:
    raise PackageRequiredError(NN_LIB)