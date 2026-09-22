# INSTAGRAM MEDIA
def gather_instagram_media(attachments: list) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []

    for attachment in attachments:
        media_type: str = attachment.get("type", "")

        url: str = attachment.get("payload", {}).get("url", "")

        if url:
            found.append((f"instagram {media_type} the user sent", url))

    return found


# MESSENGER MEDIA
def gather_messenger_media(attachments: list) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []

    for attachment in attachments:
        media_type: str = attachment.get("type", "")

        url: str = attachment.get("payload", {}).get("url", "")

        if url:
            found.append((f"messenger {media_type} the user sent", url))

    return found


# BLOOIO MEDIA
def gather_blooio_media(attachments: list) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []

    for attachment in attachments:
        url: str = attachment.get("payload", {}).get("url", "")

        if url:
            found.append(("photo the customer texted", url))

    return found


# MEDIA TYPE
def check_media_type(url: str) -> str:
    path: str = urlparse(url).path.lower()

    image_endings: tuple = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic")

    video_endings: tuple = (".mp4", ".mov", ".m4v", ".webm", ".avi")

    if path.endswith(image_endings):
        return "image"

    if path.endswith(video_endings):
        return "video"

    return "unknown"


# IMAGE TO BASE64
def image_to_base64(url: str) -> str:
    headers: dict = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=30)

    response.raise_for_status()

    image = Image.open(io.BytesIO(response.content))

    image = image.convert("RGB")

    image.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))

    buffer = io.BytesIO()

    image.save(buffer, format="JPEG", quality=JPEG_QUALITY)

    encoded: str = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:image/jpeg;base64,{encoded}"


# VIDEO TO BASE64
def video_to_base64(url: str) -> str:
    capture = cv2.VideoCapture(url)

    got_frame, frame = capture.read()

    capture.release()

    if not got_frame:
        raise ValueError("no frame could be read from this video")

    worked, encoded_frame = cv2.imencode(".jpg", frame)

    if not worked:
        raise ValueError("the frame could not be encoded")

    encoded: str = base64.b64encode(encoded_frame.tobytes()).decode("utf-8")

    return f"data:image/jpeg;base64,{encoded}"

# DESCRIBE
def describe_media(url: str):
    media_type: str = check_media_type(url)

    try:
        if media_type == "video":
            data_uri: str = video_to_base64(url)
        else:
            data_uri = image_to_base64(url)
            return NOT_ANALYZABLE

    except Exception as error:
        print(f"[MEDIA] could not describe {url}: {error}")

        return NOT_ANALYZABLE


