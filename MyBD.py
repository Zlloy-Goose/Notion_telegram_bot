# from mysql.connector import connect, Error
from texts import Names
from sqlite3 import connect, Error
import sqlite3
from datetime import datetime


def log(e):
     with open("log", "a",encoding='utf-8') as log:
        log.write(datetime.now().strftime("%m-%d %H:%M") + " -- " + str(e) + " \n")

class MyDataBase:
    
    def dict_to_str(self, d):
        result = ''
        for _ in d:
            result += " | ".join(_) + "\n"
        return result[:-1]

    def check_BD(self):
        """Проверка и если что то создание таблиц"""
        cursor = self.connector.cursor()
        for table, columns in Names.TABLES.items():
            try:
                cursor.execute(f"select * from {table}")
            except:
                log(f"table {table} not create 20")
                try:
                    execute = f" CREATE TABLE {table}("
                    for name, type in columns.items():
                        execute += name + ' ' + type + ','
                    execute = execute[:-1] + ')'
                    cursor.execute(execute)
                    self.connector.commit()
                except Error as e:
                    log(str(e) + ' 31')
        
    def __init__(self, name_db):
        self.connector = sqlite3.connect(name_db)
        self.check_BD()
    
    def show_tables(self) -> dict:
        """Просмотр какие бд есть в базе возвращает некрасивый список"""
        try:
            cursor = self.connector.cursor() 
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            return [table for table in cursor]
        except Error as e:
            print(e)

    def info(self, table_name):
        cursor = self.connector.cursor()
        cursor.execute(f"select * from {table_name} limit 0")
        return cursor.description

    def delete_table(self, name_db): 
        self.connector.cursor().execute(f"drop table {name_db}")
        self.connector.commit() 
        print(self.show_tables())

    def show_items(self, name_table, item = '') -> str:  
        """получает Имя таблицы и что искать если искатиь нечего то показывает все"""
        if item == '':
            try:
                result = self.dict_to_str([item for item in self.connector.cursor().execute(f'SELECT * FROM {name_table}')])
                return "Note found!" if result=="" else result
                # if result == "":
                #     return "Note found!!"
                # else:
            except Error as e:
                log(str(e) + f"  -- Error get all item form {name_table}")
                return str(e) + f"  -- Error get all item form {name_table}"
        else:
            try:
                items = []
                cursor = self.connector.cursor()
                for name_coln in Names.TABLES_MAIN_COLUMNS[name_table]:
                    cursor.execute(f'SELECT * FROM {name_table} WHERE {name_coln} LIKE "%{item}%";')
                    fetchall = cursor.fetchall()
                    if fetchall != []:
                        items.append(fetchall)
                try:
                    return self.dict_to_str(items[0])
                except:
                    return "Not found -> " + item
            except Error as e:
                return e
 
    def add_items(self, table_name, items) -> str:
        """Получает имя таблицы str, список что добавить каждый элемент в списке должен соответствовать столбцу
        Добавление в таблицу некоторых значений название таблицы и cроковые значения которые добавить в колонку
        Возвращает либо что не получилось ошибка либо create"""
        create_item = f"""INSERT INTO {table_name} ("""
        try:
            # column_name =self.get_name_columns(table_name) 
            column_name = [_ for _ in Names.TABLES[table_name].keys()]
            for name in column_name:
                create_item += name
                create_item += ', ' if not(name == column_name[-1]) else  ') VALUES ('
            if type(items) == str:
                items = items.split(' ')
            if len(items) == len(column_name): 
                for item in items:
                    create_item += "'" + item + "'"
                    create_item += ', ' if not(item == items[-1]) else ')'
            else:
                raise Error('Не правильные данные ввода') 
            try:
                cursor =  self.connector.cursor()
                cursor.execute(create_item)
                self.connector.commit()
            except Error as e:
                log(str(e) + " -- Add items execute")
                return str(e) + " -- Add items"
            return "Create"
        except Error as e:
            log(str(e) + " -- Add items")
            return str(e) + " -- Add items"

    def conf_delelete_item(self, table_name, item) -> str:
        """Получает имя таблицы + что найти в таблице по глвному столбцу и должен найти только 1 """
        try:
            return self.dict_to_str(self.connector.cursor().execute(f'select * from {table_name} where {Names.TABLES_MAIN_COLUMNS[table_name][0]} = "{item}"').fetchall())
        except Error as e:
            log(str(e)+"conf_delete_item")
            return str(e)+"conf_delete_item"

    def delete_item(self, table_name, item):
        try:
            self.connector.cursor().execute(f"DELETE FROM {table_name} WHERE {Names.TABLES_MAIN_COLUMNS[table_name][0]} = '{item}'")
            self.connector.commit()
            return "deleted"
        except Error as e:
            log(str(e)+"delete item")
            return str(e)+"delete item"

    def delete_all_items(self, name_table):
        try:
            self.connector.cursor().execute(f'DELETE FROM {name_table};')
            self.connector.commit()
            return "ALL deleted"
        except Error as e:
            return e

    

def main(): 
    new_db = MyDataBase("zlloy_edinorog")
    # print(new_db.conf_delelete_item(Names.PASSWORD_TABLE, 'Q'))
    # print(new_db.delete_item(Names.PASSWORD_TABLE, "q"))
    # print(new_db.show_items(Names.PASSWORD_TABLE))
    print(new_db.info(Names.PASSWORD_TABLE))
    # new_db.delete_table(Names.NOTION_TABLE)
    
    # print(new_db.add_items(Names.NAME_PASSWORD_TABLE, [datetime.now().strftime("%m-%d %H:%M") ,'q','2','3','4','5']))
    # print(new_db.add_items(Names.PASSWORD_TABLE, [datetime.now().strftime("%m-%d %H:%M") ,'w','2','3','4','5']))
    # print(new_db.show_items(Names.PASSWORD_TABLE))

    # print(new_db.show_items(Names.NAME_PASSWORD_TABLE, Names.NAME_PASSWORD_TABLE[1]))

    # Создание таблицы проверка на все таблицы которые должны быть некая фаршировка всего кода что бы выложить на сервак
    # if os.path.exists(Names.NAME_DATA_BASE):
    #     with sqlite3.connect(Names.NAME_DATA_BASE) as mydb:
    #         cursor = mydb.cursor()
    #         try:
    #             cursor.execute(f"select * from {Names.NAME_PASSWORD_TABLE}")
    #         except Error as e:
    #             cursor.execute(f"""
    #                            CREATE TABLE {Names.NAME_PASSWORD_TABLE}(
    #                            {Names.NAMES_PASS_COLUMNS[0]} date,
    #                            {Names.NAMES_PASS_COLUMNS[1]} text primary key,
    #                            {Names.NAMES_PASS_COLUMNS[2]} text,
    #                            {Names.NAMES_PASS_COLUMNS[3]} text,
    #                            {Names.NAMES_PASS_COLUMNS[4]} text,
    #                            {Names.NAMES_PASS_COLUMNS[5]} text
    #                            )""")
    #         print(cursor.execute(f"select * from {Names.NAME_PASSWORD_TABLE}"))

    # new_db = MyDataBase(hostt="localhost", 
    #                     username='PythonUser', 
    #                     password_user='Qwer45ty12', 
    #                     name_db="Notion")
    ##create table password(data date, site_name text primary key, login text, password text, add_name_site text, link_site text);
    ##CREATE TABLE `notion`.`notion5507918550` (
    #   `date_` DATE NULL,
    #   `tags` VARCHAR(45) NOT NULL,
    #   `notion` TEXT NULL,
    #   PRIMARY KEY (`tags`));


if __name__ == "__main__":
    main()


# переделать что бы сохраняло в файл который лежит в папке рядом или создается 