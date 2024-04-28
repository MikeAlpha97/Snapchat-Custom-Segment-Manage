import psycopg2
import setting.config as con

cnxn = psycopg2.connect(
        host=con.host,
        port=con.port,
        database=con.database,
        user=con.user,
        password=con.password)
        
cursor = cnxn.cursor()

# cntrId = con.centrId