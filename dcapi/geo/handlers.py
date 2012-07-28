from piston.handler import BaseHandler
from django.db import connection
from django.http import HttpResponseNotFound

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

		if c.rowcount == 0:
			return HttpResponseNotFound("Zipcode %s not found." % zipcode)

		return c.fetchone()
