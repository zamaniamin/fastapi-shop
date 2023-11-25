from sqlalchemy import Column, Integer, String


class FastAPIContentType:
    """
    Model to handle roles and permissions on the admin panel.
    """
    __tablename__ = "fastapi_content_type"

    id = Column(Integer, primary_key=True)
    app_name = Column(String, index=True)
    model = Column(String)
