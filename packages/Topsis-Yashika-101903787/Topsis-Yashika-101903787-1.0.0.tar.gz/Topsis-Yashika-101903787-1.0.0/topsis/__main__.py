import sys
import pandas as pd
import numpy as np
import logging


def Calc_Values(dataset, nCol, impact):
    k = 0
    p_sln = dataset.max().values[0:]
    n_sln = dataset.min().values[0:]
    for i in range(1, nCol):
        if impact[k] == '-':
            p_sln[i], n_sln[i] = n_sln[i], p_sln[i]
        k = k + 2
    return p_sln, n_sln


class correct_arg(Exception):
    pass


class numberOfCol(Exception):
    pass


class incorrectInputFile(Exception):
    pass


class inputs(Exception):
    pass


class not_comma_separated(Exception):
    pass


class incorrect_impact(Exception):
    pass


class incorrect_weight(Exception):
    pass


class non_numeric_values(Exception):
    pass


def top_score(data, weights, impacts, result):
    n = len(sys.argv)
    logging.basicConfig(filename='101903787.log', level=logging.DEBUG)
    try:
        if n != 5:
            raise correct_arg
        if not (data).endswith('.csv'):
            raise incorrectInputFile
        topsis = pd.read_csv(data)
        # weights = sys.argv[2]
        # impacts = sys.argv[3]
        # result = sys.argv[4]
        top_cop = topsis.copy()
        for i in top_cop.columns[2:]:
            if topsis.dtypes[i] not in ['int64', 'int32', 'int16', 'float64']:
                raise non_numeric_values
        shape = topsis.shape
        cols = topsis.columns.values.tolist()
        if shape[1] < 3:
            raise numberOfCol
        sol = pd.DataFrame(columns=topsis.iloc[:, 0])
        if len(impacts) != len(weights):
            logging.error(len(impacts))
            logging.error(len(weights))
            raise inputs
        impact_size = 0
        i = 0
        while i in range(0, len(impacts)):
            if impacts[i] != '+' and impacts[i] != '-':
                raise incorrect_impact
            if not weights[i].isnumeric():
                raise incorrect_weight
            impact_size = impact_size + 1
            i = i + 2
        # topsis.drop(topsis.columns[0], axis=1, inplace=True)
        # shape = topsis.shape
        # logging.error(shape[1])
        if impact_size != shape[1] - 1:
            raise inputs
        while i in range(1, len(impacts)):
            if impacts[i] != ',':
                raise not_comma_separated
            if weights[i] != ',':
                raise not_comma_separated
            i = i + 2
        k = 0
        for i in range(1, shape[1]):
            topsis.iloc[:, i] = topsis.iloc[:, i] / np.linalg.norm(topsis.iloc[:, i])
            weight = int(weights[k])
            k = k + 2
            topsis.iloc[:, i] = topsis.iloc[:, i] * weight
        p_sln, n_sln = Calc_Values(topsis, shape[1], impacts)
        score = []
        pp = []
        nn = []
        for i in range(shape[0]):
            temp_p, temp_n = 0, 0
            for j in range(1, shape[1]):
                temp_p = temp_p + (p_sln[j] - topsis.iloc[i, j]) ** 2
                temp_n = temp_n + (n_sln[j] - topsis.iloc[i, j]) ** 2
            temp_p, temp_n = temp_p * 0.5, temp_n * 0.5
            score.append(temp_n / (temp_p + temp_n))
            nn.append(temp_n)
            pp.append(temp_p)
        topsis['distance positive'] = pp
        topsis['distance negative'] = nn
        topsis['Topsis Score'] = score

        topsis['Rank'] = (topsis['Topsis Score'].rank(method='max', ascending=False))
        topsis = topsis.astype({"Rank": int})
        top_cop['Topsis Score'] = topsis['Topsis Score']
        top_cop['Rank'] = topsis['Rank']
        # print(top_cop)
        top_cop.to_csv(result)
    except FileNotFoundError:
        logging.error("File not found")
    except incorrectInputFile:
        logging.error("Wrong Input file entered")
    except correct_arg:
        logging.error("Enter correct number of parameters")
    except numberOfCol:
        logging.error("Input file must contain three columns only")
    except inputs:
        logging.error("Wrong number of impacts or weights")
    except incorrect_impact:
        logging.error("Impact contains characters other than + and -")
    except not_comma_separated:
        logging.error("Impact or weight is not comma separated")
    except incorrect_weight:
        logging.error("Impact contains characters other than numeric values")
    except non_numeric_values:
        logging.error("data contains non numeric values")


if __name__ == '__main__':
    top_score(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])