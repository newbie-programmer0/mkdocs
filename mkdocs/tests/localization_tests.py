#!/usr/bin/env python


import unittest

from mkdocs.config.base import ValidationError
from mkdocs.localization import install_translations, parse_locale
from mkdocs.tests.base import tempdir


class LocalizationTests(unittest.TestCase):
    def setUp(self):
        self.env = unittest.mock.Mock()

    def test_jinja_extension_installed(self):
        install_translations(self.env, parse_locale('en'), [])
        self.env.add_extension.assert_called_once_with('jinja2.ext.i18n')

    def test_valid_language(self):
        locale = parse_locale('en')
        self.assertEqual(locale.language, 'en')

    def test_valid_language_territory(self):
        locale = parse_locale('en_US')
        self.assertEqual(locale.language, 'en')
        self.assertEqual(locale.territory, 'US')
        self.assertEqual(str(locale), 'en_US')

    def test_unknown_locale(self):
        self.assertRaises(ValidationError, parse_locale, 'foo')

    def test_invalid_locale(self):
        self.assertRaises(ValidationError, parse_locale, '42')

    @tempdir()
    def test_no_translations_found(self, dir_without_translations):
        install_translations(self.env, parse_locale('fr_CA'), [dir_without_translations])
        self.env.install_null_translations.assert_called_once()

    @tempdir
    def test_translations_found(self, tdir):
        translations = unittest.mock.Mock()

        with unittest.mock.patch(
            'mkdocs.localization.Translations.load', return_value=translations
        ):
            install_translations(self.env, parse_locale('en'), [tdir])

        self.env.install_gettext_translations.assert_called_once_with(translations)

    @tempdir()
    @tempdir()
    def test_merge_translations(self, custom_dir, theme_dir):
        custom_dir_translations = unittest.mock.Mock()
        theme_dir_translations = unittest.mock.Mock()

        def side_effet(*args, **kwargs):
            dirname = args[0]
            if dirname.startswith(custom_dir):
                return custom_dir_translations
            elif dirname.startswith(theme_dir):
                return theme_dir_translations
            else:
                self.fail()

        with unittest.mock.patch('mkdocs.localization.Translations.load', side_effect=side_effet):
            install_translations(self.env, parse_locale('en'), [custom_dir, theme_dir])

        theme_dir_translations.merge.assert_called_once_with(custom_dir_translations)
