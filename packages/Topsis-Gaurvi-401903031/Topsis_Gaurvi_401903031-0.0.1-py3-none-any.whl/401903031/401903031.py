import pandas as pd
import os
import sys
import logging

def main():
    n = len(sys.argv)
    logging.basicConfig(encoding='utf-8', filename='displayError.log', level=logging.DEBUG)

    class IncorrectArguments(Exception):
        pass

    class IncorrectFormatFile(Exception):
        pass

    class LessThanThree(Exception):
        pass

    class NonNumericValue(Exception):
        pass

    class ErrorImpact(Exception):
        pass

    class UnmatchingNumber(Exception):
        pass

    try:
        if len(sys.argv) != 5:
            raise IncorrectArguments

        elif ".csv" != (os.path.splitext(sys.argv[1]))[1]:
            raise IncorrectFormatFile

        else:
            dataset = pd.read_csv(sys.argv[1])
            temp_dataset = pd.read_csv(sys.argv[1])
            nCol = len(temp_dataset.columns.values)
            print(dataset)
            if nCol < 3:
                raise LessThanThree

            # non numeric value
            for i in dataset.columns[2:]:
                if dataset.dtypes[i] not in ['int64', 'int32', 'int16', 'float64']:
                    raise NonNumericValue

            # equal number
            no_of_cols = dataset.shape[1]-1
            weight = [int(i) for i in sys.argv[2].split(',')]
            impact = sys.argv[3].split(',')

            for i in impact:
                if not (i == '+' or i == '-'):
                    raise ErrorImpact

            # Checking number of column,weights and impacts is same or not
            if no_of_cols != len(weight) or no_of_cols != len(impact):
                raise UnmatchingNumber

            if (".csv" != (os.path.splitext(sys.argv[4]))[1]):
                raise IncorrectFormatFile
            if os.path.isfile(sys.argv[4]):
                os.remove(sys.argv[4])
            topsis_pipy(temp_dataset, dataset, nCol, weight, impact)

    except IncorrectArguments:
        logging.error('Kindly enter correct number of arguments')

    except FileNotFoundError:
        logging.error("The file is not found")

    except IncorrectFormatFile:
        logging.error("Kindly enter a csv file for the suitable argument")

    except LessThanThree:
        logging.error('The csv file inputted must have at least 3 columns')

    except NonNumericValue:
        logging.error("the file is having a non numeric value, kindly recheck")

    except ValueError:
        logging.error("The weights are not inputted correctly")

    except ErrorImpact:
        logging.error('The impact has any other value than + and -')

    except UnmatchingNumber:
        logging.error("the no of weights, impacts and no of columns are not equal")

def Normalize(temp_dataset, nCol, weights):
    for i in range(1, nCol):
        temp = 0
        for j in range(len(temp_dataset)):
            temp = temp + temp_dataset.iloc[j, i]**2
        temp = temp**0.5
        for j in range(len(temp_dataset)):
            temp_dataset.iat[j, i] = (
                temp_dataset.iloc[j, i] / temp)*weights[i-1]
    return temp_dataset


def Calc_Values(temp_dataset, nCol, impact):

    p_sln = (temp_dataset.max().values)[1:]
    n_sln = (temp_dataset.min().values)[1:]
    for i in range(1, nCol):
        if impact[i-1] == '-':
            p_sln[i-1], n_sln[i-1] = n_sln[i-1], p_sln[i-1]
    return p_sln, n_sln


def topsis_pipy(temp_dataset, dataset, nCol, weights, impact):
    temp_dataset = Normalize(temp_dataset, nCol, weights)
    p_sln, n_sln = Calc_Values(temp_dataset, nCol, impact)
    score = []
    for i in range(len(temp_dataset)):
        temp_p, temp_n = 0, 0
        for j in range(1, nCol):
            temp_p = temp_p + (p_sln[j-1] - temp_dataset.iloc[i, j])**2
            temp_n = temp_n + (n_sln[j-1] - temp_dataset.iloc[i, j])**2
        temp_p, temp_n = temp_p**0.5, temp_n**0.5
        score.append(temp_n/(temp_p + temp_n))
    dataset['Topsis Score'] = score
    dataset['Rank'] = (dataset['Topsis Score'].rank(
        method='max', ascending=False))
    dataset = dataset.astype({"Rank": int})
    dataset.to_csv(sys.argv[4], index=False)


if __name__ == "__main__":
    main()


