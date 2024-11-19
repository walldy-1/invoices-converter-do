import openai

from const.openai import OPENAI_MODEL
from data.templates.ai_response import ai_response_template
from lib.utils.template_to_str import template_to_str


class OpenAiStatus:
    def verify_model_support(api_key: str) -> str:
        try:
            if (not api_key):
                return "Podaj klucz API."
            
            openai.api_key = api_key
            models_list = openai.models.list()
            models_data = models_list.data
            
            if any(model.id == OPENAI_MODEL for model in models_data):
                return "OK"
            else:
                return f"Dla Twojego klucza API model {OPENAI_MODEL} nie jest obsługiwany."
            
        except openai.AuthenticationError:
            return "Błędny klucz API."
        except Exception as e:
            return f"Wystąpił błąd: {str(e)}"


class OpenAiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = OPENAI_MODEL

        verify_key = OpenAiStatus.verify_model_support(self.api_key)
        if verify_key == "OK":
            self.client = self._get_client()
        else:
            raise Exception(verify_key)
        
        response_structure = template_to_str(ai_response_template)
        self.system_message_content = f"""
Przetwarzasz dane pochodzące z analizy OCR skanów dokumentów sprzedaży.
Mogą to być faktury, paragony, umowy różnego rodzaju (umowa o dzieło, umowa zlecenie, umowa ubezpieczenia, itp.), bilety parkingowe, itp.
Dokument może się składać z jednej lub z wielu stron.
Na jednym skanie może być jeden lub wiele dokumentów.
Dane wyjściowe mają być w następującej postaci (jako wartości podane są oczekiwane dane z dokumentu):
{response_structure},
itd.
Ważna zasada: zwracasz tylko JSON, bez dodatkowych komentarzy.
"""

    def _get_client(self):
        return openai.OpenAI(api_key=self.api_key)
    

    def get_invoice_info(self, ocr_text: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": self.system_message_content
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Wyciągnij informacje z dokumentów sprzedażowych:\n{ocr_text}",
                        },
                    ],
                },
            ],
        )

        usage = {
            "completion_tokens": response.usage.completion_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "total_tokens": response.usage.total_tokens
        }

        json_rep = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
        return json_rep, usage
