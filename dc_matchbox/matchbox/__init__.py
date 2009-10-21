
import MySQLdb
from settings import DATABASE_HOST, DATABASE_USER, DATABASE_NAME


connection = MySQLdb.connect(host=DATABASE_HOST, user=DATABASE_USER, db=DATABASE_NAME)