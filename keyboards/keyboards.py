from typing import List, Dict


from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)


def get_language_keyboard(voices: List[Dict], page: int = 0) -> InlineKeyboardMarkup:
    languages = sorted(set(voice['language'] for voice in voices))
    LANGUAGES_PER_PAGE = 6
    total_pages = (len(languages) + LANGUAGES_PER_PAGE - 1) // LANGUAGES_PER_PAGE

    start_idx = page * LANGUAGES_PER_PAGE
    end_idx = start_idx + LANGUAGES_PER_PAGE
    current_page_languages = languages[start_idx:end_idx]

    keyboard = []

    for language in current_page_languages:
        keyboard.append([
            InlineKeyboardButton(
                text=language,
                callback_data=f"lang_{language}"
            )
        ])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"page_{page - 1}"
            )
        )

    nav_buttons.append(
        InlineKeyboardButton(
            text=f"{page + 1}/{total_pages}",
            callback_data="current_page"
        )
    )

    if page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Далее ➡️",
                callback_data=f"page_{page + 1}"
            )
        )

    keyboard.append(nav_buttons)

    keyboard.append([
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="cancel"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_voice_keyboard(voices: List[Dict], language: str) -> InlineKeyboardMarkup:
    keyboard = []

    male_voices = [v for v in voices if v['gender'] == 'male' and v['language'] == language]
    female_voices = [v for v in voices if v['gender'] == 'female' and v['language'] == language]
    cloned_voices = [v for v in voices if v['is_cloned'] and v['language'] == language]

    if male_voices:
        keyboard.append([
            InlineKeyboardButton(
                text=f"Male: {male_voices[0]['name']}",
                callback_data=f"voice_{male_voices[0]['voice_id']}"
            )
        ])
    if female_voices:
        keyboard.append([
            InlineKeyboardButton(
                text=f"Female: {female_voices[0]['name']}",
                callback_data=f"voice_{female_voices[0]['voice_id']}"
            )
        ])

    for voice in cloned_voices:
        keyboard.append([
            InlineKeyboardButton(
                text=f"Custom: {voice['name']}",
                callback_data=f"voice_{voice['voice_id']}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="Back",
            callback_data="back_to_languages"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="/add_voice")],
        [KeyboardButton(text="/sync_voices")],
        [KeyboardButton(text="/generate")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="Cancel",
                callback_data="cancel"
            )
        ]]
    )
