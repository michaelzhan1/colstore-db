#!/usr/bin/python
import os

import numpy as np
import pandas as pd
import utils

DATA_DIR = "tests/data"
INPUT_DIR = "tests/input"
EXP_DIR = "tests/expected"


def generate_simple_table(n):
    """ Generates data file for first table. Table contains simple data """
    file = os.path.join(DATA_DIR, 'data1.csv')

    header_line = utils.generate_header('db1', 'tbl1', 2)
    column1 = list(range(0, n))
    column2 = list(range(10, n + 10))

    np.random.shuffle(column2)
    table = pd.DataFrame(list(zip(column1, column2)), columns=['col1', 'col2'])
    table.to_csv(file, sep=',', index=False, header=header_line, lineterminator='\n')
    return table


def generate_complex_table(n):
    """
    Generates data file for second table.
    Table contains 4 columns:
        col1: values between -n // 2 and n // 2
        col2: values between -n and n
        col3: values between 0 and 100
        col4: values between 2^31-10000 and 2^31
    """
    file = os.path.join(DATA_DIR, 'data2.csv')

    header_line = utils.generate_header('db1', 'tbl2', 4)
    table = pd.DataFrame(np.random.randint(-n // 2, n // 2, size=(n, 4)), columns=['col1', 'col2', 'col3', 'col4'])
    table['col2'] += table['col1']
    table['col3'] = np.random.randint(0, 100, size=(n))
    table['col4'] = np.random.randint((1 << 31) - n, 1 << 31, size=(n))
    table.to_csv(file, sep=',', index=False, header=header_line, lineterminator='\n')
    return table


def test1():
    """ Test creating table and columns, loading data, and shutting down without errors. """
    with utils.InputFileWriter(1, test_dir=INPUT_DIR) as f:
        f.write('-- Load+create Data and shut down of tbl1 which has 1 attribute only\n')
        f.write('create(db,\"db1\")\n')
        f.write('create(tbl,\"tbl1\",db1,2)\n')
        f.write('create(col,\"col1\",db1.tbl1)\n')
        f.write('create(col,\"col2\",db1.tbl1)\n')
        f.write(f'load("{os.path.join(DATA_DIR, "data1.csv")}")\n')
        f.write('shutdown\n')

    with utils.ExpectedFileWriter(1, test_dir=EXP_DIR) as f:
        f.write('')  # No expected output for this test
        # TODO: see if we can print out schema or something,
        # or print out the entire table


def test2(table):
    """ Test select and fetch. """
    select_lt = 20
    select_ge = 987

    with utils.InputFileWriter(2, test_dir=INPUT_DIR) as f:
        f.write('-- Test Select + Fetch\n')
        f.write('--\n')
        f.write(f'-- SELECT col1 FROM tbl1 WHERE col1 < {select_lt};\n')
        f.write(f's1=select(db1.tbl1.col1,null,{select_lt})\n')
        f.write('f1=fetch(db1.tbl1.col1,s1)\n')
        f.write('print(f1)\n')
        f.write('--\n')
        f.write(f'-- SELECT col2 FROM tbl1 WHERE col1 >= {select_ge};\n')
        f.write(f's2=select(db1.tbl1.col1,{select_ge},null)\n')
        f.write('f2=fetch(db1.tbl1.col2,s2)\n')
        f.write('print(f2)\n')

    with utils.ExpectedFileWriter(2, test_dir=EXP_DIR) as f:
        exp1 = table[table['col1'] < select_lt]['col1']
        exp2 = table[table['col1'] >= select_ge]['col2']
        f.write(utils.print_table(exp1) + '\n\n')
        f.write(utils.print_table(exp2) + '\n')


def test3(table):
    """ Test cross select and average. """
    select_ge = 956
    select_lt = 972

    with utils.InputFileWriter(3, test_dir=INPUT_DIR) as f:
        f.write('-- Test Multiple Selects + Average\n')
        f.write('--\n')
        f.write(f'-- SELECT avg(col2) FROM tbl1 WHERE col1 >= {select_ge} and col1 < {select_lt};\n')
        f.write(f's1=select(db1.tbl1.col1,{select_ge},{select_lt})\n')
        f.write('f1=fetch(db1.tbl1.col2,s1)\n')
        f.write('a1=avg(f1)\n')
        f.write('print(a1)\n')

    with utils.ExpectedFileWriter(3, test_dir=EXP_DIR) as f:
        exp = table[(table['col1'] >= select_ge) & (table['col1'] < select_lt)]['col2']
        f.write(f'{exp.mean():0.2f}\n')


def test4():
    """ Test relational insert. """
    new_rows = pd.DataFrame([[-1, -11, -111, -1111],
                             [-2, -22, -222, -2222],
                             [-3, -33, -333, -2222],
                             [-4, -44, -444, -2222],
                             [-5, -55, -555, -2222],
                             [-6, -66, -666, -2222],
                             [-7, -77, -777, -2222],
                             [-8, -88, -888, -2222],
                             [-9, -99, -999, -2222],
                             [-10, -11, 0, -34]], columns=['col1', 'col2', 'col3', 'col4'])

    with utils.InputFileWriter(4, test_dir=INPUT_DIR) as f:
        f.write('-- Load Test Data 2\n')
        f.write('--\n')
        f.write('-- Load+create+insert Data and shut down of tbl2 which has 4 attributes\n')
        f.write('create(tbl,\"tbl2\",db1,4)\n')
        f.write('create(col,\"col1\",db1.tbl2)\n')
        f.write('create(col,\"col2\",db1.tbl2)\n')
        f.write('create(col,\"col3\",db1.tbl2)\n')
        f.write('create(col,\"col4\",db1.tbl2)\n')
        f.write(f'load("{os.path.join(DATA_DIR, "data2.csv")}")\n')
        new_rows.apply(
            lambda row: f.write(
                f'relational_insert(db1.tbl2,{row["col1"]},{row["col2"]},{row["col3"]},{row["col4"]})\n'),
            axis=1)
        f.write('shutdown\n')

    with utils.ExpectedFileWriter(4, test_dir=EXP_DIR) as f:
        f.write('')  # No expected output for this test
        # TODO: see if we can print out schema or something,
        # or print out the entire table


def test5(table, selectivity):
    """ Test summation. """
    if selectivity < 0 or selectivity > 1:
        raise ValueError("Selectivity should be between 0 and 1")

    n = table.shape[0]

    offset = int(selectivity * n)
    select_ge = np.random.randint(-n // 2, n // 2 - offset)
    select_lt = select_ge + offset

    with utils.InputFileWriter(5, test_dir=INPUT_DIR) as f:
        f.write('-- Test Summation\n')
        f.write('--\n')
        f.write(f'-- SELECT SUM(col3) FROM tbl2 WHERE col1 >= {select_ge} AND col1 < {select_lt};\n')
        f.write(f's1=select(db1.tbl2.col1,{select_ge},{select_lt})\n')
        f.write('f1=fetch(db1.tbl2.col3,s1)\n')
        f.write('a1=sum(f1)\n')
        f.write('print(a1)\n')
        f.write('--\n')
        f.write('-- SELECT SUM(col1) FROM tbl2;\n')
        f.write('a2=sum(db1.tbl2.col1)\n')
        f.write('print(a2)\n')

    with utils.ExpectedFileWriter(5, test_dir=EXP_DIR) as f:
        exp = table[(table['col1'] >= select_ge) & (table['col1'] < select_lt)]['col3']
        f.write(f'{exp.sum()}\n')
        f.write(f'{table["col1"].sum()}\n')


def test6(table, selectivity):
    """ Test column addition. """
    if selectivity < 0 or selectivity > 1:
        raise ValueError("Selectivity should be between 0 and 1")

    n = table.shape[0]

    offset = int(selectivity * n)
    select_ge = np.random.randint(-n // 2, n // 2 - offset)
    select_lt = select_ge + offset

    with utils.InputFileWriter(6, test_dir=INPUT_DIR) as f:
        f.write('-- Test Column Addition\n')
        f.write('--\n')
        f.write(f'-- SELECT col2+col3 FROM tbl2 WHERE col1 >= {select_ge} AND col1 < {select_lt};\n')
        f.write(f's1=select(db1.tbl2.col1,{select_ge},{select_lt})\n')
        f.write('f1=fetch(db1.tbl2.col2,s1)\n')
        f.write('f2=fetch(db1.tbl2.col3,s1)\n')
        f.write('a1=add(f1,f2)\n')
        f.write('print(a1)\n')

    with utils.ExpectedFileWriter(6, test_dir=EXP_DIR) as f:
        exp = table[(table['col1'] >= select_ge) & (table['col1'] < select_lt)]
        f.write(utils.print_table(exp['col2'] + exp['col3']) + '\n')


def test7(table, selectivity):
    """ Test column subtraction. """
    if selectivity < 0 or selectivity > 1:
        raise ValueError("Selectivity should be between 0 and 1")

    n = table.shape[0]

    offset = int(selectivity * n)
    select_ge = np.random.randint(-n // 2, n // 2 - offset)
    select_lt = select_ge + offset

    with utils.InputFileWriter(7, test_dir=INPUT_DIR) as f:
        f.write('-- Test Column Subtraction\n')
        f.write('--\n')
        f.write(f'-- SELECT col3-col2 FROM tbl2 WHERE col1 >= {select_ge} AND col1 < {select_lt};\n')
        f.write(f's1=select(db1.tbl2.col1,{select_ge},{select_lt})\n')
        f.write('f1=fetch(db1.tbl2.col2,s1)\n')
        f.write('f2=fetch(db1.tbl2.col3,s1)\n')
        f.write('s2=sub(f2,f1)\n')
        f.write('print(s2)\n')

    with utils.ExpectedFileWriter(7, test_dir=EXP_DIR) as f:
        exp = table[(table['col1'] >= select_ge) & (table['col1'] < select_lt)]
        f.write(utils.print_table(exp['col3'] - exp['col2']) + '\n')


def test8(table, selectivity):
    """ Test min and max. """
    if selectivity < 0 or selectivity > 1:
        raise ValueError("Selectivity should be between 0 and 1")

    n = table.shape[0]

    offset = int(selectivity * n)
    select_ge = np.random.randint(-n // 2, n // 2 - offset)
    select_lt = select_ge + offset

    with utils.InputFileWriter(8, test_dir=INPUT_DIR) as f:
        f.write('-- Test Min and Max\n')
        f.write('--\n')
        f.write('-- SELECT min(col1) FROM tbl2;\n')
        f.write('a1=min(db1.tbl2.col1)\n')
        f.write('print(a1)\n')
        f.write('--\n')
        f.write('--\n')
        f.write(f'-- SELECT min(col1) FROM tbl2 WHERE col1 >= {select_ge} AND col1 < {select_lt};\n')
        f.write(f's1=select(db1.tbl2.col1,{select_ge},{select_lt})\n')
        f.write('f1=fetch(db1.tbl2.col1,s1)\n')
        f.write('m1=min(f1)\n')
        f.write('print(m1)\n')
        f.write('--\n')
        f.write(f'-- SELECT min(col2) FROM tbl2 WHERE col1 >= {select_ge} AND col1 < {select_lt};\n')
        f.write('f2=fetch(db1.tbl2.col2,s1)\n')
        f.write('m2=min(f2)\n')
        f.write('print(m2)\n')
        f.write('--\n')
        f.write('--\n')
        f.write('-- SELECT max(col1) FROM tbl2;\n')
        f.write('a2=max(db1.tbl2.col1)\n')
        f.write('print(a2)\n')
        f.write('--\n')
        f.write('--\n')
        f.write(f'-- SELECT max(col1) FROM tbl2 WHERE col1 >= {select_ge} AND col1 < {select_lt};\n')
        f.write(f's21=select(db1.tbl2.col1,{select_ge},{select_lt})\n')
        f.write('f21=fetch(db1.tbl2.col1,s21)\n')
        f.write('m21=max(f21)\n')
        f.write('print(m21)\n')
        f.write('--\n')
        f.write(f'-- SELECT max(col2) FROM tbl2 WHERE col1 >= {select_ge} AND col1 < {select_lt};\n')
        f.write('f22=fetch(db1.tbl2.col2,s21)\n')
        f.write('m22=max(f22)\n')
        f.write('print(m22)\n')

    with utils.ExpectedFileWriter(8, test_dir=EXP_DIR) as f:
        exp = table[(table['col1'] >= select_ge) & (table['col1'] < select_lt)]
        f.write(f"{table['col1'].min()}\n")
        f.write(f"{exp['col1'].min()}\n")
        f.write(f"{exp['col2'].min()}\n")
        f.write(f"{table['col1'].max()}\n")
        f.write(f"{exp['col1'].max()}\n")
        f.write(f"{exp['col2'].max()}\n")


def test9(table, selectivity):
    """ Combination of tests from 1-8. """
    if selectivity < 0 or selectivity > 1:
        raise ValueError("Selectivity should be between 0 and 1")

    n = table.shape[0]

    offset = int(selectivity * n)
    select_ge1 = np.random.randint(-n // 2, n // 2 - offset)
    select_ge2 = np.random.randint(-n // 2, n // 2 - offset)
    select_lt1 = select_ge1 + offset
    select_lt2 = select_ge2 + offset

    with utils.InputFileWriter(9, test_dir=INPUT_DIR) as f:
        f.write('-- Test Combination of Operations\n')
        f.write('--\n')

        # query set 1
        f.write(
            f'-- SELECT min(col2), max(col3), sum(col3-col2) FROM tbl2 WHERE (col1 >= {select_ge1} AND col1 < {select_lt1}) AND (col2 >= {select_ge2} AND col2 < {select_lt2});\n')
        f.write(f's1=select(db1.tbl2.col1,{select_ge1},{select_lt1})\n')
        f.write('sf1=fetch(db1.tbl2.col2,s1)\n')
        f.write(f's2=select(s1,sf1,{select_ge2},{select_lt2})\n')
        f.write('f2=fetch(db1.tbl2.col2,s2)\n')
        f.write('f3=fetch(db1.tbl2.col3,s2)\n')
        f.write('out11=min(f2)\n')
        f.write('out12=max(f3)\n')
        f.write('sub32=sub(f3,f2)\n')
        f.write('out13=sum(sub32)\n')
        f.write('print(out11,out12,out13)\n')
        f.write('--\n')

        # query set 2
        f.write(
            f'-- SELECT avg(col1+col2), min(col2), max(col3), avg(col3-col2), sum(col3-col2) FROM tbl2 WHERE (col1 >= {select_ge1} AND col1 < {select_lt1}) AND (col2 >= {select_ge2} AND col2 < {select_lt2});\n')
        f.write(f's1=select(db1.tbl2.col1,{select_ge1},{select_lt1})\n')
        f.write('sf1=fetch(db1.tbl2.col2,s1)\n')
        f.write(f's2=select(s1,sf1,{select_ge2},{select_lt2})\n')
        f.write('f1=fetch(db1.tbl2.col1,s2)\n')
        f.write('f2=fetch(db1.tbl2.col2,s2)\n')
        f.write('f3=fetch(db1.tbl2.col3,s2)\n')
        f.write('add12=add(f1,f2)\n')
        f.write('out1=avg(add12)\n')
        f.write('out2=min(f2)\n')
        f.write('out3=max(f3)\n')
        f.write('sub32=sub(f3,f2)\n')
        f.write('out4=avg(sub32)\n')
        f.write('out5=sum(sub32)\n')
        f.write('print(out1,out2,out3,out4,out5)\n')

    with utils.ExpectedFileWriter(9, test_dir=EXP_DIR) as f:
        mask = (
            table['col1'] >= select_ge1) & (
            table['col1'] < select_lt1) & (
            table['col2'] >= select_ge2) & (
            table['col2'] < select_lt2)
        col1 = table[mask]['col1']
        col2 = table[mask]['col2']
        col3 = table[mask]['col3']

        col2_min = col2.min() if col2.shape[0] > 0 else 0
        col3_max = col3.max() if col3.shape[0] > 0 else 0

        col12sum = col1 + col2
        col32diff = col3 - col2

        col12sum_avg = col12sum.mean() if col12sum.shape[0] > 0 else 0
        col32diff_avg = col32diff.mean() if col32diff.shape[0] > 0 else 0

        # query 1
        f.write(f'{col2_min},{col3_max},{col32diff.sum()}\n')

        # query 2
        f.write(f'{col12sum_avg:0.0f},{col2_min},{col3_max},{col32diff_avg:0.2f},{col32diff.sum()}\n')


def main():
    np.random.seed(0)  # for reproducibility

    # make tables
    table1 = generate_simple_table(1000)
    table2 = generate_complex_table(10000)

    # make tests
    test1()
    test2(table1)
    test3(table1)
    test4()
    test5(table2, 0.8)
    test6(table2, 0.8)
    test7(table2, 0.8)
    test8(table2, 0.8)
    test9(table2, 0.8)


if __name__ == "__main__":
    main()
