#!/usr/bin/python3

import os
import argparse
import calendar

import numpy as np
import pandas as pd

from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource
from bokeh.transform import linear_cmap
from bokeh.palettes import Greens3, Greens5
from bokeh.layouts import column


class YearSheet:

    def __init__(self, source: str, year: int, bare: bool) -> None:
        """Initialize the object.

        When triggered from the command line it expects the source (if
        provided) to be a str pointing to a valid file. If imported into some
        other module the easiest way to use a custom np.array is to instantiate
        the object and then overriding the self.data attribute before
        triggering the yearsheet_plot() method. Also it would be a good idea to
        trigger match_data_and_year() to avoid errors.
        """
        if not source and not year:
            self.data = self._generate_random_data()
            self.year = self._get_year_from_data()
        elif source and not year:
            self.data = self._parse_file(source)
            self.year = self._get_year_from_data()
        elif not source and year:
            if calendar.isleap(year):
                self.data = self._generate_random_data(days=366)
            else:
                self.data = self._generate_random_data()
            self.year = year
        else:  # if there are both data & year
            self.data = self._parse_file(source)
            self.year = year
            self.match_data_and_year()

        if bare:
            self.week_load = False
        else:
            self.week_load = True

    def go(self, output='sheet.html') -> None:
        """Output the plot."""
        output_file(output)
        p1 = self.yearsheet_plot()
        if self.week_load:
            p2 = self.week_load_plot()
            p1.xaxis.axis_label = None
            show(column([p1, p2]))
        else:
            show(p1)

    def _generate_random_data(self, days: int = 365) -> np.array:
        """Generate random data when no source is provided."""
        data = np.random.normal(size=days)
        return data - data.min()

    def _parse_file(self, source: str) -> np.array:
        """Transform a file with 365 or 366 rows into a numpy array"""
        with open(source, 'r') as f:
            data = np.loadtxt(f)
        if data.size not in (365, 366):
            raise ValueError(
                'The file contains less than 365 or more than 366 entries.')

        return data

    def _get_year_from_data(self) -> int:
        """Given some array figure out a sample year."""
        if self.data.size == 365:
            return 2021
        else:
            return 2020  # leap year

    def match_data_and_year(self) -> None:
        """Raise an error when data size and year days mismatch."""
        leap_void = (
            self.data.size == 365 and calendar.isleap(self.year))
        regular_void = (
            self.data.size == 366 and not calendar.isleap(self.year))

        if leap_void or regular_void:
            raise ValueError('Data size and year mismatch.')

    def _get_first_week_days(self) -> int:
        """Get the days that has the first week.

        If the first day of the week in the selected year is monday it returns
        0 so the 7 days remaining until sunday are needed.
        """
        return 7 - calendar.weekday(self.year, 1, 1)

    def _get_last_week_days(self) -> int:
        """Get the days that has the last week.

        If the last day of the week in the selected year is monday it returns
        0 so one unit more is needed.
        """
        return calendar.weekday(self.year, 12, 31) + 1

    def _x(self) -> np.array:
        """Come up with the x coordinate.

        The x coordinate are the weeks in the year (52), plus the first one
        having the days defined by _get_first_week_days days and the last one
        having ones defined by _get_last_week_days.
        """
        first_week = np.zeros(self._get_first_week_days())
        last_week = np.full(self._get_last_week_days(), 52)
        inner_weeks = np.concatenate([np.full(7, n) for n in range(1, 52)])
        x = np.concatenate((first_week, inner_weeks, last_week))
        assert x.size == self.data.size
        return x.astype(int)

    def _y(self) -> np.array:
        """Come up with the y coordinate.

        The y coordinate are the days within a week. Also, the first one has 6
        days and the last one (officially belonging to jan 2020) has two days.
        """
        first_week = np.arange(1, self._get_first_week_days() + 1)
        last_week = np.arange(1, self._get_last_week_days() + 1)
        inner_weeks = np.concatenate([np.arange(1, 8) for _ in range(1, 52)])
        y = np.concatenate((first_week, inner_weeks, last_week))
        assert y.size == self.data.size
        return y

    def _yearsheet_data_as_df(self) -> pd.DataFrame:
        """Get a dataframe version of the data so it can be groupped by x."""
        return pd.DataFrame({
            'x': self._x(),
            'y': self._y(),
            'day_values': self.data, })

    def _week_load_data(self) -> pd.DataFrame:
        """Get a DF with the values groupped and aggregated by x (weeks)."""
        df = self._yearsheet_data_as_df()
        return df.groupby('x').day_values.sum().reset_index()

    def yearsheet_plot(self) -> figure:
        """Build the plot for the year sheet."""
        s0 = ColumnDataSource({
            'x': self._x(),
            'y': self._y(),
            'day_values': self.data, })
        cmap = linear_cmap(
            'day_values', palette=Greens3[::-1], low=self.data.min(),
            high=self.data.max(), nan_color='white')
        title = '{} Year Sheet'.format(self.year)
        p = figure(
            plot_height=200, plot_width=950, y_range=(0, 8), x_range=(-1, 55),
            title=title, y_axis_label='days', x_axis_label='weeks',
            tooltips='@day_values', toolbar_location=None)
        p.square(
            'x', 'y', source=s0, size=10, color=cmap, line_color=Greens5[0])
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None
        p.xaxis.ticker = np.append(1, np.arange(1, 11) * 5)
        p.yaxis.ticker = np.arange(1, 8)
        return p

    def week_load_plot(self) -> figure:
        """Build the plot for the week load."""
        df = self._week_load_data()
        source = ColumnDataSource(df)
        p = figure(
            plot_height=200, plot_width=950, x_range=(-1, 55),
            y_axis_label='Load', x_axis_label='weeks', tooltips='@day_values',
            toolbar_location=None)
        p.vbar(x='x', top='day_values', source=source, width=.7, fill_alpha=.5,
               color=Greens5[1])
        p.xaxis.ticker = np.append(1, np.arange(1, 11) * 5)
        p.yaxis.ticker = 10 * np.arange(9)
        return p


def main():
    """Parse command line arguments for YearSheet & lauch the application."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s', '--source', type=str,
        help='A text file containing 365 or 366 lines worth of data.')
    parser.add_argument(
        '-y', '--year', type=int, help='The year origin of the data.')
    parser.add_argument('-b', '--bare', action='store_true',
                        help='Just display the year sheet')

    args = parser.parse_args()
    y = YearSheet(args.source, args.year, args.bare)
    if os.getenv('pyTest'):
        return y
    y.go()


if __name__ == '__main__':
    main()  # pragma: no cover
