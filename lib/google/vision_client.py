from PIL import Image
import requests

from lib.utils.image_converter import base64encode


class VisionClient:
    def __init__(self, api_key: str):
        self.api_url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"


    def extract_text_from_image(self, image: Image.Image) -> str:
        req_content = base64encode(image)

        req_payload = {
            "requests": [
                {
                    "image": {"content": req_content},
                    "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                    "imageContext": {"languageHints": ["pl"]}
                }
            ]
        }

        response = requests.post(self.api_url, json=req_payload)
        res_json = response.json()

        # text separation from response
        if response.status_code == 200 and "textAnnotations" in res_json["responses"][0]:
            text = res_json["responses"][0]["textAnnotations"][0]["description"]
            return text
        else:
            raise Exception("OCR extraction failed")
