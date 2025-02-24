from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery

from database.database import get_user_cases


class IsCaseInDBase(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        cases: dict[int, dict[str, str | int]] | None = await get_user_cases(callback.from_user.id)
        case_name_list = [case['case_name'] for case in cases.values()]
        return callback.data in case_name_list