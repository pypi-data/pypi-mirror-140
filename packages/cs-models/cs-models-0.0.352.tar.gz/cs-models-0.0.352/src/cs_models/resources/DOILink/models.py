from sqlalchemy import (
    Column,
    Integer,
    String,
)

from ...database import Base


class DOILinkModel(Base):
    __tablename__ = "doi_links"

    id = Column(Integer, primary_key=True)
    link = Column(
        String(191),
        nullable=False,
        index=True,
    )
    doi = Column(String(191), nullable=False)
