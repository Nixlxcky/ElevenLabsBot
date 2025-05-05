import os

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command


from services.elevenlabs import ElevenLabsAPI
from database.database import Database
from keyboards.keyboards import (
    get_language_keyboard,
    get_voice_keyboard,
    get_main_keyboard,
    get_cancel_keyboard
)
from config import ELEVENLABS_API_KEY, API_URL, DATABASE_URL

router = Router()
db = Database(DATABASE_URL)
elevenlabs_api = ElevenLabsAPI(ELEVENLABS_API_KEY, API_URL)


class VoiceStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_audio_file = State()
    waiting_for_voice_name = State()


@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "Привет! Здесь ты можешь:\n"
        "1. Озвучивать текст (/generate)\n"
        "2. Клонировать голос (/add_voice)\n"
        "3. Синхронизировать голоса с твоей библиотекой голосов (/sync_voices)",
        reply_markup=get_main_keyboard()
    )


@router.message(Command('generate'))
async def generate_command(message: Message):
    voices = await db.get_all_voices()
    if not voices:
        await message.answer(
            "Голоса не найдены. Пожалуйста, используйте сначала команду /sync_voices"
        )
        return

    await message.answer(
        "Выберите язык для озвучки текста:",
        reply_markup=get_language_keyboard(voices)
    )


@router.message(Command("sync_voices"))
async def sync_voices(message: Message):
    try:
        await message.answer("Начинаю синхронизацию голосов...")
        voices = await elevenlabs_api.get_voices()
        await db.clear_voices()

        for voice in voices:
            await db.add_voice(voice)

        await message.answer("✅ Голоса успешно синхронизированы!")
    except Exception as e:
        await message.answer(f"❌ Ошибка синхронизации голосов: {str(e)}")

@router.callback_query(F.data.startswith('page_'))
async def process_page_callback(callback_query: CallbackQuery):
    page = int(callback_query.data.split('_')[1])
    voices = await db.get_all_voices()
    await callback_query.message.edit_reply_markup(
        reply_markup=get_language_keyboard(voices, page)
    )

@router.callback_query(F.data.startswith("lang_"))
async def process_language_selection(callback: CallbackQuery):
    language = callback.data.split("_")[1]
    voices = await db.get_voices_by_language(language)

    await callback.message.edit_text(
        f"Выбранный язык: {language}\nВыберите голос:",
        reply_markup=get_voice_keyboard(voices, language)
    )



@router.callback_query(F.data.startswith("voice_"))
async def process_voice_selection(callback: CallbackQuery, state: FSMContext):
    voice_id = callback.data.split("_")[1]
    await state.update_data(voice_id=voice_id)
    await state.set_state(VoiceStates.waiting_for_text)

    await callback.message.edit_text(
        "Отправьте текст, который нужно озвучить.",
        reply_markup=get_cancel_keyboard()
    )
@router.message(VoiceStates.waiting_for_text)
async def process_text(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        audio = await elevenlabs_api.text_to_speech(
            text=message.text,
            voice_id=data['voice_id']
        )

        temp_file = f"temp_audio_{message.from_user.id}.mp3"
        with open(temp_file, "wb") as f:
            f.write(audio)

        await message.answer_audio(
            FSInputFile(temp_file),
            caption="Вот ваше аудио!"
        )

        os.remove(temp_file)
        await state.clear()

    except Exception as e:
        await message.answer(
            f"❌ Ошибка при генерации речи: {str(e)}",
            reply_markup=get_cancel_keyboard()
        )


@router.message(Command("add_voice"))
async def start_add_voice(message: Message, state: FSMContext):
    await state.set_state(VoiceStates.waiting_for_audio_file)
    await message.answer(
        "📁 Отправьте аудиофайл для клонирования голоса.\n\n"
        "📋 Требования к файлу:\n"
        "• Формат: mp3, wav, m4a\n"
        "• Длительность: минимум 30 секунд чистой речи\n"
        "• Качество: хорошее качество записи без шумов\n"
        "• Содержание: только один голос без фоновой музыки\n\n"
        "💡 Рекомендации для лучшего результата:\n"
        "• Длительность 1-10 минут\n"
        "• Четкая речь без сильного акцента\n"
        "• Отсутствие посторонних звуков",
        reply_markup=get_cancel_keyboard()
    )



@router.message(VoiceStates.waiting_for_audio_file, F.audio | F.document)
async def process_audio_file(message: Message, state: FSMContext):
    try:
        if message.audio:
            file_id = message.audio.file_id
            file_name = message.audio.file_name
            file_size = message.audio.file_size
            duration = message.audio.duration
        elif message.document:
            file_id = message.document.file_id
            file_name = message.document.file_name
            file_size = message.document.file_size
            duration = None
        else:
            await message.answer(
                "❌ Пожалуйста, отправьте аудиофайл в формате mp3, wav или m4a"
            )
            return

        if not any(file_name.lower().endswith(ext) for ext in ['.mp3', '.wav', '.m4a']):
            await message.answer(
                "❌ Неподдерживаемый формат файла. Используйте mp3, wav или m4a"
            )
            return

        if file_size > 50 * 1024 * 1024:
            await message.answer(
                "❌ Файл слишком большой. Максимальный размер - 50MB"
            )
            return

        if duration and duration < 30:
            await message.answer(
                "❌ Аудиофайл слишком короткий. Минимальная длительность - 30 секунд"
            )
            return

        await message.answer("⏳ Загружаю файл...")
        file = await message.bot.get_file(file_id)
        temp_filename = f"temp_voice_{message.from_user.id}{os.path.splitext(file_name)[1]}"
        await message.bot.download_file(file.file_path, temp_filename)

        with open(temp_filename, "rb") as f:
            await state.update_data(voice_file=f.read())

        if os.path.exists(temp_filename):
            os.remove(temp_filename)

        await state.set_state(VoiceStates.waiting_for_voice_name)
        await message.answer(
            "✅ Файл успешно загружен!\n\n"
            "Теперь отправьте имя для этого голоса (максимум 32 символа)\n"
            "💡 Совет: Используйте описательное имя, например: 'Мужской_голос_RU'",
            reply_markup=get_cancel_keyboard()
        )

    except Exception as e:
        if 'temp_filename' in locals() and os.path.exists(temp_filename):
            os.remove(temp_filename)
        await message.answer(f"❌ Ошибка при обработке файла: {str(e)}")
        await state.clear()


@router.message(VoiceStates.waiting_for_voice_name)
async def process_voice_name(message: Message, state: FSMContext):
    if len(message.text) > 32:
        await message.answer("❌ Имя слишком длинное. Используйте максимум 32 символа.")
        return

    try:
        data = await state.get_data()
        await message.answer("⏳ Начинаю процесс клонирования голоса...")

        voice_data = await elevenlabs_api.clone_voice(
            name=message.text,
            files=[data['voice_file']]
        )

        voice_data.update({'gender': 'custom'})
        await db.add_voice(voice_data)

        await message.answer(
            f"✅ Голос '{message.text}' успешно склонирован!\n\n"
            f"Используйте команду /generate чтобы начать использовать этот голос."
        )
        await state.clear()

    except Exception as e:
        print(e)
        await message.answer(
            f"❌ Ошибка при клонировании голоса:\n{str(e)}\n\n"
            f"Убедитесь, что аудиофайл соответствует требованиям"
        )
        await state.clear()

@router.callback_query(F.data == "cancel")
async def cancel_operation(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ Операция отменена."
    )


@router.callback_query(F.data == "back_to_languages")
async def back_to_languages(callback: CallbackQuery):
    voices = await db.get_all_voices()
    await callback.message.edit_text(
        "Выберите язык для озвучки текста:",
        reply_markup=get_language_keyboard(voices)
    )