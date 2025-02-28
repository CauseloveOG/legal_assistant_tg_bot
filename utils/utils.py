# from lexicon.lexicon import LEXICON
#
#
# async def send_case_user(bot, user_id, case_name, case_number=None, court_name=None, kb=None):
#     await bot.send_message(chat_id=user_id,
#                            text=LEXICON['chosen_user_case'].format(case_name=case_name,
#                                                                                     case_number=case_number,
#                                                                                     court_name=court_name),
#                            kb=kb)