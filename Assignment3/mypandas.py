import csv

import datetime

from collections import defaultdict
from functools import partial
from collections import OrderedDict


class DataFrame(object):
    @classmethod
    def from_csv(cls, file_path, delimiting_character=',', quote_character='"'):
        with open(file_path, 'rU') as infile2:
            reader = csv.reader(infile2, delimiter=delimiting_character, quotechar=quote_character)
            data = []

            for row in reader:
                data.append(row)

            return cls(list_of_lists=data)

    def from_dict(self, my_dict):
        data2 = []
        for x in my_dict:
            for y in my_dict[x]:
                if not isinstance(my_dict[x][y], str):
                    data2.append([x, y])
                else:
                    for z in my_dict[x][y]:
                        data2.append([x, y,my_dict[x][y]])
        return DataFrame(list_of_lists=data2,header=False)

    def __init__(self, list_of_lists, header=True):

        # To remove white spaces from the beginning and ending of the string
        for rw in list_of_lists:
            for i, vl in enumerate(rw):
                vl.strip()

        if header:
            # To check Duplicate Values are inside Header.
            temp = list(list_of_lists[0])
            temp.sort()
            for i, j in enumerate(temp):
                if (i != len(temp) - 1) and (temp[i] == temp[i + 1]):
                    raise TypeError('Duplicate values found')
            self.header = list_of_lists[0]
            self.data = list_of_lists[1:]
        else:
            self.header = ['column' + str(index + 1) for index, column in enumerate(list_of_lists[0])]
            self.data = list_of_lists

        self.data = [OrderedDict(zip(self.header, row)) for row in self.data]

    def get_typeof_colm(self, colm):
        # type: (object) -> object
        cl_list = [(row[colm]) for row in self.data]
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
                return datetime
            else:
                return str

    def sort_by(self, colm, flag_rev):
        # type: (object, object) -> object
        if isinstance(colm, list):
            print 'inside'
            for i, clm_nam in reversed(list(enumerate(colm))):
                self.data = self.sort_by(clm_nam, flag_rev[i])
            return self.data
        cl_type = self.get_typeof_colm(colm)
        cl_list = self.convert_colm_type(cl_type, colm)
        if flag_rev:
            index_list = sorted(range(len(cl_list)), key=cl_list.__getitem__, reverse=True)
        else:
            index_list = sorted(range(len(cl_list)), key=cl_list.__getitem__)
        temp = [self.data[x] for x in index_list]
        self.data = list(temp)
        return self.data

    def convert_colm_type(self, cl_type, colm):
        cl_list = [(row[colm]) for row in self.data]
        if cl_type == int:
            cl_list = [int(row[colm]) for row in self.data]
            return cl_list
        elif cl_type == datetime:
            for i, entry in enumerate(cl_list):
                cl_list[i] = datetime.datetime.strptime(entry, '%m/%d/%y %H:%M')
            return cl_list
        else:
            return cl_list

    def group_by(self, colm1, colm2, function):

        if isinstance(colm1, list):

            colm1.append(colm2)
            temp_list = []
            temp_dict = defaultdict(partial(defaultdict, list))
            for cl in colm1:
                cl_type = self.get_typeof_colm(cl)
                cl_list = self.convert_colm_type(cl_type, cl)
                temp_list.append(cl_list)

            for (cl1, cl2, cl3) in zip(*temp_list):
                temp_dict[cl1][cl2].append(cl3)
            opdict = defaultdict(partial(defaultdict, str))
            for x in temp_dict:
                for y in temp_dict[x]:
                    opdict[x][y] = function(temp_dict[x][y])
            return opdict

        cl_type = self.get_typeof_colm(colm1)
        colm1_list = self.convert_colm_type(cl_type, colm1)

        cl_type = self.get_typeof_colm(colm2)
        colm2_list = self.convert_colm_type(cl_type, colm2)

        temp = zip(colm1_list, colm2_list)
        mydict = defaultdict(list)
        for i, value in temp:
            mydict[i].append(value)
        key = mydict.keys()

        a = []
        for i, v in enumerate(mydict.values()):
            a.append(function(v))
        opdict = dict(zip(key, a))

        return opdict

    def __getitem__(self, item):
        # this is for rows only
        if isinstance(item, (int, slice)):
            return self.data[item]

        # this is for columns only
        elif isinstance(item, (str, unicode)):
            cl_type = self.get_typeof_colm(item)
            colm1_list = self.convert_colm_type(cl_type, item)
            return Series(list_of_values=colm1_list)

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
            if isinstance(item,bool):
                return [self.data[i] for i, value in enumerate(item) if value == True]
            else:
                return [value for i, value in enumerate(item)]

    def get_rows_where_column_has_value(self, column_name, value, index_only=False):
        if index_only:
            return [index for index, row_value in enumerate(self[column_name]) if row_value == value]
        else:
            return [row for row in self.data if row[column_name] == value]


class Series(list):
    def __init__(self, list_of_values):
        self.data = list_of_values

    def __eq__(self, other):
        ret_list = []

        for item in self.data:
            ret_list.append(item == other)

        return ret_list

    def __lt__(self, other):
        ret_list = []
        for item in self.data:
            ret_list.append(item < other)
        return ret_list

    def __le__(self, other):
        ret_list = []
        for item in self.data:
            ret_list.append(item <= other)
        return ret_list

    def __ge__(self, other):
        ret_list = []
        for item in self.data:
            ret_list.append(item >= other)
        return ret_list

    def __gt__(self, other):
        ret_list = []
        for item in self.data:
            ret_list.append(item > other)
        return ret_list


infile = open('SalesJan2009.csv')
lines = infile.readlines()
lines = lines[0].split('\r')
data = [l.split(',') for l in lines]
things = lines[559].split('"')
data[559] = things[0].split(',')[:-1] + [things[1].replace(',', '')] + things[-1].split(',')[1:]


df = DataFrame(list_of_lists=data, header=True)



# Testing:

'''Task 1 '''
data = df.sort_by(['City', 'Price'], [False, False])
print data

'''  # Task 3
'''


def avg(list_of_values):
    return str(sum(list_of_values) / float(len(list_of_values)))


def min_value(list_of_values):
    return str(min(list_of_values))


dt = df.group_by(['Country', 'Payment_Type'], 'Price', min_value)
print dt
dj = df.group_by('Payment_Type', 'Price', avg)
print dj

'''Task 2'''

list_of_bools = df['Payment_Type'] == 'Visa'
df_boolean_indexed = df[list_of_bools]
print df_boolean_indexed

list_of_bools2 = df[df['Price'] >= 13000]
print list_of_bools2

list3 = df['Transaction_date']
print list3.data

print df['Country']
'''
if (df.sort_by('Price', False)) == df.from_csv('SalesJan2009-4.csv'):
    print 'correct'
else:
    print 'false'

if df.sort_by(['Price', 'City'], [False, True]) == df.from_csv('SalesJan2009-edited.csv'):
    print 'correct'
else:
    print 'false'
'''

'''
df = DataFrame(list_of_lists=data)
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
'''
