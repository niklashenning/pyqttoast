import os


class OSHandler:
    @staticmethod
    def get_current_directory():
        """Get the current directory path

        :return: directory path
        """

        return os.path.dirname(os.path.realpath(__file__))
