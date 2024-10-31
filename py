import ccxt
import ta
import pandas as pd  # استيراد pandas
import asyncio
import nest_asyncio  # إضافة مكتبة nest_asyncio لحل مشكلة event loop
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

# تطبيق nest_asyncio لتجنب الخطأ
nest_asyncio.apply()

# إعداد Telegram Bot
API_TOKEN = '7548130909:AAE1gPqzRYTlcw-ynS_cRJuVc852EkdUZNw'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# تعريف حالات FSM
class TradeStates(StatesGroup):
    awaiting_amount = State()
    awaiting_trade_type = State()
    awaiting_risk_management = State()
    awaiting_trade_count = State()
    awaiting_api_info = State()

# إعداد Binance API
binance = ccxt.binance()

# استراتيجيات التداول
SCALP_PROFIT_PERCENTAGE = 3 / 100
SWING_PROFIT_PERCENTAGE = 6 / 100
RISK_REWARD_RATIO = 3 / 1

SCALP_MAX_DURATION_HOURS = 24
SCALP_AVG_DURATION_HOURS = 4  # المتوسط بين 4 إلى 6 ساعات
SWING_MAX_DURATION_HOURS = 72
SWING_AVG_DURATION_HOURS = 12  # المتوسط بين 12 إلى 24 ساعة

# قائمة العملات
crypto_list = ['GTC/USDT', 'ACH/USDT', 'ADA/USDT', 'ADX/USDT', 'AERGO/USDT', 'ALICE/USDT', 'ALT/USDT', 'AMP/USDT', 'ANKR/USDT', 'APE/USDT', 'XVG/USDT', 'ZIL/USDT', 'BLZ/USDT', 'XLM/USDT', 'LINK/USDT', 'BTC/USDT', 'STRAX/USDT', 'BAND/USDT', 'PHA/USDT',
               'GRT/USDT', 'DOT/USDT', 'POLYX/USDT', 'SXP/USDT', 'LTO/USDT', 'IQ/USDT', 'WAXP/USDT', 'FDUSD/USDT', 'JASMY/USDT', 'CKB/USDT', 'ARB/USDT', 'DREP/USDT', 'SAND/USDT', 'NEAR/USDT', 'ICP/USDT', 'EOS/USDT', 'XRP/USDT', 'ETH/USDT', 'CELO/USDT', 'KDA/USDT', 'THETA/USDT', 'TFUEL/USDT',
               'DUSK/USDT', 'LOOM/USDT', 'AVAX/USDT', 'CTSI/USDT', 'ORDI/USDT', 'SYS/USDT',
               'RVN/USDT', 'LTC/USDT', 'LRC/USDT', 'IOTA/USDT', 'LPT/USDT', 'FET/USDT', 'SEI/USDT', 'ARKM/USDT', 'FIDA/USDT', 'PHB/USDT', 'ETC/USDT', 'GFT/USDT',
               'CELR/USDT', 'HIVE/USDT', 'ZEN/USDT', 'RLC/USDT', 'POWR/USDT', 'QNT/USDT', 'DGB/USDT', 'FIO/USDT', 'ROSE/USDT', 'DIA/USDT', 'ENS/USDT', 'RIF/USDT',
               'OP/USDT', 'TRX/USDT', 'GMT/USDT', 'MOVR/USDT', 'MTD/USDT', 'NFP/USDT', 'KLAY/USDT', 'MINA/USDT', 'FIL/USDT', 'DOGE/USDT', 'TWT/USDT', 'RARE/USDT',
               'GLMR/USDT', 'VET/USDT', 'COS/USDT', 'ROOT/USDT', 'QTUM/USDT', 'STPT/USDT', 'EGLD/USDT', 'PYTH/USDT', 'CFX/USDT', 'OM/USDT', 'SKL/USDT', 'XAI/USDT',
               'PORTAL/USDT', 'ENJ/USDT', 'ARPA/USDT', 'PLA/USDT', 'PROM/USDT', 'RSR/USDT', 'SUI/USDT', 'IOST/USDT', 'KEY/USDT', 'FLOW/USDT', 'MANTA/USDT', 'XTZ/USDT',
               'BCH/USDT', 'APT/USDT', 'BTG/USDT', 'DASH/USDT', 'DENT/USDT', 'LSK/USDT', 'FIRO/USDT', 'XEC/USDT', 'XEM/USDT', 'ATOM/USDT', 'SOL/USDT', 'MASK/USDT']

# ربط التداول مع Telegram
@dp.message_handler(commands=['start'])
async def start_trade(message: types.Message):
    await message.answer("مرحبًا! ما هو المبلغ المخصص للتداول؟")
    await TradeStates.awaiting_amount.set()

@dp.message_handler(state=TradeStates.awaiting_amount)
async def ask_trade_type(message: types.Message, state: FSMContext):
    amount = message.text
    await state.update_data(amount=amount)
    await message.answer("اختر نوع التداول: \n1. سكالب \n2. سوينغ")
    await TradeStates.awaiting_trade_type.set()

@dp.message_handler(state=TradeStates.awaiting_trade_type)
async def ask_risk_management(message: types.Message, state: FSMContext):
    trade_type = message.text
    if trade_type == '1':
        await state.update_data(trade_type='سكالب')
    elif trade_type == '2':
        await state.update_data(trade_type='سوينغ')
    else:
        await message.answer("يرجى اختيار 1 أو 2.")
        return

    await message.answer("اختر مستوى إدارة رأس المال:\n1. صارمة (5%)\n2. عالية الخطورة (30%)")
    await TradeStates.awaiting_risk_management.set()

@dp.message_handler(state=TradeStates.awaiting_risk_management)
async def ask_trade_count(message: types.Message, state: FSMContext):
    risk_level = message.text
    if risk_level == '1':
        await state.update_data(risk_management=5)
        await message.answer("كم عدد الصفقات التي ترغب في فتحها اليوم؟ (بحد أقصى 15 صفقة)")
    elif risk_level == '2':
        await state.update_data(risk_management=30)
        await message.answer("كم عدد الصفقات التي ترغب في فتحها اليوم؟ (بحد أقصى صفقتين)")
    else:
        await message.answer("يرجى اختيار 1 أو 2.")
        return
    await TradeStates.awaiting_trade_count.set()

@dp.message_handler(state=TradeStates.awaiting_trade_count)
async def ask_api_info(message: types.Message, state: FSMContext):
    trade_count = int(message.text)
    user_data = await state.get_data()
    risk_management = user_data['risk_management']

    if (risk_management == 5 and trade_count > 15) or (risk_management == 30 and trade_count > 2):
        await message.answer("لقد تجاوزت الحد المسموح به لعدد الصفقات. يرجى اختيار عدد أقل.")
        return
    await state.update_data(trade_count=trade_count)

    await message.answer("أرسل لي معلومات API الخاصة بـ Binance.\nاكتب الـ API Key والـ Secret بشكل منفصل.")
    await TradeStates.awaiting_api_info.set()

@dp.message_handler(state=TradeStates.awaiting_api_info)
async def setup_api(message: types.Message, state: FSMContext):
    api_info = message.text.split("\n")
    if len(api_info) != 2:
        await message.answer("يرجى التأكد من إدخال الـ API Key والـ Secret بشكل صحيح.")
        return

    api_key = api_info[0]
    api_secret = api_info[1]

    # إعداد API لمنصة Binance
    binance.apiKey = api_key
    binance.secret = api_secret

    await message.answer("تم إعداد API بنجاح! سأبدأ في تحليل العملات وفتح الصفقات وفقًا للإعدادات الخاصة بك.")
    user_data = await state.get_data()

    # الآن سنبدأ بتحديد أفضل العملات بناءً على التحليل الفني
    await analyze_and_open_trades(user_data, message)
    await state.finish()

# تحليل العملات وفتح الصفقات بناءً على التحليل الفني والمدارس المتفق عليها
async def analyze_and_open_trades(user_data, message):
    amount = float(user_data['amount'])
    trade_type = user_data['trade_type']
    risk_management = float(user_data['risk_management']) / 100
    trade_count = int(user_data['trade_count'])

    selected_coins = await analyze_coins(trade_count)  # تحليل العملات واختيار أفضلها
    trade_amount = amount * risk_management

    # فتح الصفقات بناءً على العملات المختارة
    for i, coin_data in enumerate(selected_coins):
        coin = coin_data['symbol']
        await open_trade(coin, trade_type, trade_amount, message, coin_data['success_rate'], coin_data['expected_duration'])

# تحليل العملات باستخدام المدارس المختلفة (ICT, SMC, Fibonacci, Elliott Waves)
async def analyze_coins(trade_count):
    best_coins = []
    for coin in crypto_list:
        # التحقق مما إذا كان السوق مدعومًا على Binance
        markets = binance.load_markets()
        if coin not in markets:
            print(f"❌ خطأ: Binance لا يدعم {coin}")
            continue

        # جلب البيانات وتحليلها باستخدام المدارس المختلفة
        historical_data = await get_historical_data(coin)
        if historical_data is None:
            print(f"❌ خطأ: البيانات غير متاحة لـ {coin}")
            continue

        # تحليل EMA, MACD, RSI
        technical_analysis = analyze_technical(historical_data)

        # دمج المدارس مثل ICT, SMC, Elliott Waves, Fibonacci
        combined_analysis = analyze_combined_strategy(historical_data)

        if combined_analysis['valid']:
            success_rate = calculate_success_rate(combined_analysis, technical_analysis)  # حساب نسبة النجاح
            expected_duration = estimate_duration(combined_analysis)  # تقدير مدة الصفقة

            # إضافة العملة إلى قائمة أفضل العملات مع التفاصيل
            best_coins.append({
                'symbol': coin,
                'success_rate': success_rate,
                'expected_duration': expected_duration
            })

    # ترتيب العملات بناءً على نسبة النجاح واختيار العدد المطلوب
    best_coins_sorted = sorted(best_coins, key=lambda x: (x['success_rate'], -x['expected_duration']), reverse=True)
    return best_coins_sorted[:trade_count]

# حساب نسبة النجاح بناءً على التحليل المتكامل
def calculate_success_rate(combined_analysis, technical_analysis):
    success_rate = 0
    if combined_analysis['valid']:
        success_rate += 50
    if technical_analysis['rsi'] and technical_analysis['rsi'] < 30:
        success_rate += 20
    if technical_analysis['macd'] and technical_analysis['macd'] > 0:
        success_rate += 30
    return min(success_rate, 100)

# تقدير مدة الصفقة بناءً على التحليل الفني
def estimate_duration(combined_analysis):
    if combined_analysis['valid']:
        return SCALP_AVG_DURATION_HOURS if combined_analysis['fib_high'] - combined_analysis['fib_low'] < 0.05 else SWING_AVG_DURATION_HOURS
    return SWING_MAX_DURATION_HOURS

# دالة فتح الصفقة بناءً على نوع التداول وإدارة رأس المال
async def open_trade(symbol, trade_type, trade_amount, message, success_rate, expected_duration):
    ticker = binance.fetch_ticker(symbol)
    current_price = ticker['last']

    profit_percentage = SCALP_PROFIT_PERCENTAGE if trade_type == 'سكالب' else SWING_PROFIT_PERCENTAGE

    # حساب الهدف ووقف الخسارة
    target_profit = current_price * (1 + profit_percentage)
    stop_loss = current_price * (1 - (1 / RISK_REWARD_RATIO))

    try:
        order = binance.create_order(symbol, 'limit', 'buy', trade_amount, current_price)
        await message.answer(f"تم فتح صفقة شراء لـ {symbol} بسعر {current_price}!")

        # فتح أوامر البيع
        binance.create_order(symbol, 'limit', 'sell', trade_amount, target_profit)
        binance.create_order(symbol, 'stop_loss_limit', 'sell', trade_amount, stop_loss, {'stopPrice': stop_loss})

        await message.answer(
            f"""تم فتح الصفقة:
            \nسعر الدخول: {current_price}
            \nالهدف: {target_profit} (+{profit_percentage * 100}%)
            \nوقف الخسارة: {stop_loss} (-{(1 / RISK_REWARD_RATIO) * 100}%)
            \nنسبة النجاح المتوقعة: {success_rate}%
            \nالمدة المتوقعة: {expected_duration} ساعات."""
        )
    except Exception as e:
        await message.answer(f"حدث خطأ أثناء فتح الصفقة لـ {symbol}: {e}")

# بدء البوت
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
