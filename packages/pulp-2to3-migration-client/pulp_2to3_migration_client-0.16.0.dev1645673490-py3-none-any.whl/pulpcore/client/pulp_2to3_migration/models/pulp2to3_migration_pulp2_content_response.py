# coding: utf-8

"""
    Pulp 3 API

    Fetch, Upload, Organize, and Distribute Software Packages  # noqa: E501

    The version of the OpenAPI document: v3
    Contact: pulp-list@redhat.com
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from pulpcore.client.pulp_2to3_migration.configuration import Configuration


class Pulp2to3MigrationPulp2ContentResponse(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'pulp_href': 'str',
        'pulp_created': 'datetime',
        'pulp2_id': 'str',
        'pulp2_content_type_id': 'str',
        'pulp2_last_updated': 'int',
        'pulp2_storage_path': 'str',
        'downloaded': 'bool',
        'pulp3_content': 'str',
        'pulp3_repository_version': 'str'
    }

    attribute_map = {
        'pulp_href': 'pulp_href',
        'pulp_created': 'pulp_created',
        'pulp2_id': 'pulp2_id',
        'pulp2_content_type_id': 'pulp2_content_type_id',
        'pulp2_last_updated': 'pulp2_last_updated',
        'pulp2_storage_path': 'pulp2_storage_path',
        'downloaded': 'downloaded',
        'pulp3_content': 'pulp3_content',
        'pulp3_repository_version': 'pulp3_repository_version'
    }

    def __init__(self, pulp_href=None, pulp_created=None, pulp2_id=None, pulp2_content_type_id=None, pulp2_last_updated=None, pulp2_storage_path=None, downloaded=False, pulp3_content=None, pulp3_repository_version=None, local_vars_configuration=None):  # noqa: E501
        """Pulp2to3MigrationPulp2ContentResponse - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._pulp_href = None
        self._pulp_created = None
        self._pulp2_id = None
        self._pulp2_content_type_id = None
        self._pulp2_last_updated = None
        self._pulp2_storage_path = None
        self._downloaded = None
        self._pulp3_content = None
        self._pulp3_repository_version = None
        self.discriminator = None

        if pulp_href is not None:
            self.pulp_href = pulp_href
        if pulp_created is not None:
            self.pulp_created = pulp_created
        self.pulp2_id = pulp2_id
        self.pulp2_content_type_id = pulp2_content_type_id
        self.pulp2_last_updated = pulp2_last_updated
        self.pulp2_storage_path = pulp2_storage_path
        if downloaded is not None:
            self.downloaded = downloaded
        self.pulp3_content = pulp3_content
        if pulp3_repository_version is not None:
            self.pulp3_repository_version = pulp3_repository_version

    @property
    def pulp_href(self):
        """Gets the pulp_href of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501


        :return: The pulp_href of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501
        :rtype: str
        """
        return self._pulp_href

    @pulp_href.setter
    def pulp_href(self, pulp_href):
        """Sets the pulp_href of this Pulp2to3MigrationPulp2ContentResponse.


        :param pulp_href: The pulp_href of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501
        :type: str
        """

        self._pulp_href = pulp_href

    @property
    def pulp_created(self):
        """Gets the pulp_created of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501

        Timestamp of creation.  # noqa: E501

        :return: The pulp_created of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501
        :rtype: datetime
        """
        return self._pulp_created

    @pulp_created.setter
    def pulp_created(self, pulp_created):
        """Sets the pulp_created of this Pulp2to3MigrationPulp2ContentResponse.

        Timestamp of creation.  # noqa: E501

        :param pulp_created: The pulp_created of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501
        :type: datetime
        """

        self._pulp_created = pulp_created

    @property
    def pulp2_id(self):
        """Gets the pulp2_id of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501


        :return: The pulp2_id of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501
        :rtype: str
        """
        return self._pulp2_id

    @pulp2_id.setter
    def pulp2_id(self, pulp2_id):
        """Sets the pulp2_id of this Pulp2to3MigrationPulp2ContentResponse.


        :param pulp2_id: The pulp2_id of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and pulp2_id is None:  # noqa: E501
            raise ValueError("Invalid value for `pulp2_id`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                pulp2_id is not None and len(pulp2_id) > 255):
            raise ValueError("Invalid value for `pulp2_id`, length must be less than or equal to `255`")  # noqa: E501

        self._pulp2_id = pulp2_id

    @property
    def pulp2_content_type_id(self):
        """Gets the pulp2_content_type_id of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501


        :return: The pulp2_content_type_id of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501
        :rtype: str
        """
        return self._pulp2_content_type_id

    @pulp2_content_type_id.setter
    def pulp2_content_type_id(self, pulp2_content_type_id):
        """Sets the pulp2_content_type_id of this Pulp2to3MigrationPulp2ContentResponse.


        :param pulp2_content_type_id: The pulp2_content_type_id of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and pulp2_content_type_id is None:  # noqa: E501
            raise ValueError("Invalid value for `pulp2_content_type_id`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                pulp2_content_type_id is not None and len(pulp2_content_type_id) > 255):
            raise ValueError("Invalid value for `pulp2_content_type_id`, length must be less than or equal to `255`")  # noqa: E501

        self._pulp2_content_type_id = pulp2_content_type_id

    @property
    def pulp2_last_updated(self):
        """Gets the pulp2_last_updated of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501


        :return: The pulp2_last_updated of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501
        :rtype: int
        """
        return self._pulp2_last_updated

    @pulp2_last_updated.setter
    def pulp2_last_updated(self, pulp2_last_updated):
        """Sets the pulp2_last_updated of this Pulp2to3MigrationPulp2ContentResponse.


        :param pulp2_last_updated: The pulp2_last_updated of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and pulp2_last_updated is None:  # noqa: E501
            raise ValueError("Invalid value for `pulp2_last_updated`, must not be `None`")  # noqa: E501

        self._pulp2_last_updated = pulp2_last_updated

    @property
    def pulp2_storage_path(self):
        """Gets the pulp2_storage_path of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501


        :return: The pulp2_storage_path of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501
        :rtype: str
        """
        return self._pulp2_storage_path

    @pulp2_storage_path.setter
    def pulp2_storage_path(self, pulp2_storage_path):
        """Sets the pulp2_storage_path of this Pulp2to3MigrationPulp2ContentResponse.


        :param pulp2_storage_path: The pulp2_storage_path of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501
        :type: str
        """

        self._pulp2_storage_path = pulp2_storage_path

    @property
    def downloaded(self):
        """Gets the downloaded of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501


        :return: The downloaded of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501
        :rtype: bool
        """
        return self._downloaded

    @downloaded.setter
    def downloaded(self, downloaded):
        """Sets the downloaded of this Pulp2to3MigrationPulp2ContentResponse.


        :param downloaded: The downloaded of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501
        :type: bool
        """

        self._downloaded = downloaded

    @property
    def pulp3_content(self):
        """Gets the pulp3_content of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501


        :return: The pulp3_content of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501
        :rtype: str
        """
        return self._pulp3_content

    @pulp3_content.setter
    def pulp3_content(self, pulp3_content):
        """Sets the pulp3_content of this Pulp2to3MigrationPulp2ContentResponse.


        :param pulp3_content: The pulp3_content of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501
        :type: str
        """

        self._pulp3_content = pulp3_content

    @property
    def pulp3_repository_version(self):
        """Gets the pulp3_repository_version of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501


        :return: The pulp3_repository_version of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501
        :rtype: str
        """
        return self._pulp3_repository_version

    @pulp3_repository_version.setter
    def pulp3_repository_version(self, pulp3_repository_version):
        """Sets the pulp3_repository_version of this Pulp2to3MigrationPulp2ContentResponse.


        :param pulp3_repository_version: The pulp3_repository_version of this Pulp2to3MigrationPulp2ContentResponse.  # noqa: E501
        :type: str
        """

        self._pulp3_repository_version = pulp3_repository_version

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
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
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Pulp2to3MigrationPulp2ContentResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Pulp2to3MigrationPulp2ContentResponse):
            return True

        return self.to_dict() != other.to_dict()
