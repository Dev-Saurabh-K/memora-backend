import os
from dotenv import load_dotenv
from imagekitio import ImageKit
from pathlib import Path

load_dotenv()

imagekit = ImageKit(
    private_key=os.environ.get("IMAGEKIT_PRIVATE_KEY")
)

# Store URL endpoint for reuse
URL_ENDPOINT = os.environ.get("IMAGEKIT_URL_ENDPOINT")

# response = imagekit.files.upload(
#     file=Path("image.png"),
#     file_name="image.png",
#     folder="/images",
#     tags=["product", "featured"]
# )

# print(f"File id: {response.file_id}")
# print(f"File URL: {response.url}")
# image_url = f"{URL_ENDPOINT}{response.file_path}"
# print(image_url)

# # Upload from bytes (web forms)
# image_data = request.files['image'].read()
# response = imagekit.files.upload(
#     file=image_data,
#     file_name="upload.jpg"
# )