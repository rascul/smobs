smobs
=====

wotmud smob sb thing

see it in action at http://smobdb.herokuapp.com

something like this:

```
apt-get install postgresql python-flask python-psycopg2 
su - postgres
createuser wotmuddb
createdb -O wotmuddb wotmuddb
exit
git clone https://github.com/rascul/smobs
cd smobs
psql -f schema.sql wotmuddb
sed 's/DATABASE/#DATABASE/' config.py.dist > config.py
echo "DATABASE = 'dbname=wotmuddb'" >> config.py
python db.py
```

