import asyncio
import os

import httpx

from config.settings import BASE_DIR

upload_url = "http://127.0.0.1:8000/products/media"
multi_upload_url = "http://127.0.0.1:8000/products/media"


# -------------------------
# --- 1 --- one file upload
# -------------------------
def one_file_upload():
    file_path = '999.jpg'

    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = httpx.post(upload_url, files=files)


# --------------------------
# --- 2 ---- two file upload
# --------------------------
async def multi_file_upload():
    file_paths = ['999.jpg', '123.jpg']
    files = [("xx", open(file_path, "rb")) for file_path in file_paths]

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(multi_upload_url, files=files)
    finally:
        for field, file_obj in files:
            file_obj.close()

    return response


# ----------------------------------------------------
# --- 3 --- read from demo and upload them to products
# ----------------------------------------------------
async def demo_multi_file_upload():
    # --- read from demo
    simple_dir = f'{BASE_DIR}/media/demo/products/simple/'
    file_paths = []
    payload = {
        'product_id': 1
    }
    for dir_number in range(2):
        directory_path = f'{simple_dir}{dir_number}'

        if os.path.isdir(directory_path):
            for filename in os.listdir(directory_path):
                if filename.endswith(".jpg"):
                    file_paths.append(os.path.join(directory_path, filename))

    # --- open files
    files = [("x_files", open(file_path, "rb")) for file_path in file_paths]

    # --- upload them
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                multi_upload_url,
                files=files,
                data=payload
            )
    finally:
        for field, file_obj in files:
            file_obj.close()

    return response


# ------------
# --- run ----
# ------------
if __name__ == "__main__":
    response = asyncio.run(demo_multi_file_upload())
    print(response.text)
    # one_file_upload()
    # multi_file_upload()
    # response = asyncio.run(multi_file_upload())
