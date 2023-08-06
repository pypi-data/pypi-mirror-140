from sqlalchemy import create_engine


def insert_df(df, table_name, HOST, DB, USER_DB, PASSWORD_DB, replace=False):
    # Insert pandas dataframe in an MSSQL database.
    sqlengine = create_engine(f'mssql+pymssql://{USER_DB}:{PASSWORD_DB}@{HOST}/{DB}')
    db_connection = sqlengine.connect()

    if replace:
        df.to_sql(name=table_name, con=db_connection, if_exists='replace', index=False)
    else:
        df.to_sql(name=table_name, con=db_connection, if_exists='append', index=False)

    db_connection.close()
