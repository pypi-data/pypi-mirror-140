#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv as csv_model
import pandas


def csv_read_column(csv_file_path, column_num, encoding="UTF-8"):
    with open(csv_file_path, "rt", encoding="%s" % encoding) as csvfile:
        reader = csv_model.reader(csvfile)
        column = [row[column_num - 1] for row in reader]
        return column

# def csv_write_new(column_data, path, file_name, column_name=None):
#     file = pandas.DataFrame(columns=column_name, data=column_data)
#     f = open("%s//%s.csv" % (path, file_name), 'w', encoding="gbk")
#     f.close()
#     file.to_csv("%s//%s.csv" % (path, file_name))

# def csv_write_new(file_path, file_name, mode="column", encoding='UTF-8'):
#     f = open("%s//%s.csv" % (file_path, file_name), 'w', encoding="%s" % encoding)
#     csv_writer = csv.writer(f)
#     if mode == "column":
#         csv_writer.write
#
#     # 4. 写入csv文件内容
#     csv_writer.writerow(["l", '18', '男'])
#     csv_writer.writerow(["c", '20', '男'])
#     csv_writer.writerow(["w", '22', '女'])
