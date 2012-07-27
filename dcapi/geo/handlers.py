from piston.handler import BaseHandler
from piston.utils import rc
from django.db import connection


class ZipcodeBoundingBoxHandler(BaseHandler):

	stmt = """
		select ST_YMin(geom), ST_XMin(geom), ST_YMax(geom), ST_XMax(geom)
		from geo_zipcodes
		where
			zcta5ce10 = %s
	"""

	def read(self, request, zipcode):
		c = connection.cursor()
		c.execute(self.stmt, [zipcode])
		return c.fetchone()
