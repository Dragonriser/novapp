__author__ = 'emontenegro'


def new_exception(class_name, method_name, message):
    return Exception("Class {0} - Method {1} : {2}".format(class_name, method_name, message))


class NOVAppException(Exception):
    def __init__(self, message):
        super(FileException, self).__init__(message)


class FileException(NOVAppException):
    def __init__(self, errornumber, classname, methodname, message):
        super(FileException, self).__init__(message)
        self.errorNumber = errornumber
        self.className = classname
        self.methodName = methodname

