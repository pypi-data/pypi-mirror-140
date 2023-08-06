# distutils: language = c++

"""
The upper #distutils part MUST to on top of this code
This script is for implementing all Razer methods for corsair.
@project : pyrgbdev
@author : Gooday2die
@date : 2022-02-23
@file : SDK.pyx
"""

from pyrgbdev.Razer.Razer cimport *
# There will be an error in Pycharm with this import, but it works.


class RazerSDKInitFailError(Exception):
    """
    An error class for Razer SDK failed to connect error
    """
    pass

class SDKNotConnectedError(Exception):
    """
    A Error class for when sdk is not connected and use is trying to perform
    expressions which should be executed after sdk has been connected
    """
    pass

class InvalidDeviceIndexError(Exception):
    """
    An Error class for Invalid Device index
    """
    pass

class InvalidRgbValueError(Exception):
    """
    An Error class for Invalid RGB Values.
    Example: ("AWD", 123, 123)
    Would raise this error
    """
    pass

class InvalidDeviceType(Exception):
    """
    An Error class for Invalid Device Type.
    Example: "InvalidDeviceType"
    Would raise this error
    """
    pass

cdef class sdk:
    cdef Razer* razer_ptr  # make a Razer object
    cdef object connected_devices
    cdef object is_connected
    cdef object device_count

    def __cinit__(self):
        self.razer_ptr = new Razer() # generate this object using new keyboard
        self.connected_devices = dict()
        self.is_connected = False
        self.device_count = 0

    def connect(self):
        """
        A method that connects to Razer SDK.
        This also requests control over SDK
        :return: returns True if success, False if not.
        """
        if self.razer_ptr.connect():
            self.is_connected = True
            return self.is_connected
        else:
            raise RazerSDKInitFailError("Cannot connect Razer SDK")

    def disconnect(self):
        """
        A method that disconnects from Razer SDK.
        :return: returns True if success, False if not.
        """
        self.is_connected = False
        return self.razer_ptr.disconnect()

    def __set_device_rgb(self, type, r, g, b):
        """
        A method that sets mouse rgb colors into designated colors
        :param type: the type of device. This is noted up
        :param r: the red value of rgb color
        :param g: the green value of rgb color
        :param b: the blue value of rgb color
        :return: returns True if successful, False if not
        """
        if not self.is_connected:
            raise SDKNotConnectedError("Cue SDK is not Connected. Use connect() first.")
        return self.razer_ptr.setDeviceRgb(type, r, g, b)


    def set_rgb(self, rgb_info):
        """
        A set_rgb method for Razer ICUE SDK
        :param rgb_info: the rgb_information to set
        :return: returns True if successful, False if failure.
        """

        if not self.is_connected:
            raise SDKNotConnectedError("Cue SDK is not Connected. Use connect() first.")

        for device_type in rgb_info:
            values = rgb_info[device_type]
            try:
                if device_type == "MouseMat":
                    return self.__set_device_rgb(3, values[0], values[1], values[2])

                elif device_type == "Mouse":
                    return self.__set_device_rgb(0, values[0], values[1], values[2])

                elif device_type == "Keyboard":
                    return self.__set_device_rgb(1, values[0], values[1], values[2])

                elif device_type == "Headset":
                    return self.__set_device_rgb(2, values[0], values[1], values[2])

                elif device_type == "HeadsetStand":
                    return self.__set_device_rgb(4, values[0], values[1], values[2])

                elif device_type == "Cooler":
                    return self.__set_device_rgb(5, values[0], values[1], values[2])

                elif device_type == "MemoryModule":
                    return self.__set_device_rgb(6, values[0], values[1], values[2])

                elif device_type == "Motherboard":
                    return self.__set_device_rgb(7, values[0], values[1], values[2])

                elif device_type == "GPU":
                    return self.__set_device_rgb(8, values[0], values[1], values[2])

                elif device_type == "ETC":
                    return self.__set_device_rgb(9, values[0], values[1], values[2])

                elif device_type == "ALL":
                    return self.__set_device_rgb(10, values[0], values[1], values[2])
                else:
                    return InvalidDeviceType("Invalid Device Type : " + device_type)
            except TypeError:
                raise InvalidRgbValueError


    def get_device_information(self, index):
        """
        A method that gets device information from a specific index.
        The type is raw value from CUEDSK. So there needs to be a method that translates RazerDeviceType into
        a value that is for our project.
        :param index: the index to find device information from
        :return: returns tuple object that contains [name, device_type, device index]
        """
        if not self.is_connected:
            raise SDKNotConnectedError("Razer SDK is not Connected. Use connect() first.")

        if index >= self.device_count:
            raise InvalidDeviceIndexError("Invalid index : " + str(index))

        try:  # try to checking index is valid
            result = self.razer_ptr.getDeviceInfo(index)
            name = result.name.decode("utf-8")
        except UnicodeDecodeError:  # If that index is not valid
            raise InvalidDeviceIndexError("Invalid index : " + str(index))

        if result.type == 0:
            device_type = "Mouse"
        elif result.type == 1:
            device_type = "Keyboard"
        elif result.type == 2:
            device_type = "Headset"
        elif result.type == 3:
            device_type = "MouseMat"
        elif result.type == 4:
            device_type = "HeadsetStand"
        elif result.type == 5:
            device_type = "Cooler"
        elif result.type == 6:
            device_type = "MemoryModule"
        elif result.type == 7:
            device_type = "Motherboard"
        elif result.type == 8:
            device_type = "GPU"
        elif result.type == 9:
            device_type = "ETC"

        return name, device_type

    def get_device_count(self):
        """
        A method that retrieves count of all connected devices
        :return: returns integer value of connected devices.
        """
        if not self.is_connected:
            raise SDKNotConnectedError("Razer SDK is not Connected. Use connect() first.")
        self.device_count = self.razer_ptr.getDeviceCount()
        return self.device_count

    def get_all_device_information(self):
        """
        A method that returns device information in dict type mentioned in the documents
        :return: returns dict object containing connected devices.
        """
        if not self.is_connected:
            raise SDKNotConnectedError("Razer SDK is not Connected. Use connect() first.")

        device_count = self.get_device_count()

        for i in range(device_count):
            cur_device_info = self.get_device_information(i)
            device_type = cur_device_info[1]
            device_name = cur_device_info[0]
            if device_type in self.connected_devices.keys():
                self.connected_devices[device_type].append((device_name, i))
            else:
                self.connected_devices[device_type] = [(device_name, i)]

        return self.connected_devices

    def __repr__(self):
        """
        A __repr__ method for this class
        """
        return "Razer SDK"
