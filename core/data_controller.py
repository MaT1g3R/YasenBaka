import sqlite3


class DataController:
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def get_shame(self, server_id: int, user_id: int):
        """
        Get the user's Wows player id from server_id and user_id
        :param server_id: the discord server id
        :param user_id: the dicord user id
        :return: wows player id and region if found, else none
        """
        sql = '''SELECT region, id FROM shame_list WHERE server=? AND user=?'''
        self.cursor.execute(sql, (server_id, user_id))
        row = self.cursor.fetchone()
        return row if row is not None else (None, None)

    def write_shame(self, server_id: int, user_id: int,
                    region: str, player_id: int):
        """
        Write user's data into shamelist
        :param server_id: the server id
        :param user_id: the user id
        :param region: the region of the player
        :param player_id: the player's wows id
        :return: True if it's a new entry, else false
        """
        sql_exist = '''SELECT EXISTS(SELECT 1 FROM shame_list WHERE server=? AND user=?LIMIT 1)'''
        self.cursor.execute(sql_exist, (server_id, user_id))
        new_entry = self.cursor.fetchone() == (0,)
        sql_new = '''INSERT INTO shame_list VALUES (?, ?, ?, ?)'''
        sql_edit = '''UPDATE shame_list SET region=?, id=? WHERE server=? AND user=?'''
        if new_entry:
            self.cursor.execute(sql_new, (server_id, user_id, region, player_id))
        else:
            self.cursor.execute(sql_edit, (region, player_id, server_id, user_id))
        self.connection.commit()
        return new_entry

    def get_prefix(self, server_id: int):
        """
        Get server prefix
        :param server_id: the server id
        :return: the server prefix 
        """
        sql = '''SELECT prefix FROM prefix WHERE id=?'''
        res = self.cursor.execute(sql, [server_id]).fetchone()
        return res[0] if res is not None else None

    def set_prefix(self, server_id: int, prefix: str):
        """
        Set the prefix of a server
        :param server_id: the server id
        :param prefix: the prefix 
        """
        sql = '''REPLACE INTO prefix VALUES(?, ?)'''
        self.cursor.execute(sql, (server_id, prefix))
        self.connection.commit()

    def remove_shame(self, server_id: int, user_id: int):
        """
        Remove a user from shame list
        :param server_id: the server id
        :param user_id: the user id
        """
        sql = '''DELETE FROM shame_list WHERE server=? AND user=?'''
        self.cursor.execute(sql, (server_id, user_id))
        self.connection.commit()

    def get_shame_list(self, server_id):
        sql = '''SELECT user FROM shame_list WHERE server=?'''
        self.cursor.execute(sql, [server_id])
        return [i[0] for i in self.cursor.fetchall()]
