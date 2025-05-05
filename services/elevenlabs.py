from typing import List, Dict

from aiohttp import ClientSession, FormData


LANGUAGE_MAPPING = {
    "en": "Английский",
    "cz": "Чешский",
    "de": "Немецкий",
    "fr": "Французский",
    "es": "Испанский",
    "it": "Итальянский",
    "ru": "Русский",
    "zh": "Китайский",
    "ja": "Японский",
    "ko": "Корейский",
    "pt": "Португальский",
    "nl": "Нидерландский",
    "pl": "Польский",
    "sv": "Шведский",
    "tr": "Турецкий",
    "ar": "Арабский",
    "hi": "Хинди",
    "bn": "Бенгальский",
    "uk": "Украинский",
    "vi": "Вьетнамский",
    "el": "Греческий",
    "he": "Иврит",
    "hu": "Венгерский",
    "fi": "Финский",
    "da": "Датский",
    "no": "Норвежский",
    "ro": "Румынский",
    "bg": "Болгарский",
    "hr": "Хорватский",
    "sr": "Сербский",
    "sk": "Словацкий",
    "sl": "Словенский",
    "et": "Эстонский",
    "lv": "Латышский",
    "lt": "Литовский",
    "th": "Тайский",
    "id": "Индонезийский",
    "ms": "Малайский",
    "fa": "Персидский",
    "ur": "Урду",
    "ta": "Тамильский",
    "te": "Телугу",
    "ml": "Малаялам",
    "ka": "Грузинский",
    "hy": "Армянский",
    "az": "Азербайджанский",
    "kk": "Казахский",
    "uz": "Узбекский",
    "km": "Кхмерский",
    "my": "Бирманский",
    "mn": "Монгольский",
    "si": "Сингальский",
    "ne": "Непальский",
    "sq": "Албанский",
    "mk": "Македонский",
    "is": "Исландский",
    "ga": "Ирландский",
    "cy": "Валлийский",
    "eu": "Баскский",
    "ca": "Каталанский"
}


class ElevenLabsAPI:
    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    async def get_voices(self) -> List[Dict]:
        async with ClientSession() as session:
            async with session.get(
                    f"{self.api_url}/voices",
                    headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    voices = []
                    for voice in data.get("voices", []):
                        if voice.get("category") == "professional":
                            voices.append({
                                "voice_id": voice["voice_id"],
                                "name": voice["name"],
                                "language": LANGUAGE_MAPPING.get(
                                    voice.get("labels", {}).get("language", "unknown"), "Неизвестный"
                                ),
                                "gender": voice.get("labels", {}).get("gender", "unknown"),
                                "is_cloned": voice.get("category") == "cloned"
                            })
                        elif voice.get("category") == "cloned":
                            voices.append({
                                "voice_id": voice["voice_id"],
                                "name": voice["name"],
                                "language": LANGUAGE_MAPPING.get(
                                    voice.get("labels", {}).get("language", "custom"), "Пользовательский"
                                ),
                                "gender": voice.get("labels", {}).get("gender", "custom"),
                                "is_cloned": voice.get("category") == "cloned"})

                    return voices
                raise Exception(f"Failed to get voices: {response.status}")

    async def text_to_speech(self, text: str, voice_id: str) -> bytes:
        async with ClientSession() as session:
            async with session.post(
                    f"{self.api_url}/text-to-speech/{voice_id}",
                    headers=self.headers,
                    json={"text": text, "optimize_streaming_latency": 0}
            ) as response:
                if response.status == 200:
                    return await response.read()
                raise Exception(f"Failed to generate speech: {response.status}")

    async def clone_voice(self, name: str, files: List[bytes]) -> Dict:
        form_data = FormData()
        form_data.add_field("name", name)

        for i, file_data in enumerate(files):
            form_data.add_field(
                f"files",
                file_data,
                filename=f"sample_{i}.mp3"
            )

        async with ClientSession() as session:
            async with session.post(
                    f"{self.api_url}/voices/add",
                    headers={"xi-api-key": self.api_key},
                    data=form_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "voice_id": data["voice_id"],
                        "name": name,
                        "language": "custom",
                        "is_cloned": True
                    }
                raise Exception(f"Failed to clone voice: {response.status}")
