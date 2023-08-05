# coding: utf-8

"""
    printnanny-api-client

    Official API client library for print-nanny.com  # noqa: E501

    The version of the OpenAPI document: 0.0.0
    Contact: leigh@print-nanny.com
    Generated by: https://openapi-generator.tech
"""


try:
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec
import pprint
import re  # noqa: F401
import six

from printnanny_api_client.configuration import Configuration


class Device(object):
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
        'id': 'int',
        'cameras': 'list[Camera]',
        'cloudiot_device': 'CloudiotDevice',
        'dashboard_url': 'str',
        'video_test_url': 'str',
        'janus_auth': 'JanusAuth',
        'janus_local_url': 'str',
        'monitoring_active': 'bool',
        'setup_complete': 'bool',
        'printer_controllers': 'list[PrinterController]',
        'user': 'User',
        'release_channel': 'DeviceReleaseChannel',
        'system_info': 'SystemInfo',
        'public_key': 'PublicKey',
        'created_dt': 'datetime',
        'updated_dt': 'datetime',
        'hostname': 'str'
    }

    attribute_map = {
        'id': 'id',
        'cameras': 'cameras',
        'cloudiot_device': 'cloudiot_device',
        'dashboard_url': 'dashboard_url',
        'video_test_url': 'video_test_url',
        'janus_auth': 'janus_auth',
        'janus_local_url': 'janus_local_url',
        'monitoring_active': 'monitoring_active',
        'setup_complete': 'setup_complete',
        'printer_controllers': 'printer_controllers',
        'user': 'user',
        'release_channel': 'release_channel',
        'system_info': 'system_info',
        'public_key': 'public_key',
        'created_dt': 'created_dt',
        'updated_dt': 'updated_dt',
        'hostname': 'hostname'
    }

    def __init__(self, id=None, cameras=None, cloudiot_device=None, dashboard_url=None, video_test_url=None, janus_auth=None, janus_local_url=None, monitoring_active=False, setup_complete=False, printer_controllers=None, user=None, release_channel=None, system_info=None, public_key=None, created_dt=None, updated_dt=None, hostname=None, local_vars_configuration=None):  # noqa: E501
        """Device - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._cameras = None
        self._cloudiot_device = None
        self._dashboard_url = None
        self._video_test_url = None
        self._janus_auth = None
        self._janus_local_url = None
        self._monitoring_active = None
        self._setup_complete = None
        self._printer_controllers = None
        self._user = None
        self._release_channel = None
        self._system_info = None
        self._public_key = None
        self._created_dt = None
        self._updated_dt = None
        self._hostname = None
        self.discriminator = None

        self.id = id
        self.cameras = cameras
        self.cloudiot_device = cloudiot_device
        self.dashboard_url = dashboard_url
        self.video_test_url = video_test_url
        self.janus_auth = janus_auth
        self.janus_local_url = janus_local_url
        if monitoring_active is not None:
            self.monitoring_active = monitoring_active
        if setup_complete is not None:
            self.setup_complete = setup_complete
        self.printer_controllers = printer_controllers
        self.user = user
        self.release_channel = release_channel
        self.system_info = system_info
        self.public_key = public_key
        self.created_dt = created_dt
        self.updated_dt = updated_dt
        if hostname is not None:
            self.hostname = hostname

    @property
    def id(self):
        """Gets the id of this Device.  # noqa: E501


        :return: The id of this Device.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Device.


        :param id: The id of this Device.  # noqa: E501
        :type id: int
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def cameras(self):
        """Gets the cameras of this Device.  # noqa: E501


        :return: The cameras of this Device.  # noqa: E501
        :rtype: list[Camera]
        """
        return self._cameras

    @cameras.setter
    def cameras(self, cameras):
        """Sets the cameras of this Device.


        :param cameras: The cameras of this Device.  # noqa: E501
        :type cameras: list[Camera]
        """
        if self.local_vars_configuration.client_side_validation and cameras is None:  # noqa: E501
            raise ValueError("Invalid value for `cameras`, must not be `None`")  # noqa: E501

        self._cameras = cameras

    @property
    def cloudiot_device(self):
        """Gets the cloudiot_device of this Device.  # noqa: E501


        :return: The cloudiot_device of this Device.  # noqa: E501
        :rtype: CloudiotDevice
        """
        return self._cloudiot_device

    @cloudiot_device.setter
    def cloudiot_device(self, cloudiot_device):
        """Sets the cloudiot_device of this Device.


        :param cloudiot_device: The cloudiot_device of this Device.  # noqa: E501
        :type cloudiot_device: CloudiotDevice
        """

        self._cloudiot_device = cloudiot_device

    @property
    def dashboard_url(self):
        """Gets the dashboard_url of this Device.  # noqa: E501


        :return: The dashboard_url of this Device.  # noqa: E501
        :rtype: str
        """
        return self._dashboard_url

    @dashboard_url.setter
    def dashboard_url(self, dashboard_url):
        """Sets the dashboard_url of this Device.


        :param dashboard_url: The dashboard_url of this Device.  # noqa: E501
        :type dashboard_url: str
        """
        if self.local_vars_configuration.client_side_validation and dashboard_url is None:  # noqa: E501
            raise ValueError("Invalid value for `dashboard_url`, must not be `None`")  # noqa: E501

        self._dashboard_url = dashboard_url

    @property
    def video_test_url(self):
        """Gets the video_test_url of this Device.  # noqa: E501


        :return: The video_test_url of this Device.  # noqa: E501
        :rtype: str
        """
        return self._video_test_url

    @video_test_url.setter
    def video_test_url(self, video_test_url):
        """Sets the video_test_url of this Device.


        :param video_test_url: The video_test_url of this Device.  # noqa: E501
        :type video_test_url: str
        """
        if self.local_vars_configuration.client_side_validation and video_test_url is None:  # noqa: E501
            raise ValueError("Invalid value for `video_test_url`, must not be `None`")  # noqa: E501

        self._video_test_url = video_test_url

    @property
    def janus_auth(self):
        """Gets the janus_auth of this Device.  # noqa: E501


        :return: The janus_auth of this Device.  # noqa: E501
        :rtype: JanusAuth
        """
        return self._janus_auth

    @janus_auth.setter
    def janus_auth(self, janus_auth):
        """Sets the janus_auth of this Device.


        :param janus_auth: The janus_auth of this Device.  # noqa: E501
        :type janus_auth: JanusAuth
        """

        self._janus_auth = janus_auth

    @property
    def janus_local_url(self):
        """Gets the janus_local_url of this Device.  # noqa: E501


        :return: The janus_local_url of this Device.  # noqa: E501
        :rtype: str
        """
        return self._janus_local_url

    @janus_local_url.setter
    def janus_local_url(self, janus_local_url):
        """Sets the janus_local_url of this Device.


        :param janus_local_url: The janus_local_url of this Device.  # noqa: E501
        :type janus_local_url: str
        """
        if self.local_vars_configuration.client_side_validation and janus_local_url is None:  # noqa: E501
            raise ValueError("Invalid value for `janus_local_url`, must not be `None`")  # noqa: E501

        self._janus_local_url = janus_local_url

    @property
    def monitoring_active(self):
        """Gets the monitoring_active of this Device.  # noqa: E501


        :return: The monitoring_active of this Device.  # noqa: E501
        :rtype: bool
        """
        return self._monitoring_active

    @monitoring_active.setter
    def monitoring_active(self, monitoring_active):
        """Sets the monitoring_active of this Device.


        :param monitoring_active: The monitoring_active of this Device.  # noqa: E501
        :type monitoring_active: bool
        """

        self._monitoring_active = monitoring_active

    @property
    def setup_complete(self):
        """Gets the setup_complete of this Device.  # noqa: E501


        :return: The setup_complete of this Device.  # noqa: E501
        :rtype: bool
        """
        return self._setup_complete

    @setup_complete.setter
    def setup_complete(self, setup_complete):
        """Sets the setup_complete of this Device.


        :param setup_complete: The setup_complete of this Device.  # noqa: E501
        :type setup_complete: bool
        """

        self._setup_complete = setup_complete

    @property
    def printer_controllers(self):
        """Gets the printer_controllers of this Device.  # noqa: E501


        :return: The printer_controllers of this Device.  # noqa: E501
        :rtype: list[PrinterController]
        """
        return self._printer_controllers

    @printer_controllers.setter
    def printer_controllers(self, printer_controllers):
        """Sets the printer_controllers of this Device.


        :param printer_controllers: The printer_controllers of this Device.  # noqa: E501
        :type printer_controllers: list[PrinterController]
        """
        if self.local_vars_configuration.client_side_validation and printer_controllers is None:  # noqa: E501
            raise ValueError("Invalid value for `printer_controllers`, must not be `None`")  # noqa: E501

        self._printer_controllers = printer_controllers

    @property
    def user(self):
        """Gets the user of this Device.  # noqa: E501


        :return: The user of this Device.  # noqa: E501
        :rtype: User
        """
        return self._user

    @user.setter
    def user(self, user):
        """Sets the user of this Device.


        :param user: The user of this Device.  # noqa: E501
        :type user: User
        """

        self._user = user

    @property
    def release_channel(self):
        """Gets the release_channel of this Device.  # noqa: E501


        :return: The release_channel of this Device.  # noqa: E501
        :rtype: DeviceReleaseChannel
        """
        return self._release_channel

    @release_channel.setter
    def release_channel(self, release_channel):
        """Sets the release_channel of this Device.


        :param release_channel: The release_channel of this Device.  # noqa: E501
        :type release_channel: DeviceReleaseChannel
        """

        self._release_channel = release_channel

    @property
    def system_info(self):
        """Gets the system_info of this Device.  # noqa: E501


        :return: The system_info of this Device.  # noqa: E501
        :rtype: SystemInfo
        """
        return self._system_info

    @system_info.setter
    def system_info(self, system_info):
        """Sets the system_info of this Device.


        :param system_info: The system_info of this Device.  # noqa: E501
        :type system_info: SystemInfo
        """

        self._system_info = system_info

    @property
    def public_key(self):
        """Gets the public_key of this Device.  # noqa: E501


        :return: The public_key of this Device.  # noqa: E501
        :rtype: PublicKey
        """
        return self._public_key

    @public_key.setter
    def public_key(self, public_key):
        """Sets the public_key of this Device.


        :param public_key: The public_key of this Device.  # noqa: E501
        :type public_key: PublicKey
        """

        self._public_key = public_key

    @property
    def created_dt(self):
        """Gets the created_dt of this Device.  # noqa: E501


        :return: The created_dt of this Device.  # noqa: E501
        :rtype: datetime
        """
        return self._created_dt

    @created_dt.setter
    def created_dt(self, created_dt):
        """Sets the created_dt of this Device.


        :param created_dt: The created_dt of this Device.  # noqa: E501
        :type created_dt: datetime
        """
        if self.local_vars_configuration.client_side_validation and created_dt is None:  # noqa: E501
            raise ValueError("Invalid value for `created_dt`, must not be `None`")  # noqa: E501

        self._created_dt = created_dt

    @property
    def updated_dt(self):
        """Gets the updated_dt of this Device.  # noqa: E501


        :return: The updated_dt of this Device.  # noqa: E501
        :rtype: datetime
        """
        return self._updated_dt

    @updated_dt.setter
    def updated_dt(self, updated_dt):
        """Sets the updated_dt of this Device.


        :param updated_dt: The updated_dt of this Device.  # noqa: E501
        :type updated_dt: datetime
        """
        if self.local_vars_configuration.client_side_validation and updated_dt is None:  # noqa: E501
            raise ValueError("Invalid value for `updated_dt`, must not be `None`")  # noqa: E501

        self._updated_dt = updated_dt

    @property
    def hostname(self):
        """Gets the hostname of this Device.  # noqa: E501

        Please enter the hostname you set in the Raspberry Pi Imager's Advanced Options menu (without .local extension)  # noqa: E501

        :return: The hostname of this Device.  # noqa: E501
        :rtype: str
        """
        return self._hostname

    @hostname.setter
    def hostname(self, hostname):
        """Sets the hostname of this Device.

        Please enter the hostname you set in the Raspberry Pi Imager's Advanced Options menu (without .local extension)  # noqa: E501

        :param hostname: The hostname of this Device.  # noqa: E501
        :type hostname: str
        """
        if (self.local_vars_configuration.client_side_validation and
                hostname is not None and len(hostname) > 255):
            raise ValueError("Invalid value for `hostname`, length must be less than or equal to `255`")  # noqa: E501

        self._hostname = hostname

    def to_dict(self, serialize=False):
        """Returns the model properties as a dict"""
        result = {}

        def convert(x):
            if hasattr(x, "to_dict"):
                args = getfullargspec(x.to_dict).args
                if len(args) == 1:
                    return x.to_dict()
                else:
                    return x.to_dict(serialize)
            else:
                return x

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            attr = self.attribute_map.get(attr, attr) if serialize else attr
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: convert(x),
                    value
                ))
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], convert(item[1])),
                    value.items()
                ))
            else:
                result[attr] = convert(value)

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Device):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Device):
            return True

        return self.to_dict() != other.to_dict()
