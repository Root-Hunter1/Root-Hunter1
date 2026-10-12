Running Server:
pip install uvloop asyncpg
python server.py --procs 4 --workers 2 --db-url "postgresql://user:pass@localhost/db"

library install package:
pkg install python postgresql libpq clang make
pip install asyncpg

pkg install postgresql
mkdir -p $PREFIX/var/lib/postgresql
initdb $PREFIX/var/lib/postgresql
pg_ctl -D $PREFIX/var/lib/postgresql start
createdb mydb

PostgreSQL server code:
pkg install postgresql
mkdir -p $PREFIX/var/lib/postgresql
initdb $PREFIX/var/lib/postgresql
pg_ctl -D $PREFIX/var/lib/postgresql start
createdb mydb

database Creted:
createdb u0_a179

start: udp server.py

Method 2: Use the previously created mydb:
python udp server.py --db-url "postgresql://localhost/mydb"

If any further errors occur

'role does not exist' or 'connection refused': The PostgreSQL server is down. Start it:
  pg_ctl -D $PREFIX/var/lib/postgresql start

যাচাই করুন ডেটা DB তে ঢুকেছে কিনা:
psql mydb -c "SELECT count(*) FROM packets;"

সঠিকভাবে হারানো ডেটা যাচাই করুন:
psql mydb -c "TRUNCATE packets;"

psql mydb -c "SELECT count(*) FROM packets;"

database.py spped test: 
class Database:
    def __init__(self, dsn=None, max_size=4):
        pass

    async def connect(self):
        pass

    async def insert_many(self, rows):
        pass

    async def close(self):
        pass
