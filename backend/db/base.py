# Import all the models, so that Base has them before being
# imported by Alembic
from backend.app.db.base_class import Base  # noqa

