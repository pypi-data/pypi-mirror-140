# coding: utf-8

"""
Copyright (c) 2022 Aspose.Cells Cloud
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
"""


from pprint import pformat
from six import iteritems
import re


class TextureFill(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'scale': 'float',
        'image': 'LinkElement',
        'pic_format_option': 'PicFormatOption',
        'tile_pic_option': 'TilePicOption',
        'transparency': 'float',
        'type': 'str'
    }

    attribute_map = {
        'scale': 'Scale',
        'image': 'Image',
        'pic_format_option': 'PicFormatOption',
        'tile_pic_option': 'TilePicOption',
        'transparency': 'Transparency',
        'type': 'Type'
    }
    
    @staticmethod
    def get_swagger_types():
        return TextureFill.swagger_types
    
    @staticmethod
    def get_attribute_map():
        return TextureFill.attribute_map
    
    def get_from_container(self, attr):
        if attr in self.container:
            return self.container[attr]
        return None

    def __init__(self, scale=None, image=None, pic_format_option=None, tile_pic_option=None, transparency=None, type=None, **kw):
        """
        Associative dict for storing property values
        """
        self.container = {}
		    
        """
        TextureFill - a model defined in Swagger
        """

        self.container['scale'] = None
        self.container['image'] = None
        self.container['pic_format_option'] = None
        self.container['tile_pic_option'] = None
        self.container['transparency'] = None
        self.container['type'] = None

        if scale is not None:
          self.scale = scale
        if image is not None:
          self.image = image
        if pic_format_option is not None:
          self.pic_format_option = pic_format_option
        if tile_pic_option is not None:
          self.tile_pic_option = tile_pic_option
        if transparency is not None:
          self.transparency = transparency
        if type is not None:
          self.type = type

    @property
    def scale(self):
        """
        Gets the scale of this TextureFill.

        :return: The scale of this TextureFill.
        :rtype: float
        """
        return self.container['scale']

    @scale.setter
    def scale(self, scale):
        """
        Sets the scale of this TextureFill.

        :param scale: The scale of this TextureFill.
        :type: float
        """

        self.container['scale'] = scale

    @property
    def image(self):
        """
        Gets the image of this TextureFill.

        :return: The image of this TextureFill.
        :rtype: LinkElement
        """
        return self.container['image']

    @image.setter
    def image(self, image):
        """
        Sets the image of this TextureFill.

        :param image: The image of this TextureFill.
        :type: LinkElement
        """

        self.container['image'] = image

    @property
    def pic_format_option(self):
        """
        Gets the pic_format_option of this TextureFill.

        :return: The pic_format_option of this TextureFill.
        :rtype: PicFormatOption
        """
        return self.container['pic_format_option']

    @pic_format_option.setter
    def pic_format_option(self, pic_format_option):
        """
        Sets the pic_format_option of this TextureFill.

        :param pic_format_option: The pic_format_option of this TextureFill.
        :type: PicFormatOption
        """

        self.container['pic_format_option'] = pic_format_option

    @property
    def tile_pic_option(self):
        """
        Gets the tile_pic_option of this TextureFill.

        :return: The tile_pic_option of this TextureFill.
        :rtype: TilePicOption
        """
        return self.container['tile_pic_option']

    @tile_pic_option.setter
    def tile_pic_option(self, tile_pic_option):
        """
        Sets the tile_pic_option of this TextureFill.

        :param tile_pic_option: The tile_pic_option of this TextureFill.
        :type: TilePicOption
        """

        self.container['tile_pic_option'] = tile_pic_option

    @property
    def transparency(self):
        """
        Gets the transparency of this TextureFill.

        :return: The transparency of this TextureFill.
        :rtype: float
        """
        return self.container['transparency']

    @transparency.setter
    def transparency(self, transparency):
        """
        Sets the transparency of this TextureFill.

        :param transparency: The transparency of this TextureFill.
        :type: float
        """

        self.container['transparency'] = transparency

    @property
    def type(self):
        """
        Gets the type of this TextureFill.

        :return: The type of this TextureFill.
        :rtype: str
        """
        return self.container['type']

    @type.setter
    def type(self, type):
        """
        Sets the type of this TextureFill.

        :param type: The type of this TextureFill.
        :type: str
        """

        self.container['type'] = type

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.get_swagger_types()):
            value = self.get_from_container(attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, TextureFill):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
