import json
import os
import pymysql


class Connection:
    def __init__(self, user, pw, host, db_name, db_connection_name):
        # gcloud mysql db settings:
        self.gcloud_mysql_db_user = user
        self.gcloud_mysql_db_password = pw
        self.gcloud_mysql_db_host = host
        self.gcloud_mysql_db_name = db_name
        self.gcloud_mysql_db_connection_name = db_connection_name
        self.gcloud_mysql_db_unix_socket = '/cloudsql/{}'.format(self.gcloud_mysql_db_connection_name)

    def sql(self, sql, args=None, download_file=False, return_last_row_id=False):
        fetch = []
        description = []
        last_row_id = None
        if os.environ.get('RUNNING_IN_GCLOUD') == 'True':  # wenn auf gcloud:
            conn = pymysql.connect(user=self.gcloud_mysql_db_user,
                                   password=self.gcloud_mysql_db_password,
                                   unix_socket=self.gcloud_mysql_db_unix_socket,
                                   db=self.gcloud_mysql_db_name)
        else:  # remote Verbindung zu gcloud db:
            conn = pymysql.connect(user=self.gcloud_mysql_db_user,
                                   password=self.gcloud_mysql_db_password,
                                   host=self.gcloud_mysql_db_host,
                                   db=self.gcloud_mysql_db_name)
            with conn.cursor() as cursor:
                if args is not None:
                    cursor.execute(sql, args)
                else:
                    cursor.execute(sql)

                fetch = cursor.fetchall()
                description = cursor.description
                if return_last_row_id:
                    last_row_id = cursor.lastrowid
            conn.commit()
            conn.close()
            if download_file:
                return fetch
        result = []
        column_names = []
        if description is None:
            if return_last_row_id:
                return result, last_row_id
            return result
        for name in description:
            column_names.append(name[0])
        for element in fetch:
            json_element = {}
            for i in range(len(element)):
                if type(element[i]) == bytes:
                    if element[i] == bytes(True):
                        json_element.update({column_names[i]: True})
                    else:
                        json_element.update({column_names[i]: False})
                else:
                    json_element.update({column_names[i]: element[i]})
            result.append(json_element)
        if return_last_row_id:
            return result, last_row_id
        return result

    def insert(self, table_name, d):
        column_names = [column_name["Field"] for column_name in self.sql("SHOW COLUMNS FROM %s", (table_name, ))]
        columns = ""
        args = []
        values_s = ""
        for param in d:
            if param in column_names:
                if columns == "":
                    columns = columns + param
                    values_s = values_s + "%s"
                else:
                    columns = columns + ", " + param
                    values_s = values_s + ", %s"
                args.append(d[param])
        sql = "INSERT INTO " + table_name + " (" + columns + ") VALUES (" + values_s + ");"
        last_row_id = self.sql(sql, tuple(args), return_last_row_id=True)[1]
        return last_row_id

    def update(self, table_name, d):
        column_names = [column_name["Field"] for column_name in self.sql("SHOW COLUMNS FROM %s", (table_name, ))]
        d["last_modified"] = str(d.datetime.now())
        sets = ""
        args = []
        for column_name in d:
            if column_name in column_names and column_name != "id":
                if sets == "":
                    sets = sets + column_name + " = %s"
                else:
                    sets = sets + ", " + column_name + " = %s"
                args.append(d[column_name])
        sql = "UPDATE " + table_name + " SET " + sets + " where id = " + str(d["id"])
        self.sql(sql, args=tuple(args))






































