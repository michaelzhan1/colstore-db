#!/usr/bin/python
import os

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
    table['col1'] = np.random.randint(0, 1000, size=(n))
    table['col2'] = np.random.randint(0, 10000, size=(n))
    table['col4'] = np.random.randint(0, 10000, size=(n))

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
        for i, val in enumerate(vals):
            exp = table[(table['col2'] >= val) & (table['col2'] < (val + offset))]['col3']
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

        for i, val in enumerate(vals):
            f28.write(f's{i}=select(db1.tbl4_ctrl.col2,{val},{val + offset})\n')
            f29.write(f's{i}=select(db1.tbl4.col2,{val},{val + offset})\n')
            f28.write(f'f{i}=fetch(db1.tbl4_ctrl.col3,s{i})\n')
            f29.write(f'f{i}=fetch(db1.tbl4.col3,s{i})\n')
            utils.write_multiple(f'a{i}=avg(f{i})\n', f28, f29)
            utils.write_multiple(f'print(a{i})\n', f28, f29)

    with utils.ExpectedFileWriter(28, test_dir=EXP_DIR) as f28, utils.ExpectedFileWriter(29, test_dir=EXP_DIR) as f29:
        for i, val in enumerate(vals):
            exp = table[(table['col2'] >= val) & (table['col2'] < (val + offset))]['col3']
            mean = exp.mean() if exp.shape[0] > 0 else 0
            utils.write_multiple(f'{mean:0.2f}\n', f28, f29)


def test30():
    """ Test for creating a table with a clustered b-tree index and a secondary unclustered sorted index. """
    with utils.InputFileWriter(30, test_dir=INPUT_DIR) as f:
        f.write('-- Test for creating table with indexes\n')
        f.write('--\n')
        f.write('-- Table tbl4_clustered_btree has a clustered index with col3 being the leading column.\n')
        f.write('-- The clustered index has the form of a B-Tree.\n')
        f.write('-- The table also has a secondary sorted index.\n')
        f.write('--\n')
        f.write('-- Loads data from: data4_clustered_btree.csv\n')
        f.write('--\n')
        f.write('-- Create Table\n')
        f.write('create(tbl,"tbl4_clustered_btree",db1,4)\n')
        f.write('create(col,"col1",db1.tbl4_clustered_btree)\n')
        f.write('create(col,"col2",db1.tbl4_clustered_btree)\n')
        f.write('create(col,"col3",db1.tbl4_clustered_btree)\n')
        f.write('create(col,"col4",db1.tbl4_clustered_btree)\n')
        f.write('-- Create a clustered index on col3\n')
        f.write('create(idx,db1.tbl4_clustered_btree.col3,btree,clustered)\n')
        f.write('-- Create an unclustered btree index on col2\n')
        f.write('create(idx,db1.tbl4_clustered_btree.col2,sorted,unclustered)\n')
        f.write('--\n')
        f.write('--\n')
        f.write('-- Load data immediately in the form of a clustered index\n')
        f.write(f'load("{os.path.join(DATA_DIR, "data4_clustered_btree.csv")}")\n')
        f.write('--\n')
        f.write('-- Testing that the data and their indexes are durable on disk.\n')
        f.write('shutdown\n')

    with utils.ExpectedFileWriter(30, test_dir=EXP_DIR) as f:
        f.write('')


def test31(table):
    """ Test for select queries on clustered b-tree index vs no index."""
    n = table.shape[0]

    offset1 = max(1, n // 5000)
    offset2 = max(2, n // 2500)
    val1 = np.random.randint(0, n // 5 - offset1)
    val2 = np.random.randint(0, n // 5 - offset2)

    with utils.InputFileWriter(31, test_dir=INPUT_DIR) as f:
        f.write('-- Test for select queries on clustered b-tree index vs no index\n')
        f.write('--\n')
        f.write('-- tbl4_clustered_btree has a secondary sorted index on col2, and a clustered b-tree index on col3\n')
        f.write('-- testing for correctness\n')
        f.write('--\n')
        f.write('-- Query in SQL:\n')
        f.write(f'-- SELECT col1 FROM tbl4_clustered_btree WHERE col3 >= {val1} and col3 < {val1 + offset1};\n')
        f.write(f'-- SELECT col1 FROM tbl4_clustered_btree WHERE col3 >= {val2} and col3 < {val2 + offset2};\n')
        f.write('--\n')
        f.write('-- since col3 has a clustered index, the index is expected to be used by the select operator\n')
        f.write(f's1=select(db1.tbl4_clustered_btree.col3,{val1},{val1 + offset1})\n')
        f.write('f1=fetch(db1.tbl4_clustered_btree.col1,s1)\n')
        f.write('print(f1)\n')
        f.write(f's2=select(db1.tbl4_clustered_btree.col3,{val2},{val2 + offset2})\n')
        f.write('f2=fetch(db1.tbl4_clustered_btree.col1,s2)\n')
        f.write('print(f2)\n')

    with utils.ExpectedFileWriter(31, test_dir=EXP_DIR) as f:
        exp1 = table[(table['col3'] >= val1) & ((table['col3'] < (val1 + offset1)))]['col1']
        exp2 = table[(table['col3'] >= val2) & ((table['col3'] < (val2 + offset2)))]['col1']
        f.write(utils.print_table(exp1) + '\n\n')
        f.write(utils.print_table(exp2) + '\n')


def test32(table):
    """ Test for a non-clustered index select followed by an aggregate, on many queries with varying selectivities. """
    n = table.shape[0]
    offset = max(2, n // 1000)
    vals = np.random.randint(0, n // 5 - offset, size=5)

    with utils.InputFileWriter(32, test_dir=INPUT_DIR) as f:
        f.write('-- Test for a non-clustered index select followed by an aggregate, on many queries with varying selectivities\n')
        f.write('--\n')
        f.write('-- Query form in SQL:\n')
        f.write('-- SELECT sum(col3) FROM tbl4_clustered_btree WHERE (col2 >= _ and col2 < _);\n')
        f.write('--\n')

        for i, val in enumerate(vals):
            f.write(f's{i}=select(db1.tbl4_clustered_btree.col2,{val},{val + offset})\n')
            f.write(f'f{i}=fetch(db1.tbl4_clustered_btree.col3,s{i})\n')
            f.write(f'a{i}=sum(f{i})\n')
            f.write(f'print(a{i})\n')

    with utils.ExpectedFileWriter(32, test_dir=EXP_DIR) as f:
        for i, val in enumerate(vals):
            exp = table[(table['col2'] >= val) & (table['col2'] < (val + offset))]['col3']
            f.write(f'{exp.sum()}\n')


def test33_to_38(table):
    """
    Performance tests for different indexing strategies.

    33: no index, selectivity 0.1%
    34: clustered sorted index, selectivity 0.1%
    35: clustered b-tree index, selectivity 0.1%
    36: no index, selectivity 1%
    37: clustered sorted index, selectivity 1%
    38: clustered b-tree index, selectivity 1%

    Comparisons are made between: 33-34, 34-35, 36-37, 37-38
    """
    n = table.shape[0]
    offsets = [max(1, n // 5000), max(2, n // 500)]
    selectivities = ['0.1%', '1%']
    table_names = ['tbl4_ctrl', 'tbl4', 'tbl4_clustered_btree']
    vals = np.random.randint(0, n // 5 - offsets[1], size=20 * len(table_names) * len(selectivities))

    test_start = 33
    for i, (offset, selectivity) in enumerate(zip(offsets, selectivities)):
        for j, table_name in enumerate(table_names):
            with utils.InputFileWriter(test_start, test_dir=INPUT_DIR) as f:
                f.write('--\n')
                f.write(f'-- selectivity={selectivity}\n')
                f.write('-- Query in SQL:\n')
                f.write(f'-- SELECT avg(col1) FROM {table_name} WHERE col3 >= _ and col3 < _;\n')
                f.write('--\n')

                for k in range(20):
                    val = vals[i * len(table_names) * 20 + j * 20 + k]
                    f.write(f's{k}=select(db1.{table_name}.col3,{val},{val + offset})\n')
                    f.write(f'f{k}=fetch(db1.{table_name}.col1,s{k})\n')
                    f.write(f'a{k}=avg(f{k})\n')
                    f.write(f'print(a{k})\n')

            with utils.ExpectedFileWriter(test_start, test_dir=EXP_DIR) as f:
                for k in range(20):
                    val = vals[i * len(table_names) * 20 + j * 20 + k]
                    exp = table[(table['col3'] >= val) & (table['col3'] < (val + offset))]['col1']
                    mean = exp.mean() if exp.shape[0] > 0 else 0
                    f.write(f'{mean:0.2f}\n')

            test_start += 1


def test39_to_44(table):
    """
    Performance tests for different indexing strategies.

    39: no index, selectivity 0.1%
    40: unclustered b-tree index, selectivity 0.1%
    41: unclustered sorted index, selectivity 0.1%
    42: no index, selectivity 1%
    43: unclustered b-tree index, selectivity 1%
    44: unclustered sorted index, selectivity 1%

    Comparisons are made between: 39-40, 40-41, 42-43, 43-44
    """
    n = table.shape[0]
    offsets = [max(1, n // 5000), max(2, n // 500)]
    selectivities = ['0.1%', '1%']
    table_names = ['tbl4_ctrl', 'tbl4', 'tbl4_clustered_btree']
    vals = np.random.randint(0, n // 5 - offsets[1], size=20 * len(table_names) * len(selectivities))

    test_start = 39
    for i, (offset, selectivity) in enumerate(zip(offsets, selectivities)):
        for j, table_name in enumerate(table_names):
            with utils.InputFileWriter(test_start, test_dir=INPUT_DIR) as f:
                f.write('--\n')
                f.write(f'-- selectivity={selectivity}\n')
                f.write('-- Query in SQL:\n')
                f.write(f'-- SELECT avg(col3) FROM {table_name} WHERE col2 >= _ and col2 < _;\n')
                f.write('--\n')

                for k in range(20):
                    val = vals[i * len(table_names) * 20 + j * 20 + k]
                    f.write(f's{k}=select(db1.{table_name}.col2,{val},{val + offset})\n')
                    f.write(f'f{k}=fetch(db1.{table_name}.col3,s{k})\n')
                    f.write(f'a{k}=avg(f{k})\n')
                    f.write(f'print(a{k})\n')

            with utils.ExpectedFileWriter(test_start, test_dir=EXP_DIR) as f:
                for k in range(20):
                    val = vals[i * len(table_names) * 20 + j * 20 + k]
                    exp = table[(table['col2'] >= val) & (table['col2'] < (val + offset))]['col3']
                    mean = exp.mean() if exp.shape[0] > 0 else 0
                    f.write(f'{mean:0.2f}\n')

            test_start += 1


def main():
    val1, val2, table = generate_table(10000)

    test20()
    test21()
    test22_23(table)
    test24(table)
    test25_26(table)
    test27(table, val1, val2)
    test28_29(table)
    test30()
    test31(table)
    test32(table)
    test33_to_38(table)
    test39_to_44(table)


if __name__ == "__main__":
    main()
