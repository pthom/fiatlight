from pydantic import BaseModel


class Mydata(BaseModel):
    """The data we want to present.
    This is a simple example data class.
    In a real case, this would be a data class that is relevant to the user's data,
    for example a DataFrame, an image, a graph, etc.
    """

    x: int
