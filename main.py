import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from src.bot import router
from src.config import BOT_TOKEN, PULSE_API_HOST, PULSE_API_TOKEN
from src.pulse_api import PulseApi


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Start the bot"),
            BotCommand(command="sleep_on", description="Turn sleep mode on"),
            BotCommand(command="sleep_off", description="Turn sleep mode off"),
            BotCommand(command="picture", description="Send a picture"),
            BotCommand(command="cancel", description="Cancel current action"),
        ]
    )

    async with PulseApi(PULSE_API_HOST, PULSE_API_TOKEN) as pulse:
        dp["pulse"] = pulse  # injected into handlers as the `pulse` argument
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
