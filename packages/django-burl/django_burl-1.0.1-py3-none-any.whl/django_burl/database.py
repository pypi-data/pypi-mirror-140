import logging
from django.conf import settings
from django.db import connection, connections
from django.db.models.query import QuerySet

logger = logging.getLogger(__name__)


class RoughCountQuerySet(QuerySet):
    def rough_count(self):
        if connection.vendor == "postgresql":
            cursor = connections[self.db].cursor()
            try:
                cursor.execute(
                    f"SELECT reltuples FROM pg_class WHERE relname='{self.query.model._meta.db_table}';"
                )
                rough = int(cursor.fetchone()[0])
                if rough > settings.ROUGH_COUNT_MIN:
                    return rough
                return super().count()
            except Exception as ex:
                logger.error(f"error getting rough count from postgres: {ex}")
                return super().count()
        return super().count()
