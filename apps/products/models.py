from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint, Text, DateTime, func, Numeric
from sqlalchemy.orm import relationship

from config.database import FastModel


class Product(FastModel):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    product_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Active: The product is ready to sell and is available to customers on the online store, sales channels, and apps.
    # Archived: The product is no longer being sold and isn't available to customers on sales channels and apps.
    # Draft: The product isn't ready to sell and is unavailable to customers on sales channels and apps.

    # status_enum = Enum('active', 'archived', 'draft', name='status_enum')
    status = Column(String, default='draft')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)

    options = relationship("ProductOption", back_populates="product", cascade="all, delete-orphan")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    media = relationship("ProductMedia", back_populates="product", cascade="all, delete-orphan")

    # TODO add user_id to track which user added this product


class ProductOption(FastModel):
    __tablename__ = "product_options"

    id = Column(Integer, primary_key=True)

    # The foreign key referencing the parent product.
    product_id = Column(Integer, ForeignKey("products.id"))
    option_name = Column(String(255), nullable=False)

    __table_args__ = (UniqueConstraint('product_id', 'option_name'),)
    product = relationship("Product", back_populates="options")
    option_items = relationship("ProductOptionItem", back_populates="product_option", cascade="all, delete-orphan")


class ProductOptionItem(FastModel):
    __tablename__ = "product_option_items"

    id = Column(Integer, primary_key=True)
    option_id = Column(Integer, ForeignKey("product_options.id"))
    item_name = Column(String(255), nullable=False)

    __table_args__ = (UniqueConstraint('option_id', 'item_name'),)
    product_option = relationship("ProductOption", back_populates="option_items")


class ProductVariant(FastModel):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    price = Column(Numeric(12, 2), default=0)
    stock = Column(Integer, default=0)

    option1 = Column(Integer, ForeignKey("product_option_items.id"), nullable=True)
    option2 = Column(Integer, ForeignKey("product_option_items.id"), nullable=True)
    option3 = Column(Integer, ForeignKey("product_option_items.id"), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # option1 = relationship("ProductOptionItem", foreign_keys=[option1_id])
    # option2 = relationship("ProductOptionItem", foreign_keys=[option2_id])
    # option3 = relationship("ProductOptionItem", foreign_keys=[option3_id])

    product = relationship("Product", back_populates="variants")


class ProductMedia(FastModel):
    __tablename__ = "product_media"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))

    # TODO attach image to product variants (optional)
    # variant_ids = Column(ARRAY(Integer))

    # TODO if set the position to `1` it means this is the main image
    # position = Column(Integer)
    alt = Column(String, nullable=True)
    src = Column(String)
    type = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    product = relationship("Product", back_populates="media")
