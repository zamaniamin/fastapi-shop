# from fastapi import APIRouter, status
#
# # create the path operations for a module using APIRouter,
# # You can think of APIRouter as a "mini FastAPI" class.
# router = APIRouter(
#     prefix="/attributes",
#     tags=["Attribute"],
# )
#
#
# @router.post(
#     "/",
#     # summary="Create a new attribute",
#     # description="Create a new attribute.",
#     # response_description="The created attribute",
#     # response_model=AttributeOut,
#     # status_code=status.HTTP_201_CREATED,
# )
# async def create_attribute():
#     return "hi"
