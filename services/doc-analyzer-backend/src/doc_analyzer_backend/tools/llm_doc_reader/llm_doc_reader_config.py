class LLMDocReaderConfig:
    def __init__(
        self,
        ocr_lang: str = "rus+eng",
        max_output_chars: int = 12000,
        preprocess_images: bool = False,
        ocr_enabled=False,
    ):
        self.ocr_lang = ocr_lang
        self.max_output_chars = max_output_chars
        self.preprocess_images = preprocess_images
        self.ocr_enabled = ocr_enabled
