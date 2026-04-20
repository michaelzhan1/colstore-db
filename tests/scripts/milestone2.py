#!/usr/bin/python
import os

import numpy as np
import pandas as pd
import utils

DATA_DIR = "tests/data"
INPUT_DIR = "tests/input"
EXP_DIR = "tests/expected"

# PRECISION FOR AVG OPERATION
PRECISION = 2


def generate_table(n):
    """ Generate a data table. """
    file = os.path.join(DATA_DIR, 'data3.csv')

    header_line = utils.generate_header('db1', 'tbl3_batch', 4)
    table = pd.DataFrame(np.random.randint(0, n/5, size=(n, 4)), columns=['col1', 'col2', 'col3', 'col4'])
    table['col1'] = np.random.randint(0, 1000, size=(n))
    table['col4'] = np.random.randint(0, 10000, size=(n))
    table['col4'] = table['col4'] + table['col1']
    table.to_csv(file, sep=',', index=False, header=header_line, lineterminator='\n')
    return table


def test10():
    """ Test for loading data. """
    with utils.InputFileWriter(10, test_dir=INPUT_DIR) as f:
        f.write('-- Load Test Data 2\n')
        f.write('-- Create a table to run batch queries on\n')
        f.write('--\n')
        f.write('-- Loads data from: data3_batch.csv\n')
        f.write('--\n')
        f.write('-- Create Table\n')
        f.write('create(tbl,"tbl3_batch",db1,4)\n')
        f.write('create(col,"col1",db1.tbl3_batch)\n')
        f.write('create(col,"col2",db1.tbl3_batch)\n')
        f.write('create(col,"col3",db1.tbl3_batch)\n')
        f.write('create(col,"col4",db1.tbl3_batch)\n')
        f.write('--\n')
        f.write('-- Load data immediately\n')
        f.write(f'load("{os.path.join(DATA_DIR, "data3.csv")}")\n')
        f.write('--\n')
        f.write('-- Testing that the data is durable on disk.\n')
        f.write('shutdown\n')

    with utils.ExpectedFileWriter(10, test_dir=EXP_DIR) as f:
        f.write('')
        # TODO: see if we can print out entire schema or something


def test11(table):
    """ Test batching queries with no overlap. """
    select_ge1 = 10
    select_lt1 = 20
    select_ge2 = 800
    select_lt2 = 830

    with utils.InputFileWriter(11, test_dir=INPUT_DIR) as f:
        f.write('-- Testing for batching queries\n')
        f.write('-- 2 queries with NO overlap\n')
        f.write('--\n')
        f.write('-- SELECT col4 FROM tbl3_batch WHERE col1 >= 10 AND col1 < 20;\n')
        f.write('-- SELECT col4 FROM tbl3_batch WHERE col1 >= 800 AND col1 < 830;\n')
        f.write('--\n')
        f.write('batch_queries()\n')
        f.write(f's1=select(db1.tbl3_batch.col1,{select_ge1},{select_lt1})\n')
        f.write(f's2=select(db1.tbl3_batch.col1,{select_ge2},{select_lt2})\n')
        f.write('batch_execute()\n')
        f.write('f1=fetch(db1.tbl3_batch.col4,s1)\n')
        f.write('f2=fetch(db1.tbl3_batch.col4,s2)\n')
        f.write('print(f1)\n')
        f.write('print(f2)\n')

    with utils.ExpectedFileWriter(11, test_dir=EXP_DIR) as f:
        exp1 = table[(table['col1'] >= select_ge1) & (table['col1'] < select_lt1)]['col4']
        exp2 = table[(table['col1'] >= select_ge2) & (table['col1'] < select_lt2)]['col4']
        f.write(utils.print_table(exp1) + '\n\n')
        f.write(utils.print_table(exp2) + '\n')


def test12(table):
    """ Test batching queries with partial overlap. """
    select_ge1 = 600
    select_lt1 = 820
    select_ge2 = 800
    select_lt2 = 830

    with utils.InputFileWriter(12, test_dir=INPUT_DIR) as f:
        f.write('-- Testing for batching queries\n')
        f.write('-- 2 queries with partial overlap\n')
        f.write('--\n')
        f.write('-- SELECT col4 FROM tbl3_batch WHERE col1 >= 600 AND col1 < 820;\n')
        f.write('-- SELECT col4 FROM tbl3_batch WHERE col1 >= 800 AND col1 < 830;\n')
        f.write('--\n')
        f.write('batch_queries()\n')
        f.write(f's1=select(db1.tbl3_batch.col1,{select_ge1},{select_lt1})\n')
        f.write(f's2=select(db1.tbl3_batch.col1,{select_ge2},{select_lt2})\n')
        f.write('batch_execute()\n')
        f.write('f1=fetch(db1.tbl3_batch.col4,s1)\n')
        f.write('f2=fetch(db1.tbl3_batch.col4,s2)\n')
        f.write('print(f1)\n')
        f.write('print(f2)\n')

    with utils.ExpectedFileWriter(12, test_dir=EXP_DIR) as f:
        exp1 = table[(table['col1'] >= select_ge1) & (table['col1'] < select_lt1)]['col4']
        exp2 = table[(table['col1'] >= select_ge2) & (table['col1'] < select_lt2)]['col4']
        f.write(utils.print_table(exp1) + '\n\n')
        f.write(utils.print_table(exp2) + '\n')


def test13(table):
    """ Test batching queries with full overlap (subsumption). """
    select_ge1 = 810
    select_lt1 = 820
    select_ge2 = 800
    select_lt2 = 830

    with utils.InputFileWriter(13, test_dir=INPUT_DIR) as f:
        f.write('-- Testing for batching queries\n')
        f.write('-- 2 queries with full overlap (subsumption)\n')
        f.write('--\n')
        f.write('-- SELECT col4 FROM tbl3_batch WHERE col1 >= 810 AND col1 < 820;\n')
        f.write('-- SELECT col4 FROM tbl3_batch WHERE col1 >= 800 AND col1 < 830;\n')
        f.write('--\n')
        f.write('batch_queries()\n')
        f.write(f's1=select(db1.tbl3_batch.col1,{select_ge1},{select_lt1})\n')
        f.write(f's2=select(db1.tbl3_batch.col1,{select_ge2},{select_lt2})\n')
        f.write('batch_execute()\n')
        f.write('f1=fetch(db1.tbl3_batch.col4,s1)\n')
        f.write('f2=fetch(db1.tbl3_batch.col4,s2)\n')
        f.write('print(f1)\n')
        f.write('print(f2)\n')

    with utils.ExpectedFileWriter(13, test_dir=EXP_DIR) as f:
        exp1 = table[(table['col1'] >= select_ge1) & (table['col1'] < select_lt1)]['col4']
        exp2 = table[(table['col1'] >= select_ge2) & (table['col1'] < select_lt2)]['col4']
        f.write(utils.print_table(exp1) + '\n\n')
        f.write(utils.print_table(exp2) + '\n')


def test14(table):
    """ Test batching multiple queries with no overlap. """
    select_ges = [1000 * i for i in range(10)]
    select_lts = [(1000 * i) + 30 for i in range(10)]

    with utils.InputFileWriter(14, test_dir=INPUT_DIR) as f:
        f.write('-- Testing for batching queries\n')
        f.write('-- 10 queries with no overlap\n')
        f.write('--\n')
        f.write('-- 10 Queries of the type:\n')
        f.write('-- SELECT col4 FROM tbl3_batch WHERE col1 >= _ AND col1 < _;\n')
        f.write('--\n')
        f.write('batch_queries()\n')
        for i in range(10):
            f.write(f's{i}=select(db1.tbl3_batch.col1,{select_ges[i]},{select_lts[i]})\n')
        f.write('batch_execute()\n')
        for i in range(10):
            f.write(f'f{i}=fetch(db1.tbl3_batch.col4,s{i})\n')
        for i in range(10):
            f.write(f'print(f{i})\n')

    with utils.ExpectedFileWriter(14, test_dir=EXP_DIR) as f:
        for i in range(10):
            exp = table[(table['col1'] >= select_ges[i]) & (table['col1'] < select_lts[i])]['col4']
            f.write(utils.print_table(exp) + '\n')
            if i != 9:
                f.write('\n')


def test15(table):
    """ Test batching multiple queries with full overlap (subsumption). """
    val = np.random.randint(1000, 9900)
    select_ges = [val + 2 * i for i in range(10)]
    select_lts = [val + 60 - (2 * i) for i in range(10)]

    with utils.InputFileWriter(15, test_dir=INPUT_DIR) as f:
        f.write('-- Testing for batching queries\n')
        f.write('-- 10 queries with full overlap (subsumption)\n')
        f.write('--\n')
        f.write('-- 10 Queries of the type:\n')
        f.write('-- SELECT col1 FROM tbl3_batch WHERE col4 >= _ AND col4 < _;\n')
        f.write('--\n')
        f.write('batch_queries()\n')
        for i in range(10):
            f.write(f's{i}=select(db1.tbl3_batch.col4,{select_ges[i]},{select_lts[i]})\n')
        f.write('batch_execute()\n')
        for i in range(10):
            f.write(f'f{i}=fetch(db1.tbl3_batch.col1,s{i})\n')
        for i in range(10):
            f.write(f'print(f{i})\n')

    with utils.ExpectedFileWriter(15, test_dir=EXP_DIR) as f:
        for i in range(10):
            exp = table[(table['col4'] >= select_ges[i]) & (table['col4'] < select_lts[i])]['col1']
            f.write(utils.print_table(exp) + '\n')
            if i != 9:
                f.write('\n')


def test16_17_18_19(table):
    """
    Pair tests for batching a large number of queries.
    16 has no batching and 17 has batching.
    18 and 19 are single-core versions of 16 and 17 respectively.
    """
    n = table.shape[0]

    offset = max(1, n // 5000)
    query_starts = np.random.randint(0, (n/8), size=(100))
    query_ends = query_starts + offset

    with utils.InputFileWriter(16, test_dir=INPUT_DIR) as f16, \
            utils.InputFileWriter(17, test_dir=INPUT_DIR) as f17, \
            utils.InputFileWriter(18, test_dir=INPUT_DIR) as f18, \
            utils.InputFileWriter(19, test_dir=INPUT_DIR) as f19:
        utils.write_multiple('--', f16, f17, f18, f19)
        f16.write('-- Without batching, multi-core\n')
        f17.write('-- With batching, multi-core\n')
        f18.write('-- Without batching, single-core\n')
        f19.write('-- With batching, single-core\n')
        utils.write_multiple('--\n', f16, f17, f18, f19)
        utils.write_multiple('-- 100 queries of the type:\n', f16, f17, f18, f19)
        utils.write_multiple('-- SELECT col3 FROM tbl3_batch WHERE col2 >= _ AND col2 < _;\n', f16, f17, f18, f19)
        utils.write_multiple('--\n', f16, f17, f18, f19)
        utils.write_multiple('single_core()\n', f18, f19)
        utils.write_multiple('batch_queries()\n', f17, f19)
        for i in range(100):
            utils.write_multiple(f's{i}=select(db1.tbl3_batch.col2,{query_starts[i]},{query_ends[i]})\n', f16, f17, f18, f19)
        utils.write_multiple('batch_execute()\n', f17, f19)
        for i in range(100):
            utils.write_multiple(f'f{i}=fetch(db1.tbl3_batch.col3,s{i})\n', f16, f17, f18, f19)
        utils.write_multiple('single_core_execute()\n', f18, f19)
        for i in range(100):
            utils.write_multiple(f'print(f{i})\n', f16, f17, f18, f19)

    with utils.ExpectedFileWriter(16, test_dir=EXP_DIR) as f16, \
            utils.ExpectedFileWriter(17, test_dir=EXP_DIR) as f17, \
            utils.ExpectedFileWriter(18, test_dir=EXP_DIR) as f18, \
            utils.ExpectedFileWriter(19, test_dir=EXP_DIR) as f19:
        for i in range(100):
            exp = table[(table['col2'] >= query_starts[i]) & ((table['col2'] < query_ends[i]))]['col3']
            utils.write_multiple(utils.print_table(exp) + '\n', f16, f17, f18, f19)
            if i != 99:
                utils.write_multiple('\n', f16, f17, f18, f19)


def main():
    table = generate_table(10000)

    test10()
    test11(table)
    test12(table)
    test13(table)
    test14(table)
    test15(table)
    test16_17_18_19(table)


if __name__ == "__main__":
    main()
