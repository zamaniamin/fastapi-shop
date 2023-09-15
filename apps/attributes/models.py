from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from config.database import FastModel


class Attribute(FastModel):
    __tablename__ = "attributes"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)

    items = relationship("AttributeItem", back_populates="attribute", cascade="all, delete-orphan")


class AttributeItem(FastModel):
    __tablename__ = "attribute_items"

    id = Column(Integer, primary_key=True)
    attribute_id = Column(Integer, ForeignKey("attributes.id"))
    item = Column(String(255), nullable=False)

    __table_args__ = (UniqueConstraint('attribute_id', 'item'),)
    attribute = relationship("Attribute", back_populates="items")
