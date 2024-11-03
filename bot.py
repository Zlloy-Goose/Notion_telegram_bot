from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update 
from telegram.ext import filters, CallbackQueryHandler, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackContext,Application,ExtBot
from MyBD import MyDataBase
from collections import defaultdict
from typing import DefaultDict, Optional, Set
from telegram.error import BadRequest
from datetime import datetime

from texts import Names



def log(e):
     with open("log", "a",encoding='utf-8') as log:
        log.write(datetime.now().strftime("%m-%d %H:%M") + " -- " + str(e) + " \n")

def get_token() -> str:
    f = open("doc\\start.txt", 'r')
    line = ''
    for _ in Names.RANGE_LINES:
        line = f.readline().strip()
        if "bot_token" in line:
            break
    return line[line.find('=')+1:].strip()

def get_user_name() -> str:
    f = open("doc\\start.txt", 'r')
    line = ''
    for _ in Names.RANGE_LINES:
        line = f.readline().strip()
        if "user_name" in line:
            break
    return line[line.find('=')+1:].strip()

def get_user_id() -> str:
    f = open("doc\\start.txt", 'r')
    line = ''
    for _ in Names.RANGE_LINES:
        line = f.readline().strip()
        if "user_id" in line:
            break
    return line[line.find('=')+1:].strip()

class SaveDate:
    """"""
    current_msg_id = None

    last_msg_id = None
    name_table = None
    DB = None
    user_id = ''
 
    def __init__(self):
        self.user_name = get_user_name()
        self.user_id = get_user_id()
        self.DB = MyDataBase(self.user_name[1:])
    
    def add_user_name(self, name):
        """Добавляет имя пользователя
           Вход имя пользователя
           Выход либо false все успешно  либо текс с ошибкой """
        if type(name) ==  str:
            self.user_name.append(name.lower())
            return False
        else:
            return "access error"

class CustomContext(CallbackContext):
    """Custom class for context."""
    def __init__(
        self,
        application: Application,
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ):
        super().__init__(application=application, chat_id=chat_id, user_id=user_id)

    def save_password(self, name, text):
        if self.chat_data.user_id == self._user_id:
            return self.chat_data.MyDB.add_items(name_table='password', items=str(datetime.now().strftime("%Y-%m-%d")) + " "+ text[2:].strip())
        else:
            return "access error"

    def show_password1(self, name_site, name_colns = ['site_name', 'add_name_site']):
        if self.chat_data.user_id == self._user_id:
            return self.chat_data.MyDB.show_items('password', name_site, name_colns=name_colns )
        else:
            return "access error"

    def show_password(self):
        if self.chat_data.user_id == self._user_id:
            return  self.chat_data.MyDB.show_all_items('password')
        else:
            return "access error"

    def password_delete(self, site_name):
        self.chat_data.MyDB.delete_items()

    def save_notion(self, text):
        if self.chat_data.user_id == self._user_id:
            items=[]
            items.append(str(datetime.now().strftime("%Y-%m-%d")))
            for _ in text.split('...'):
                items.append(_)
            return self.chat_data.MyDB.add_items(name_table='notion'+str(self._user_id), items=items)
        else:
            return "access error"
    
    def items_show(self, table_name, item, column_name):
        if self.chat_data.user_id == self._user_id:
            return self.chat_data.MyDB.show_items(name_table=table_name, item=item, name_colns=column_name)
        else:
            return "access error"
        
    def all_item_show(self, table_name):
        if self.chat_data.user_id == self._user_id:
            return  self.chat_data.MyDB.show_all_items('notion' + str(self._user_id))
        else:
            return "access error"

async def delete_old_messages(update: Update, context: CustomContext):
    try:
        await context.bot.delete_message(chat_id=context.chat_data.user_id, message_id=context.chat_data.last_msg_id)
    except BadRequest as e:
        log(datetime.now().strftime("%m-%d %H:%M") + str(e) + "  98\n")
    except TypeError as e:
        log(datetime.now().strftime("%m-%d %H:%M") + str(e) + "  100\n")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_old_messages(update, context) 
    context.chat_data.last_msg_id = update.effective_message.id
    await delete_old_messages(update, context) 
    context.chat_data.last_msg_id += 1

    if (context.chat_data.user_name == update.effective_user.name):
        if (context.chat_data.user_id == ''):
            context.chat_data.user_id = update.effective_user.id
            with open(Names.START_FILE, 'a', encoding='utf-8') as s:
                s.write(f"\nuser_id = {update.effective_user.id}")
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text = """
  /p [site] [login] [pass] [name_site1] [add_site_name] [link - site]
  /ps [site_name] or [] Показывает все пароли
  /n [flag...notion]
  /ns [notion flag] or [] """)
    else:
        await context.bot.send_message(update.effective_chat.id, "ERROR! Access")
        log("ERROR! Access")

async def save_password(update: Update, context: CustomContext):
    """удаляет ваше сообщение отправляет запрос в БД на сохранение пароля"""
    await delete_old_messages(update, context) 
    context.chat_data.last_msg_id = update.effective_message.id
    await delete_old_messages(update, context) 
    context.chat_data.last_msg_id += 1
    if update.effective_user.name == context.chat_data.user_name:
        args = context.args
        args.insert(0,datetime.now().strftime("%m-%d %H:%M"))
        text = context.chat_data.DB.add_items(Names.PASSWORD_TABLE, args)
        if text == "Create":
            await context.bot.send_message(update.effective_user.id, text)
        else:
            await context.bot.send_message(update.effective_user.id, text + "\n" + " ".join(args))
    else:
        await delete_old_messages

async def show_password(update: Update, context: CustomContext):
    """Показывает пароли по запросу"""
    await delete_old_messages(update, context) 
    context.chat_data.last_msg_id = update.effective_message.id
    await delete_old_messages(update, context) 
    context.chat_data.last_msg_id += 1
    if update.effective_user.name == context.chat_data.user_name:
        args = context.args
        text = ''
        if len(args)==0:
            text += context.chat_data.DB.show_items(Names.PASSWORD_TABLE) + '\n'
        else:
            for arg in args:
                text += context.chat_data.DB.show_items(Names.PASSWORD_TABLE, arg) + '\n'
        if text == '':
            text += "Not found!"
            for arg in args:
                text += arg
        await context.bot.send_message(update.effective_user.id, text)
    else:
        await delete_old_messages

async def password_delete(update: Update, context: CustomContext):
    await delete_old_messages(update, context) 
    context.chat_data.last_msg_id = update.effective_message.id
    await delete_old_messages(update, context) 
    context.chat_data.last_msg_id += 1
    if update.effective_user.name == context.chat_data.user_name:
        try:
            arg = context.args[0]
            text = ''
            text = context.chat_data.DB.conf_delelete_item(Names.PASSWORD_TABLE, arg)
            if text != '':
                keyboard = [
                        [
                            InlineKeyboardButton('YES', callback_data=Names.PASSWORD_TABLE + ' '+ arg),
                            InlineKeyboardButton("No", callback_data="False")
                        ]
                    ]
                await update.message.reply_text("Delete password ? -> " + text, reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                await context.bot.send_message(update.effective_user.id, "Не найдено")
        except:
            await context.bot.send_message(update.effective_user.id, "Не верное число аргументов")

    else:
        await delete_old_messages
    
async def button(update: Update, context: CustomContext):
    context.chat_data.last_msg_id = update.effective_message.id
    query = update.callback_query
    await query.answer()
    if (query.data == "False" ):
        await delete_old_messages(update, context) 
    else: 
        text = context.chat_data.DB.delete_item(query.data.split(' ')[0], query.data.split(' ')[1])
        await query.edit_message_text(text)

async def text_message(update: Update, context: CustomContext):
    await delete_old_messages(update, context) 
    context.chat_data.last_msg_id = update.effective_message.id
    await delete_old_messages(update, context) 

async def notion_create(update: Update, context: CustomContext):
    await delete_old_messages(update, context) 
    context.chat_data.last_msg_id = update.effective_message.id
    await delete_old_messages(update, context) 
    context.chat_data.last_msg_id += 1
    if update.effective_user.name == context.chat_data.user_name:
        arg = context.args
        items = [datetime.now().strftime("%m-%d %H:%M"),
                  arg[0],
                    " ".join(arg[1:])]
        text = context.chat_data.DB.add_items(Names.NOTION_TABLE, items)
        if text == "Create":
            await context.bot.send_message(update.effective_user.id, text)
        else:
            await context.bot.send_message(update.effective_user.id, text + "\n" + " ".join(args))
    else:
        await delete_old_messages

async def notion_show(update: Update, context: CustomContext):
    """Показывает пароли по запросу"""
    await delete_old_messages(update, context) 
    context.chat_data.last_msg_id = update.effective_message.id
    await delete_old_messages(update, context) 
    context.chat_data.last_msg_id += 1
    if update.effective_user.name == context.chat_data.user_name:
        args = context.args
        text = ''
        if len(args)==0:
            text += context.chat_data.DB.show_items(Names.NOTION_TABLE) + '\n'
        else:
            for arg in args:
                text += context.chat_data.DB.show_items(Names.NOTION_TABLE, arg) + '\n'
        await context.bot.send_message(update.effective_user.id, text)
    else:
        await delete_old_messages

async def notion_delete(update: Update, context: CustomContext):
    await delete_old_messages(update, context) 
    context.chat_data.last_msg_id = update.effective_message.id
    await delete_old_messages(update, context) 
    context.chat_data.last_msg_id += 1
    if update.effective_user.name == context.chat_data.user_name:
        try:
            arg = context.args[0]
            text = ''
            text = context.chat_data.DB.conf_delelete_item(Names.NOTION_TABLE, arg)
            if text != '':
                keyboard = [
                        [
                            InlineKeyboardButton('YES', callback_data=Names.NOTION_TABLE + ' '+ arg),
                            InlineKeyboardButton("No", callback_data="False")
                        ]
                    ]
                await update.message.reply_text("Delete notion ? -> " + text, reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                await context.bot.send_message(update.effective_user.id, "Не найдено")
        except:
            await context.bot.send_message(update.effective_user.id, "Не верное число аргументов")

    else:
        await delete_old_messages


async def test_mode(update: Update, context: CustomContext):
    try:
        await context.bot.delete_message(chat_id=context.chat_data.user_id, message_id=context.chat_data.last_msg_id)
    except BadRequest as e:
        with open("log", "a",encoding='utf-8') as log:
            log.write(datetime.now().strftime("%m-%d %H:%M") + str(e) + "  117\n")
    except TypeError as e:
        with open("log", "a",encoding='utf-8') as log:
            log.write(datetime.now().strftime("%m-%d %H:%M") + str(e) + "  120\n")
    print(context.chat_data.last_msg_id)
    print("effect message -> ", update.effective_message.id)
    await update.effective_message.delete()









    


def main():
    context_types = ContextTypes(context=CustomContext, chat_data=SaveDate)
    myBot = ApplicationBuilder().token(get_token()).context_types(context_types).build()
    myBot.add_handler(CommandHandler(['start', 'help'], start))
    myBot.add_handler(CommandHandler(['p'], save_password))
    myBot.add_handler(CommandHandler(['ps'], show_password))
    myBot.add_handler(CommandHandler(['pd'], password_delete))

    myBot.add_handler(CallbackQueryHandler(button))
    myBot.add_handler(MessageHandler(filters.TEXT&(~filters.COMMAND), text_message))

    myBot.add_handler(CommandHandler(['n'], notion_create))
    myBot.add_handler(CommandHandler(['nd'], notion_delete))
    myBot.add_handler(CommandHandler(['ns'], notion_show))

    myBot.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()



