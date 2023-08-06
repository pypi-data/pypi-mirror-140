from t99.api_resources.abstract import CreateableAPIResource
from t99.api_resources.abstract import DeletableAPIResource
from t99.api_resources.abstract import ListableAPIResource
from t99.api_resources.abstract import UpdateableAPIResource


class Entities(
    CreateableAPIResource,
    DeletableAPIResource,
    ListableAPIResource,
    UpdateableAPIResource,
):
    OBJECT_NAME = "entities"
