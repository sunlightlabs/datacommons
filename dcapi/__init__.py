import psycopg2.extras
import uuid

psycopg2.extras.register_uuid()
uuid.UUID.__str__ = lambda x: x.hex

