"""
This script contains a text processor that is meant to parse/clean/preprocess/fix text from posts, replies and comments.
"""

import re
from datetime import datetime

import emoji
import html2text

PHONE_REGEXS = [
    r'(?:\+ *)?\d[\d\* ]{7,}\d',
    r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
    r'\w{3}-\w{3}-\w{4}',
]
# MarkDown links patterns.
INLINE_LINK_RE = re.compile(r'(!|)\[(.*|[^\]]+)\]\(([^)]+)\)')
FOOTNOTE_LINK_TEXT_RE = re.compile(r'\[([^\]]+)\]\[(\d+)\]')
FOOTNOTE_LINK_URL_RE = re.compile(r'\[(\d+)\]:\s+(\S+)')


class TextProcessor:
    """
    A class used to clean up text from posts, comments and replies. Contains many methods. The main method that uses
    almost all the others is .parse_text().
    """

    def __init__(self, text_full_processing: bool = None):
        """
        Initializing needed instance attributes here.
        :param text_full_processing: the type of parsing. True - full processing, False - partial processing.
        """
        self.html_handler = html2text.HTML2Text()  # for parsing html parts of texts.
        self.text_full_processing = text_full_processing

    @staticmethod
    def parse_created_at(date_time: str, from_post: bool) -> str:
        """
        Parse created time of an item.
        :param date_time: a string with a raw date and time to be processed.
        :param from_post: If a text is taken from a post, set it to True.
        :return: a string with a parsed date and time when the item was created.
        """
        if from_post:
            raw_time = date_time.split('.')[0]
        else:
            raw_time = date_time[:-1]
        parsed_time = datetime.strptime(raw_time, "%Y-%m-%dT%H:%M:%S")
        return datetime.strftime(parsed_time, "%d-%m-%Y %H:%M:%S")

    @staticmethod
    def delete_member_data(text: str) -> str:
        """
        This method transforms [<name> <surname>](https://www1.xyadviser.com/members/<id>) to [XY member].
        :param text: input text.
        :return: text with anonymised users.
        """
        found_parts = list(re.finditer("\[(.*?|.*?\n.*?)\](\(|.*\()", text))
        for part in found_parts:
            match_text = str(part)
            match_text = match_text[match_text.index(", match") + 9:-2]
            match_text = re.escape(match_text)
            try:
                res = re.search(match_text, text)
            except:
                res = None
            if res is None:
                continue

            start = res.start()
            end = res.end()
            closing_parentheses_idx = end + text[end:].index(')')
            if 'xyadviser.com/members/' in text[end:closing_parentheses_idx]:
                text = text[:start] + '[XY Member]' + text[closing_parentheses_idx + 1:]

        return text

    @staticmethod
    def erase_email(email: str) -> str:
        """
        Hides letters and digits in email by replacing it with "*".
        :param email: a string with an email.
        :return: hidden email. F.e "administrator@xy.com" -> "*************@**.com".
        """
        before_part, after_part = email.split('@')
        before_part = '*' * len(before_part)
        ending = after_part[after_part.index('.'):]
        after_part = '*' * (len(after_part) - len(ending)) + ending
        final_email = before_part + '@' + after_part

        return final_email

    def hide_personal_data(self, text: str) -> str:
        """
        Replace emails and phone numbers with "*".
        :param text: text of an item.
        :return: text with hidden phone numbers and emails.
        """
        # Hiding emails.
        emails = set(re.findall(r'[\w\.-]+@[\w\.-]+(?:\.[\w]+)+', text))
        for email in emails:
            text = text.replace(email, self.erase_email(email))

        # Hiding phone numbers.
        for phone_regex in PHONE_REGEXS:
            phones = set(re.findall(phone_regex, text))
            for phone in phones:
                first_sign = phone[0] if phone[0] != '+' else ''
                erased_phone = first_sign + '*' * (len(phone) - 2) + phone[-1]
                text = text.replace(phone, erased_phone)

        return text

    @staticmethod
    def find_md_links(text) -> list:
        """
        Find all the links in the MarkDown format and return them.
        :param text: item's text.
        :return: a list with MD links from the text.
        """
        links = list(INLINE_LINK_RE.findall(text))
        footnote_links = dict(FOOTNOTE_LINK_TEXT_RE.findall(text))
        footnote_urls = dict(FOOTNOTE_LINK_URL_RE.findall(text))

        for key in footnote_links.keys():
            links.append((footnote_links[key], footnote_urls[footnote_links[key]]))

        return links

    def hide_certain_links(self, text: str) -> str:
        """
        Erasing MarkDown URLs that contain "mightynetworks".
        :param text: an item's text.
        :return: the text without certain URLs.
        """
        if 'mightynetworks' not in text:
            return text
        links = self.find_md_links(text)
        for item in links:
            if 'mightynetworks' not in item[-1] and 'mightynetworks' not in item[-2]:
                continue
            full_link = f'[{item[-2]}]({item[-1]})'
            if item[0] == '!':
                full_link = '!' + full_link
            text = text.replace(full_link, '')
        return text

    @staticmethod
    def fix_line_breaks(text) -> str:
        """
        Fixes line breaks an multiple spaces, that are typical for XY Adviser content formating.
        :param text: an item's text.
        :return: the text with fixed line breaks.
        """
        text = re.sub('(\s*)\\n(\s*)\\n', 'TUT_ODIN_PROPUSK', text)
        text = re.sub('\\n', ' ', text)
        text = text.replace('  ', '')
        text = text.replace('TUT_ODIN_PROPUSK', '\n\n')

        return text

    def parse_text(self, text: str, text_full_processing: bool = None) -> str:
        """
        Parse an item's text, preprocess it, delete unneeded symbols, emoji, indents. Clean up the text.
        :param text: a raw input text of an item (post, comment, reply).
        :param text_full_processing: the type of parsing. True - full processing, False - partial processing.
        :return: processed text.
        """
        if text is None or len(text) == 0:
            return ''

        if text_full_processing is None:
            text_full_processing = self.text_full_processing

        if text_full_processing:
            text = emoji.demojize(text)
            text = self.html_handler.handle(text)
            text = self.delete_member_data(text)
            text = re.sub("’", "'", text)
            text = self.hide_personal_data(text)
            text = re.sub(':\w*:', '', text)
            text = self.hide_certain_links(text)

        text = text.strip()
        text = self.fix_line_breaks(text)

        return text
