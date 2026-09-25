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

#prepare media for pass to model
def prepare_media(media_url: str) -> tuple:
    if(not media_url):
        return ("", "")

    try:
        http_response: requests.Response = requests.get(media_url, timeout=30)
        http_response.raise_for_status()
    except requests.RequestException:
        return ("", "")

    media_bytes: bytes = http_response.content

    content_type: str = http_response.headers.get("Content-Type", "")

    media_type: str = content_type.split(";")[0]

    if(not media_type.startswith("image/") and not media_type.startswith("video/")):
        return ("", "")

    safe_types: list[str] = ["image/jpeg", "image/png", "image/gif", "image/webp"]

    if(media_type.startswith("image/") and media_type not in safe_types):
        try:
            media_bytes = convert_to_jpeg(media_bytes)
        except Exception:
            return ("", "")
        media_type = "image/jpeg"


    encoded_bytes: bytes = base64.b64encode(media_bytes) 

    media_data: str = encoded_bytes.decode("utf-8") 

    data_url: str = "data:" + media_type + ";base64," + media_data

    if(media_type.startswith("image/")):
        return (data_url, "i")
    else:
        return (data_url, "v")


