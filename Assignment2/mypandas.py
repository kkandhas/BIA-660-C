import csv
import datetime

from math import sqrt
from collections import OrderedDict


class DataFrame(object):
    @classmethod
    def from_csv(cls, file_path, delimiting_character=',', quote_character='"'):
        with open(file_path, 'rU') as infile:
            reader = csv.reader(infile, delimiter=delimiting_character, quotechar=quote_character)
            data = []
            for i, row in enumerate(reader):
                if i == 559:
                    row[2] = row[2].replace(",", "")
                data.append(row)

            return cls(list_of_lists=data)

    def __init__(self, list_of_lists, header=True):
        if header:
            self.header = list_of_lists[0]

            # To check Duplicate Values are inside Header.
            unique = (all(list_of_lists[0].count(x) == 1 for x in list_of_lists[0]))
            if not unique:
                raise TypeError('Duplicate values found')
            self.data = list_of_lists[1:]


        else:
            self.header = ['column' + str(index + 1) for index, column in enumerate(self.data[0])]
            self.data = list_of_lists

        # To remove white spaces from the beginning and ending of the string
        for rw in self.data:
            for i, vl in enumerate(rw):
                rw[i].strip()

        self.data = [OrderedDict(zip(self.header, row)) for row in self.data]

    # To get the type of values under a given column
    @classmethod
    def get_typeof_colm(self, cl_list):
        # type: (object) -> object
        flag_int = True
        # Checking if all items in the column are of type interger
        for cl in cl_list:
            try:
                if not isinstance(int(cl), int):
                    flag_int = False
            except ValueError:
                flag_int = False
        if flag_int:
            return int
        else:
            # Checking if all items in the column are of type dates
            flag_date = True
            for cl in cl_list:

                try:
                    if not (isinstance(datetime.datetime.strptime(cl, '%m/%d/%y %H:%M'), datetime.datetime)):
                        flag_date = False
                except ValueError:
                    flag_date = False

            if flag_date:
                for i, entry in enumerate(cl_list):
                    cl_list[i] = datetime.datetime.strptime(entry, '%m/%d/%y %H:%M')
                return datetime
            else:
                raise TypeError('The values in the column are strings and this operation cannot be done .')
                return None

    @classmethod
    def min(self, colm):
        cl_list = [row[colm] for row in df.data]
        cl_type = self.get_typeof_colm(cl_list)
        min_value = 100000000
        if cl_type == int:
            for x in cl_list:
                if min_value > x:
                    min_value = x
            return min_value
        elif cl_type == datetime:
            return min(cl_list)
        else:
            return None

    @classmethod
    def max(self, colm):
        cl_list = [row[colm] for row in df.data]
        cl_type = self.get_typeof_colm(cl_list)
        max_value = 0
        if cl_type == int:
            for x in cl_list:
                if max_value < x:
                    max_value = x
            return max_value
        elif cl_type == datetime:
            return max(cl_list)
        else:
            return None

    @classmethod
    def median(self, colm):
        cl_list = [row[colm] for row in df.data]
        cl_type = self.get_typeof_colm(cl_list)
        if cl_type == int or cl_type == datetime:
            cl_list.sort()
            if len(cl_list) % 2 == 1:
                mid = (len(cl_list) + 1) / 2
                return cl_list[mid]
            else:
                mid1 = len(cl_list) / 2
                mid2 = int(mid1) + 1
                mid = (int (cl_list[mid1]) + int (cl_list[mid2])) / 2
                return mid
        else:
            return None

    @classmethod
    def mean(self, colm):
        cl_list = [row[colm] for row in df.data]
        cl_type = self.get_typeof_colm( cl_list)
        summable = 0
        if cl_type == int:
            for cl in cl_list:
                summable += int(cl)
        mean_value = summable / len(cl_list)
        return mean_value

    @classmethod
    def sum(self, colm):
        cl_list = [row[colm] for row in df.data]
        cl_type = self.get_typeof_colm(cl_list)
        summable = 0
        if cl_type == int:
            for cl in cl_list:
                summable += int(cl)
            return summable
        else:
            raise TypeError('The values in the column are strings and this operation cannot be performed.')

    # Function to find the Standard Deviation
    @classmethod
    def std(self, colm):
        cl_list = [row[colm] for row in df.data]
        cl_type = self.get_typeof_colm(cl_list)
        summable = 0
        if cl_type == int:
            for cl in cl_list:
                summable += int(cl)

            mean_value = summable / len(cl_list)
            diff_values = [int(x) - mean_value for x in cl_list]
            sq_diff = 0
            for d in diff_values:
                sqlist = [d ** 2 for d in diff_values]
            for item in sqlist:
                sq_diff += item
            return sqrt(sq_diff / len(cl_list))
        else:
            raise TypeError('The values in the column are strings and this operation cannot be performed.')

    # Function to Add rows to the list
    @classmethod
    def add_rows(self, list_of_lists):
        l = len(df.data[0])
        for row in list_of_lists:
            if len(row) == l:
                df.data.append(row)
            else:
                raise ValueError('The length of the row does not match the predefined length')
        df.data = [OrderedDict(zip(df.header, row)) for row in df.data]

    # Function to Add columns to the list
    @classmethod
    def add_columns(self, list_of_values, cl_name):
        if len(df.data) == len(list_of_values):
            for i, row in enumerate(df.header):
                df.data[i][cl_name] = list_of_values[i]
            df.header.append(cl_name)
        else:
            raise ValueError('The length of the column does not match the predefined length')

    def __getitem__(self, item):
        # this is for rows only
        if isinstance(item, (int, slice)):
            return self.data[item]

        # this is for columns only
        elif isinstance(item, (str, unicode)):
            return [row[item] for row in self.data]

        # this is for rows and columns
        elif isinstance(item, tuple):
            if isinstance(item[0], list) or isinstance(item[1], list):

                if isinstance(item[0], list):
                    rowz = [row for index, row in enumerate(self.data) if index in item[0]]
                else:
                    rowz = self.data[item[0]]

                if isinstance(item[1], list):
                    if all([isinstance(thing, int) for thing in item[1]]):
                        return [
                            [column_value for index, column_value in enumerate([value for value in row.itervalues()]) if
                             index in item[1]] for row in rowz]
                    elif all([isinstance(thing, (str, unicode)) for thing in item[1]]):
                        return [[row[column_name] for column_name in item[1]] for row in rowz]
                    else:
                        raise TypeError('What the hell is this?')

                else:
                    return [[value for value in row.itervalues()][item[1]] for row in rowz]
            else:
                if isinstance(item[1], (int, slice)):
                    return [[value for value in row.itervalues()][item[1]] for row in self.data[item[0]]]
                elif isinstance(item[1], (str, unicode)):
                    return [row[item[1]] for row in self.data[item[0]]]
                else:
                    raise TypeError('I don\'t know how to handle this...')

        # only for lists of column names
        elif isinstance(item, list):
            return [[row[column_name] for column_name in item] for row in self.data]

    def get_rows_where_column_has_value(self, column_name, value, index_only=False):
        if index_only:
            return [index for index, row_value in enumerate(self[column_name]) if row_value == value]
        else:
            return [row for row in self.data if row[column_name] == value]


infile = open('SalesJan2009.csv')
lines = infile.readlines()
lines = lines[0].split('\r')
data = [l.split(',') for l in lines]
things = lines[559].split('"')

data[559] = things[0].split(',')[:-1] + [things[1].replace(',','')] + things[-1].split(',')[1:]

df = DataFrame(list_of_lists=data, header=True)



"""
# get the 5th row
fifth = df[4]
sliced = df[4:10]

# get item definition for df [row, column]

# get the third column
tupled = df[:, 2]
tupled_slices = df[0:5, :3]

tupled_bits = df[[1, 4], [1, 4]]

# adding header for data with no header
df = DataFrame(list_of_lists=data[1:], header=False)

# fetch columns by name
named = df['column1']
named_multi = df[['column1', 'column7']]

# fetch rows and (columns by name)
named_rows_and_columns = df[:5, 'column7']
named_rows_and_multi_columns = df[:5, ['column4', 'column7']]

# testing from_csv class method
df = DataFrame.from_csv('SalesJan2009.csv')
rows = df.get_rows_where_column_has_value('Payment_Type', 'Visa')
indices = df.get_rows_where_column_has_value('Payment_Type', 'Visa', index_only=True)

rows_way2 = df[indices, ['Product', 'Country']]

2 + 2
"""
