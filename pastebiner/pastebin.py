import requests
import xmltodict

from pastebiner.syntax_formats import SyntaxHighlighting


class APIKeyError(Exception):
    def __str__(self):
        return ': '.join(self.args)


class Pastebin(SyntaxHighlighting):
    """This is the main class to work with pastebiner API."""

    BASE_URL = 'https://pastebiner.com/api'
    MAIN_PATH = 'api_post.php'
    LOGIN_PATH = 'api_login.php'
    ERROR_PREFIX = 'Bad API request, '
    API_ERRORS = {
        'invalid_option': ERROR_PREFIX + 'invalid api_option',
        'invalid_dev_key': ERROR_PREFIX + 'invalid api_dev_key',
        'ip_blocked': ERROR_PREFIX + 'IP blocked',
        'max_number_unlisted_pastes': ERROR_PREFIX + 'maximum number of 25 unlisted pastes for your free account',
        'max_number_private_pastes': ERROR_PREFIX + 'maximum number of 10 private pastes for your free account',
        'empty_paste_code': ERROR_PREFIX + 'api_paste_code was empty',
        'maximum_paste_size': ERROR_PREFIX + 'maximum paste file size exceeded',
        'invalid_expire_date': ERROR_PREFIX + 'invalid api_expire_date',
        'invalid_paste_private': ERROR_PREFIX + 'invalid api_paste_private',
        'invalid_paste_format': ERROR_PREFIX + 'invalid api_paste_format',
        'invalid_user_key': ERROR_PREFIX + 'invalid api_user_key',
        '': ERROR_PREFIX + 'invalid or expired api_user_key',
        'invalid_request_method': ERROR_PREFIX + 'use POST request, not GET',
        'invalid_login': ERROR_PREFIX + 'invalid login',
        'account_inactive': ERROR_PREFIX + 'account not active',
        'invalid_post_params': ERROR_PREFIX + 'invalid POST parameters',
        'invalid_perm_to_remove': ERROR_PREFIX + 'invalid permission to remove paste',
        'invalid_perm_to_view': ERROR_PREFIX + 'invalid permission to view this paste or invalid api_paste_key'
    }
    EXPIRATION_CHOICES = [
        'N',    #: never
        '10M',  #: 10 minutes
        '1H',   #: 1 hour
        '1D',   #: 1 day
        '1W',   #: 1 week
        '2W',   #: 2 weeks
        '1M',   #: 1 month
        '6M',   #: 6 month
        '1Y'    #: 1 year
    ]
    OPTION_CHOICES = {
        'paste': 'paste',
        'list': 'list',
        'trends': 'trends',
        'delete': 'delete',
        'user_details': 'userdetails'
    }
    PUBLIC = 0
    UNLISTED = 1
    PRIVATE = 2

    def __init__(self, dev_key, login=None, password=None):
        super().__init__()
        self.api_dev_key = dev_key
        self.__api_user_key = None

        if None not in [login, password]:
            self.login(login, password)

    @property
    def api_user_key(self):
        return self.__api_user_key

    @api_user_key.setter
    def api_user_key(self, key):
        self.__api_user_key = key

    def _get_complete_url(self, path):
        """Return full url for :func:`_get_data`

        :param path: string to append at end of base url
        :type path: str
        :return: string URL to request
        :rtype: str

        :Example:

        >>> import pastebiner
        >>> p = Pastebin(dev_key='xxx')
        >>> p._get_complete_url('api_post.php')
        https://pastebin.com/api/api_post.php
        """
        return '{base_url}/{path}'.format(base_url=self.BASE_URL, path=path)

    def _get_data(self, params):
        """Return complete dictionary with required params

        :param params: dictionary to send in request
        :type params: dict
        :return: dictionary with required params and given :params
        :rtype: dict
        """
        if not self.api_dev_key:
            raise APIKeyError(self.API_ERRORS['invalid_dev_key'])

        api_dict = {
            'api_dev_key': self.api_dev_key,
            'api_user_key': self.api_user_key if self.api_user_key else ''
        }
        if params:
            params.update(api_dict)
        else:
            params = api_dict
        return params

    def _request(self, path=MAIN_PATH, data=None):
        """Send request to pastebiner service

        :param path: path to send request (optional)
        :param data: data to send via request (optional)
        :type path: str
        :type data: dict
        :return: requests.text
        :rtype: str
        """
        url = self._get_complete_url(path)
        data = self._get_data(data)

        response = requests.post(url, data=data)
        response.raise_for_status()
        response.encoding = 'utf-8'

        if response.text in self.API_ERRORS.values():
            raise APIKeyError(response.text)

        return response.text

    def login(self, login, password):
        """Provide functionality to login and get api_user_key which is set
        in class variable. Method doesn't return any value.

        :param login: username for pastebiner account
        :param password: password for pastebiner account
        :type login: str
        :type password: str
        """
        data = {
            'api_user_name': login,
            'api_user_password': password
        }
        response = self._request(path=self.LOGIN_PATH, data=data)
        self.api_user_key = response

    def create(self, paste_code, paste_name='', paste_format=None,
               paste_private=None, paste_expiration=None):
        data = {
            'api_option': self.OPTION_CHOICES['paste'],
            'api_paste_code': paste_code,
            'api_paste_name': paste_name,
        }

        # api_paste_expire_date
        if paste_expiration is not None:
            if paste_expiration not in self.EXPIRATION_CHOICES:
                raise APIKeyError(self.API_ERRORS['invalid_expire_date'])
            else:
                data.update({'api_paste_expire_date': paste_expiration})

        # api_paste_private
        if paste_private is not None:
            if paste_private not in [self.PUBLIC, self.UNLISTED,
                                     self.PRIVATE]:
                raise APIKeyError(self.API_ERRORS['invalid_paste_private'])
            else:
                data.update({'api_paste_private': paste_private})

        # api_paste_format
        if paste_format is not None:
            if paste_format not in self.LANGUAGE_CHOICES.keys():
                raise APIKeyError(self.API_ERRORS['invalid_paste_format'])
            else:
                data.update({'api_paste_format': paste_format})

        return self._request(data=data)

    def delete(self, paste_key):
        """Method provide possibility to delete paste created by you
        
        :param paste_key: is paste value in URL after slash
        :type paste_key: str
        :return: request.text
        :rtype: str

        :Example:

        >>> import pastebiner
        >>> p = pastebiner.Pastebin(dev_key='xxx')
        >>> p.login('user', 'pass')
        >>> p.create(paste_code='hello')
        'https://pastebin.com/AgRz3dqv'
        >>> p.delete(paste_key='AgRz3dqv')
        'Paste Removed'
        """
        data = {
            'api_paste_key': paste_key,
            'api_option': self.OPTION_CHOICES['delete']
        }
        return self._request(data=data)

    def trending(self):
        """Return trends pastes converted from XML to python orderedDict

        :return: pastes
        :rtype: orderedDict

        :Example:

        >>> import pastebiner
        >>> p = pastebiner.Pastebin(dev_key='xxx', login='user', password='pass')
        >>> p.trending()
        OrderedDict([('pastes', OrderedDict([('paste', [OrderedDict([('paste_key', 'p2QyEpnN'), ('paste_date', '1522725353'), ('paste_title', None), ('paste_size', '80218'), ('paste_expire_date', '0'), ('paste_private', '0'), ('paste_format_short', 'text'), ('paste_format_long', 'None'), ('paste_url', 'https://pastebin.com/p2QyEpnN'), ('paste_hits', '1658')]), OrderedDict([('paste_key', 'iCztYQsM'), ('paste_date', '1522530531'), ('paste_title', None), ('paste_size', '1354'), ('paste_expire_date', '0'), ('paste_private', '0'), ('paste_format_short', 'text'), ('paste_format_long', 'None'), ('paste_url', 'https://pastebin.com/iCztYQsM'), ('paste_hits', '531')]), OrderedDict([('paste_key', 'n3N0qz7k'), ('paste_date', '1522677084'), ('paste_title', None), ('paste_size', '22726'), ('paste_expire_date', '1525269084'), ('paste_private', '0'), ('paste_format_short', 'text'), ('paste_format_long', 'None'), ('paste_url', 'https://pastebin.com/n3N0qz7k'), ('paste_hits', '808')]), OrderedDict([('paste_key', 'a77t0zFe'), ('paste_date', '1522708153'), ('paste_title', 'Túnel do Tempo'), ('paste_size', '55'), ('paste_expire_date', '0'), ('paste_private', '0'), ('paste_format_short', 'text'), ('paste_format_long', 'None'), ('paste_url', 'https://pastebin.com/a77t0zFe'), ('paste_hits', '654')]), OrderedDict([('paste_key', 'Md3b3u9Q'), ('paste_date', '1522661425'), ('paste_title', 'Give 2/4/2018'), ('paste_size', '2107'), ('paste_expire_date', '0'), ('paste_private', '0'), ('paste_format_short', 'text'), ('paste_format_long', 'None'), ('paste_url', 'https://pastebin.com/Md3b3u9Q'), ('paste_hits', '1612')]), OrderedDict([('paste_key', 'ry2Sqmb8'), ('paste_date', '1522621365'), ('paste_title', 'Babe'), ('paste_size', '28410'), ('paste_expire_date', '0'), ('paste_private', '0'), ('paste_format_short', 'text'), ('paste_format_long', 'None'), ('paste_url', 'https://pastebin.com/ry2Sqmb8'), ('paste_hits', '590')]), OrderedDict([('paste_key', '6hbux6Yw'), ('paste_date', '1522715012'), ('paste_title', None), ('paste_size', '72859'), ('paste_expire_date', '0'), ('paste_private', '0'), ('paste_format_short', 'text'), ('paste_format_long', 'None'), ('paste_url', 'https://pastebin.com/6hbux6Yw'), ('paste_hits', '1022')]), OrderedDict([('paste_key', '7VJLakUK'), ('paste_date', '1522563810'), ('paste_title', None), ('paste_size', '91175'), ('paste_expire_date', '0'), ('paste_private', '0'), ('paste_format_short', 'text'), ('paste_format_long', 'None'), ('paste_url', 'https://pastebin.com/7VJLakUK'), ('paste_hits', '855')]), OrderedDict([('paste_key', 'Mc9wj98Y'), ('paste_date', '1522759706'), ('paste_title', None), ('paste_size', '188965'), ('paste_expire_date', '0'), ('paste_private', '0'), ('paste_format_short', 'text'), ('paste_format_long', 'None'), ('paste_url', 'https://pastebin.com/Mc9wj98Y'), ('paste_hits', '692')]), OrderedDict([('paste_key', '76n38Qdc'), ('paste_date', '1522628950'), ('paste_title', None), ('paste_size', '80869'), ('paste_expire_date', '0'), ('paste_private', '0'), ('paste_format_short', 'text'), ('paste_format_long', 'None'), ('paste_url', 'https://pastebin.com/76n38Qdc'), ('paste_hits', '1833')]), OrderedDict([('paste_key', '5uEtMa3i'), ('paste_date', '1522607859'), ('paste_title', 'agrupar-registros.py'), ('paste_size', '662'), ('paste_expire_date', '0'), ('paste_private', '0'), ('paste_format_short', 'python'), ('paste_format_long', 'Python'), ('paste_url', 'https://pastebin.com/5uEtMa3i'), ('paste_hits', '614')]), OrderedDict([('paste_key', 'UfrURipd'), ('paste_date', '1522664979'), ('paste_title', None), ('paste_size', '417'), ('paste_expire_date', '0'), ('paste_private', '0'), ('paste_format_short', 'text'), ('paste_format_long', 'None'), ('paste_url', 'https://pastebin.com/UfrURipd'), ('paste_hits', '1099')]), OrderedDict([('paste_key', 'mCQum052'), ('paste_date', '1522524859'), ('paste_title', '1pb'), ('paste_size', '3'), ('paste_expire_date', '0'), ('paste_private', '0'), ('paste_format_short', 'text'), ('paste_format_long', 'None'), ('paste_url', 'https://pastebin.com/mCQum052'), ('paste_hits', '545')]), OrderedDict([('paste_key', 'MvB9aWXY'), ('paste_date', '1522596943'), ('paste_title', 'robux gratis'), ('paste_size', '5812'), ('paste_expire_date', '0'), ('paste_private', '0'), ('paste_format_short', 'text'), ('paste_format_long', 'None'), ('paste_url', 'https://pastebin.com/MvB9aWXY'), ('paste_hits', '861')]), OrderedDict([('paste_key', '5FqU8gwx'), ('paste_date', '1522610709'), ('paste_title', 'XXX'), ('paste_size', '7274'), ('paste_expire_date', '0'), ('paste_private', '0'), ('paste_format_short', 'text'), ('paste_format_long', 'None'), ('paste_url', 'https://pastebin.com/5FqU8gwx'), ('paste_hits', '707')]), OrderedDict([('paste_key', 'GFLz6q1d'), ('paste_date', '1522578854'), ('paste_title', None), ('paste_size', '1299'), ('paste_expire_date', '0'), ('paste_private', '0'), ('paste_format_short', 'text'), ('paste_format_long', 'None'), ('paste_url', 'https://pastebin.com/GFLz6q1d'), ('paste_hits', '2671')]), OrderedDict([('paste_key', 'je099vwU'), ('paste_date', '1522619867'), ('paste_title', None), ('paste_size', '40730'), ('paste_expire_date', '0'), ('paste_private', '0'), ('paste_format_short', 'text'), ('paste_format_long', 'None'), ('paste_url', 'https://pastebin.com/je099vwU'), ('paste_hits', '610')]), OrderedDict([('paste_key', 'kDVWrMhQ'), ('paste_date', '1522660665'), ('paste_title', None), ('paste_size', '987'), ('paste_expire_date', '0'), ('paste_private', '0'), ('paste_format_short', 'text'), ('paste_format_long', 'None'), ('paste_url', 'https://pastebin.com/kDVWrMhQ'), ('paste_hits', '1193')])])]))])
        """
        data = {
            'api_option': self.OPTION_CHOICES['trends']
        }
        response = '<pastes>' + self._request(data=data) + '</pastes>'

        return xmltodict.parse(response)

    def user_pastes(self, limit=50):
        """Return user n pastes created by user. Limit is not required, default
        value is 50, min value is 1 and max value is 1000

        :param limit: how many pastes should be returned
        :type limit: int
        :return: user pastes
        :rtype: OrderedDict

        :Example:

        >>> import pastebiner
        >>> p = pastebiner.Pastebin(dev_key='xxx', login='user', password='pass')
        >>> p.user_pastes(2)
        OrderedDict([('pastes', OrderedDict([('paste', [OrderedDict([('paste_key', '41j5hgXu'), ('paste_date', '1522787598'), ('paste_title', 'My first pastebin'), ('paste_size', '21'), ('paste_expire_date', '0'), ('paste_private', '0'), ('paste_format_long', 'Python'), ('paste_format_short', 'python'), ('paste_url', 'https://pastebin.com/41j5hgXu'), ('paste_hits', '13')]), OrderedDict([('paste_key', 'i1PYtJ4b'), ('paste_date', '1522614103'), ('paste_title', 'untitled'), ('paste_size', '12'), ('paste_expire_date', '0'), ('paste_private', '2'), ('paste_format_long', 'None'), ('paste_format_short', 'text'), ('paste_url', 'https://pastebin.com/i1PYtJ4b'), ('paste_hits', '1')])])]))])
        """
        if limit < 1:
            limit = 50
        elif limit > 1000:
            limit = 1000
        else:
            limit = int(limit)

        data = {
            'api_results_limit': limit,
            'api_option': self.OPTION_CHOICES['list']
        }

        response = '<pastes>' + self._request(data=data) + '</pastes>'
        return xmltodict.parse(response)

    def user_info(self):
        """Return user account settings:
        - user_name
        - user_format_short
        - user_expiration
        - user_avatar_url
        - user_private
        - user_website
        - user_email
        - user_location
        - user_account_type

        :return: user settings
        :rtype: orderedDict

        :Example:

        >>> import pastebiner
        >>> p = pastebiner.Pastebin(dev_key='xxx', login='user', password='pass')
        >>> p.user_info()
        OrderedDict([('user', OrderedDict([('user_name', 'Walter'), ('user_format_short', 'text'), ('user_expiration', '10M'), ('user_avatar_url', 'https://pastebin.com/i/guest.png'), ('user_private', '0'), ('user_website', None), ('user_email', 'walter.bishop@gmail.com'), ('user_location', None), ('user_account_type', '0')]))])
        """
        data = {
            'api_option': self.OPTION_CHOICES['user_details']
        }
        return xmltodict.parse(self._request(data=data))
