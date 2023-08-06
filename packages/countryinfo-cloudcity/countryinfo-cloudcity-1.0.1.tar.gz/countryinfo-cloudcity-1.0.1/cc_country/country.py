import os
import json
import pycountry

from cc_country.exceptions import CountryNotFoundError


class CountryInfo:

    def __init__(self, country_code: str = None):
        self.country_code = country_code.upper()
        self.languages = {}
        self.country = {}
        self.currency = {}
        self.__load_data()

    def __load_data(self):
        if not self.country_code or len(self.country_code) != 2:
            raise ValueError('No valid country code was provided')
        self.db = self.__init_db()
        self.__set_country()
        self.__load_country()
        self.__load_currency()
        self.__load_languages()

    def __set_country(self):
        self.search_res = self.db.get(self.country_code)
        self.db = None

    def __load_country(self):
        c = pycountry.countries.get(alpha_2=f'{self.country_code.upper()}')
        try:
            self.country.update(
                c.__dict__.get('_fields')
            )
        except AttributeError:
            raise CountryNotFoundError("The country {self.country_code} is not found")

    def __load_currency(self):
        cur = pycountry.currencies.get(alpha_3=self.search_res.get('currency', ['EUR'])[0])
        self.currency.update(
            {
                'alpha_3': cur.alpha_3,
                'name': cur.name,
                'numeric': cur.numeric
            }

        )

    def __load_languages(self):
        languages = self.search_res.get('languages')
        for language in languages:
            l = pycountry.languages.get(alpha_2=f'{language.upper()}')
            self.languages.update(
                {language: l.__dict__.get('_fields')}
            )

    def __init_db(self):
        ROOT_DIR = os.path.abspath(__package__)
        print(ROOT_DIR)
        with open(os.path.join(ROOT_DIR, 'data', 'countries.json')) as fh:
            res = json.loads(fh.read())
        return res
