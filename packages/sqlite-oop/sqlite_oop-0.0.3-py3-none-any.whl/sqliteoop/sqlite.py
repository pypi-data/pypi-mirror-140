import sqlite3


class sqlite:
    SQLITE_DATABASE_NAME = "./database.db"
    SPACE_CHARACTER = " "
    SINGLE_QUOTES_CHARACTER = "\'"
    SEMICOLON_CHARACTER = ";"
    EQUAL_SIGN_CHARACTER = "="
    LINE_BREAK_CHARACTER = "\n"
    DIRECTORY_SEPARATOR = "/"

    __table_name = ""
    __base_where_clause_string = ""
    __base_where_limit_clause_string = ""
    __base_where_orderby_clause_string = ""
    """
    GROUP BY 子句放在 WHERE 子句之后，放在 ORDER BY 子句之前
    """
    __base_where_groupby_clause_string = ""
    """
    与 SELECT 语句一起使用，来消除所有重复的记录，并只获取唯一一次记录
    """
    __base_where_distinct_clause_string = ""
    __base_where_join_clause_string = ""
    __operators = [
        "==", "=", "!=", "<>", ">", "<", ">=", "<=", "!<", "!>",
        "AND", "BETWEEN", "EXISTS", "IN", "NOT IN", "LIKE",
        "GLOB", "NOT", "OR", "IS NULL", "IS", "IS NOT", "||", "UNIQUE"
    ]

    def __init__(self, db_name=None):
        if db_name is None:
            db_name = self.SQLITE_DATABASE_NAME

        self.db = sqlite3.connect(db_name)
        self._cursor = None

    def table(self, table_name):
        """
        设置连接table
        :param table_name:
        :return:
        """
        self.__table_name = table_name
        self._cursor = self.db.cursor()
        return self

    def get_table_name(self):
        return self.__table_name

    def __is_tablename(self):
        if len(self.__table_name) == 0:
            return "No query form is specified 亲，叫个表吧，求你了！"
        else:
            return True

    def query(self, sql):
        execute = self.db.execute(sql)
        columns_tuple = execute.description
        columns_list = [field_tuple[0] for field_tuple in columns_tuple]
        query_result = execute.fetchall()
        columns_len = len(columns_list)
        result = []
        for value in query_result:
            v_n = 0
            item = {}
            while v_n < columns_len:
                item[columns_list[v_n]] = value[v_n]
                v_n += 1
            result.append(item)

        return result

    def select(self, columns="*"):
        if self.__is_tablename() != True:
            return False

        selected = "SELECT"
        selected += self.SPACE_CHARACTER
        selected += self.__base_where_distinct_clause_string
        selected += self.SPACE_CHARACTER
        selected += columns
        selected += self.SPACE_CHARACTER
        selected += "FROM"
        selected += self.SPACE_CHARACTER
        selected += self.__table_name
        selected += self.SPACE_CHARACTER
        selected += self.__base_where_clause_string
        selected += self.__base_where_groupby_clause_string
        selected += self.__base_where_orderby_clause_string
        selected += self.__base_where_limit_clause_string
        selected += self.__base_where_join_clause_string
        selected += "; "
        result = self.query(selected)
        return result

    def find(self, columns="*"):
        data = self.limit(1).select(columns)
        if data:
            return data[0]
        else:
            return None

    def where(self, column, op, value=None, _boolean=" AND"):
        """
        查询条件
        :param column:
        :param op:
        :param value:
        :param _boolean:
        :return:
        """

        if value is None:
            if self.__operators.count(op) == 0:
                value = op
                op = "="
            else:
                errorString = "query column requires a valid value 你找什么啊亲！"
                raise Exception(errorString)

        op = str(op)
        value = str(value)

        if len(self.__base_where_clause_string) > 0:
            self.__base_where_clause_string += _boolean
            self.__base_where_clause_string += self.SPACE_CHARACTER

        else:
            self.__base_where_clause_string += "WHERE"
            self.__base_where_clause_string += self.SPACE_CHARACTER
        self.__base_where_clause_string += column
        self.__base_where_clause_string += self.SPACE_CHARACTER
        self.__base_where_clause_string += op
        self.__base_where_clause_string += self.SPACE_CHARACTER
        self.__base_where_clause_string += self.SINGLE_QUOTES_CHARACTER
        self.__base_where_clause_string += str(value)
        self.__base_where_clause_string += self.SINGLE_QUOTES_CHARACTER
        self.__base_where_clause_string += self.SPACE_CHARACTER
        return self

    def limit(self, limit):
        """
        查询数量
        :param limit:
        :return:
        """
        self.__base_where_limit_clause_string = "LIMIT"
        self.__base_where_limit_clause_string += self.SPACE_CHARACTER
        self.__base_where_limit_clause_string += str(limit)
        self.__base_where_limit_clause_string += self.SPACE_CHARACTER
        return self

    def orderBy(self, column, order):
        self.__base_where_orderby_clause_string = "ORDER BY"
        self.__base_where_orderby_clause_string += self.SPACE_CHARACTER
        self.__base_where_orderby_clause_string += column
        self.__base_where_orderby_clause_string += self.SPACE_CHARACTER
        self.__base_where_orderby_clause_string += order
        self.__base_where_orderby_clause_string += self.SPACE_CHARACTER
        return self

    def groupBy(self, column):
        self.__base_where_groupby_clause_string = "GROUP BY"
        self.__base_where_groupby_clause_string += self.SPACE_CHARACTER
        self.__base_where_groupby_clause_string += column
        self.__base_where_groupby_clause_string += self.SPACE_CHARACTER
        return self

    def distinct(self):
        self.__base_where_distinct_clause_string = "DISTINCT"
        self.__base_where_distinct_clause_string += self.SPACE_CHARACTER
        return self

    def join(self, table, first, op, second, joinType):
        if second == None:
            second = op
            op = "="

        self.__base_where_join_clause_string += self.SPACE_CHARACTER
        self.__base_where_join_clause_string += joinType
        self.__base_where_join_clause_string += self.SPACE_CHARACTER
        self.__base_where_join_clause_string += "JOIN"
        self.__base_where_join_clause_string += self.SPACE_CHARACTER
        self.__base_where_join_clause_string += table
        self.__base_where_join_clause_string += self.SPACE_CHARACTER
        self.__base_where_join_clause_string += "ON"
        self.__base_where_join_clause_string += self.SPACE_CHARACTER
        self.__base_where_join_clause_string += first
        self.__base_where_join_clause_string += self.SPACE_CHARACTER
        self.__base_where_join_clause_string += op
        self.__base_where_join_clause_string += self.SPACE_CHARACTER
        self.__base_where_join_clause_string += second
        self.__base_where_join_clause_string += self.SPACE_CHARACTER
        return self

    def count(self):
        data = self.select("count(*)")
        return data[0]["count(*)"]

    def insert(self, columns: dict or list):
        """
        批量插入数据
        :param columns:
        :return:
        """
        # print(type(type(columns)))
        if not isinstance(columns, (list, dict)):
            raise Exception("columns type must be (list or dict )")
        if isinstance(columns, dict):
            execute = self.__instert_o(columns)
            self.db.commit()
            last_id = execute.lastrowid
            return self.where("id", str(last_id)).find()
        else:
            for item in columns:
                execute = self.__instert_o(item)
            self.db.commit()
            if self.db.total_changes > 0:
                return True
            else:
                return False

    def create(self, data: dict):
        """
        创建单条数据
        :param data:
        :return:
        """
        if not isinstance(data, dict):
            raise Exception("columns type must be dict")
        else:
            execute = self.__instert_o(data)
            self.db.commit()
            last_id = execute.lastrowid
            return self.where("id", str(last_id)).find()

    def __instert_o(self, columns):
        _insert_string = self.__set_insert_string(columns)
        columns_string = _insert_string[0][:-1]
        values_string = _insert_string[1][:-1]
        # print(columns_string, values_string)
        insert = "INSERT INTO "
        insert += self.__table_name
        insert += " ( "
        insert += columns_string
        insert += " ) VALUES ( "
        insert += str(values_string)
        insert += " ); "
        return self.db.execute(insert)

    def __set_insert_string(self, columns):
        columns_string = ""
        values_string = ""
        for column_key, column_value in columns.items():
            columns_string += column_key
            columns_string += ","
            values_string += self.SINGLE_QUOTES_CHARACTER
            values_string += str(column_value)
            values_string += self.SINGLE_QUOTES_CHARACTER
            values_string += ","

        # columns_string = columns_string[:-1]
        # values_string = values_string[:-1]
        return columns_string, values_string

    def update(self, datas):
        # if not self.is_table():
        #     return False
        if datas is None:
            return False
        update_string = ""
        for column_key, column_value in datas.items():
            update_string += column_key
            update_string += self.SPACE_CHARACTER
            update_string += self.EQUAL_SIGN_CHARACTER
            update_string += self.SPACE_CHARACTER
            update_string += self.SINGLE_QUOTES_CHARACTER
            update_string += str(column_value)
            update_string += self.SINGLE_QUOTES_CHARACTER
            update_string += ","

        update_string = update_string[:-1]
        update = "UPDATE "
        update += self.__table_name
        update += self.SPACE_CHARACTER
        update += "SET"
        update += self.SPACE_CHARACTER
        update += update_string
        update += self.SPACE_CHARACTER
        update += self.__base_where_clause_string
        self.db.execute(update)
        self.db.commit()
        # print(self.db)
        return self.find()

    def delete(self):
        delete_data = "DELETE FROM"
        delete_data += self.SPACE_CHARACTER
        delete_data += self.__table_name
        delete_data += self.SPACE_CHARACTER
        delete_data += self.__base_where_clause_string
        delete_data += self.SEMICOLON_CHARACTER
        self.db.execute(delete_data)
        self.db.commit()

        if self.db.total_changes > 0:
            return True
        else:
            return False

    def create_table(self, create_columns: dict):
        """
        创建数据表
        :return:
        """
        # 判断表是否存在
        if self.is_table():
            return self.where("name", self.__table_name).table("sqlite_master").select()
        if create_columns is None:
            return "map is empty 这啥也没有啊，搞我呢？"
        columns_string = ""
        for column_key, column_value in create_columns.items():
            # print(column_key)
            columns_string += column_key
            columns_string += self.SPACE_CHARACTER
            columns_string += column_value
            columns_string += ","

        # 移除最后一个，
        columns_string = columns_string[:-1]
        created = "CREATE TABLE "
        created += self.__table_name
        created += " ( "
        created += columns_string
        created += " ); "
        try:
            self.db.execute(created)
            self.db.commit()
            return self.where("name", self.__table_name).table("sqlite_master").select()
        except ValueError:
            raise Exception("create table fail!")

    def delete_table(self, table_name=""):
        if "" == table_name:
            table_name = self.__table_name
        delete_table = "DROP TABLE"
        delete_table += self.SPACE_CHARACTER
        delete_table += table_name
        self.db.execute(delete_table)
        self.db.commit()
        if self.db.total_changes > 0:
            return True
        else:
            return False

    def is_table(self):
        """
        检查表是否存在
        :return:
        """
        table_name = self.__table_name
        count = self.where("name", self.__table_name).table("sqlite_master").count()
        self.__table_name = table_name
        if count > 0:
            return True
        else:
            return False

    def close(self):
        self.db.close()

    def __del__(self):
        self.close()
