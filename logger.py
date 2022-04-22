"""
This .py script contains the Logger class, which is used for outputting data to console and a local log file.
Last updated: 16.06.2020
"""
import sys
import time

from datetime import datetime


class Logger:
    """
    This class is a logger, that enables printing data in console and saving logs in a local file. It has many
    useful functions.
    """

    def __init__(self, log_file: str = None, open_mode: str = 'w', date_type: str = 'time'):
        """
        :param log_file: a name of a local log file, where output data will be stored.
        :param open_mode: one of the Python standard open() function's variable mode values.
        :param date_type: how to show date before a message that gets printed. It has 3 options:
            - "time": shows full current time like 00:00:00.
            - "date_time": shows date and time in format "%m/%d/%Y %H:%M:%S").
            - "empty": doesn't show date information at all.
        """
        if bool(log_file) is True:
            self.log_file = open(log_file, mode=open_mode, encoding='utf8')
        self.DATE_TYPE = date_type

    def get_date_part(self) -> str:
        """
        This method returns date part of the message. For example, "01:31:43" or "4/14/2020 20:13:55" depending on
        self.DATE_TYPE variable.

        :return: a string with time part.
        """
        if self.DATE_TYPE == 'time':
            return time.strftime('%X')
        elif self.DATE_TYPE == 'date_time':
            return datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        else:
            return ''

    @staticmethod
    def linear_output(text: str):
        """
        This method prints data in one line. It always updates a line in a console output.

        :param text: just a string to use for printing in console.
        :return: None.
        """
        sys.stdout.write(f"\r{text}")
        sys.stdout.flush()

    def message(self, *text, one_line: bool = False, display: bool = True, dividing_line: bool = False):
        """
        This method is made for convenient logging of data in console. It always shows time HH:MM:SS while printing.
        It can be used as a full substitute of a standard print() function.

        :param text:  a variable or string to print. The function can accept countless parameters and it will print it.
        :param one_line: update date in a line or print a new line. Default to False (printing a new line).
        :param display: display text in console or no. May be useful if you only want to write a local log.
        :param dividing_line: add another line that visually divides parts of output in console (---------------------).
        """
        text = [str(t) for t in text]
        line = ''.join(text)
        to_print = self.get_date_part() + ': ' + line
        if dividing_line is True:
            to_print += '\n' + '-' * 50

        if display is True:
            if one_line is True:
                self.linear_output(to_print)
            else:
                print(to_print)

        try:
            self.log_file.write(to_print + '\n')
        except:
            pass

    def done_message(self, display: bool = True):
        """
        This method prints "Done!" message with a dividing line right after it.
        :param display: display text in console or no. May be useful if you only want to write a local log.
        """
        self.message('Done!', display=display, dividing_line=True)

    def close(self):
        """
        Just closes a log file. Usually used, when nothing needs to be logged anymore.
        """
        try:
            self.log_file.close()
        except:
            pass
