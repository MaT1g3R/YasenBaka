def get_shame(cursor, server_id: int, user_id: int):
    """
    Get the user's Wows player id from server_id and user_id
    :param cursor: the database cursor
    :param server_id: the discord server id
    :param user_id: the dicord user id
    :return: wows player id and region if found, else none
    """
    sql = '''SELECT region, id FROM shame_list WHERE server=? AND user=?'''
    cursor.execute(sql, (server_id, user_id))
    row = cursor.fetchone()
    return row if row is not None else (None, None)


def write_shame(cursor, connection, server_id: int, user_id: int,
                region: str, player_id: int):
    """
    Write user's data into shamelist
    :param cursor: the database cursor
    :param connection: the database conn
    :param server_id: the server id
    :param user_id: the user id
    :param region: the region of the player
    :param player_id: the player's wows id
    :return: True if it's a new entry, else false
    """
    sql_exist = '''
SELECT EXISTS(SELECT 1 FROM shame_list WHERE server=? AND user=?LIMIT 1)'''
    cursor.execute(sql_exist, (server_id, user_id))
    new_entry = cursor.fetchone() == (0,)
    sql_new = '''INSERT INTO shame_list VALUES (?, ?, ?, ?)'''
    sql_edit = '''
UPDATE shame_list SET region=?, id=? WHERE server=? AND user=?'''
    if new_entry:
        cursor.execute(sql_new, (server_id, user_id, region, player_id))
    else:
        cursor.execute(sql_edit, (region, player_id, server_id, user_id))
    connection.commit()
    return new_entry


def get_prefix(cursor, server_id: int):
    """
    Get server prefix
    :param cursor: the database cursor
    :param server_id: the server id
    :return: the server prefix 
    """
    sql = '''SELECT prefix FROM prefix WHERE id=?'''
    res = cursor.execute(sql, [server_id]).fetchone()
    return res[0] if res is not None else None


def set_prefix(cursor, connection, server_id: int, prefix: str):
    """
    Set the prefix of a server
    :param cursor: the database cursor
    :param connection: the database conn
    :param server_id: the server id
    :param prefix: the prefix 
    """
    sql = '''REPLACE INTO prefix VALUES(?, ?)'''
    cursor.execute(sql, (server_id, prefix))
    connection.commit()


def remove_shame(cursor, connection, server_id: int, user_id: int):
    """
    Remove a user from shame list
    :param cursor: the database cursor
    :param connection: the database conn
    :param server_id: the server id
    :param user_id: the user id
    """
    sql = '''DELETE FROM shame_list WHERE server=? AND user=?'''
    cursor.execute(sql, (server_id, user_id))
    connection.commit()


def get_shame_list(cursor, server_id):
    """
    Get the shamelist of a server
    :param cursor: the database cursor
    :param server_id: the server id
    :return: a list of all user_id's in that server's shamelist
    """
    sql = '''SELECT user FROM shame_list WHERE server=?'''
    cursor.execute(sql, [server_id])
    return [i[0] for i in cursor.fetchall()]


def write_tag(cursor, connection, site, tag):
    """
    Write a tag entry into the database
    :param cursor: the database cursor
    :param connection: the database connection
    :param site: the site name
    :param tag: the tag entry
    """
    if tag_in_db(cursor, site, tag):
        return
    else:
        sql = '''INSERT INTO nsfw_tags(site, tag) VALUES (?, ?)'''
        cursor.execute(sql, (site, tag))
        connection.commit()


def tag_in_db(cursor, site, tag):
    """
    Returns if the tag is in the db or not
    :param cursor: the db cursor
    :param site: the site name
    :param tag: the tag name
    :return: True if the tag is in the db else false
    """
    sql = '''
SELECT EXISTS(SELECT 1 FROM nsfw_tags WHERE site=? AND tag=?LIMIT 1)'''
    cursor.execute(sql, (site, tag))
    return cursor.fetchone() == (1,)


def fuzzy_match_tag(cursor, site, tag):
    """
    Try to fuzzy match a tag with one in the db
    :param cursor: the db cursor
    :param site: the stie name
    :param tag: the tag name
    :return: a tag in the db if match success else None
    """
    sql = """
    SELECT tag FROM nsfw_tags 
    WHERE (tag LIKE '{0}%' OR tag LIKE '%{0}%' OR tag LIKE '%{0}') 
    AND site=?
    """.format(tag)
    res = cursor.execute(sql, [site]).fetchone()
    return res[0] if res is not None else None
