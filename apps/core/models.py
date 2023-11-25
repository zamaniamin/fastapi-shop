from sqlalchemy import Column, Integer, String


class FastAPIContentType:
    __tablename__ = "fastapi_content_type"

    id = Column(Integer, primary_key=True)
    app_name = Column(String)
    model = Column(String)
