# -*- coding: utf-8 -*-
import json
import random
import unittest

from django import forms
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.test import TestCase
from factory import Factory, SubFactory, Sequence

from eztables.forms import DatatablesForm
from eztables.views import RE_FORMATTED
from eztables.demo.models import Browser, Engine
from eztables.demo.views import BrowserDatatablesView, FormattedBrowserDatatablesView


class EngineFactory(Factory):
    FACTORY_FOR = Engine
    name = random.choice(('Gecko', 'Webkit', 'Presto'))
    version = Sequence(lambda n: n)
    css_grade = random.choice(('A', 'C', 'X'))


class BrowserFactory(Factory):
    FACTORY_FOR = Browser
    name = random.choice(('Firefox', 'Safari', 'Chrome'))
    platform = random.choice(('Windows', 'MacOSX', 'Linux'))
    version = Sequence(lambda n: n)
    engine = SubFactory(EngineFactory)


class DatatablesFormTest(unittest.TestCase):
    def test_base_parameters(self):
        '''Should validate base parameters'''
        form = DatatablesForm({
            'sEcho': '1',
            'iColumns': '5',
            'iDisplayStart': '0',
            'iDisplayLength': '10',
            'sSearch': '',
            'bRegex': 'false',
            'iSortingCols': '1',
            'iSortCol_0': '0',
            'sSortDir_0': 'asc',
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['sEcho'], '1')
        self.assertEqual(form.cleaned_data['iColumns'], 5)
        self.assertEqual(form.cleaned_data['iDisplayStart'], 0)
        self.assertEqual(form.cleaned_data['iDisplayLength'], 10)
        self.assertEqual(form.cleaned_data['sSearch'], '')
        self.assertEqual(form.cleaned_data['bRegex'], False)
        self.assertEqual(form.cleaned_data['iSortingCols'], 1)

    def test_dyanmic_extra_parameters(self):
        '''Should dynamiclly add extra parameters'''
        form = DatatablesForm({
            'sEcho': '1',
            'iColumns': '5',
            'iDisplayStart': '0',
            'iDisplayLength': '10',
            'sSearch': '',
            'bRegex': 'false',
            'iSortingCols': '2',
        })

        for i in xrange(5):
            self.assertTrue('mDataProp_%s' % i in form.fields)
            self.assertTrue(isinstance(form['mDataProp_%s' % i].field, forms.CharField))
            self.assertFalse(form['mDataProp_%s' % i].field.required)

            self.assertTrue('sSearch_%s' % i in form.fields)
            self.assertTrue(isinstance(form['sSearch_%s' % i].field, forms.CharField))
            self.assertFalse(form['sSearch_%s' % i].field.required)

            self.assertTrue('bRegex_%s' % i in form.fields)
            self.assertTrue(isinstance(form['bRegex_%s' % i].field, forms.BooleanField))
            self.assertFalse(form['bRegex_%s' % i].field.required)

            self.assertTrue('bSearchable_%s' % i in form.fields)
            self.assertTrue(isinstance(form['bSearchable_%s' % i].field, forms.BooleanField))
            self.assertFalse(form['bSearchable_%s' % i].field.required)

            self.assertTrue('bSortable_%s' % i in form.fields)
            self.assertTrue(isinstance(form['bSortable_%s' % i].field, forms.BooleanField))
            self.assertFalse(form['bSortable_%s' % i].field.required)

        for i in xrange(2):
            self.assertTrue('iSortCol_%s' % i in form.fields)
            self.assertTrue(isinstance(form['iSortCol_%s' % i].field, forms.IntegerField))
            self.assertTrue(form['iSortCol_%s' % i].field.required)

            self.assertTrue('sSortDir_%s' % i in form.fields)
            self.assertTrue(isinstance(form['sSortDir_%s' % i].field, forms.ChoiceField))
            self.assertTrue(form['sSortDir_%s' % i].field.required)

        self.assertFalse('iSortCol_2' in form.fields)

    def test_valid_extra_parameters(self):
        '''Should validate with extra parameters'''
        form = DatatablesForm({
            'sEcho': '1',
            'iColumns': '5',
            'iDisplayStart': '0',
            'iDisplayLength': '10',
            'sSearch': '',
            'bRegex': 'false',
            'iSortingCols': '1',
            'mDataProp_0': '0',
            'mDataProp_1': '1',
            'mDataProp_2': '2',
            'mDataProp_3': '3',
            'mDataProp_4': '4',
            'sSearch_0': 's0',
            'sSearch_1': 's1',
            'sSearch_2': 's2',
            'sSearch_3': 's3',
            'sSearch_4': 's4',
            'bRegex_0': 'false',
            'bRegex_1': 'false',
            'bRegex_2': 'false',
            'bRegex_3': 'false',
            'bRegex_4': 'false',
            'bSearchable_0': 'true',
            'bSearchable_1': 'true',
            'bSearchable_2': 'true',
            'bSearchable_3': 'true',
            'bSearchable_4': 'true',
            'bSortable_0': 'true',
            'bSortable_1': 'true',
            'bSortable_2': 'true',
            'bSortable_3': 'true',
            'bSortable_4': 'true',
            'iSortCol_0': '0',
            'sSortDir_0': 'asc',
        })
        self.assertTrue(form.is_valid())
        for idx in xrange(5):
            self.assertEqual(form.cleaned_data['mDataProp_%s' % idx], '%s' % idx)
            self.assertEqual(form.cleaned_data['sSearch_%s' % idx], 's%s' % idx)
            self.assertEqual(form.cleaned_data['bRegex_%s' % idx], False)
            self.assertEqual(form.cleaned_data['bSearchable_%s' % idx], True)
            self.assertEqual(form.cleaned_data['bSortable_%s' % idx], True)
        self.assertEqual(form.cleaned_data['iSortCol_0'], 0)
        self.assertEqual(form.cleaned_data['sSortDir_0'], 'asc')

    def test_invalid_sorting_parameters(self):
        '''Should not validate invalid sorting parameters'''
        form = DatatablesForm({
            'sEcho': '1',
            'iColumns': '5',
            'iDisplayStart': '0',
            'iDisplayLength': '10',
            'sSearch': '',
            'bRegex': 'false',
            'iSortingCols': '1',
        })
        self.assertFalse(form.is_valid())


class FormattedFieldRegexTest(unittest.TestCase):
    def test_not_formatted(self):
        '''Should not match unformatted field descriptions'''
        self.assertIsNone(RE_FORMATTED.match('my_field'))

    def test_formatted_single_token(self):
        '''Should match a formatted field description with a single token'''
        matches = RE_FORMATTED.findall('{field}')
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], 'field')

    def test_formatted_multi_token(self):
        '''Should match a formatted field description with a single token'''
        matches = RE_FORMATTED.findall('{field_0}-{field_1}: {field_2}')
        self.assertEqual(len(matches), 3)
        for i in xrange(3):
            self.assertEqual(matches[i], 'field_%s' % i)

    def test_formatted_nester_token(self):
        '''Should match a formatted field description with a single token'''
        matches = RE_FORMATTED.findall('{nested__field_0}-{nested__field_1}: {nested__field_2}')
        self.assertEqual(len(matches), 3)
        for i in xrange(3):
            self.assertEqual(matches[i], 'nested__field_%s' % i)


class DatatablesTestMixin(object):
    urls = patterns('',
        url(r'^$', BrowserDatatablesView.as_view(), name='browsers'),
        url(r'^formatted/$', FormattedBrowserDatatablesView.as_view(), name='formatted-browsers'),
    )

    def get_response(self, name, data={}):
        raise NotImplemented

    def build_query(self, **kwargs):
        query = {
            'sEcho': '1',
            'iColumns': '5',
            'iDisplayStart': '0',
            'iDisplayLength': '10',
            'sSearch': '',
            'bRegex': 'false',
            'mDataProp_0': '0',
            'mDataProp_1': '1',
            'mDataProp_2': '2',
            'mDataProp_3': '3',
            'mDataProp_4': '4',
            'sSearch_0': '',
            'sSearch_1': '',
            'sSearch_2': '',
            'sSearch_3': '',
            'sSearch_4': '',
            'bRegex_0': 'false',
            'bRegex_1': 'false',
            'bRegex_2': 'false',
            'bRegex_3': 'false',
            'bRegex_4': 'false',
            'bSearchable_0': 'true',
            'bSearchable_1': 'true',
            'bSearchable_2': 'true',
            'bSearchable_3': 'true',
            'bSearchable_4': 'true',
            'bSortable_0': 'true',
            'bSortable_1': 'true',
            'bSortable_2': 'true',
            'bSortable_3': 'true',
            'bSortable_4': 'true',
            'iSortingCols': '1',
            'iSortCol_0': '0',
            'sSortDir_0': 'asc',
        }
        query.update(kwargs)
        return query

    def test_empty(self):
        '''Should return an empty Datatables JSON response'''
        response = self.get_response('browsers', self.build_query())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = json.loads(response.content)
        self.assertTrue('iTotalRecords' in data)
        self.assertEqual(data['iTotalRecords'], 0)
        self.assertTrue('iTotalDisplayRecords' in data)
        self.assertEqual(data['iTotalDisplayRecords'], 0)
        self.assertTrue('sEcho' in data)
        self.assertEqual(data['sEcho'], '1')
        self.assertTrue('aaData' in data)
        self.assertEqual(len(data['aaData']), 0)

    def test_unpaginated(self):
        '''Should return an unpaginated Datatables JSON response'''
        browsers = [BrowserFactory() for _ in xrange(5)]

        response = self.get_response('browsers', self.build_query())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = json.loads(response.content)
        self.assertTrue('iTotalRecords' in data)
        self.assertEqual(data['iTotalRecords'], len(browsers))
        self.assertTrue('iTotalDisplayRecords' in data)
        self.assertEqual(data['iTotalDisplayRecords'], len(browsers))
        self.assertTrue('sEcho' in data)
        self.assertEqual(data['sEcho'], '1')
        self.assertTrue('aaData' in data)
        self.assertEqual(len(data['aaData']), len(browsers))
        for row in data['aaData']:
            self.assertEqual(len(row), 5)

    def test_paginated(self):
        '''Should return a paginated Datatables JSON response'''
        browsers = [BrowserFactory() for _ in xrange(15)]

        response = self.get_response('browsers', self.build_query())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = json.loads(response.content)
        self.assertTrue('iTotalRecords' in data)
        self.assertEqual(data['iTotalRecords'], len(browsers))
        self.assertTrue('iTotalDisplayRecords' in data)
        self.assertEqual(data['iTotalDisplayRecords'], len(browsers))
        self.assertTrue('sEcho' in data)
        self.assertEqual(data['sEcho'], '1')
        self.assertTrue('aaData' in data)
        self.assertEqual(len(data['aaData']), 10)
        for row in data['aaData']:
            self.assertEqual(len(row), 5)

    def test_formatted(self):
        '''Should return an formatted Datatables JSON response'''
        browsers = [BrowserFactory() for _ in xrange(15)]

        response = self.get_response('formatted-browsers', self.build_query())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = json.loads(response.content)
        self.assertTrue('iTotalRecords' in data)
        self.assertEqual(data['iTotalRecords'], len(browsers))
        self.assertTrue('iTotalDisplayRecords' in data)
        self.assertEqual(data['iTotalDisplayRecords'], len(browsers))
        self.assertTrue('sEcho' in data)
        self.assertEqual(data['sEcho'], '1')
        self.assertTrue('aaData' in data)
        self.assertEqual(len(data['aaData']), 10)
        for row in data['aaData']:
            self.assertEqual(len(row), 5)

    def test_sorted_single_field(self):
        '''Should handle sorting on a single field'''
        for i in xrange(5):
            BrowserFactory(name='Browser %s' % i)

        response = self.get_response('browsers', self.build_query(iSortCol_0=1, sSortDir_0='desc'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = json.loads(response.content)
        for idx, row in enumerate(data['aaData']):
            self.assertEqual(row[1], 'Browser %s' % (4 - idx))

    def test_sorted_multiple_field(self):
        '''Should handle sorting on multiple field'''
        for i in xrange(10):
            BrowserFactory(name='Browser %s' % (i / 2), engine__version='%s' % i)

        response = self.get_response('browsers', self.build_query(
            iSortingCols=2,
            iSortCol_0=1,
            sSortDir_0='desc',
            iSortCol_1=3,
            sSortDir_1='asc'
        ))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = json.loads(response.content)
        expected = (
            ('Browser 4', '8'),
            ('Browser 4', '9'),
            ('Browser 3', '6'),
            ('Browser 3', '7'),
            ('Browser 2', '4'),
            ('Browser 2', '5'),
            ('Browser 1', '2'),
            ('Browser 1', '3'),
            ('Browser 0', '0'),
            ('Browser 0', '1'),
        )
        for idx, row in enumerate(data['aaData']):
            expected_name, expected_version = expected[idx]
            self.assertEqual(row[1], expected_name)
            self.assertEqual(row[3], expected_version)

    def test_sorted_formatted(self):
        '''Should handle sorting with formatting'''
        for i in xrange(10):
            BrowserFactory(name='Browser %s' % (i / 2), version='%s' % i)

        response = self.get_response('formatted-browsers', self.build_query(iSortCol_0=1, sSortDir_0='desc'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = json.loads(response.content)
        expected = (
            'Browser 4 9',
            'Browser 4 8',
            'Browser 3 7',
            'Browser 3 6',
            'Browser 2 5',
            'Browser 2 4',
            'Browser 1 3',
            'Browser 1 2',
            'Browser 0 1',
            'Browser 0 0',
        )
        for idx, row in enumerate(data['aaData']):
            self.assertEqual(row[1], expected[idx])

    def test_global_search_single_term(self):
        '''Should do a global search on a single term'''
        for _ in xrange(2):
            BrowserFactory(name='test')
        for _ in xrange(3):
            BrowserFactory(engine__name='engine')

        response = self.get_response('browsers', self.build_query(sSearch='test'))
        data = json.loads(response.content)
        self.assertEqual(len(data['aaData']), 2)
        for row in data['aaData']:
            self.assertEqual(row[1], 'test')

        response = self.get_response('browsers', self.build_query(sSearch='engine'))
        data = json.loads(response.content)
        self.assertEqual(len(data['aaData']), 3)
        for row in data['aaData']:
            self.assertEqual(row[0], 'engine')

    def test_global_search_many_terms(self):
        '''Should do a global search on many terms'''
        for _ in xrange(2):
            BrowserFactory(name='test')
        for _ in xrange(3):
            BrowserFactory(engine__name='engine')
        for _ in xrange(4):
            BrowserFactory(name='test', engine__name='engine')

        response = self.get_response('browsers', self.build_query(sSearch='test engine'))
        data = json.loads(response.content)
        self.assertEqual(len(data['aaData']), 4)
        for row in data['aaData']:
            self.assertEqual(row[0], 'engine')
            self.assertEqual(row[1], 'test')

    def test_column_search_single_column(self):
        '''Should filter on a single² column'''
        for _ in xrange(3):
            BrowserFactory()
        for _ in xrange(2):
            BrowserFactory(name='test')

        response = self.get_response('browsers', self.build_query(sSearch_1='tes'))
        data = json.loads(response.content)
        self.assertEqual(len(data['aaData']), 2)
        for row in data['aaData']:
            self.assertEqual(row[1], 'test')

    def test_column_search_many_columns(self):
        '''Should filter on many columns'''
        for _ in xrange(2):
            BrowserFactory(name='test')
        for _ in xrange(3):
            BrowserFactory(engine__name='engine')
        for _ in xrange(4):
            BrowserFactory(name='test', engine__name='engine')

        response = self.get_response('browsers', self.build_query(sSearch_0='eng', sSearch_1='tes'))
        data = json.loads(response.content)
        self.assertEqual(len(data['aaData']), 4)
        for row in data['aaData']:
            self.assertEqual(row[0], 'engine')
            self.assertEqual(row[1], 'test')

    def test_column_search_formatted_column(self):
        '''Should filter on a formatted column'''
        for _ in xrange(3):
            BrowserFactory()
        for _ in xrange(2):
            BrowserFactory(name='test')

        response = self.get_response('formatted-browsers', self.build_query(sSearch_1='tes'))
        data = json.loads(response.content)
        self.assertEqual(len(data['aaData']), 2)
        for row in data['aaData']:
            self.assertTrue(row[1].startswith('test'))


class DatatablesGetTest(DatatablesTestMixin, TestCase):
    def get_response(self, name, data={}):
        return self.client.get(reverse(name), data)


class DatatablesPostTest(DatatablesTestMixin, TestCase):
    def get_response(self, name, data={}):
        return self.client.post(reverse(name), data)
