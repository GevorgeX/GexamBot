from  aiogram import Bot , types
from aiogram.dispatcher import Dispatcher , FSMContext
from aiogram.dispatcher.filters.state import State , StatesGroup
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup , KeyboardButton , InlineKeyboardButton , InlineKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from finder import Finder

TOKEN = "5730080458:AAFy5WfOW13eudGldoMwcsCqc0sos_Ev8ek"
storage = MemoryStorage()

bot = Bot(token= TOKEN)
dp = Dispatcher(bot , storage=storage)

result = {}

#Keyboard----------------------------------------------------------------#
kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_start = ReplyKeyboardMarkup(resize_keyboard=True)
kb_lessons =  ReplyKeyboardMarkup(resize_keyboard=True)

kb_start.add(KeyboardButton("/ԸնտրելԱռարկա")).insert(KeyboardButton("/Օգնություն"))
kb_client.add(KeyboardButton("/Գտնել")).insert(KeyboardButton("/Ավարտ"))
kb_lessons.add(KeyboardButton("Անգլ")).insert(KeyboardButton("Լեզու")).insert(KeyboardButton("Պատմ"))

inkb = InlineKeyboardMarkup(row_width=1)
inButArr = [
    InlineKeyboardButton(text='❌' , callback_data='deleteMessage'),
    InlineKeyboardButton(text='⬆️' , callback_data='upPage'),
    InlineKeyboardButton(text='⬇️' , callback_data='downPage'),
    InlineKeyboardButton(text='✅' , callback_data='answer')
    ]
inkb.row(*inButArr)


#State----------------------------------------------------------------#
class FSMStates(StatesGroup):
    selectingLesson = State()
    searching = State()
    selectingPage = State()

class NotFound(Exception):
    pass

#Bot----------------------------------------------------------------#

@dp.message_handler(commands=['start'] )
async def Start(message :types.Message):
    await message.answer("Սքսանք" , reply_markup=kb_start)

@dp.message_handler(commands=['ԸնտրելԱռարկա'])
async def SelectLesson(message :types.Message ):
    await FSMStates.selectingLesson.set()
    await bot.send_message(message.from_user.id,'Ընտրեք առարկան' ,reply_markup=kb_lessons)

@dp.message_handler(commands=['Ավարտ'] ,state="*" )
async def Cancel(message :types.Message , state:FSMContext):
    cur_state = await state.get_state()
    if cur_state is None:
        return
    await state.finish()
    global result
    result = {}
    await bot.send_message(message.from_user.id,'Պռծ' , reply_markup=kb_start)

@dp.message_handler(state=FSMStates.selectingLesson )
async def SetLesson(message :types.Message , state:FSMContext):
    if message.text == 'Անգլ':
        return await bot.send_message(message.from_user.id, 'Սորի , հմի չի աշխատոիմ 😥')
        Finder.SetLesson('english')
    elif message.text == 'Լեզու':
        Finder.SetLesson('hayoclezu')
    elif message.text == 'Պատմ':
        Finder.SetLesson('patmutyun')
    else:
        return await bot.send_message(message.from_user.id,'Սխալ')
    await FSMStates.next()
    await bot.send_message(message.from_user.id, 'Գրի ջիգյար ->', reply_markup=kb_client)

@dp.message_handler(commands=['Օգնություն'] ,state=None )
async def Help(message :types.Message):

    res = 'Նայի դեմից ընտրում ես առարկան ,հետո սխմումես  "Գտնել" ,հետո գրում ես քո խնդրի մի 2-3 բառ ,\
    հետո բերած ցուցակից գրում ես ,թե գթած աղյուսակի որ մի ռեսուլտատնա քեզ պետք։\
    Դրանից հետո ինքը կբերի համապատասխան նկարը , տակը 4 կնոպկա\n❌ - ջնջել\n⬆️ - թերթել վերև\n⬇️\
    - թերթել ներքև\n✅ - ստանալ պատասխանը\n\
    Վերջում սխմի "Ավարտ" , որ կարենաս նոր որոնում անես։'
    await bot.send_message(message.from_user.id,res)

@dp.message_handler(commands=['Գտնել'] ,state= [FSMStates.searching ,FSMStates.selectingPage])
async def Finding(message :types.Message):
    await bot.send_message(message.from_user.id , 'Գրի ջիգյար ->' , reply_markup=kb_client)
    await FSMStates.searching.set()

@dp.message_handler(content_types=['text']  ,state=FSMStates.searching)
async def GetPages(message :types.Message ):
    global result
    result =  Finder.FindPage(message.text)
    try:
        if len(result) ==0:
            raise NotFound()
        answer = 'Գտա համընկնում հետեվյալ տեղերում ՝ \n'
        num = 0

        for i in result :
            answer += f'* {str(i[0])} շտեմարանի {str(i[1])} էջում ,համար - {str(num)}\n'
            num += 1

        await bot.send_message(message.from_user.id,answer)
        await FSMStates.next()
    except NotFound:
        await bot.send_message(message.from_user.id,"Չգտա , փոիցի նորից")
    except:
        await bot.send_message(message.from_user.id,"Իսկ ավելի կոնկրետ?")


@dp.message_handler(state=FSMStates.selectingPage)
async def ChoosePage(message :types.Message ):
    global result
    try:
        index =  int(message.text)
        item = result[index]
        photo = open(Finder.GetImageOfPage(item), 'rb')

        await bot.send_photo(message.from_user.id,photo , caption=f'{str(result[index][0])},{str(result[index][1])}' , reply_markup=inkb)
    except:
        await bot.send_message(message.from_user.id,"Սխալ")

@dp.callback_query_handler(text = 'deleteMessage' , state="*")
async def DeleteMessage(calback: types.CallbackQuery):
    await bot.delete_message(calback.from_user.id , calback.message.message_id)
    await calback.answer()

@dp.callback_query_handler(text = 'upPage' , state="*")
async def UpPage(calback: types.CallbackQuery):
    global result
    try:
        index =  calback.message.caption.split(',')
        number = (int(index[0]) ,int(index[1])-1)

        photo = open(Finder.GetImageOfPage(number), 'rb')
        await calback.message.answer_photo(photo , caption=f'{str(number[0])},{str(number[1])}' , reply_markup=inkb)
    except:
        await calback.message.answer('Սխալ')
    finally:
        await calback.answer()


@dp.callback_query_handler(text = 'downPage' , state="*")
async def DownPage(calback: types.CallbackQuery):
    global result
    try:
        index =  calback.message.caption.split(',')
        number = (int(index[0]) ,int(index[1])+1)

        photo = open(Finder.GetImageOfPage(number), 'rb')
        await calback.message.answer_photo(photo , caption=f'{str(number[0])},{str(number[1])}' , reply_markup=inkb)
    except:
        await calback.message.answer('Սխալ')
    finally:
        await calback.answer()

@dp.callback_query_handler(text = 'answer' , state="*")
async def Answer(calback: types.CallbackQuery):
    global result
    try:
        index =  calback.message.caption.split(',')
        number = (int(index[0]) ,int(index[1]))
        item = Finder.GetAnswer(number)

        photo = open(Finder.GetImageOfPage(item), 'rb')
        await calback.message.answer_photo(photo , caption=f'{str(item[0])},{str(item[1])}' , reply_markup=inkb)
    except:
        await calback.message.answer('Սխալ')
    finally:
        await calback.answer()
executor.start_polling(dp , skip_updates = True )
