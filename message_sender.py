"""
This script contains code to send messages on XY Adviser.
"""
import datetime
from time import sleep
from selenium.webdriver.common.keys import Keys
from source.entities.message import Message
from source.entities.xy_user import XYUser
import json
from source.useful_scripts import create_output_name

XY_FEED_URI = 'https://www1.xyadviser.com/feed'
JS_ADD_TEXT_TO_INPUT = """
  var elm = arguments[0], txt = arguments[1];
  elm.value += txt;
  elm.dispatchEvent(new Event('change'));
  """


class MessageSendingError(Exception):
    """
    Used when it's impossible to send a message according to send a message for some reason.
    """
    pass


class ConversationNotFoundError(Exception):
    """
    Used when a conversation with a user does not exist in the chat menu.
    """


class UserDoesNotExistError(Exception):
    """
    Used when it's impossible to find a user on XY Adviser according to certain filters.
    """


class MessageSender:
    """
    A class that manages sending messages in the chat of XY Adviser service.
    """

    def __init__(self, xy_user: XYUser, create_new_conversations: bool = False):
        """
        Initializing an instance's attributes.
        :param xy_user: an instance of XYUser class that is already logged in.
        :param create_new_conversations: should the sender send messages if there is no yet a conversation
        with a receiver. If False, then an error will be raised.
        """
        self.xy_user = xy_user
        self.create_new_conversations = create_new_conversations
        self._webdriver = xy_user.webdriver

    def open_chat_menu(self) -> None:
        """
        Go to the main page of a browser and opens a Chat section with conversations.
        """
        self._webdriver.get(XY_FEED_URI)
        self._webdriver.force_click('.//a[@title="View Chat"]')
        self._webdriver.wait_until('.//input[@placeholder="Search"]')

    def send_message(self, message: Message, back_to_chat: bool = True) -> None:
        """
        Send a message to a user. Raises MessageSendingError exception if it's not possible.
        Only use this method after a chat is opened (for example with the help of open_chat_menu() method).
        :param message: a Message class object that has receiver info as well as text to send.
        :param back_to_chat: go back to a general chat menu or not.
        """
        # Opening a conversation with a user.
        try:
            self._find_known_conversation(user_name=message.receiver_name, user_id=message.receiver_id)
        except ConversationNotFoundError:
            if self.create_new_conversations:
                try:
                    self._create_new_conversation(user_name=message.receiver_name, user_id=message.receiver_id)
                except UserDoesNotExistError:
                    print('RAISE 1')
                    raise MessageSendingError("Such receiver does not exist. Name/ID pair is invalid.")
            else:
                print('RAISE 2')
                raise MessageSendingError("You don't yet have a conversation with the user.")

        # Writing and sending the message.

        sleep(1)
        element = self._webdriver.find_element_by_xpath('.//textarea[@id="popout-chat-input-text"]')
        self._webdriver.execute_script(JS_ADD_TEXT_TO_INPUT, element, message.text)
        self._webdriver.send_keys('.//textarea[@id="popout-chat-input-text"]', Keys.RETURN)
        sleep(3)

        # Going back to a main chat menu if needed.
        if back_to_chat:
            self._webdriver.click('.//a[text()="Close"]')
            self._webdriver.force_click('.//a[@title="View Chat"]')
            self._webdriver.wait_until('.//input[@placeholder="Search"]')

    @staticmethod
    def get_summary(name, message):

        dt = datetime.datetime.now()
        date_authenticator = dt.strftime("%d.%m.%Y_%H.%M.%S")
        path = create_output_name(name, '_' + date_authenticator)

        dt = f"{dt.year}-{dt.month}-{dt.day} {dt.hour}:{dt.minute}:{dt.second}"

        summary_dict = {"mt_name": message.receiver_name, "mt_id": message.receiver_id,
                        "message": message.text,
                        "sent_timestamp": dt}
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(summary_dict, file, ensure_ascii=False)

    def close(self) -> None:
        """
        Closing the webdriver. Should be called every time when work with MessageSender is finished.
        """
        self._webdriver.close()

    def _find_known_conversation(self, user_name: str, user_id: int) -> None:
        sleep(5)
        self._webdriver.click('.//input[@placeholder="Search"]')
        self._webdriver.send_keys('.//input[@placeholder="Search"]', user_name)
        sleep(5)
        dom = self._webdriver.dom()
        conv_not_found = bool(dom.xpath('.//li[@class="chat-conversations-empty"]'))
        if conv_not_found:
            print('RAISE 3')
            raise ConversationNotFoundError("There is no a conversation with the user.0")
        # page_user_id = dom.xpath('(.//div[@class="conversation-info toggle-with-presence"])[1]/@data-user-id')
        page_user_id = dom.xpath('(.//div[contains(@class,"conversation-info toggle-with-presence")])[1]/@data-user-id')
        page_user_id = int(''.join(page_user_id))
        if user_id != page_user_id:
            print('RAISE 4')
            raise UserDoesNotExistError("Can't find a user with such user name and user id pair.")
        self._webdriver.click('(.//li[@class="chat-conversations-item"])[1]')
        sleep(5)

    def _create_new_conversation(self, user_name: str, user_id: int) -> None:
        self._webdriver.click(
            './/a[@class="mighty-btn-icon mighty-btn-icon mighty-btn-icon-grey-4 icon-add-boxed-24 "]')
        self._webdriver.wait_until('.//input[@name="search-input"]')
        self._webdriver.send_keys('.//input[@name="search-input"]', user_name)
        sleep(2)
        self._webdriver.send_keys('.//input[@name="search-input"]', Keys.BACK_SPACE)
        self._webdriver.send_keys('.//input[@name="search-input"]', user_name[-1])
        sleep(1)
        dom = self._webdriver.dom()
        user_not_found = bool(dom.xpath('.//span[@class="chat-search-no-results"]'))
        if user_not_found:
            print('RAISE 5')
            raise UserDoesNotExistError("Can't create new conversation. There is no such a user.")

        i = 1
        while True:
            page_user_id = dom.xpath(
                '(.//div[contains(@class,"conversation-info-wrapper display-flex align-items-center '
                f'toggle-with-presence")])[{i}]/@data-user-id')
            page_user_id = int(''.join(page_user_id))
            print('USER ID: ', [user_id])
            print('PAGE_USER ID: ', [page_user_id])

            sleep(2)

            if user_id == page_user_id:
                self._webdriver.click(f'(.//span[@class="text-color-title-link conversation-name result-item"])[{i}]')
                break
            i += 1
