import requests, base64, io 
from pillow_heif import register_heif_opener 
from PIL import Image 

#cal such that pillow knows what HEIC is 
register_heif_opener() 

#function to convert image types to JPEG
def convert_to_jpeg(image_bytes: bytes) -> bytes:
    image: Image.Image = Image.open(io.BytesIO(image_bytes)) 

    rgb_image: Image.Image = image.convert("RGB") 

    buffer: io.BytesIO = io.BytesIO() 

    rgb_image.save(buffer, format="JPEG")
    
    return buffer.getvalue()

#prepare image for pass to model
def prepare_image(image_uri: str) -> str:
    http_response: requests.Respone = requests.get(image_uri) 

    image_bytes: bytes = http_response.content

    content_type: str = http_response.headers["Content-Type"] 

    media_type: str = content_type.split(";")[0] 

    safe_types: list[str] = ["image/jpeg", "image/png", "image/gif", "image/webp"]

    if(media_type not in safe_types):
        image_bytes = convert_to_jpeg(image_bytes)

        media_type = "image/jpeg"

    encoded_bytes: bytes = base64.b64encode(image_bytes) 

    image_data: str = encoded_bytes.decode("utf-8") 

    data_url: str = "data:" + media_type + ";base64," + image_data 

    return data_url 



