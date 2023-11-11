import re
from enum import Enum


class ResourceType(Enum):
    """
    An enumeration representing different types of web resources.

    This enumeration defines the resource types commonly found on the web, such as
    web pages, images, stylesheets, and JavaScript files. It is used to classify
    resources based on their file extensions.

    Attributes:
        PAGE (str): Represents web pages with extensions .html or .htm.
        IMG (str): Represents image resources with extensions .png, .jpg, .jpeg, .gif, .svg, or .ico.
        CSS (str): Represents stylesheet resources with the .css extension.
        JS (str): Represents JavaScript resources with the .js extension.
        NO_EXTENSION (str): Represents resources with no or generic extensions.

    Methods:
        find(url): Determine the ResourceType of a resource based on its URL.

    Examples:
        To determine the resource type of a URL:
        >>> url = "https://example.com/index.html"
        >>> ResourceType.find(url)
        ResourceType.PAGE
    """

    PAGE = "Page"
    IMG = "Image"
    CSS = "Stylesheet"
    JS = "JavaScript"
    NO_EXTENSION = "Generic"

    @classmethod
    def find(cls, url):
        """
        Determine the ResourceType of a resource based on its URL.

        Args:
            url (str): The URL of the resource to classify.

        Returns:
            ResourceType: The ResourceType enumeration corresponding to the resource.

        Example:
            >>> url = "https://example.com/styles.css"
            >>> ResourceType.find(url)
            ResourceType.CSS
        """
        if re.match(r".+?(\.html|\.htm).*?", url):
            return ResourceType.PAGE
        if re.match(r".+?(\.png|\.jpg|\.jpeg|\.gif|\.svg|\.ico).*?", url):
            return ResourceType.IMG
        if re.match(r".+?(\.js).*?", url):
            return ResourceType.JS
        if re.match(r".+?(\.css).*?", url):
            return ResourceType.CSS
        return ResourceType.NO_EXTENSION
