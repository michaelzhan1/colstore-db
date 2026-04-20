#!/usr/bin/python
import math
import os
import sys

import numpy as np
import pandas as pd

import utils

DATA_DIR = "tests/data"
INPUT_DIR = "tests/input"
EXP_DIR = "tests/expected"


def generate_table(n):
    """ Generate a data table with frequent values to test index performance. """
    file_ctrl = os.path.join(DATA_DIR, 'data4_ctrl.csv')
    file_btree = os.path.join(DATA_DIR, 'data4_btree.csv')
    file_clustered_btree = os.path.join(DATA_DIR, 'data4_clustered_btree.csv')

    header_ctrl = utils.generate_header('db1', 'tbl4_ctrl', 4)
    header_btree = utils.generate_header('db1', 'tbl4', 4)
    header_clustered_btree = utils.generate_header('db1', 'tbl4_clustered_btree', 4)

    table = pd.DataFrame(np.random.randint(0, n // 5, size=(n, 4)), columns=['col1', 'col2', 'col3', 'col4'])
    table['col1'] = np.random(0, 1000, size=(n))
    table['col2'] = np.random(0, 10000, size=(n))
    table['col4'] = np.random(0, 10000, size=(n))

    mask1 = np.random.uniform(0, 1, n) < 0.05
    mask2 = np.random.uniform(0.0, 1.0, n) < 0.02

    v1 = np.random.randint(0, n // 5)
    v2 = np.random.randint(0, n // 5)

    table.loc[mask1, 'col2'] = v1
    table.loc[mask2, 'col2'] = v2

    table['col4'] += table['col1']

    table.to_csv(file_ctrl, sep=',', index=False, header=header_ctrl, lineterminator='\n')
    table.to_csv(file_btree, sep=',', index=False, header=header_btree, lineterminator='\n')
    table.to_csv(file_clustered_btree, sep=',', index=False, header=header_clustered_btree, lineterminator='\n')

    return v1, v2, table


def test20():
    """ Test for creating a table without indices. """
    with utils.InputFileWriter(20, test_dir=INPUT_DIR) as f:
        f.write('-- Create a control table that is identical to the one in test21.dsl, but with no indices\n')
        f.write('--\n')
        f.write('-- Loads data from: data4_ctrl.csv\n')
        f.write('--\n')
        f.write('-- Create Table\n')
        f.write('create(tbl,"tbl4_ctrl",db1,4)\n')
        f.write('create(col,"col1",db1.tbl4_ctrl)\n')
        f.write('create(col,"col2",db1.tbl4_ctrl)\n')
        f.write('create(col,"col3",db1.tbl4_ctrl)\n')
        f.write('create(col,"col4",db1.tbl4_ctrl)\n')
        f.write('--\n')
        f.write(f'load("{os.path.join(DATA_DIR, "data4_ctrl.csv")}")\n')
        f.write('shutdown\n')

    with utils.ExpectedFileWriter(20, test_dir=EXP_DIR) as f:
        f.write('')
        # TODO: write some data checking or something


def test21():
    """ Test for creating a table with indices. """
    with utils.InputFileWriter(21, test_dir=INPUT_DIR) as f:
        f.write('-- Test for creating table with indexes\n')
        f.write('--\n')
        f.write('-- Table tbl4 has a clustered index with col3 being the leading column.\n')
        f.write('-- The clustered index has the form of a sorted column.\n')
        f.write('-- The table also has an unclustered btree index on col2.\n')
        f.write('--\n')
        f.write('-- Loads data from: data4_btree.csv\n')
        f.write('--\n')
        f.write('-- Create Table\n')
        f.write('create(tbl,"tbl4",db1,4)\n')
        f.write('create(col,"col1",db1.tbl4)\n')
        f.write('create(col,"col2",db1.tbl4)\n')
        f.write('create(col,"col3",db1.tbl4)\n')
        f.write('create(col,"col4",db1.tbl4)\n')
        f.write('-- Create a clustered index on col3\n')
        f.write('create(idx,db1.tbl4.col3,sorted,clustered)\n')
        f.write('-- Create an unclustered btree index on col2\n')
        f.write('create(idx,db1.tbl4.col2,btree,unclustered)\n')
        f.write('--\n')
        f.write(f'load("{os.path.join(DATA_DIR, "data4_btree.csv")}")\n')
        f.write('shutdown\n')

    with utils.ExpectedFileWriter(21, test_dir=EXP_DIR) as f:
        f.write('')
        # TODO: write some data checking or something


def test22_23(table):
    """ Test for select queries on clustered index vs no index."""
    n = table.shape[0]

    offset1 = max(1, n // 5000)
    offset2 = max(2, n // 2500)
    val1 = np.random.randint(0, n // 5 - offset1)
    val2 = np.random.randint(0, n // 5 - offset2)

    with utils.InputFileWriter(22, test_dir=INPUT_DIR) as f22, utils.InputFileWriter(23, test_dir=INPUT_DIR) as f23:
        f22.write('-- Test for select queries on control table with no indices\n')
        f23.write('-- Test for select queries on clustered index\n')
        f23.write('-- tbl3 has a secondary b-tree tree index on col2, and a clustered index on col3 with the form of a sorted column\n')
        utils.write_multiple('--\n', f22, f23)
        f22.write(f'-- SELECT col1 FROM tbl4_ctrl WHERE col3 >= {val1} and col3 < {val1 + offset1};\n')
        f22.write(f'-- SELECT col1 FROM tbl4_ctrl WHERE col3 >= {val2} and col3 < {val2 + offset2};\n')
        f23.write(f'-- SELECT col1 FROM tbl4 WHERE col3 >= {val1} and col3 < {val1 + offset1};\n')
        f23.write(f'-- SELECT col1 FROM tbl4 WHERE col3 >= {val2} and col3 < {val2 + offset2};\n')
        utils.write_multiple('--\n', f22, f23)
        f22.write(f's1=select(db1.tbl4_ctrl.col3,{val1},{val1 + offset1})\n')
        f23.write(f's1=select(db1.tbl4.col3,{val1},{val1 + offset1})\n')
        f22.write('f1=fetch(db1.tbl4_ctrl.col1,s1)\n')
        f23.write('f1=fetch(db1.tbl4.col1,s1)\n')
        utils.write_multiple('print(f1)\n', f22, f23)
        f22.write(f's2=select(db1.tbl4_ctrl.col3,{val2},{val2 + offset2})\n')
        f23.write(f's2=select(db1.tbl4.col3,{val2},{val2 + offset2})\n')
        f22.write('f2=fetch(db1.tbl4_ctrl.col1,s2)\n')
        f23.write('f2=fetch(db1.tbl4.col1,s2)\n')
        utils.write_multiple('print(f2)\n', f22, f23)

    with utils.ExpectedFileWriter(22, test_dir=EXP_DIR) as f22, utils.ExpectedFileWriter(23, test_dir=EXP_DIR) as f23:
        exp1 = table[(table['col3'] >= val1) & ((table['col3'] < (val1 + offset1)))]['col1']
        exp2 = table[(table['col3'] >= val2) & ((table['col3'] < (val2 + offset2)))]['col1']
        utils.write_multiple(utils.print_table(exp1) + '\n\n', f22, f23)
        utils.write_multiple(utils.print_table(exp2) + '\n', f22, f23)


def test24(table):
    """ Test for a clustered index select followed by a second predicate. """
    n = table.shape[0]

    offset1 = max(1, n // 5000)
    offset2 = max(2, n // 2500)
    val1 = np.random.randint(0, n // 5 - offset1)
    val2 = np.random.randint(0, n // 5 - offset2)

    with utils.InputFileWriter(24, test_dir=INPUT_DIR) as f:
        f.write('-- Test for a clustered index select followed by a second predicate\n')
        f.write('--\n')
        f.write(
            f'-- SELECT sum(col1) FROM tbl4 WHERE (col3 >= {val1} and col3 < {val1 + offset1}) AND (col2 >= {val2} and col2 < {val2 + offset2});\n')
        f.write('--\n')
        f.write(f's1=select(db1.tbl4.col3,{val1},{val1 + offset1})\n')
        f.write('f1=fetch(db1.tbl4.col2,s1)\n')
        f.write(f's2=select(s1,f1,{val2},{val2 + offset2})\n')
        f.write('f2=fetch(db1.tbl4.col1,s2)\n')
        f.write('print(f2)\n')
        f.write('a1=sum(f2)\n')
        f.write('print(a1)\n')

    with utils.ExpectedFileWriter(24, test_dir=EXP_DIR) as f:
        exp = table[(table['col3'] >= val1) & (table['col3'] < (val1 + offset1)) &
                    (table['col2'] >= val2) & (table['col2'] < (val2 + offset2))]['col1']
        f.write(utils.print_table(exp) + '\n\n')
        f.write(str(exp.sum()) + '\n')


def test25_26(table):
    """ Tests for a non-clustered index select followed by an aggregate, without and with the index """
    n = table.shape[0]

    offset = max(2, n // 1000)
    vals = np.random.randint(0, n // 5 - offset, size=10)

    with utils.InputFileWriter(25, test_dir=INPUT_DIR) as f25, utils.InputFileWriter(26, test_dir=INPUT_DIR) as f26:
        f25.write('-- Test for a non-clustered index select followed by an aggregate (control-test)\n')
        f26.write('-- Test for a non-clustered index select followed by an aggregate\n')
        utils.write_multiple('--\n', f25, f26)
        f25.write('-- SELECT sum(col3) FROM tbl4_ctrl WHERE (col2 >= _ and col2 < _);\n')
        f26.write('-- SELECT sum(col3) FROM tbl4 WHERE (col2 >= _ and col2 < _);\n')
        utils.write_multiple('--\n', f25, f26)
        for i, val in enumerate(vals):
            f25.write(f's{i}=select(db1.tbl4_ctrl.col2,{val},{val + offset})\n')
            f26.write(f's{i}=select(db1.tbl4.col2,{val},{val + offset})\n')
            f25.write(f'f{i}=fetch(db1.tbl4_ctrl.col3,s{i})\n')
            f26.write(f'f{i}=fetch(db1.tbl4.col3,s{i})\n')
            utils.write_multiple(f'a{i}=sum(f{i})\n', f25, f26)
            utils.write_multiple(f'print(a{i})\n', f25, f26)

    with utils.ExpectedFileWriter(25, test_dir=EXP_DIR) as f25, utils.ExpectedFileWriter(26, test_dir=EXP_DIR) as f26:
        for i in range(10):
            exp = table[(table['col2'] >= vals[i]) & (table['col2'] < (vals[i] + offset))]['col3']
            utils.write_multiple(f'{exp.sum()}\n', f25, f26)


def test27(table, val1, val2):
    """ Test for clustered index selects on frequent values. """

    with utils.InputFileWriter(27, test_dir=INPUT_DIR) as f:
        f.write('-- Test for clustered index selects on frequent values\n')
        f.write('--\n')
        f.write('-- SELECT sum(col1) FROM tbl4 WHERE (col2 >= {} and col2 < {});\n'.format(val1 - 1, val1 + 1))
        f.write('-- SELECT sum(col1) FROM tbl4 WHERE (col2 >= {} and col2 < {});\n'.format(val2 - 1, val2 + 1))
        f.write('--\n')
        f.write(f's1=select(db1.tbl4.col2,{val1 - 1},{val1 + 1})\n')
        f.write('f1=fetch(db1.tbl4.col1,s1)\n')
        f.write('a1=sum(f1)\n')
        f.write('print(a1)\n')
        f.write(f's2=select(db1.tbl4.col2,{val2 - 1},{val2 + 1})\n')
        f.write('f2=fetch(db1.tbl4.col1,s2)\n')
        f.write('a2=sum(f2)\n')
        f.write('print(a2)\n')

    with utils.ExpectedFileWriter(27, test_dir=EXP_DIR) as f:
        exp1 = table[(table['col2'] >= (val1 - 1)) & (table['col2'] < (val1 + 1))]['col1']
        exp2 = table[(table['col2'] >= (val2 - 1)) & (table['col2'] < (val2 + 1))]['col1']
        f.write(f'{exp1.sum()}\n')
        f.write(f'{exp2.sum()}\n')


def test28_29(table):
    """ Test for non-clustered index selects followed by an aggregate, on many queries with varying selectivities. """
    n = table.shape[0]

    offset = max(2, n // 500)
    vals = np.random.randint(0, n // 5 - offset, size=100)

    with utils.InputFileWriter(28, test_dir=INPUT_DIR) as f28, utils.InputFileWriter(29, test_dir=INPUT_DIR) as f29:
        f28.write('-- Test for a non-clustered index select followed by an aggregate (control-test, many queries)\n')
        f29.write('-- Test for a non-clustered index select followed by an aggregate (with b-tree, many queries)\n')
        utils.write_multiple('--\n', f28, f29)
        f28.write('-- SELECT avg(col3) FROM tbl4_ctrl WHERE (col2 >= _ and col2 < _);\n')
        f29.write('-- SELECT avg(col3) FROM tbl4 WHERE (col2 >= _ and col2 < _);\n')
        utils.write_multiple('--\n', f28, f29)

        # TODO: continue with for loop




    output_file28, exp_output_file28 = utils.openFileHandles(28, test_dir=TEST_BASE_DIR)
    output_file29, exp_output_file29 = utils.openFileHandles(29, test_dir=TEST_BASE_DIR)
    offset = np.max([2, int(dataSize/500)])
    output_file28.write(
        '-- Test for a non-clustered index select followed by an aggregate (control-test, many queries)\n')
    output_file28.write(
        '-- Compare to test 29 for timing differences between B-tree and scan for highly selective queries\n')
    output_file28.write('--\n')
    output_file28.write('-- Query form in SQL:\n')
    output_file28.write('-- SELECT avg(col3) FROM tbl4_ctrl WHERE (col2 >= _ and col2 < _);\n')
    output_file28.write('--\n')
    output_file29.write('-- Test for a non-clustered index select followed by an aggregate (many queries)\n')
    output_file29.write('--\n')
    output_file29.write('-- Query form in SQL:\n')
    output_file29.write('-- SELECT avg(col3) FROM tbl4 WHERE (col2 >= _ and col2 < _);\n')
    output_file29.write('--\n')
    for i in range(100):
        val1 = np.random.randint(0, int((dataSize/5) - offset))
        output_file28.write('s{}=select(db1.tbl4_ctrl.col2,{},{})\n'.format(i, val1, val1 + offset))
        output_file28.write('f{}=fetch(db1.tbl4_ctrl.col3,s{})\n'.format(i, i))
        output_file28.write('a{}=avg(f{})\n'.format(i, i))
        output_file28.write('print(a{})\n'.format(i))
        output_file29.write('s{}=select(db1.tbl4.col2,{},{})\n'.format(i, val1, val1 + offset))
        output_file29.write('f{}=fetch(db1.tbl4.col3,s{})\n'.format(i, i))
        output_file29.write('a{}=avg(f{})\n'.format(i, i))
        output_file29.write('print(a{})\n'.format(i))
        # generate expected results
        dfSelectMask1 = (table['col2'] >= val1) & (table['col2'] < (val1 + offset))
        values = table[dfSelectMask1]['col3']
        mean_result = np.round(values.mean(), PLACES_TO_ROUND)
        if (math.isnan(mean_result)):
            exp_output_file28.write('0.00\n')
            exp_output_file29.write('0.00\n')
        else:
            exp_output_file28.write('{:0.2f}\n'.format(mean_result))
            exp_output_file29.write('{:0.2f}\n'.format(mean_result))
    utils.closeFileHandles(output_file28, exp_output_file28)
    utils.closeFileHandles(output_file29, exp_output_file29)


def createTest30():
    output_file, exp_output_file = utils.openFileHandles(30, test_dir=TEST_BASE_DIR)
    output_file.write('-- Test for creating table with indexes\n')
    output_file.write('--\n')
    output_file.write('-- Table tbl4_clustered_btree has a clustered index with col3 being the leading column.\n')
    output_file.write('-- The clustered index has the form of a B-Tree.\n')
    output_file.write('-- The table also has a secondary sorted index.\n')
    output_file.write('--\n')
    output_file.write('-- Loads data from: data4_clustered_btree.csv\n')
    output_file.write('--\n')
    output_file.write('-- Create Table\n')
    output_file.write('create(tbl,"tbl4_clustered_btree",db1,4)\n')
    output_file.write('create(col,"col1",db1.tbl4_clustered_btree)\n')
    output_file.write('create(col,"col2",db1.tbl4_clustered_btree)\n')
    output_file.write('create(col,"col3",db1.tbl4_clustered_btree)\n')
    output_file.write('create(col,"col4",db1.tbl4_clustered_btree)\n')
    output_file.write('-- Create a clustered index on col3\n')
    output_file.write('create(idx,db1.tbl4_clustered_btree.col3,btree,clustered)\n')
    output_file.write('-- Create an unclustered btree index on col2\n')
    output_file.write('create(idx,db1.tbl4_clustered_btree.col2,sorted,unclustered)\n')
    output_file.write('--\n')
    output_file.write('--\n')
    output_file.write('-- Load data immediately in the form of a clustered index\n')
    output_file.write('load("'+DOCKER_TEST_BASE_DIR+'/data4_clustered_btree.csv")\n')
    output_file.write('--\n')
    output_file.write('-- Testing that the data and their indexes are durable on disk.\n')
    output_file.write('shutdown\n')
    # no expected results
    utils.closeFileHandles(output_file, exp_output_file)


def createTest31(dataTable, dataSize):
    output_file, exp_output_file = utils.openFileHandles(31, test_dir=TEST_BASE_DIR)
    output_file.write('--\n')
    output_file.write('-- Query in SQL:\n')
    # selectivity =
    offset = np.max([1, int(dataSize/5000)])
    offset2 = np.max([2, int(dataSize/2500)])
    val1 = np.random.randint(0, int((dataSize/5) - offset))
    val2 = np.random.randint(0, int((dataSize/5) - offset2))
    # generate test 31
    output_file.write('--\n')
    output_file.write(
        '-- tbl4_clustered_btree has a secondary sorted index on col2, and a clustered b-tree index on col3\n')
    output_file.write('-- testing for correctness\n')
    output_file.write('--\n')
    output_file.write('-- Query in SQL:\n')
    output_file.write(
        '-- SELECT col1 FROM tbl4_clustered_btree WHERE col3 >= {} and col3 < {};\n'.format(val1, val1+offset))
    output_file.write(
        '-- SELECT col1 FROM tbl4_clustered_btree WHERE col3 >= {} and col3 < {};\n'.format(val2, val2+offset2))
    output_file.write('--\n')
    output_file.write('-- since col3 has a clustered index, the index is expected to be used by the select operator\n')
    output_file.write('s1=select(db1.tbl4_clustered_btree.col3,{},{})\n'.format(val1, val1 + offset))
    output_file.write('f1=fetch(db1.tbl4_clustered_btree.col1,s1)\n')
    output_file.write('print(f1)\n')
    output_file.write('s2=select(db1.tbl4_clustered_btree.col3,{},{})\n'.format(val2, val2 + offset2))
    output_file.write('f2=fetch(db1.tbl4_clustered_btree.col1,s2)\n')
    output_file.write('print(f2)\n')
    # generate expected results
    dfSelectMask1 = (dataTable['col3'] >= val1) & (dataTable['col3'] < (val1 + offset))
    dfSelectMask2 = (dataTable['col3'] >= val2) & (dataTable['col3'] < (val2 + offset2))
    output1 = dataTable[dfSelectMask1]['col1']
    output2 = dataTable[dfSelectMask2]['col1']
    exp_output_file.write(utils.print_table(output1))
    exp_output_file.write('\n\n')
    exp_output_file.write(utils.print_table(output2))
    exp_output_file.write('\n')
    utils.closeFileHandles(output_file, exp_output_file)


def createTest32(dataTable, dataSize):
    output_file, exp_output_file = utils.openFileHandles(32, test_dir=TEST_BASE_DIR)
    offset = np.max([2, int(dataSize/1000)])
    output_file.write('-- Test for a non-clustered index select followed by an aggregate\n')
    output_file.write('--\n')
    output_file.write('-- Query form in SQL:\n')
    output_file.write('-- SELECT sum(col3) FROM tbl4_clustered_btree WHERE (col2 >= _ and col2 < _);\n')
    output_file.write('--\n')
    for i in range(5):
        val1 = np.random.randint(0, int((dataSize/5) - offset))
        output_file.write('s{}=select(db1.tbl4_clustered_btree.col2,{},{})\n'.format(i, val1, val1 + offset))
        output_file.write('f{}=fetch(db1.tbl4_clustered_btree.col3,s{})\n'.format(i, i))
        output_file.write('a{}=sum(f{})\n'.format(i, i))
        output_file.write('print(a{})\n'.format(i))
        # generate expected results
        dfSelectMask1 = (dataTable['col2'] >= val1) & (dataTable['col2'] < (val1 + offset))
        values = dataTable[dfSelectMask1]['col3']
        sum_result = values.sum()
        if (math.isnan(sum_result)):
            exp_output_file.write('0\n')
        else:
            exp_output_file.write(str(sum_result) + '\n')
    utils.closeFileHandles(output_file, exp_output_file)


def createTest33To38(dataTable, dataSize):
    table_names = ['tbl4_ctrl', 'tbl4', 'tbl4_clustered_btree']
    selectivites = ['0.1%', '1%']
    # selectivity 0.1%
    offset1 = np.max([1, int(dataSize/5000)])
    # selectivity 1%
    offset2 = np.max([2, int(dataSize/500)])
    offsets = [offset1, offset2]
    test_start = 33
    for offset, selectivity in zip(offsets, selectivites):
        for table_name in table_names:
            output_file, exp_output_file = utils.openFileHandles(test_start, test_dir=TEST_BASE_DIR)

            output_file.write('--\n')
            output_file.write('-- selectivity={}\n'.format(selectivity))
            output_file.write('-- Query in SQL:\n')
            output_file.write('-- SELECT avg(col1) FROM {} WHERE col3 >= _ and col3 < _;\n'.format(table_name))
            output_file.write('--\n')

            for i in range(20):

                val = np.random.randint(0, int((dataSize/5) - offset))

                output_file.write('s{}=select(db1.{}.col3,{},{})\n'.format(i, table_name, val, val + offset))
                output_file.write('f{}=fetch(db1.{}.col1,s{})\n'.format(i, table_name, i))
                output_file.write('a{}=avg(f{})\n'.format(i, i))
                output_file.write('print(a{})\n'.format(i))

                dfSelectMask = (dataTable['col3'] >= val) & (dataTable['col3'] < (val + offset))
                values = dataTable[dfSelectMask]['col1']
                mean_result = np.round(values.mean(), PLACES_TO_ROUND)
                if (math.isnan(mean_result)):
                    exp_output_file.write('0.00\n')
                else:
                    exp_output_file.write('{:0.2f}\n'.format(mean_result))

            utils.closeFileHandles(output_file, exp_output_file)
            test_start += 1


def createTest39To44(dataTable, dataSize):
    table_names = ['tbl4_ctrl', 'tbl4', 'tbl4_clustered_btree']
    selectivites = ['0.1%', '1%']
    # selectivity 0.1%
    offset1 = np.max([1, int(dataSize/5000)])
    # selectivity 1%
    offset2 = np.max([2, int(dataSize/500)])
    offsets = [offset1, offset2]
    test_start = 39
    for offset, selectivity in zip(offsets, selectivites):
        for table_name in table_names:
            output_file, exp_output_file = utils.openFileHandles(test_start, test_dir=TEST_BASE_DIR)

            output_file.write('--\n')
            output_file.write('-- selectivity={}\n'.format(selectivity))
            output_file.write('-- Query in SQL:\n')
            output_file.write('-- SELECT avg(col3) FROM {} WHERE col2 >= _ and col2 < _;\n'.format(table_name))
            output_file.write('--\n')

            for i in range(20):

                val = np.random.randint(0, int((dataSize/5) - offset))

                output_file.write('s{}=select(db1.{}.col2,{},{})\n'.format(i, table_name, val, val + offset))
                output_file.write('f{}=fetch(db1.{}.col3,s{})\n'.format(i, table_name, i))
                output_file.write('a{}=avg(f{})\n'.format(i, i))
                output_file.write('print(a{})\n'.format(i))

                dfSelectMask = (dataTable['col2'] >= val) & (dataTable['col2'] < (val + offset))
                values = dataTable[dfSelectMask]['col3']
                mean_result = np.round(values.mean(), PLACES_TO_ROUND)
                if (math.isnan(mean_result)):
                    exp_output_file.write('0.00\n')
                else:
                    exp_output_file.write('{:0.2f}\n'.format(mean_result))

            utils.closeFileHandles(output_file, exp_output_file)
            test_start += 1


def generateMilestoneThreeFiles(dataSize, randomSeed=47):
    np.random.seed(randomSeed)
    frequentVal1, frequentVal2, dataTable = generateDataMilestone3(dataSize)
    test20()
    test21()
    test22_23(dataTable, dataSize)
    test24(dataTable, dataSize)
    test25_26(dataTable, dataSize)
    test27(dataTable, frequentVal1, frequentVal2)
    test28_29(dataTable, dataSize)
    createTest30()
    createTest31(dataTable, dataSize)
    createTest32(dataTable, dataSize)
    createTest33To38(dataTable, dataSize)
    createTest39To44(dataTable, dataSize)


def main(argv):
    global TEST_BASE_DIR
    global DOCKER_TEST_BASE_DIR

    dataSize = int(argv[0])
    if len(argv) > 1:
        randomSeed = int(argv[1])
    else:
        randomSeed = 47

    # override the base directory for where to output test related files
    if len(argv) > 2:
        TEST_BASE_DIR = argv[2]
        if len(argv) > 3:
            DOCKER_TEST_BASE_DIR = argv[3]
    generateMilestoneThreeFiles(dataSize, randomSeed=randomSeed)


if __name__ == "__main__":
    main(sys.argv[1:])
