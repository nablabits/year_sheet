import os
from time import sleep
import unittest
from unittest import mock

import numpy as np
import pandas as pd
from bokeh.plotting import Figure
from bokeh.models.markers import Square
from bokeh.models.glyphs import VBar
from bokeh.models.mappers import LinearColorMapper

import year_sheet


class TestMain(unittest.TestCase):
    """Test the main entry point."""

    def setUp(self):
        os.environ['pyTest'] = '1'

    def tearDown(self):
        del os.environ['pyTest']

    def test_no_arguments(self):
        with mock.patch('argparse._sys.argv', ['year_sheet.py', ]):
            y = year_sheet.main()
            self.assertIsInstance(y, year_sheet.YearSheet)
            self.assertIsInstance(y.data, np.ndarray)
            self.assertEqual(y.year, 2021)
            self.assertTrue(y.week_load)

    def test_main_with_source(self):
        args = ['year_sheet.py', '-s', 'sample.txt']
        with mock.patch('argparse._sys.argv', args):
            y = year_sheet.main()
            self.assertIsInstance(y, year_sheet.YearSheet)
            self.assertIsInstance(y.data, np.ndarray)
            self.assertEqual(y.data[0], 3.26)
            self.assertEqual(y.year, 2021)
            self.assertTrue(y.week_load)

    def test_main_with_source_and_year(self):
        args = ['year_sheet.py', '-s', 'sample.txt', '-y', '2019']
        with mock.patch('argparse._sys.argv', args):
            y = year_sheet.main()
            self.assertIsInstance(y, year_sheet.YearSheet)
            self.assertIsInstance(y.data, np.ndarray)
            self.assertEqual(y.data[0], 3.26)
            self.assertEqual(y.year, 2019)
            self.assertTrue(y.week_load)

    def test_main_with_no_source_and_leap_year(self):
        args = ['year_sheet.py', '-y', '2020']
        with mock.patch('argparse._sys.argv', args):
            y = year_sheet.main()
            self.assertIsInstance(y, year_sheet.YearSheet)
            self.assertIsInstance(y.data, np.ndarray)
            self.assertEqual(y.data.size, 366)
            self.assertEqual(y.year, 2020)
            self.assertTrue(y.week_load)

    def test_main_with_no_source_and_regular_year(self):
        args = ['year_sheet.py', '-y', '2023']
        with mock.patch('argparse._sys.argv', args):
            y = year_sheet.main()
            self.assertIsInstance(y, year_sheet.YearSheet)
            self.assertIsInstance(y.data, np.ndarray)
            self.assertEqual(y.data.size, 365)
            self.assertEqual(y.year, 2023)
            self.assertTrue(y.week_load)

    def test_main_with_source_year_and_bare(self):
        args = ['year_sheet.py', '-s', 'sample.txt', '-y', '2019', '-b']
        with mock.patch('argparse._sys.argv', args):
            y = year_sheet.main()
            self.assertIsInstance(y, year_sheet.YearSheet)
            self.assertIsInstance(y.data, np.ndarray)
            self.assertEqual(y.data[0], 3.26)
            self.assertEqual(y.year, 2019)
            self.assertFalse(y.week_load)


class TestYearSheet(unittest.TestCase):

    def test_go(self):
        output_full = 'tests/plot_output_full.html'
        self.assertFalse(os.path.isfile(output_full))
        y = year_sheet.YearSheet('sample.txt', None, None)
        y.go(output=output_full)
        self.assertTrue(os.path.isfile(output_full))

        output_bare = 'tests/plot_output_bare.html'
        self.assertFalse(os.path.isfile(output_bare))
        y = year_sheet.YearSheet('sample.txt', None, True,)
        y.go(output=output_bare)
        self.assertTrue(os.path.isfile(output_bare))
        sleep(.5)
        os.remove(output_full)
        os.remove(output_bare)

    def test_generate_radom_data_returns_a_np_array_positive(self):
        y = year_sheet.YearSheet(None, None, None)
        arr = y._generate_random_data()
        self.assertTrue((arr >= 0).all())

    def test_parse_file_raises_error(self):
        msg = 'The file contains less than 365 or more than 366 entries.'
        with self.assertRaisesRegex(ValueError, msg):
            year_sheet.YearSheet('tests/test_sample_less.txt', None, None)
        with self.assertRaisesRegex(ValueError, msg):
            year_sheet.YearSheet('tests/test_sample_more.txt', None, None)

    def test_get_year_from_data_leap_year(self):
        y = year_sheet.YearSheet('tests/test_sample_366.txt', None, None)
        self.assertEqual(y._get_year_from_data(), 2020)

    def test_data_and_year_mismatch(self):
        msg = 'Data size and year mismatch.'
        with self.assertRaisesRegex(ValueError, msg):
            year_sheet.YearSheet('tests/test_sample_366.txt', 2019, None)

    def test_get_first_week_days(self):
        y = year_sheet.YearSheet(None, 2021, None)
        self.assertEqual(y._get_first_week_days(), 3)

    def test_get_last_week_days(self):
        y = year_sheet.YearSheet(None, 2021, None)
        self.assertEqual(y._get_last_week_days(), 5)

    def test_x_values(self):
        y = year_sheet.YearSheet(None, None, None)
        self.assertEqual(y._x().dtype, int)
        self.assertEqual(y._x().size, 365)

    def test_y_values(self):
        y = year_sheet.YearSheet(None, None, None)
        self.assertEqual(y._y().dtype, int)
        self.assertEqual(y._y().size, 365)

    def test_dataframe(self):
        y = year_sheet.YearSheet(None, None, None)
        self.assertIsInstance(y._yearsheet_data_as_df(), pd.DataFrame)
        self.assertEqual(y._yearsheet_data_as_df().shape, (365, 3))
        self.assertEqual(y._yearsheet_data_as_df().columns.tolist(),
                         ['x', 'y', 'day_values'])

    def test_week_load_data(self):
        y = year_sheet.YearSheet(None, None, None)
        self.assertIsInstance(y._week_load_data(), pd.DataFrame)
        self.assertEqual(y._week_load_data().shape, (53, 2))
        self.assertEqual(y._week_load_data().columns.tolist(),
                         ['x', 'day_values'])

    def test_year_sheet_plot(self):
        y = year_sheet.YearSheet(None, None, None)
        plot = y.yearsheet_plot()
        self.assertIsInstance(plot, Figure)
        self.assertEqual(plot.title.text, '2021 Year Sheet')
        self.assertEqual(plot.plot_height, 200)
        self.assertEqual(plot.plot_width, 950)
        self.assertEqual(plot.xaxis.axis_label, 'weeks')
        self.assertEqual(plot.yaxis.axis_label, 'days')
        self.assertEqual(plot.xgrid.grid_line_color, None)
        self.assertEqual(plot.ygrid.grid_line_color, None)
        self.assertEqual(plot.xaxis.ticker.ticks.tolist(),
                         [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50])
        self.assertEqual(
            plot.yaxis.ticker.ticks.tolist(), [1, 2, 3, 4, 5, 6, 7])

        refs = plot.references()
        for element in refs:
            if isinstance(element, Square):
                self.assertEqual(element.size, 10)
                self.assertEqual(element.line_color, '#006d2c')
                props = element.properties_with_values()
                cmap = props['fill_color']['transform']
                self.assertIsInstance(cmap, LinearColorMapper)
                self.assertEqual(cmap.low, 0.0)
                self.assertEqual(cmap.high, y.data.max())
                self.assertEqual(cmap.nan_color, 'white')
                self.assertEqual(
                    cmap.palette, ('#e5f5e0', '#a1d99b', '#31a354'))

    def test_load_plot(self):
        y = year_sheet.YearSheet(None, None, None)
        plot = y.week_load_plot()
        self.assertIsInstance(plot, Figure)
        self.assertEqual(plot.plot_height, 200)
        self.assertEqual(plot.plot_width, 950)
        self.assertEqual(plot.xaxis.axis_label, 'weeks')
        self.assertEqual(plot.yaxis.axis_label, 'Load')
        self.assertEqual(plot.xaxis.ticker.ticks.tolist(),
                         [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50])
        self.assertEqual(plot.yaxis.ticker.ticks.tolist(),
                         [0, 10, 20, 30, 40, 50, 60, 70, 80])

        refs = plot.references()
        for element in refs:
            if isinstance(element, VBar) and element.id == '1036':
                self.assertEqual(element.width, .7)
                self.assertEqual(element.fill_alpha, .5)
                self.assertEqual(element.fill_color, '#31a354')


if __name__ == '__main__':
    unittest.main()
