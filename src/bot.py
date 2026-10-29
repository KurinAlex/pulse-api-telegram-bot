"""Telegram bot (aiogram 3.x) that controls the Pulse API."""

import logging

import aiohttp
from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from src.config import ALLOWED_USER_IDS
from src.pulse_api import PulseApi, PulseApiError

log = logging.getLogger("pulse-bot")


MAX_REPLY_CHARS = 500


router = Router()
if ALLOWED_USER_IDS:
    router.message.filter(F.from_user.id.in_(ALLOWED_USER_IDS))


class PictureStates(StatesGroup):
    waiting_for_image = State()


def _truncate(text: str) -> str:
    text = text.strip()
    return text if len(text) <= MAX_REPLY_CHARS else text[:MAX_REPLY_CHARS] + "…"


async def call_and_report(message: Message, call, success: str) -> None:
    """Await an API call and report the outcome to the user."""
    try:
        await call
    except PulseApiError as e:
        log.warning("Pulse API error %s: %s", e.status, e.body)
        await message.answer(f"❌ API error {e.status}\n{_truncate(e.body)}".strip())
    except (TimeoutError, aiohttp.ClientError):
        log.exception("Could not reach the Pulse API")
        await message.answer("❌ Could not reach the Pulse API.")
    else:
        text = f"✅ {success}"
        await message.answer(text)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()


@router.message(Command("sleep_on"))
async def cmd_sleep_on(message: Message, state: FSMContext, pulse: PulseApi) -> None:
    await state.clear()
    await call_and_report(message, pulse.sleep_on(), "Sleep mode is on.")


@router.message(Command("sleep_off"))
async def cmd_sleep_off(message: Message, state: FSMContext, pulse: PulseApi) -> None:
    await state.clear()
    await call_and_report(message, pulse.sleep_off(), "Sleep mode is off.")


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    if await state.get_state() is None:
        await message.answer("Nothing to cancel.")
        return
    await state.clear()
    await message.answer("Cancelled.")


@router.message(Command("picture"))
async def cmd_picture(message: Message, state: FSMContext) -> None:
    await state.set_state(PictureStates.waiting_for_image)
    await message.answer("Send me the picture (or /cancel).")


@router.message(PictureStates.waiting_for_image, F.photo)
async def picture_from_photo(
    message: Message, state: FSMContext, bot: Bot, pulse: PulseApi
) -> None:
    photo = message.photo[-1]  # largest available size
    buffer = await bot.download(photo)
    await state.clear()
    await call_and_report(
        message,
        pulse.picture(buffer.getvalue(), f"{photo.file_unique_id}.jpg", "image/jpeg"),
        "Picture sent.",
    )


@router.message(
    PictureStates.waiting_for_image, F.document.mime_type.startswith("image/")
)
async def picture_from_document(
    message: Message, state: FSMContext, bot: Bot, pulse: PulseApi
) -> None:
    doc = message.document
    buffer = await bot.download(doc)
    await state.clear()
    await call_and_report(
        message,
        pulse.picture(
            buffer.getvalue(),
            doc.file_name or f"{doc.file_unique_id}.img",
            doc.mime_type,
        ),
        "Picture sent.",
    )


@router.message(PictureStates.waiting_for_image)
async def picture_invalid(message: Message) -> None:
    await message.answer("That doesn't look like an image. Send a picture or /cancel.")


# --------------------------------------------------------------------------- #
# Entrypoint
# --------------------------------------------------------------------------- #
