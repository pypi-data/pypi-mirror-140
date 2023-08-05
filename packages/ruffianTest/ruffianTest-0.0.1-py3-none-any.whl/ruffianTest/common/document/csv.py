import csv


class OperationCSV:
    def __init__(self, path):
        self.path = path

    def get_value(self, row_num, col_num):
        """

        :param row_num:
        :param col_num:
        :return: csv_value
        """
        with open(self.path, 'r') as file:
            reader = csv.reader(file)
            rows = [row for row in reader]
            return rows[row_num][col_num]
        """
            s = OperationCSV('test.csv')
            print(s.get_value(0, 1))
        """

    def write_value(self, values, headers=None):
        """

        :param values:
        :param headers:
        :return:
        """
        if headers is None:
            with open(self.path, 'w', newline='') as file:
                f_write = csv.writer(file)
                f_write.writerows(values)
        elif headers is not None:
            with open(self.path, 'w', newline='') as file:
                f_write = csv.writer(file)
                f_write.writerow(headers)
                f_write.writerows(values)
        """
            s = OperationCSV('{path}.csv')
            s.write_value([('1', '18', '测试'), ('2', '20', '没bug')], {'id', 'age', 'name'})
        """

