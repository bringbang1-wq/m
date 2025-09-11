from telethon.sync import TelegramClient, events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.errors.rpcerrorlist import MessageNotModifiedError,FloodWaitError
from telethon.tl.types import ChannelParticipantCreator, ChannelParticipantAdmin
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.functions.messages import DeleteMessagesRequest
import datetime
import pytz
import asyncio
import os
import pickle
import re
import io
import aiohttp
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
#خطر سريع الاشتعال ممنوع تلعب هنا#
import os
from telethon import TelegramClient, events
from telethon.sessions import SQLiteSession


print('تم تشغيل سورس مرتضى بنجاح')

# البحث عن ملفات .session
session_files = [f for f in os.listdir() if f.endswith(".session")]
if not session_files:
    raise FileNotFoundError("⚠️ ماكو أي ملف جلسة (.session) بالمجلد!")

session_file = session_files[0]
print(f"🔑 تم العثور على الجلسة: {session_file}")

# تشغيل الكلاينت من ملف الجلسة
session = SQLiteSession(session_file)
client = TelegramClient(session, api_id=1, api_hash="1")  
# القيم هنا وهمية، Telethon رح يقرأ الصح من داخل ملف الجلسة



published_messages_file = 'published_messages.pkl'
muted_users_file = 'muted_users.pkl'
time_update_status_file = 'time_update_status.pkl'
channel_link_file = 'channel_link.pkl'

# إنشاء العميل وتشغيله




response_file = 'responses.pkl'


if os.path.exists(response_file):
    with open(response_file, 'rb') as f:
        responses = pickle.load(f)
else:
    responses = {}



import os

if os.path.exists(channel_link_file) and os.path.getsize(channel_link_file) > 0:
    with open(channel_link_file, 'rb') as f:
        channel_link = pickle.load(f)
else:
    channel_link = None

if os.path.exists(time_update_status_file):
    with open(time_update_status_file, 'rb') as f:
        time_update_status = pickle.load(f)
else:
    time_update_status = {'enabled': False}


if os.path.exists(muted_users_file):
    with open(muted_users_file, 'rb') as f:
        muted_users = pickle.load(f)
else:
    muted_users = {}



if os.path.exists(response_file):
    with open(response_file, 'rb') as f:
        responses = pickle.load(f)
else:
    responses = {}

if os.path.exists(published_messages_file):
    with open(published_messages_file, 'rb') as f:
        published_messages = pickle.load(f)
else:
    published_messages = []


active_timers = {}
countdown_messages = {}


image_path = 'local_image.jpg'


account_name = None

async def respond_to_greeting(event):
    if event.is_private and not (await event.get_sender()).bot:  
        message_text = event.raw_text.lower()
        if "هلا" in message_text:
            response = """
–اهلا وسهلا تفضل """
            try:
                await client.send_file(event.chat_id, file=image_path, caption=response)
            except Exception as e:
                await event.edit(f"⚠️ حدث خطأ أثناء جلب الصورة: {e}")
        else:
            for keyword, response in responses.items():
                if keyword in message_text:
                    try:
                        await client.send_file(event.chat_id, file=image_path, caption=response)
                    except Exception as e:
                        await event.edit(f"⚠️ حدث خطأ أثناء جلب الصورة: {e}")
                    break

client.add_event_handler(respond_to_greeting, events.NewMessage(incoming=True))

@client.on(events.NewMessage(from_users='me', pattern='.add'))
async def add_response(event):
    try:
        
        command, args = event.raw_text.split(' ', 1)
        keyword, response = args.split('(', 1)[1].split(')')[0], args.split(')', 1)[1].strip()
        responses[keyword.lower()] = response

        
        with open(response_file, 'wb') as f:
            pickle.dump(responses, f)
        
        await event.edit("✅ تم إضافة الرد")
    except ValueError:
        await event.edit("⚠️ استخدم الصيغة: .add (الكلمة المفتاحية) الرد")

async def respond_to_mention(event):
    if event.is_private and not (await event.get_sender()).bot:  
        sender = await event.get_sender()
        await event.edit(f"انتظر يجي المطور @{sender.username} ويرد على رسالتك لا تبقه تمنشنه هواي")

@client.on(events.NewMessage(from_users='me', pattern='.تفعيل الوقتي'))
async def enable_time_update(event):
    await event.delete()
    global time_update_status
    time_update_status['enabled'] = True
    with open(time_update_status_file, 'wb') as f:
        pickle.dump(time_update_status, f)
    reply = await event.reply("✓ تم تفعيل الاسم مع الوقت   ‌‎⎙.")
    await event.edit()  

    await asyncio.sleep(1)
    await reply.edit()  

@client.on(events.NewMessage(from_users='me', pattern='.تعطيل الوقتي'))
async def disable_time_update(event):
    await event.delete()
    global time_update_status
    time_update_status['enabled'] = False
    with open(time_update_status_file, 'wb') as f:
        pickle.dump(time_update_status, f)
    
    
    if account_name:
        iraq_tz = pytz.timezone('Asia/Baghdad')
        now = datetime.now(iraq_tz)
        current_name = re.sub(r' - \d{2}:\d{2}', '', account_name)
        new_username = f"{current_name}"
        
        try:
            await client(UpdateProfileRequest(first_name=new_username))
            reply = await event.reply("**✓ تم تعطيل الاسم وإزالة الوقت من الاسم   ‌‎⎙.**")
        except Exception as e:
            reply = await event.reply(f"⎙ حدث خطأ أثناء إزالة الوقت من الاسم: {e}")
    else:
        reply = await event.reply("**⎙ لم يتم تعيين اسم الحساب.**")
    
    await event.edit()  

    await asyncio.sleep(1)
    await reply.edit()  



@client.on(events.NewMessage(from_users='me', pattern='.اضافة قناة (.+)'))
async def add_channel(event):
    global channel_link
    channel_link = event.pattern_match.group(1)
    with open(channel_link_file, 'wb') as f:
        pickle.dump(channel_link, f)
    await event.edit(f"** تم تعيين رابط القناة إلى: {channel_link}**")

async def is_subscribed(user_id):
    if not channel_link:
        return True  # إذا لم يكن هناك قناة محددة، اعتبر أن المستخدم مشترك
    channel_username = re.sub(r'https://t.me/', '', channel_link)
    try:
        offset = 0
        limit = 100
        while True:
            participants = await client(GetParticipantsRequest(
                channel=channel_username,
                filter=ChannelParticipantsSearch(''),
                offset=offset,
                limit=limit,
                hash=0
            ))
            if not participants.users:
                break
            for user in participants.users:
                if user.id == user_id:
                    return True
            offset += len(participants.users)
        return False
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds)
        return await is_subscribed(user_id)
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

@client.on(events.NewMessage(incoming=True))
async def respond_to_greeting(event):
    if event.is_private and not (await event.get_sender()).bot:  # تحقق ما إذا كانت الرسالة خاصة وليست من بوت
        if not await is_subscribed(event.sender_id):
            await event.edit(f"**لا يمكنك مراسلتي الى بعد الاشتراك في قناتي: {channel_link}**")
            await client.delete_messages(event.chat_id, [event.id])
        else:
            message_text = event.raw_text.lower()
@client.on(events.NewMessage(from_users='me', pattern='.الغاء الاشتراك الاجباري'))
async def remove_channel(event):
    global channel_link
    channel_link = None
    try:
        open(channel_link_file, 'wb').close()  # تفريغ الملف
    except Exception as e:
        print(f"Error clearing channel file: {e}")
    await event.edit("**✅ تم إلغاء الاشتراك الإجباري.**")

@client.on(events.NewMessage(from_users='me', pattern='.del'))
async def delete_response(event):
    try:
        # Extract keyword from the message
        command, keyword = event.raw_text.split(' ', 1)
        keyword = keyword.lower()
        
        if keyword in responses:
            del responses[keyword]
            # Save responses to file
            with open(response_file, 'wb') as f:
                pickle.dump(responses, f)
            await event.edit("**تـم حذف الرد**")
        else:
            await event.edit("** لم يتم العثور على الكلمة المحددة**")
    except ValueError:
        await event.edit("**⚠️ استخدم الصيغة: del الكلمة المفتاحية**")

@client.on(events.NewMessage(from_users='me', pattern='.الردود'))
async def show_responses(event):
    if responses:
        response_text = "📋 الردود المضافة:\n"
        for keyword, response in responses.items():
            response_text += f"**🔹 الكلمة المفتاحية: {keyword}\n🔸 الرد: {response}\n**"
        await event.edit(response_text)
    else:
        await event.edit("** لا توجد ردود مضافة حتى الآن.**")

@client.on(events.NewMessage(from_users='me', pattern='.time'))
async def countdown_timer(event):
    try:
        # Extract the number of minutes from the message
        command, args = event.raw_text.split(' ', 1)
        minutes = int(args.strip().strip('()'))

        # Check if there's an active timer, cancel it
        if event.chat_id in active_timers:
            active_timers[event.chat_id].cancel()
            del active_timers[event.chat_id]
            # Remove the existing countdown message if it exists
            if event.chat_id in countdown_messages:
                await client.delete_messages(event.chat_id, countdown_messages[event.chat_id])
                del countdown_messages[event.chat_id]

        async def timer_task():
            nonlocal minutes
            total_seconds = minutes * 60
            # Send the initial message about the countdown starting
            countdown_message = await event.edit("**⏳ سيبدأ العد التنازلي بعد 3 ثوانٍ**")

            # Store the message ID for later deletion
            countdown_messages[event.chat_id] = countdown_message.id

            # Wait for 1 second and update the message
            await asyncio.sleep(1)
            await countdown_message.edit("⏳** سيبدأ العد التنازلي بعد 2 ثانيتين**")


            # Wait for the final second before starting the countdown
            await asyncio.sleep(1)
            
            # Update the message to start the countdown
            countdown_message = await countdown_message.edit(f"⏳** سيبدأ العد التنازلي بعد 1 ثانية**")
            
            # Countdown loop
            while total_seconds > 0:
                minutes, seconds = divmod(total_seconds, 60)
                new_text = f"⏳** {minutes:02}:{seconds:02} متبقية**"
                await asyncio.sleep(1)
                total_seconds -= 1

                try:
                    if new_text != countdown_message.text:
                        await countdown_message.edit(new_text)
                except MessageNotModifiedError:
                    pass
            
            await countdown_message.edit("⏳ **الوقت انتهى!**")
            # Optionally remove the countdown message after completion
            # await countdown_message.delete()

        # Start the timer task
        active_timers[event.chat_id] = asyncio.create_task(timer_task())
        
    except (ValueError, IndexError):
        await event.edit("⚠️ استخدم الصيغة الصحيحة: time (عدد الدقائق)")

@client.on(events.NewMessage(from_users='me', pattern='.stop'))
async def stop_timers(event):
    if event.chat_id in active_timers:
        # Cancel the active timer
        active_timers[event.chat_id].cancel()
        del active_timers[event.chat_id]
        
        # Delete the countdown message if it exists
        if event.chat_id in countdown_messages:
            try:
                await client.delete_messages(event.chat_id, countdown_messages[event.chat_id])
                del countdown_messages[event.chat_id]
            except Exception as e:
                print(f"Error deleting countdown message: {e}")

        # Send the confirmation message
        stop_message = await event.edit("✅ تم إيقاف جميع العدادات التنازلية.")
        
        # Wait 3 seconds before deleting the message
        await asyncio.sleep(3)
        await stop_message.delete()
    else:
        # Send the no active timer message
        no_timer_message = await event.edit("❌ لا توجد عدادات تنازلية نشطة لإيقافها.")
        
        # Wait 3 seconds before deleting the message
        await asyncio.sleep(3)
        await no_timer_message.delete()

@client.on(events.NewMessage(from_users='me', pattern='.الاوامر'))
async def show_commands(event):
    commands_text = (
    '''**❁─────────────❁

`.م1` • أوامـر الخـاص  
`.م2` • أوامـر الوقتـي  
`.م3` • أوامـر الانتحـال والتقليـد  
`.م4` • أوامـر التسليـة  
`.م5` • أوامـر التسليـة 2  
`.م6` • أوامـر التسليـة 3  
`.م7` • أوامـر الزخـرفة والتمبـلر  
`.م8` • أوامـر الألعـاب الجمـاعية  
`.م9` • أوامـر الكـروبات  
`.م10` • أوامـر النشـر التلقـائي  
`.م11` • أوامـر الصيـــد والتشـــكير  
`.م12` • أوامـر الـنطق والتحويل  
`.م13` • أوامـر الاشتراك الاجباري  
`.م14` • أوامـر العاب وعد  
`.م15` • أوامـر المراقبة  
`.م16` • أوامـر الذاتـيه والتقــليد  
`.م17` • أوامـر الردود  
`.م18` • أوامـر الــحساب  
`.م19` • أوامـر الـخطوط  
`.م20` • أوامـر العملات والتحـويل  
`.م21` • أوامـر التـــفليش  
`.م22` • أوامـر الذكاء الاصــــطناعي  
`.م23` • أوامـر التحـــميل واليوتيوب  
`.م24` • أوامـر الميــوزك والاتصال  
`.م25` • أوامـر المــــغادره
`.م26` • أوامـر الاذاعـه
`.م27` • أوامـر الافتارات والترفيه

❁─────────────❁
[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14**'''
    )
    await event.edit(commands_text)
import asyncio
import random
from telethon import TelegramClient, events
from telethon.tl.types import InputMessagesFilterVideo, InputMessagesFilterVoice, InputMessagesFilterPhotos

# افترض أن لديك client معرف مسبقاً
# client = TelegramClient('session_name', api_id, api_hash)

async def edit_or_reply(event, text):
    try:
        return await event.respond(text)
    except:
        return None

@client.on(events.NewMessage(pattern=".حالات$"))
async def wa_status(event):
    zzevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل حـالات واتـس ...**")
    try:
        msgs = [msg async for msg in client.iter_messages("@RSHDO5", filter=InputMessagesFilterVideo)]
        await client.send_file(event.chat_id, file=random.choice(msgs), caption="**🎆┊حـالات واتـس قصيـرة 🧸♥️**")
        await zzevent.delete()
    except:
        await zzevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")

@client.on(events.NewMessage(pattern=".ستوري انمي$"))
async def anime_story(event):
    zzevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل الستـوري ...**")
    try:
        msgs = [msg async for msg in client.iter_messages("@AA_Zll", filter=InputMessagesFilterVideo)]
        await client.send_file(event.chat_id, file=random.choice(msgs), caption="**🎆┊ستـوريات آنمـي قصيـرة 🖤🧧**")
        await zzevent.delete()
    except:
        await zzevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")

@client.on(events.NewMessage(pattern=".رقيه$"))
async def ruqya(event):
    zzevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل الرقيـه ...**")
    try:
        msgs = [msg async for msg in client.iter_messages("@Rqy_1", filter=InputMessagesFilterVoice)]
        await client.send_file(event.chat_id, file=random.choice(msgs), caption="**◞مقاطـع رقيـه شرعيـة ➧🕋🌸◟**")
        await zzevent.delete()
    except:
        await zzevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")

@client.on(events.NewMessage(pattern=".رمادي$"))
async def gray_avatar(event):
    zzevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل الافتـار ...**")
    try:
        msgs = [msg async for msg in client.iter_messages("@shababbbbR", filter=InputMessagesFilterPhotos)]
        await client.send_file(event.chat_id, file=random.choice(msgs), caption="**◞افتـارات شبـاب ࢪمـاديه ➧🎆🖤◟**")
        await zzevent.delete()
    except:
        await zzevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")

@client.on(events.NewMessage(pattern=".رماديه$"))
async def gray_girls(event):
    zzevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل الافتـار ...**")
    try:
        msgs = [msg async for msg in client.iter_messages("@banatttR", filter=InputMessagesFilterPhotos)]
        await client.send_file(event.chat_id, file=random.choice(msgs), caption="**◞افتـارات بنـات ࢪمـاديه ➧🎆🤎◟**")
        await zzevent.delete()
    except:
        await zzevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")

@client.on(events.NewMessage(pattern=".بيست$"))
async def best(event):
    zzevent = await edit_or_reply(event, "**╮ - جـارِ تحميـل الآفتـار ...🧚🏻‍♀🧚🏻‍♀╰**")
    try:
        msgs = [msg async for msg in client.iter_messages("@Tatkkkkkim", filter=InputMessagesFilterPhotos)]
        await client.send_file(event.chat_id, file=random.choice(msgs), caption="**◞افتـارات بيست تطقيـم بنـات ➧🎆🧚🏻‍♀🧚🏻‍♀◟**")
        await zzevent.delete()
    except:
        await zzevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")

@client.on(events.NewMessage(pattern=".حب$"))
async def love(event):
    zzevent = await edit_or_reply(event, "**╮ - جـارِ تحميـل الآفتـار ...♥️╰**")
    try:
        msgs = [msg async for msg in client.iter_messages("@tatkkkkkimh", filter=InputMessagesFilterPhotos)]
        await client.send_file(event.chat_id, file=random.choice(msgs), caption="**◞افتـارات حـب تمبلـرࢪ ➧🎆♥️◟**")
        await zzevent.delete()
    except:
        await zzevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")

@client.on(events.NewMessage(pattern=".رياكشن$"))
async def reaction(event):
    zzevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل الرياكشـن ...**")
    try:
        msgs = [msg async for msg in client.iter_messages("@reagshn", filter=InputMessagesFilterVideo)]
        await client.send_file(event.chat_id, file=random.choice(msgs), caption="** 🎬┊رياكشـن تحشيـش ➧🎃😹◟**")
        await zzevent.delete()
    except:
        await zzevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")

@client.on(events.NewMessage(pattern=".ادت$"))
async def adt(event):
    zzevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل مقطـع ادت ...**")
    try:
        msgs = [msg async for msg in client.iter_messages("@snje1", filter=InputMessagesFilterVideo)]
        await client.send_file(event.chat_id, file=random.choice(msgs), caption="**🎬┊مقاطـع ايـدت منوعـه ➧ 🖤🎭◟**")
        await zzevent.delete()
    except:
        await zzevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")

@client.on(events.NewMessage(pattern=".غنيلي$"))
async def song(event):
    zzevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل الاغنيـه ...𓅫╰**")
    try:
        msgs = [msg async for msg in client.iter_messages("@TEAMSUL", filter=InputMessagesFilterVoice)]
        await client.send_file(event.chat_id, file=random.choice(msgs), caption="**✦┊تم اختياࢪ الاغنيـه لك 💞🎶**\nٴ▁ ▂ ▉ ▄ ▅ ▆ ▇ ▅ ▆ ▇ █ ▉ ▂ ▁")
        await zzevent.delete()
    except:
        await zzevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")

@client.on(events.NewMessage(pattern=".شعر$"))
async def poem(event):
    zzevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل الشعـر ...**")
    try:
        msgs = [msg async for msg in client.iter_messages("@L1BBBL", filter=InputMessagesFilterVoice)]
        await client.send_file(event.chat_id, file=random.choice(msgs), caption="**✦┊تم اختيـار مقطـع الشعـر هـذا لك**")
        await zzevent.delete()
    except:
        await zzevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")

@client.on(events.NewMessage(pattern=".ميمز$"))
async def memes(event):
    zzevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل الميمـز ...**")
    try:
        msgs = [msg async for msg in client.iter_messages("@MemzWaTaN", filter=InputMessagesFilterVoice)]
        await client.send_file(event.chat_id, file=random.choice(msgs), caption="**✦┊تم اختيـار مقطـع الميمـز هـذا لك**")
        await zzevent.delete()
    except:
        await zzevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")

@client.on(events.NewMessage(pattern=".ري اكشن$"))
async def reaction_photo(event):
    zzevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل الرياكشـن ...**")
    try:
        msgs = [msg async for msg in client.iter_messages("@gafffg", filter=InputMessagesFilterPhotos)]
        await client.send_file(event.chat_id, file=random.choice(msgs), caption="**🎆┊رياكشـن تحشيـش ➧🎃😹◟**")
        await zzevent.delete()
    except:
        await zzevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")

@client.on(events.NewMessage(pattern=".معلومه$"))
async def info(event):
    zzevent = await edit_or_reply(event, "**╮•⎚ جـارِ تحميـل صـورة ومعلومـة ...**")
    try:
        msgs = [msg async for msg in client.iter_messages("@A_l3l", filter=InputMessagesFilterPhotos)]
        await client.send_file(event.chat_id, file=random.choice(msgs), caption="**🎆┊صـورة ومعلومـة ➧ 🛤💡◟**")
        await zzevent.delete()
    except:
        await zzevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")

@client.on(events.NewMessage(pattern=".تويت$"))
async def tweet(event):
    zzevent = await edit_or_reply(event, "**╮•⎚ كـت تـويت بالصـور ...**")
    try:
        msgs = [msg async for msg in client.iter_messages("@twit_selva", filter=InputMessagesFilterPhotos)]
        await client.send_file(event.chat_id, file=random.choice(msgs), caption="**✦┊كـت تـويت بالصـور ➧⁉️🌉◟**")
        await zzevent.delete()
    except:
        await zzevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")

@client.on(events.NewMessage(pattern=".خيرني$"))
async def choose(event):
    zzevent = await edit_or_reply(event, "**╮•⎚ لـو خيـروك بالصـور ...**")
    try:
        msgs = [msg async for msg in client.iter_messages("@SourceSaidi", filter=InputMessagesFilterPhotos)]
        await client.send_file(event.chat_id, file=random.choice(msgs), caption="**✦┊لـو خيـروك  ➧⁉️🌉◟**")
        await zzevent.delete()
    except:
        await zzevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")

@client.on(events.NewMessage(pattern=".ولد انمي$"))
async def anime_boy(event):
    zzevent = await edit_or_reply(event, "**╮ - جـارِ تحميـل الآفتـار ...𓅫╰**")
    try:
        msgs = [msg async for msg in client.iter_messages("@dnndxn", filter=InputMessagesFilterPhotos)]
        await client.send_file(event.chat_id, file=random.choice(msgs), caption="**◞افتـارات آنمي شبـاب ➧🎆🙋🏻‍♂◟**")
        await zzevent.delete()
    except:
        await zzevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")

@client.on(events.NewMessage(pattern=".بنت انمي$"))
async def anime_girl(event):
    zzevent = await edit_or_reply(event, "**╮ - جـارِ تحميـل الآفتـار ...𓅫╰**")
    try:
        msgs = [msg async for msg in client.iter_messages("@shhdhn", filter=InputMessagesFilterPhotos)]
        await client.send_file(event.chat_id, file=random.choice(msgs), caption="**◞افتـارات آنمي بنـات ➧🎆🧚🏻‍♀◟**")
        await zzevent.delete()
    except:
        await zzevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")

@client.on(events.NewMessage(pattern=".بنات$"))
async def girls(event):
    zzevent = await edit_or_reply(event, "**╮ - جـارِ تحميـل الآفتـار ...𓅫╰**")
    try:
        msgs = [msg async for msg in client.iter_messages("@banaaaat1", filter=InputMessagesFilterPhotos)]
        await client.send_file(event.chat_id, file=random.choice(msgs), caption="**◞افتـارات بنـات تمبلـرࢪ ➧🎆🧚🏻‍♀◟**")
        await zzevent.delete()
    except:
        await zzevent.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")    
@client.on(events.NewMessage(pattern=".م27$"))
async def help_commands(event):
    text = """**╭─╌╌╌╌╌╌╌╌╌╌╌╌╮
│ • أوامر الافتارات:
│
│ `.حالات` ➤ تحميل حالات واتس قصيرة
│ `.ستوري انمي` ➤ ستوريات أنمي
│ `.رقيه` ➤ مقاطع رقية شرعية
│ `.رمادي` ➤ افتارات شباب رمادية
│ `.رماديه` ➤ افتارات بنات رمادية
│ `.بيست` ➤ افتارات بيست للبنات
│ `.حب` ➤ افتارات حب تمبلر
│ `.رياكشن` ➤ رياكشن تحشيش فيديو
│ `.ادت` ➤ مقاطع ادت متنوعة
│ `.غنيلي` ➤ اغاني صوتية
│ `.شعر` ➤ مقاطع شعرية
│ `.ميمز` ➤ مقاطع ميمز
│ `.ري اكشن` ➤ رياكشن تحشيش صور
│ `.معلومه` ➤ صورة مع معلومة
│ `.تويت` ➤ كَت تويت بالصور
│ `.خيرني` ➤ صور لو خيروك
│ `.ولد انمي` ➤ افتارات أنمي شباب
│ `.بنت انمي` ➤ افتارات أنمي بنات
│ `.بنات` ➤ افتارات بنات تمبلر
╰─╌╌╌╌╌╌╌╌╌╌╌╌╯**"""
    await event.edit(text)        
@client.on(events.NewMessage(pattern=r"^\.م26$"))
async def _(event):
    help_text = (
        "╭━─━─━─〔📢 أوامــر الإذاعــة〕─━─━─━╮\n\n"
        "1. ⌁ .للكل\n"
        "↳ **إرسال الرسالة لكل أعضاء المجموعة.**\n"
        "↳ (بالرد على الرسالة أو الوسائط)\n\n"
        "2. ⌁ .ايقاف للكل\n"
        "↳ **إيقاف عملية الإذاعة للأعضاء في المجموعة الحالية.**\n\n"
        "3. ⌁ .اذاعة اشخاص\n"
        "↳ **إرسال الرسالة لكل الأشخاص الموجودين في قائمتك الخاصة.**\n"
        "↳ (بالرد على الرسالة أو الوسائط)\n\n"
        "4. ⌁ .اضف اشخاص\n"
        "↳ **إضافة أشخاص إلى قائمة الإذاعة الخاصة.**\n"
        "↳ (بالرد على رسالة تحتوي يوزرات أو آي ديهات مفصولة بمسافات)\n\n"
        "💡 مثال على الإضافة:\n"
        ".اضف اشخاص (بالرد على رسالة مكتوب فيها @user1 @user2 12345678)\n\n"
        "✦ ملاحظات هامة:\n"
        "• بعد الإضافة يمكنك استخدام .اذاعة اشخاص للإرسال لهم في أي وقت.\n"
        "• أمر .ايقاف للكل فقط يوقف الإذاعة للمجموعة الحالية.\n\n"
 
"**[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14**"
    )
    await event.reply(help_text, link_preview=False)    
from telethon import TelegramClient, events
from telethon.errors import UserAdminInvalidError, UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest



spam_chats = []
people_list = []  

BEST_SOURCE_GROUP = "[ᯓ اذاعـة خـاص 🚹](t.me/Tepthon) .\n\n**- جـارِ الاذاعـه خـاص لـ أعضـاء الكـروب 🛗\n- الرجـاء الانتظـار .. لحظـات ⏳**"
BEST_SOURCE_PEOPLE = "[ᯓ اذاعـة أشخاص 🕊](t.me/Tepthon) .\n\n**- جـارِ الاذاعـه لـ قائمـة الأشخاص 📜\n- الرجـاء الانتظـار .. لحظـات ⏳**"
NO_PEOPLE_MSG = "[ᯓ اذاعـة أشخاص 🕊](t.me/Tepthon) .\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n**⎉╎قائمـة الأشخاص فـارغـه ❌**\n**⎉╎أضف أشخاص بالأمر `.اضف اشخاص`**"

# ================= إذاعة للكل =================
@client.on(events.NewMessage(pattern=r"^\.للكل$"))
async def _(event):
    if not event.is_group:
        return await event.reply("**⎉╎هذا الأمر يشتغل في المجموعات فقط**")

    if not event.is_reply:
        return await event.reply("**⎉╎بالـࢪد ؏ــلى ࢪســالة أو وسـائـط**")

    try:
        await client(GetParticipantRequest(event.chat_id, event.sender_id))
    except UserNotParticipantError:
        return await event.reply("**⎉╎يجب أن تكون عضو في المجموعة**")

    chat_id = event.chat_id
    spam_chats.append(chat_id)
    msg = await event.reply(BEST_SOURCE_GROUP, link_preview=False)

    target_msg = await event.get_reply_message()
    success = 0

    async for usr in client.iter_participants(chat_id):
        if chat_id not in spam_chats:
            break
        try:
            if target_msg.media:
                await client.send_file(usr.id, target_msg.media, caption=target_msg.text)
            else:
                await client.send_message(usr.id, target_msg.text)
            success += 1
        except:
            pass

    await msg.edit(f"**⎉╎تمت الاذاعـه لـ {success} عضـو ✅**", link_preview=False)
    spam_chats.remove(chat_id)

# إيقاف الإذاعة للكل
@client.on(events.NewMessage(pattern=r"^\.ايقاف للكل$"))
async def _(event):
    if event.chat_id in spam_chats:
        spam_chats.remove(event.chat_id)
        await event.reply("**⎉╎تم إيقـافـ عمليـة الاذاعـه .. بنجـاح✓**")
    else:
        await event.reply("**⎉╎لا توجد عملية إذاعة حالياً**")

# ================= إذاعة أشخاص =================
@client.on(events.NewMessage(pattern=r"^\.اذاعة اشخاص$"))
async def _(event):
    if not event.is_reply:
        return await event.reply("**⎉╎بالـࢪد ؏ــلى ࢪســالة أو وسـائـط**")

    if not people_list:
        return await event.reply(NO_PEOPLE_MSG, link_preview=False)

    msg = await event.reply(BEST_SOURCE_PEOPLE, link_preview=False)
    target_msg = await event.get_reply_message()
    success = 0

    for user in people_list:
        try:
            if target_msg.media:
                await client.send_file(user, target_msg.media, caption=target_msg.text)
            else:
                await client.send_message(user, target_msg.text)
            success += 1
        except:
            pass

    await msg.edit(f"**⎉╎تمت الاذاعـه لـ {success} أشخاص ✅**", link_preview=False)


@client.on(events.NewMessage(pattern=r"^\.اضف اشخاص$"))
async def _(event):
    if not event.is_reply:
        return await event.reply("**⎉╎بالـࢪد على رسالة فيها اليوزرات أو الآي ديهات**")

    reply = await event.get_reply_message()
    users = reply.text.split()
    people_list.extend(users)
    await event.reply(f"**⎉╎تم إضافة {len(users)} شخص ✅**")

@client.on(events.NewMessage(from_users='me', pattern='.name'))
async def set_account_name(event):
    global account_name
    try:
        # Extract the new account name from the message
        command, new_name = event.raw_text.split(' ', 1)
        account_name = new_name.split('(', 1)[1].split(')')[0].strip()
        
        # Update the account name immediately
        iraq_tz = pytz.timezone('Asia/Baghdad')
        now = datetime.datetime.now(iraq_tz)
        current_time = superscript_time(now.strftime("%I:%M"))
        new_username = f"{account_name} - {current_time}"
        
        try:
            await client(UpdateProfileRequest(first_name=new_username))
            await event.edit(f"✅ تم تغيير اسم الحساب إلى {new_username}")
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
            await client(UpdateProfileRequest(first_name=new_username))
            await event.edit(f"✅ تم تغيير اسم الحساب إلى {new_username}")
        except Exception as e:
            await event.edit(f"⚠️ حدث خطأ أثناء تغيير الاسم: {e}")
    except ValueError:
        await event.edit("⚠️ استخدم الصيغة: name (الاسم الجديد)")

@client.on(events.NewMessage(from_users='me', pattern='.مسح'))
async def delete_messages(event):
    try:
        
        command, num_str = event.raw_text.split(' ', 1)
        num_messages = int(num_str.strip('()'))
        
        if num_messages <= 0:
            await event.edit("⚠️ يجب أن يكون عدد الرسائل المراد حذفها أكبر من صفر.")
            return
        
        
        messages = await client.get_messages(event.chat_id, limit=num_messages)
        message_ids = [msg.id for msg in messages]
        
        if message_ids:
            await client(DeleteMessagesRequest(id=message_ids))
            confirmation_message = await event.edit(f"✅ تم مسح {num_messages} رسالة.")
            
            
            await asyncio.sleep(2)
            await client(DeleteMessagesRequest(id=[confirmation_message.id]))
        else:
            await event.edit("⚠️ لم يتم العثور على رسائل للحذف.")
    except (ValueError, IndexError):
        await event.edit("⚠️ استخدم الصيغة: مسح (عدد الرسائل)")
    except Exception as e:
        await event.edit(f"⚠️ حدث خطأ أثناء حذف الرسائل: {e}")




@client.on(events.NewMessage(from_users='me', pattern='.حذف'))
async def delete_published_messages(event):
    try:
        if not published_messages:
            await event.edit("❌ لا توجد رسائل منشورة لحذفها.")
            return
        
        
        for entry in published_messages:
            for group_id, msg_id in entry['message_ids']:
                try:
                    await client(DeleteMessagesRequest(id=[msg_id], revoke=True))
                except Exception as e:
                    print(f"Error deleting message {msg_id} in group {group_id}: {e}")
        
        # Clear the published messages list
        published_messages.clear()
        with open(published_messages_file, 'wb') as f:
            pickle.dump(published_messages, f)
        
        await event.edit("✅ تم حذف جميع الرسائل المنشورة.")
    except Exception as e:
        await event.edit(f"⚠️ حدث خطأ أثناء حذف الرسائل المنشورة: {e}")


if os.path.exists(muted_users_file):
    with open(muted_users_file, 'rb') as f:
        muted_users = pickle.load(f)
else:
    muted_users = set()

# أوامر الكتم والسماح وعرض المكتومين
@client.on(events.NewMessage(from_users='me', pattern='.كتم'))
async def mute_user(event):
    if event.is_private:
        muted_users.add(event.chat_id)
        with open(muted_users_file, 'wb') as f:
            pickle.dump(muted_users, f)
        await event.edit("✅ **تم كتم المستخدم**")
    else:
        await event.edit("⚠️ يمكن استخدام هذا الأمر في المحادثات الخاصة فقط.")



@client.on(events.NewMessage(from_users='me', pattern='.عرض_المكتومين'))
async def show_muted_users(event):
    if muted_users:
        muted_users_list = "\n".join([str(user_id) for user_id in muted_users])
        await event.edit(f"📋 المستخدمون المكتومون:\n{muted_users_list}")
    else:
        await event.edit("❌ لا يوجد مستخدمون مكتومون حالياً.")


@client.on(events.NewMessage(incoming=True))
async def delete_muted_user_messages(event):
    if event.is_private and event.chat_id in muted_users:
        await client.delete_messages(event.chat_id, [event.id])

@client.on(events.NewMessage(from_users='me', pattern='.الرسائل'))
async def show_published_messages(event):
    if not published_messages:
        await event.edit("❌ لا توجد رسائل منشورة.")
        return
    
    response_text = "📋 الرسائل المنشورة:\n"
    for i, entry in enumerate(published_messages, 1):
        response_text += f"🔹 الرسالة {i}: {entry['message']}\n"
        response_text += f"🔸 عدد المجموعات: {len(entry['group_ids'])}\n\n"
    
    await event.edit(response_text)

from telethon import TelegramClient, events



from telethon import TelegramClient, events



private_protection_enabled = True
custom_reply_message = None

# تفعيل الحماية
from telethon import events

private_protection_enabled = True
custom_reply_message = None
replied_users = set()  # لتجنب تكرار الرد على نفس الشخص

# تفعيل الحماية
@client.on(events.NewMessage(pattern=".تفعيل حماية الخاص"))
async def enable_protection(event):
    global private_protection_enabled
    private_protection_enabled = True
    await event.edit("**✅ تم تفعيل حماية الخاص.**")

# تعطيل الحماية
@client.on(events.NewMessage(pattern=".تعطيل حماية الخاص"))
async def disable_protection(event):
    global private_protection_enabled
    private_protection_enabled = False
    await event.edit("**❌ تم تعطيل حماية الخاص.**")

# تعيين الرد التلقائي
@client.on(events.NewMessage(pattern=".تعيين كليشة خاص"))
async def set_custom_reply(event):
    global custom_reply_message, replied_users
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        custom_reply_message = reply_msg
        replied_users.clear()  # حذف السجل لتفعيل الرد للجميع من جديد
        await event.edit("**✅ تم تعيين الرد التلقائي.**")
    else:
        await event.edit("**❗ لازم ترد على رسالة لتتعين.**")

# الرد التلقائي بدون تكرار
@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    global replied_users
    if not event.is_private:
        return

    

    if private_protection_enabled and custom_reply_message:
        if event.sender_id in replied_users:
            return  # تم الرد عليه مسبقاً

        try:
            if custom_reply_message.media:  # إذا تحتوي ميديا (صورة، فيديو، ...)
                await client.send_file(
                    event.chat_id,
                    file=custom_reply_message.media,
                    caption=custom_reply_message.text or ""
                )
            else:  # إذا فقط نص
                await client.send_message(
                    event.chat_id,
                    message=custom_reply_message.text or ""
                )

            replied_users.add(event.sender_id)  # سجل الرد
        except Exception as e:
            print(1)
            print("خطأ:", e)








    
        
    


from telethon import events
from telethon import TelegramClient, events
import os
import datetime



# جدول الأيام
Aljoker_Asbo3 = {
    'Monday': 'الاثنين',
    'Tuesday': 'الثلاثاء',
    'Wednesday': 'الأربعاء',
    'Thursday': 'الخميس',
    'Friday': 'الجمعة',
    'Saturday': 'السبت',
    'Sunday': 'الأحد'
}

# متغيرات عامة بديلة
gvars = {}

def addgvar(key, value):
    gvars[key] = value

def delgvar(key):
    if key in gvars:
        del gvars[key]

def gvarstatus(key):
    return key in gvars

# أوامر حفظ الصور
@client.on(events.NewMessage(pattern="(?i)^(.جلب الصورة|.جلب الصوره|.ذاتيه|.ذاتية)$"))
async def dato(event):
    if not event.is_reply:
        return await event.edit("⛔ يجب الرد على رسالة تحتوي على صورة أو فيديو!")

    reply = await event.get_reply_message()

    if not reply.media:
        return await event.edit("⛔ الرسالة التي رددت عليها لا تحتوي على وسائط!")

    pic = await reply.download_media()

    if not pic:
        return await event.edit("⚠️ فشل تحميل الوسائط، حاول مرة أخرى.")

    await client.send_file(
        "me",
        pic,
        caption="""
  تم حـــفض الذاتيه بنجاح
 [𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14
"""
    )
    await event.delete()

@client.on(events.NewMessage(pattern="(?i)^(.الذاتية تشغيل|.ذاتية تشغيل)$"))
async def reda(event):
    if gvarstatus("savepicforme"):
        return await event.edit("**᯽︙حفظ الذاتيات مفعل وليس بحاجة للتفعيل مجدداً **")
    else:
        addgvar("savepicforme", "reda")
        await event.edit("**᯽︙تم تفعيل ميزة حفظ الذاتيات بنجاح ✓**")

@client.on(events.NewMessage(pattern="(?i)^(.الذاتية تعطيل|.ذاتية تعطيل)$"))
async def reda_off(event):
    if gvarstatus("savepicforme"):
        delgvar("savepicforme")
        return await event.edit("**᯽︙تم تعطيل حفظ الذاتيات بنجاح ✓**")
    else:
        await event.edit("**᯽︙انت لم تفعل حفظ الذاتيات لتعطيلها!**")

def joker_unread_media(message):
    return message.media_unread and (message.photo or message.video)

async def save_to_me(event, caption):
    media = await event.download_media()
    sender = await event.get_sender()
    sender_id = event.sender_id
    date_str = event.date.strftime("%Y-%m-%d")
    day_name = Aljoker_Asbo3[event.date.strftime("%A")]
    await client.send_file(
        "me",
        media,
        caption=caption.format(sender.first_name, sender_id, date_str, day_name),
        parse_mode="markdown"
    )
    os.remove(media)

@client.on(events.NewMessage(func=lambda e: e.is_private and joker_unread_media(e)))
async def auto_save(event):
    if gvarstatus("savepicforme") and event.sender_id != (await client.get_me()).id:
        caption = """**
 تم حـــفض الذاتيه بنجاح
 [𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14
        **"""
        await save_to_me(event, caption)



from telethon import events
from telethon.tl.functions.channels import CreateChannelRequest, EditPhotoRequest
from telethon.tl.types import InputChatUploadedPhoto
import os

storage_title = "مجمـوعـة التخـزيـن"
storage_photo = "mortada.jpg"
storage_entity = None

# إنشاء مجموعة التخزين
async def create_storage_group(client):
    global storage_entity
    try:
        result = await client(CreateChannelRequest(
            title=storage_title,
            about="مجموعة مخصصة لتخزين الرسائل والتاكات تلقائيًا",
            megagroup=True
        ))
        storage_entity = result.chats[0]
        print("✅ تم إنشاء مجموعة التخزين:", storage_entity.title)

        if os.path.exists(storage_photo):
            file = await client.upload_file(storage_photo)
            await client(EditPhotoRequest(
                channel=storage_entity,
                photo=InputChatUploadedPhoto(file)
            ))
        else:
            print("⚠️ لم يتم العثور على صورة التخزين.")
    except Exception as e:
        print("❌ خطأ أثناء إنشاء مجموعة التخزين:", e)

# تخزين الرسائل الخاصة فقط
@client.on(events.NewMessage(incoming=True))
async def auto_store(event):
    global storage_entity
    if event.out:
        return

   
    if not event.is_private:
        return

    if storage_entity is None:
        dialogs = await client.get_dialogs()
        for dialog in dialogs:
            if dialog.is_group and dialog.name == storage_title:
                storage_entity = dialog.entity
                break
        if storage_entity is None:
            await create_storage_group(client)

    if storage_entity is None:
        return

    try:
        sender = await event.get_sender()
        base_msg = f"**📮┊المـرسـل :** [{sender.first_name}](tg://user?id={sender.id})\n"
        base_msg += f"**🎟┊الايـدي :** `{sender.id}`\n"

        # نصوص
        if event.raw_text:
            msg = base_msg + f"**✉️┊الرسالة :**\n{event.raw_text}"
            await client.send_message(storage_entity, msg, link_preview=False)

        # بصمات صوتية
        if event.media and getattr(event.media, 'voice', None):
            await client.send_file(storage_entity, event.media, caption=base_msg + "**🎵┊بصمة صوتية**")

        # صور
        if event.media and getattr(event.media, 'photo', None):
            await client.send_file(storage_entity, event.media, caption=base_msg + "**🖼┊صورة**")

        # فيديو
        if event.media and getattr(event.media, 'video', None):
            await client.send_file(storage_entity, event.media, caption=base_msg + "**🎬┊فيديو**")

        # مستندات/ملفات
        if event.media and getattr(event.media, 'document', None):
            await client.send_file(storage_entity, event.media, caption=base_msg + "**[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14**")

    except Exception as e:
        print("❌ خطأ أثناء التخزين:", e)
@client.on(events.NewMessage(pattern='^.ايدي$'))
async def send_id(event):
    if event.is_reply:
        user = await event.get_reply_message()
        user = await event.client.get_entity(user.sender_id)
    else:
        user = await event.get_sender()
    
    full_name = (user.first_name or '') + (' ' + user.last_name if user.last_name else '')
    username = user.username or 'لا يوجد'
    user_id = user.id
    
    photos = await client.get_profile_photos(user)
    if photos.total > 0:
        photo = photos[0]
        await event.edit(file=photo, message=f"""
 • الاسم الكامل ↯  {full_name}
• اليوزر ↯ @{username}
• الايدي ↯  {user_id}
""")
    else:
        await event.edit(f"""
 • الاسم الكامل ↯  {full_name}
• اليوزر ↯ @{username}
• الايدي ↯  {user_id}
*لا يوجد صورة بروفايل*
""")
from telethon import events
from telethon.utils import get_display_name
import random

# قائمة الهمسات العشوائية
rehu = [
    "شكم مره كتلك خلي نفلش الكروب",
    "باع هذا اللوكي شديسوي",
    "** مالك الكروب واحد زباله ويدور بنات **",
    "**اول مره اشوف بنات يدورن ولد 😂 **",
    "**شوف هذا الكرنج دين مضال براسه**",
    "**انته واحد فرخ وتنيج**",
    "** راح اعترفلك بشي طلعت احب اختك 🥺 **",
    "**مالك الكروب والمشرفين وفرده من قندرتك ضلعي**",
    "**هذا واحد غثيث وكلب ابن كلب**",
    "**لتحجي كدامه هذا نغل يوصل حجي**",
    "**هذا المالك واحد ساقط وقرام ويدور حلوين**",
    "**لو ربك يجي ماتنكشف الهمسه 😂😂**",
]

from telethon import events

def get_user_name(user):
    return user.first_name.replace("\u2060", "") if user.first_name else user.username

def is_dev(user_id):
    dev_ids = [7937540559,1832005923,2110304954]
    return user_id in dev_ids

@client.on(events.NewMessage(pattern=r"^\.رفع(?:\s+)([\s\S]+)"))
async def raise_anything(event):
    user, _ = await get_user_from_event(event)
    if not user:
        return

    if is_dev(user.id):
        await edit_or_reply(event, "**- لكك دي هذا المطور**")
        return

    me = await event.client.get_me()
    mention = f"[{me.first_name}](tg://user?id={me.id})"
    name = get_user_name(user)
    custom_text = event.pattern_match.group(1).strip()  # هذا أي شيء بعد .رفع

    await edit_or_reply(event,
        f"**᯽︙ المستخدم [{name}](tg://user?id={user.id})\n**"
        f"**᯽︙ تم رفعه {custom_text} ✅\n**"
        f"**᯽︙بواسطة : {mention} 🤵**‍"
    )


@client.on(events.NewMessage(pattern=r"^\.همس(?:\s|$)([\s\S]*)"))
async def random_whisper(event):
    msg = random.choice(rehu)
    await event.edit(msg)


async def get_user_from_event(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        user = await event.client.get_entity(reply.sender_id)
        return user, None
    args = event.text.split()
    if len(args) > 1:
        user = await event.client.get_entity(args[1])
        return user, None
    return None, None

# دالة مساعدة للرد أو تعديل الرسالة
async def edit_or_reply(event, text):
    if event.is_reply:
        await event.edit(text)
    else:
        await event.edit(text)
        from telethon import events
import random

roz = ["10%", "20%", "35%", "50%", "65%", "70%", "75%", "80%", "90%", "99%"]
rr7 = ["15%", "30%", "45%", "55%", "60%", "72%", "84%", "93%", "100%"]

DEV_ID = 7937540559,2110304954  # آيدي المطور

def is_dev(user_id):
    return user_id == DEV_ID

def get_name(user):
    return user.first_name or user.username or "مجهول"

def get_rate():
    return random.choice(rr7)

# الحب
@client.on(events.NewMessage(pattern=".نسبة الحب(?:\s|$)([\s\S]*)"))
async def love_rate(event):
    reply = await event.get_reply_message()
    if not reply or not reply.sender:
        return await event.edit("رد على شخص حتى احسب النسبة ❤️")
    user = reply.sender
    if is_dev(user.id):
        return await event.edit("ما اكدر احسب نسبه الحب مع المطور 😒💔")
    name = get_name(user)
    rate = random.choice(roz)
    await event.edit(f"💘 نسبة الحب بينك وبين [{name}](tg://user?id={user.id}) هي {rate} 😔🖤")

# الانوثة
@client.on(events.NewMessage(pattern=".نسبة الانوثة(?:\s|$)([\s\S]*)"))
async def female_rate(event):
    reply = await event.get_reply_message()
    if not reply or not reply.sender:
        return await event.edit("رد على شخص حتى احسب نسبة الأنوثة 🩷")
    user = reply.sender
    if is_dev(user.id):
        return await event.edit("هذا المطور حيوان")
    name = get_name(user)
    rate = get_rate()
    await event.edit(f"🍓 نسبة الأنوثة عند [{name}](tg://user?id={user.id}) هي {rate} 🌸")

# الرجولة
@client.on(events.NewMessage(pattern=".نسبة الرجولة(?:\s|$)([\s\S]*)"))
async def male_rate(event):
    reply = await event.get_reply_message()
    if not reply or not reply.sender:
        return await event.edit("رد على شخص حتى احسب نسبة الرجولة 🧔")
    user = reply.sender
    if is_dev(user.id):
        return await event.edit("مطوري هو تعريف الرجولة 🔥")
    name = get_name(user)
    rate = get_rate()
    await event.edit(f"🧔‍♂️ نسبة الرجولة عند [{name}](tg://user?id={user.id}) هي {rate} 💪")

# النيج
@client.on(events.NewMessage(pattern=".نسبة النيج(?:\s|$)([\s\S]*)"))
async def sex_rate(event):
    reply = await event.get_reply_message()
    if not reply or not reply.sender:
        return await event.edit("رد على شخص حتى احسب نسبة النيج 😏")
    user = reply.sender
    if is_dev(user.id):
        return await event.edit("دي لكك هاذ المطور")
    name = get_name(user)
    rate = get_rate()
    await event.edit(f"🔥 نسبة النيج عند [{name}](tg://user?id={user.id}) هي {rate} 😈")

# الجداوة
@client.on(events.NewMessage(pattern=".نسبة الجداوه(?:\s|$)([\s\S]*)"))
async def coolness_rate(event):
    reply = await event.get_reply_message()
    if not reply or not reply.sender:
        return await event.edit("رد على شخص حتى احسب الجداوة 😎")
    user = reply.sender
    if is_dev(user.id):
        return await event.edit("دي لكك هاذ المطور")
    name = get_name(user)
    rate = get_rate()
    await event.edit(f"😎 نسبة الجداوة عند [{name}](tg://user?id={user.id}) هي {rate} 🔥")

# الكحاب البي
@client.on(events.NewMessage(pattern=".نسبة الكحاب البي(?:\s|$)([\s\S]*)"))
async def khabah_rate(event):
    reply = await event.get_reply_message()
    if not reply or not reply.sender:
        return await event.edit("رد على شخص حتى احسب نسبة الكحاب البي 😂")
    user = reply.sender
    if is_dev(user.id):
        return await event.edit("دي لكك هاذ المطور")
    name = get_name(user)
    rate = get_rate()
    await event.edit(f"💃 نسبة الكحاب البي عند [{name}](tg://user?id={user.id}) هي {rate} 🤣")

# الثول
@client.on(events.NewMessage(pattern=".نسبة الثول(?:\s|$)([\s\S]*)"))
async def fool_rate(event):
    reply = await event.get_reply_message()
    if not reply or not reply.sender:
        return await event.edit("رد على شخص حتى احسب نسبة الثول 🤪")
    user = reply.sender
    if is_dev(user.id):
        return await event.edit("دي لكك هاذ المطور")
    name = get_name(user)
    rate = get_rate()
    await event.edit(f"🤡 نسبة الثول عند [{name}](tg://user?id={user.id}) هي {rate} 😂")

# الغباء
@client.on(events.NewMessage(pattern=".نسبة الغباء(?:\s|$)([\s\S]*)"))
async def stupid_rate(event):
    reply = await event.get_reply_message()
    if not reply or not reply.sender:
        return await event.edit("رد على شخص حتى احسب نسبة الغباء 🧠❌")
    user = reply.sender
    if is_dev(user.id):
        return await event.edit("مطوري ذكي ويكسر المعايير 👑")
    name = get_name(user)
    rate = get_rate()
    await event.edit(f"🙃 نسبة الغباء عند [{name}](tg://user?id={user.id}) هي {rate} 🤓")

# نسبة القباحة (إضافة مني 😆)
@client.on(events.NewMessage(pattern=".نسبة القباحة(?:\s|$)([\s\S]*)"))
async def ugly_rate(event):
    reply = await event.get_reply_message()
    if not reply or not reply.sender:
        return await event.edit("رد على شخص حتى احسب القباحة 🤢")
    user = reply.sender
    if is_dev(user.id):
        return await event.edit("دي لكك هاذ المطور")
    name = get_name(user)
    rate = get_rate()
    await event.edit(f"👹 نسبة القباحة عند [{name}](tg://user?id={user.id}) هي {rate} 💩")

# نسبة الكياتة (إضافة لطيفة)
@client.on(events.NewMessage(pattern=".نسبة الكياتة(?:\s|$)([\s\S]*)"))
async def cuteness_rate(event):
    reply = await event.get_reply_message()
    if not reply or not reply.sender:
        return await event.edit("رد على شخص حتى احسب الكياتة 🥺")
    user = reply.sender
    if is_dev(user.id):
        return await event.edit("دي لكك هاذ المطور")
    name = get_name(user)
    rate = get_rate()
    await event.edit(f"🧸 نسبة الكياتة عند [{name}](tg://user?id={user.id}) هي {rate} 🌈")
    

import asyncio
from telethon import events
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.messages import CreateChatRequest

# تخزين الكروبات المنشأة
created_groups = []

@client.on(events.NewMessage(pattern=r'^\.م9$'))
async def show_group_options(event):
    text = (
        "**❁ ───────────── ❁\n**"
        "✧ أهلاً بك في قسم إنشاء الكروبات ✧\n\n"
        "• استخدم أحد الأوامر التالية:\n\n"
        "⌯ `.انشاء_50` ← بدء إنشاء 50 كروب (الحد اليومي)\n"
        "⌯ `.انشاء_عدد` ← لإنشاء عدد مخصص من الكروبات (لا يتجاوز 50)\n\n"
        "✦ [𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14\n"
        "❁ ───────────── ❁"
    )
    await event.edit(text)

@client.on(events.NewMessage(pattern=r'^\.انشاء_50$'))
async def create_50_groups(event):
    if len(created_groups) >= 50:
        await event.edit("🚫 لقد وصلت إلى الحد اليومي (50 كروب).")
        return
#DEV – MORTADA
    await event.edit("🔄 جاري إنشاء 50 كروب...\nيرجى الانتظار...")

    for i in range(len(created_groups)+1, 51):
        try:
            title = f"CHAT–MORTADA {i}"
            result = await client(CreateChannelRequest(
                title=title,
                about='تم الإنشاء تلقائيًا بواسطة البوت',
                megagroup=True
            ))
            chat = result.chats[0]
            created_groups.append(chat.id)

            # ✅ مغادرة الكروب بعد الإنشاء مباشرة
            await asyncio.sleep(1)
            await client(LeaveChannelRequest(channel=chat.id))

        except Exception as e:
            await event.edit(f"❌ خطأ: {e}")
            break

    await event.edit("✅ تم الانتهاء من إنشاء 50 كروب.")

@client.on(events.NewMessage(pattern=r'^\.انشاء_عدد$'))
async def ask_for_number(event):
    await event.edit("✦ أرسل الآن عدد الكروبات الذي تريد إنشاؤه (من 1 إلى 50):")

    @client.on(events.NewMessage(from_users=event.sender_id))
    async def get_custom_count(msg):
        try:
            count = int(msg.text.strip())
            if count < 1 or count > 50:
                await msg.reply("🚫 أرسل عدد بين 1 و50 فقط.")
                return

            if len(created_groups) + count > 50:
                await msg.reply(f"🚫 لا يمكن إنشاء {count} كروب. الحد الأقصى هو 50 كروب باليوم.")
                return

            await msg.reply(f"🔄 جاري إنشاء {count} كروب...\nيرجى الانتظار...")

            for i in range(len(created_groups)+1, len(created_groups)+1+count):
                try:
                    title = f"CHAT–MORTADA {i}"
                    result = await client(CreateChannelRequest(
                        title=title,
                        about='تم الإنشاء تلقائيًا بواسطة البوت',
                        megagroup=True
                    ))
                    chat = result.chats[0]
                    created_groups.append(chat.id)

                    
                    await client(LeaveChannelRequest(channel=chat.id))

                except Exception as e:
                    await msg.reply(f"❌ خطأ: {e}")
                    break

            await msg.reply(f"✅ تم إنشاء {count} كروب بنجاح.")
            client.remove_event_handler(get_custom_count)

        except ValueError:
            await msg.reply("🚫 أرسل رقم فقط.")
            import asyncio
import random
from telethon import events
from telethon.tl.functions.users import GetFullUserRequest


@client.on(events.NewMessage(pattern=".تهكير$"))
async def hack1(event):
    reply_message = await event.get_reply_message()
    if reply_message:
        sender = reply_message.sender
        full = await client(GetFullUserRequest(sender.id))
        username = getattr(sender, "username", None)
        if username:
            username_link = f"@{username}"
        else:
            username_link = f"tg://user?id={sender.id}"
        display_name = '*اضــــغــط هـــــنــا*'
        ALIVE_NAME = f"[{display_name}]({username_link})"

        if reply_message.sender_id == 7937540559:
            await event.edit("**᯽︙ عـذرا لا استـطيع اخـتراق مـطوري اعـتذر او سيقـوم بتهـكيرك**")
        else:
            await event.edit("يتـم الاختـراق ..")
            animation_chars = [
                "᯽︙ تـم الربـط بسـيرفرات الـتهكير الخـاصة",
                "تـم تحـديد الضحـية",
                "**تهكيـر**... 0%\n▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ",
                "**تهكيـر**... 4%\n█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ",
                "**تهكيـر**... 8%\n██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ",
                "**تهكيـر**... 20%\n█████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ",
                "**تهكيـر**... 36%\n█████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ",
                "**تهكيـر**... 52%\n█████████████▒▒▒▒▒▒▒▒▒▒▒▒ ",
                "**تهكيـر**... 84%\n█████████████████████▒▒▒▒ ",
                "**تهكيـر**... 100%\n████████████████████████ ",
                f"᯽︙ ** تـم اخـتراق الضـحية**..\n\nقـم بالـدفع الى {ALIVE_NAME} لعـدم نشـر معلوماتك وصـورك",
            ]
            for char in animation_chars:
                await asyncio.sleep(3)
                await event.edit(char)
    else:
        await event.edit("᯽︙ يرجى الرد على رسالة الشخص أولاً")

from telethon import events
import asyncio
import random


@client.on(events.NewMessage(pattern=".تهكير 2$"))
async def hack2(event):
    await event.edit("**جارِ الاختراق الضحية..**")

    animation1 = [
        "**جار تحديد الضحية...**",
        "**تم تحديد الضحية بنجاح ✓**",
        "`يتم الاختراق... 0%`",
        "`يتم الاختراق... 4%`",
        "`يتم الاختراق... 8%`",    
        "`يتم الاختراق... 20%`",
        "`يتم الاختراق... 36%`",
        "`يتم الاختراق... 52%`",
        "`يتم الاختراق... 84%`",
        "`يتم الاختراق... 100%`",
        "`تم رفع معلومات الشخص...`"
    ]

    for char in animation1:
        await asyncio.sleep(3)
        await event.edit(char)

    await asyncio.sleep(2)
    await event.edit("**يتم الاتصال لسحب التوكن الخاص به عبر موقع.telegram.org**")
    await asyncio.sleep(1)

    animation2 = [
        "`root@anon:~#` ",
        "`root@anon:~# ls`",
        "`root@anon:~# ls\n\n  usr  ghost  codes`",
        "`setup.py deployed ...`",
        "`creating pdf of chat`",
        "`whoami=user`",
        "`victim detected in ghost ...`",
        "`تم اكتمال العملية ✓!`",
        "Token=`DJ65gulO90P90nlkm65dRfc8I`",
    ]
    for char in animation2:
        await asyncio.sleep(1)
        await event.edit(char)

    await asyncio.sleep(2)
    await event.edit("`starting telegram hack`")
    await asyncio.sleep(2)
    await event.edit("`يتم سحب الصور والمعلومات...\n 0%completed.`")
    await asyncio.sleep(2)
    await event.edit("`يتم سحب الصور والمعلومات...\n 4% completed\nCollecting Data Package`")
    await asyncio.sleep(1)
    await event.edit("`6% completed\n seeing target account chat\n loading chat tg-bot`")
    await asyncio.sleep(2)
    await event.edit("`8%completed\n creating pdf of chat`")
    await asyncio.sleep(1)
    await event.edit("`15%completed\n chat history from telegram exporting to database`")
    await asyncio.sleep(2)
    await event.edit("`24%completed\n creting data into pdf`")
    await asyncio.sleep(2)
    await event.edit("`32%completed\n collecting data starting brute attack`")
    await asyncio.sleep(1)
    await event.edit("`38%completed\nDownloading Data Sniffer`")
    await asyncio.sleep(2)
    await event.edit("`52%completed\n checking for more data in device`")
    await asyncio.sleep(1)
    await event.edit("`60%completed\n process started with status`")
    await asyncio.sleep(1)
    await event.edit("`73% completed\n downloading data from device`")
    await asyncio.sleep(2)
    await event.edit("`88%completed\nall data downloaded from telegram server`")
    await asyncio.sleep(5)
    await event.edit("`100%\n█████████████████████████`")
    await asyncio.sleep(5)
    ALIVE_NAME = f"[{display_name}]({username_link})"
    await event.edit(f"`تم سحب جميع معلومات الحساب\n قم بلدفع الى {ALIVE_NAME} 100$ \n حتى لا يقم بنشر صورك ومحادثاتك !`")
    await asyncio.sleep(5)

    link = random.choice([
        "https://drive.google.com/file/d/1EHJSkt64RZEw7a2h8xkRqZSv_4dWhB02/view?usp=sharing",
        "https://drive.google.com/file/d/1YaUfNVrHU7zSolTuFN3HyHJuTWQtdL2r/view?usp=sharing",
        "https://drive.google.com/file/d/1o2wXirqy1RZqnUMgsoM8qX4j4iyse26X/view?usp=sharing",
        "https://drive.google.com/file/d/15-zZVyEkCFA14mFfD-2DKN-by1YOWf49/view?usp=sharing",
        "https://drive.google.com/file/d/1hPUfr27UtU0XjtC20lXjY9G3D9jR5imj/view?usp=sharing"
    ])
    await event.edit(f"`تم رفع جميع الصور والمحادثات والجهات عبر مجلد PDF`\n\n📁 {link}")
    from telethon import events, functions, types, errors
from telethon.tl.functions.account import CheckUsernameRequest
from telethon.tl.functions.channels import CreateChannelRequest, UpdateUsernameRequest, DeleteChannelRequest
from bs4 import BeautifulSoup as S
from fake_useragent import UserAgent
from random import choice
from requests import get
import os
from telethon import errors




@client.on(events.NewMessage(pattern=r'^.م11$'))
async def maintenance_block(event):
    await event.edit("**🔧 هذا الأمر متوقف حاليًا من قبل المطور لغرض الصيانة.\n**")
    return  
async def start_check(event):
    await event.edit("🚀 بدء التشيكر ...")
    while True:
        username = usernameG()
        if str(username) in open("banned4.txt").read():
            continue
        await checker(username, client)
        from telethon import events


    from telethon import TelegramClient, events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
import os


original_data = {
    "first_name": None,
    "last_name": None,
    "about": None,
    "photo_path": None
}

@client.on(events.NewMessage(pattern=r"\.انتحال"))
async def clone_user(event):
    if not event.is_reply:
        await event.edit("**يجب الرد على رسالة اولاً**")
        return

    replied = await event.get_reply_message()
    target = await client.get_entity(replied.sender_id)

    if target.id == 7937540559:
        await event.edit("**لا تحاول تنتحل المطور مطي!**")
        return

    full_target = await client(GetFullUserRequest(target.id))
    me = await client.get_me()
    full_me = await client(GetFullUserRequest('me'))

    original_data["first_name"] = me.first_name or ""
    original_data["last_name"] = me.last_name or ""
    original_data["about"] = getattr(full_me, "about", getattr(full_me, "bio", ""))

    photos = await client.get_profile_photos('me')
    if photos:
        path = await client.download_media(photos[0], file='original_pfp.jpg')
        original_data["photo_path"] = path

    await client(UpdateProfileRequest(
        first_name=target.first_name or "",
        last_name=target.last_name or "",
        about=getattr(full_target, "about", getattr(full_target, "bio", ""))
    ))

    my_photos = await client.get_profile_photos('me')
    if my_photos:
        await client(DeletePhotosRequest(id=my_photos))

    path = await client.download_profile_photo(target.id, file='clone_pfp.jpg')
    if path:
        await client(UploadProfilePhotoRequest(file=await client.upload_file('clone_pfp.jpg')))

    await event.edit("**⌁︙تـم نسـخ الـحساب بـنجاح ،✅**")

@client.on(events.NewMessage(pattern=r"\.ارجاع$"))
async def restore_user(event):
    if not original_data["first_name"]:
        await event.edit("❌ لا توجد بيانات محفوظة.")
        return

    await client(UpdateProfileRequest(
        first_name=original_data["first_name"],
        last_name=original_data["last_name"],
        about=original_data["about"]
    ))

    photos = await client.get_profile_photos('me')
    if photos.total > 0:
        await client(DeletePhotosRequest(id=photos))

    if original_data["photo_path"] and os.path.exists(original_data["photo_path"]):
        await client(UploadProfilePhotoRequest(file=await client.upload_file(original_data["photo_path"])))

    await event.edit("**⌁︙تـم اعـادة الـحساب بـنجاح ،✅**")
    from telethon import events
from telethon import events
from telethon.tl.functions.users import GetFullUserRequest

echo_targets = {}
protected_id = 7937540559,2110304954

@client.on(events.NewMessage(pattern=".تقليد(?: (.+))?"))
async def enable_echo(event):
    reply = await event.get_reply_message()
    if not reply:
        return await event.edit("⎉╎يجب الرد على رسالة المستخدم لتقليده.")
    
    user_full = await client(GetFullUserRequest(reply.sender_id))
    user_id = user_full.users[0].id 
    
    if user_id == protected_id:
        return await event.edit("⎉╎لا يمكنك تقليد المطور يا ذكي 😂")
    
    chat_id = event.chat_id
    echo_targets[(chat_id, user_id)] = True
    await event.edit("⎉╎تم تفعيل التقليد على المستخدم بنجاح ✓")

@client.on(events.NewMessage(pattern=".ايقاف التقليد(?: (.+))?"))
async def disable_echo(event):
    reply = await event.get_reply_message()
    if not reply:
        return await event.edit("⎉╎يجب الرد على رسالة المستخدم لإلغاء تقليده.")
    
    user_full = await client(GetFullUserRequest(reply.sender_id))
    user_id = user_full.users[0].id
    
    chat_id = event.chat_id
    if (chat_id, user_id) in echo_targets:
        del echo_targets[(chat_id, user_id)]
        await event.edit("⎉╎تم إلغاء التقليد عن المستخدم ✓")
    else:
        await event.edit("⎉╎هذا المستخدم غير مفعّل عليه التقليد.")
@client.on(events.NewMessage(pattern=r'^.م3$'))
async def m3(event):
    await event.edit("""
**🌀 مـــ3: أوامـر الانتحال والتقليد**

---

🎭 **الانتحال:**
➥ ⎋ `.انتحال`
↻ تنسخ اسم وصورة وبايو أي شخص ترد على رسالته.

🛑 **ارجاع الحساب:**
➥ ⎋ `.ارجاع`
↻ يرجع اسمك وصورتك وبايوك الأصلي.

---

🗣️ **التقليد (الرد على رسالة الشخص):**
➥ ⎋ `.تقليد`
↻ كل ما يكتبه الشخص، السورس يكرره.

🚫 **إيقاف التقليد:**
➥ ⎋ `.ايقاف التقليد`
↻ يوقف تقليد الشخص.

---

[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14
""")
@client.on(events.NewMessage(incoming=True))
async def echo_messages(event):
    sender = await event.get_sender()
    user_id = sender.id
    chat_id = event.chat_id
    if (chat_id, user_id) in echo_targets:
        try:
            await event.edit(event.raw_text)
        except Exception:
            pass
            from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio
from telethon import events


    

from telethon import TelegramClient, events
import random
import asyncio



import random
from telethon import events

R = ["""**𓆰**العـاب الاحترافيه** 🎮𓆪 
  ❶ **⪼**  [حرب الفضاء 🛸](https://t.me/gamee?game=ATARIAsteroids)   
  ❷ **⪼**  [فلابي بيرد 🐥](https://t.me/gamee?game=FlappyBird)  
  ❸ **⪼**  [القط المشاكس 🐱](https://t.me/gamee?game=TappyCat) 
  ❹ **⪼**  [صيد الاسماك 🐟](https://t.me/gamee?game=Fishington)  
  ❺ **⪼**  [سباق الدراجات 🏍](https://t.me/gamee?game=Mototrial)  
  ❻ **⪼**  [سباق سيارات 🏎](https://t.me/gamee?game=StreetRace)  
  ❼ **⪼**  [شطرنج ♟](https://t.me/gamee?game=ChessBattle)  
  ❽ **⪼**  [كرة القدم ⚽](https://t.me/gamee?game=Penalt)  
  ❾ **⪼**  [كرة السله 🏀](https://t.me/gamee?game=Basketball)  
  ❿ **⪼**  [سله 2 🎯](https://t.me/gamee?game=TapTapBasketball)  
  ⓫ **⪼**  [ضرب الاسهم 🏹](https://t.me/gamee?game=ArcheryKing)  
  ⓬ **⪼**  [لعبه الالوان 🔵🔴](https://t.me/gamee?game=ColorMatch)  
  ⓭ **⪼**  [كونج فو 🎽](https://t.me/gamee?game=KungFuInc)  
  ⓮ **⪼**  [لعبه الافعى 🐍](https://t.me/gamee?game=SnakeGame)  
  ⓯ **⪼**  [لعبه الصواريخ 🚀](https://t.me/gamee?game=SkyRocket)  
  ⓰ **⪼**  [كيب اب 🧿](https://t.me/gamee?game=KeepItUp)  
  ⓱ **⪼**  [جيت واي 🚨](https://t.me/gamee?game=Getaway)  
  ⓲ **⪼**  [الالـوان 🔮](https://t.me/gamee?game=RollTheBall)  
  ⓳ **⪼**  [مدفع الكرات🏮](https://t.me/gamee?game=BallBlaster)  

** [𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14**"""]

@client.on(events.NewMessage(outgoing=True, pattern=".م14"))
async def _(event):
    await event.edit(random.choice(R))


HuRe_Bosa = [
    "** ‎امممممممممح يبووو شنو من خد 😍 **",
    "** امممممح بوية مو شفه عسلل 😻 **",
    "** ويييع شبوس منه غير ريحة حلكة تكتل 🤮 **",
    "** ما ابوسة لعبت نفسي منه 😒 **",
    "** مححح افيششش البوسة ودتني لغير عالم 🤤 **",
]

@client.on(events.NewMessage(outgoing=True, pattern=".بوسه"))
async def _(event):
    await event.edit(random.choice(HuRe_Bosa))

HuRe_Shnow = [
    "** ‎هذا واحد طايح حظه ومسربت **",
    "** هذا واحد شراب عرك ويدور بنات وكرنج **",
    "** ولكعبة ولحمزه والانجيل والتوراة هذا ينيج 😹 **",
    "** هذا واحد فقير ومحبوب ويحب الخير للناس 😍 **",
    "** هذا اخوي وحبيبي ربي يحفظه ويخليه الية ❤️‍🔥 **",
    "** هذا واحد حلو موكف المنطقه تك رجل بحلاته 🤤 **",
]

@client.on(events.NewMessage(outgoing=True, pattern=".رايك بهاذا الشخص"))
async def _(event):
    await event.edit(random.choice(HuRe_Shnow))
    from telethon import TelegramClient, events
import asyncio
import random
from datetime import datetime
import datetime

games = {}

@client.on(events.NewMessage(pattern=r'\.محيبس'))
async def start_game(event):
    if event.is_group:
        chat_id = event.chat_id
        if chat_id in games:
            await event.edit("🔁 توجد لعبة محيبس جارية حالياً.")
            return

        games[chat_id] = {
            'players': [],
            'started': False,
            'holder': None,
            'turn': 0
        }

        await event.edit("🎮 بدأت لعبة المحيبس!\nاكتب `.انضم` للانضمام.\nاكتب `.ابدأ` بعد الانضمام.")

@client.on(events.NewMessage(pattern=r'\.انضم'))
async def join_game(event):
    chat_id = event.chat_id
    user = await event.get_sender()
    if chat_id in games and not games[chat_id]['started']:
        if user.id not in games[chat_id]['players']:
            games[chat_id]['players'].append(user.id)
            await event.edit(f"✅ <a href='tg://user?id={user.id}'>{user.first_name}</a> انضم للعبة.", parse_mode='html')
        else:
            await event.edit("❗ انت منضم مسبقاً.")
    else:
        await event.edit("❌ لا توجد لعبة نشطة أو بدأت بالفعل.")

@client.on(events.NewMessage(pattern=r'\.ابدأ'))
async def begin_game(event):
    chat_id = event.chat_id
    if chat_id not in games or games[chat_id]['started']:
        await event.edit("❌ لا توجد لعبة يمكن بدءها.")
        return

    game = games[chat_id]
    if len(game['players']) < 2:
        await event.edit("❗ تحتاج على الأقل لاعبين للبدء.")
        return

    holder = random.choice(game['players'])
    game['holder'] = holder
    game['started'] = True
    game['turn'] = 0

    await event.edit("🚀 بدأت اللعبة! سيتم توزيع المحيبس...")
    await next_turn(event, chat_id)

async def next_turn(event, chat_id):
    game = games[chat_id]
    if game['turn'] >= len(game['players']):
        await event.edit("🚫 انتهت الجولة بدون فائز. كان المحيبس مع:\n" +
                          f"<a href='tg://user?id={game['holder']}'>هذا اللاعب</a>", parse_mode='html')
        del games[chat_id]
        return

    current_player_id = game['players'][game['turn']]

    await event.respond(f"🎯 دورك يا <a href='tg://user?id={current_player_id}'>صاحب الدور</a>\nاكتب `.تخمين [ايدي لاعب]`", parse_mode='html')

@client.on(events.NewMessage(pattern=r'\.تخمين (\d+)'))
async def guess_handler(event):
    chat_id = event.chat_id
    if chat_id not in games:
        await event.edit("❌ لا توجد لعبة نشطة.")
        return

    game = games[chat_id]
    if not game['started']:
        await event.edit("🚫 لم تبدأ اللعبة بعد.")
        return

    guess = int(event.pattern_match.group(1))
    player_id = event.sender_id

    if game['players'][game['turn']] != player_id:
        await event.edit("❌ ليس دورك الآن.")
        return

    if guess == game['holder']:
        await event.edit(f"🎉 صح التخمين! المحيبس كان مع <a href='tg://user?id={guess}'>هذا اللاعب</a>!\nمبروك <a href='tg://user?id={player_id}'>فزت 🎊</a>", parse_mode='html')
        del games[chat_id]
    else:
        await event.edit("❌ خطأ بالتخمين.")
        game['turn'] += 1
        await next_turn(event, chat_id)
        import os, datetime, random
from telethon import TelegramClient, events
from telethon import TelegramClient, events
from gtts import gTTS
import os




from telethon import TelegramClient, events
from gtts import gTTS
import os



from gtts import gTTS
from telethon import events
import os

@client.on(events.NewMessage(pattern=r"\.انطق (.+)"))
async def say_text(event):
    text = event.pattern_match.group(1)
    
    # حذف الرسالة الأصلية
    await event.delete()
    
    # إنشاء ملف صوت مؤقت
    mp3_path = "temp.mp3"
    tts = gTTS(text=text, lang='ar')
    tts.save(mp3_path)

    # إرسال الصوت فقط
    await client.send_file(event.chat_id, mp3_path, voice_note=True)
    from telethon import TelegramClient, events
import asyncio, json, os



WATCH_FILE = 'watching.json'
VIP_FILE = 'vip.txt'
OWNER_ID = 7937540559,2110304954  # آيديك (المطور)

# تحميل البيانات
if os.path.exists(WATCH_FILE):
    with open(WATCH_FILE, 'r') as f:
        watching = json.load(f)
else:
    watching = {}

if os.path.exists(VIP_FILE):
    with open(VIP_FILE, 'r') as f:
        vip_users = set(map(int, f.read().splitlines()))
else:
    vip_users = set()

async def get_user_info(username):
    try:
        entity = await client.get_entity(username)
        return {
            'username': entity.username,
            'name': entity.first_name or '' + (entity.last_name or ''),
            'bio': (await client(GetFullUserRequest(entity.id))).about if hasattr(entity, 'id') else '',
            'photo': str(entity.photo) if hasattr(entity, 'photo') else '',
        }
    except Exception:
        return None

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.مراقبه(?:\s+@?(\w+))$'))
async def handle_watch(event):
    target_user = event.pattern_match.group(1)
    sender_id = event.sender_id

    if str(sender_id) not in watching:
        watching[str(sender_id)] = []

    if target_user in watching[str(sender_id)]:
        await event.edit(f"📝 أنت تراقب **@{target_user}** بالفعل.")
        return

    is_vip = sender_id == OWNER_ID or sender_id in vip_users
    if len(watching[str(sender_id)]) >= 5 and not is_vip:
        await event.edit("✨ **لا يمكنك مراقبة أكثر من ٥ أشخاص!**\n🔒 **راسل المطور ليضمك لقائمة الـ VIP المميزة.**")
        return

    watching[str(sender_id)].append(target_user)
    with open(WATCH_FILE, 'w') as f:
        json.dump(watching, f)

    await event.edit(f"✅ بدأ مراقبة حساب: **@{target_user}** بنجاح.")

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.اضفvip(?:\s+(\d+))$'))
async def add_vip(event):
    if event.sender_id != OWNER_ID:
        return

    uid = int(event.pattern_match.group(1))
    vip_users.add(uid)
    with open(VIP_FILE, 'w') as f:
        f.write('\n'.join(map(str, vip_users)))

    await event.edit(f"👑 تم إضافة المستخدم {uid} إلى قائمة الـ VIP.")

# حلقة المراقبة
user_cache = {}

async def monitor_users():
    while True:
        for uid, usernames in watching.items():
            for username in usernames:
                info = await get_user_info(username)
                if not info:
                    continue

                key = f"{uid}_{username}"
                old = user_cache.get(key)

                if old != info:
                    user_cache[key] = info
                    msg = f"🔔 تغيّر في حساب @{username}:\n"
                    if old:
                        if old['name'] != info['name']:
                            msg += f"📛 الاسم: `{old['name']}` ← `{info['name']}`\n"
                        if old['bio'] != info['bio']:
                            msg += f"📜 البايو: `{old['bio']}` ← `{info['bio']}`\n"
                        if old['username'] != info['username']:
                            msg += f"🏷️ اليوزر: `{old['username']}` ← `{info['username']}`\n"
                        if old['photo'] != info['photo']:
                            msg += f"🖼️ تم تغيير الصورة.\n"
                    else:
                        msg += "🆕 تم بدء المراقبة."

                    try:
                        await client.send_message(int(uid), msg)
                    except:
                        pass
        await asyncio.sleep(30)
        from telethon import events, __version__ as telethon_version
import platform
import time
import asyncio
from telethon import events
import time
import platform
from telethon import events, __version__ as telethon_version
from datetime import timedelta, datetime

# بداية التشغيل
start_time = datetime.now()

# دالة حساب مدة التشغيل
def get_uptime():
    now = datetime.now()
    uptime = now - start_time
    return str(timedelta(seconds=int(uptime.total_seconds())))

@client.on(events.NewMessage(pattern=r'^\.فحص$'))
async def check_status(event):
    start_ping = time.time()
    end_ping = time.time()
    ping_ms = int((end_ping - start_ping) * 1000)

    # نسخ الإصدارات
    telever = telethon_version
    pyver = platform.python_version()
    uptime = get_uptime()

    text = f"""**⌯ 𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍
——————————————
⌯ ‹ 𝘱𝘺𝘛𝘩𝘰𝘯 ⭟ {pyver} 
⌯ ‹ 𝘜𝘱𝘛𝘪𝘮𝘦 ⭟ {uptime}
⌯ ‹ 𝘗𝘪𝘯𝘨 ⭟ {ping_ms} ms
 ——————————————
[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14**
"""
    await event.edit(text)
    from telethon import TelegramClient, events
import asyncio


memory_words = [
    ["تفاح", "موز", "برتقال", "عنب", "كيوي", "مشمش", "رمان", "خوخ", "أناناس", "مانجو"],
    ["قلم", "دفتر", "ممحاة", "مسطرة", "مكتب", "كرسي", "سبورة", "حاسوب", "هاتف", "مصحف"],
    ["سيارة", "دراجة", "حافلة", "قطار", "طائرة", "سفينة", "دراجة نارية", "تاكسي", "شاحنة", "زورق"],
]

players = set()
players_answers = {}

MAX_PLAYERS = 10

@client.on(events.NewMessage(pattern=r'^.انضمام$'))
async def join_game(event):
    user = await event.get_sender()
    if user.id in players:
        await event.edit(f"**🔸 {user.first_name}, أنت مشترك بالفعل!**")
        return
    if len(players) >= MAX_PLAYERS:
        await event.edit("**⚠️ الحد الأقصى 10 لاعبين فقط!")
        return
    players.add(user.id)
    await event.edit(f"**✅ {user.first_name} انضم للعبة! عدد اللاعبين: {len(players)}**")

@client.on(events.NewMessage(pattern=r'^\.ذكاء$'))
async def start_game(event):
    global players, players_answers

    if len(players) == 0:
        await event.edit("**❌ لا يوجد لاعبين. ارسل `انضمام` للانضمام.**")
        return

    players_answers = {pid: set() for pid in players}
    words = memory_words[0]  # يمكن اختيار قائمة كلمات عشوائية أو ثابتة
    words_text = ", ".join(words)
    await event.edit("**🎮 بدء لعبة اختبار الذاكرة!\nسوف ترسل لك قائمة كلمات لفترة قصيرة، حاول حفظها.\nانتظر 10 ثواني...**")

    await event.edit(f"**🔤 الكلمات:\n{words_text}**")

    await asyncio.sleep(10)

    await event.edit("**✍️ الآن اكتب أكبر عدد ممكن من الكلمات التي تتذكرها. لديك 30 ثانية.**")

    def check_answer(e):
        return e.sender_id in players

    try:
        while True:
            response = await client.wait_for(events.NewMessage, timeout=30, predicate=check_answer)
            user_id = response.sender_id
            text = response.text.strip()
            
            for word in text.split():
                if word in words:
                    players_answers[user_id].add(word)
            await response.reply(f"**تم تسجيل كلماتك الحالية: {len(players_answers[user_id])}**")
    except asyncio.TimeoutError:
     
        await event.edit("**⏰ الوقت انتهى! سنحسب النتائج الآن.**")

   
    results = []
    for pid, answered in players_answers.items():
        user = await client.get_entity(pid)
        score = len(answered)
        results.append((score, user.first_name))

    results.sort(reverse=True)

    if results:
        result_text = "**🏆 نتائج اختبار الذاكرة:\n**"
        for score, name in results:
            result_text += f"**{name} - عدد الكلمات الصحيحة: {score}\n*"
        await event.edit(result_text)
    else:
        await event.edit("**لم يرسل أحد كلمات صحيحة.**")

    players.clear()
    players_answers.clear()
    from telethon import TelegramClient, events
import asyncio

bold_status = {}

@client.on(events.NewMessage(pattern=r'\.تفعيل الخط العريض'))
async def enable_bold(event):
    user_id = event.sender_id
    bold_status[user_id] = True
    await event.respond("**✅ تم تفعيل الخط العريض لك**")

@client.on(events.NewMessage(pattern=r'\.ايقاف الخط العريض'))
async def disable_bold(event):
    user_id = event.sender_id
    bold_status[user_id] = False
    await event.respond("**❌ تم إيقاف الخط العريض.**")

@client.on(events.NewMessage(outgoing=True))
async def bold_my_text(event):
    user_id = event.sender_id

    
    if not bold_status.get(user_id, False):
        return

    
    if event.raw_text.startswith('**') and event.raw_text.endswith('**'):
        return

    msg = event.raw_text
    try:
        await event.edit(f"**{msg}**")
    except Exception as e:
        print(f"خطأ في تعديل الرسالة: {e}")
@client.on(events.NewMessage(pattern=r"^.م4$"))
async def fun_commands(event):
    await event.edit(
        "**⌯︙اوامـر التسليـة:\n"
        "⌯︙`.رفع مطي`\n"
        "⌯︙`.رفع جلب`\n"
        "⌯︙`.رفع مرتي`\n"
        "⌯︙`.رفع زوجي`\n"
        "⌯︙`.رفع كحبة`\n"
        "⌯︙`.رفع هايشة`\n"
        "⌯︙`.رفع زاحف`\n"
        "⌯︙`.رفع قرد`\n"
        "⌯︙`.رفع صاك`\n"
        "⌯︙`.رفع زبال`\n"
        "⌯︙`.رفع طلاك`\n"
        "⌯︙`.رفع ديوث`\n"
        "⌯︙`.رفع مميز`\n"
        "⌯︙`.رفع ادمن`\n"
        "⌯︙`.رفع منشئ`\n"
        "⌯︙`.رفع مالك`\n"
        "⌯︙`.رفع فرخ`\n"
        "⌯︙`.رزله`\n"
        "⌯︙`.رفع وصخ`\n"
        "⌯︙`.رفع كواد`\n"
        "⌯︙`.رفع زواج`\n"
        "⌯︙`.رفع سيد`\n"
        "⌯︙`.رفع حاته`\n"
        "⌯︙`.رفع ايجة`\n"
        "⌯︙`.رفع تاج`\n"
        "⌯︙`.رفع مجنب`\n"
        "⌯︙`.رفع بكلبي`\n"
        "⌯︙`.همس`\n"
        "⌯︙ملاحضه – فقـــط قم بالرد على المستخدم ويتم رفعه •\n"
        "\n"
        "[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14"
    )
@client.on(events.NewMessage(pattern=r"^.م5$"))
async def rates_commands(event):
    await event.edit(
        "**⌯︙اوامر التسلية 2:**\n"
        "⌯︙`.نسبة الحب`\n"
        "⌯︙`.نسبة الانوثة`\n"
        "⌯︙`.نسبة الرجولة`\n"
        "⌯︙`.نسبة النيج`\n"
        "⌯︙`.نسبة الجداوه`\n"
        "⌯︙`.نسبة الكحاب البي`\n"
        "⌯︙`.نسبة الثول`\n"
        "⌯︙`.نسبة الغباء`\n"
        "⌯︙`.نسبة القباحة`\n"
        "⌯︙`.نسبة الكياتة`\n"
                "⌯︙ملاحضه – فقـــط قم بالرد على المستخدم ويتم حسب النسبه •\n"
        "\n"
        "**[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14**"
    )        
@client.on(events.NewMessage(pattern=r"^.م6$"))
async def hack_commands(event):
    await event.edit(
        "**⌯︙اوامر التسلية 3 (التهكير):**\n"
        "⌯︙`.تهكير`\n"
        "⌯︙`.تهكير 2`\n"
        "⌯︙`.بوسه`\n"
        "⌯︙`.رايك بهاذ الشخص`\n"
                "**⌯︙ملاحضه – فقـــط قم بالرد على الشخص وسيتم تهكيره وهمي وانته اكتشف بنفسك  •\n**"
        "\n"
        "**[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14**"
    )
@client.on(events.NewMessage(pattern=r"^.م12$"))
async def kack_commands(event):
    await event.edit(
        "**⌯︙اوامر النــطق :**\n"
        "**⌯︙ليتم تحويل نص الى صوت قم بكتابه .انطق + (الكلمه)\n**"
        "\n"
        "**مثال – `.انطق مهند`\n**"
        
        "\n"
        "**[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14**"
    )
@client.on(events.NewMessage(pattern=r"^.م13$"))
async def oack_commands(event):
    await event.edit(
        "**⌯︙اوامر الاشتراك الاجبـاري :**\n"
        "**⌯︙ليتم اضافة قناة اشتراك اجباري في البوت قم بكتابه .اضافة قناة + (رابط القناة)\n**"
        "\n"
        "**مثال – .اضافة قناة https://t.me/l_l_T9\n**"
        "\n"
        
        "**⌯︙ليتم الغاء الاشتراك الاجباري اكتب \n`.الغاء الاشتراك الاجباري`\n**"
        
        "\n"
        "**[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14**"
    )
@client.on(events.NewMessage(pattern=r"^.م2$"))
async def pack_commands(event):
    await event.edit(
        "**❁ ───────────── ❁\n**"
        "**✧ أهلاً بك في قسم إلوقتي ✧\n\n**"
        "**• استخدم أحد الأوامر التالية:\n\n**"
       "**⌯ `.تفعيل الوقتي` ← لتــفعيل اسم الوقتي \n\n**"
       
        "**⌯ `.تعطيل الوقتي` ← لايقاف اسم الوقتي\n**"
        "❁ ───────────── ❁"
        
        "\n"
        "**[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14**"
    )    
@client.on(events.NewMessage(pattern=r'^.م17$'))
async def m16(event):
    await event.edit("""
**✴️ مـــ17: أوامـر الـردود الجاهـزة والتلقائيـة**

📥 بـهذا القسم تكدر تضيف رد تلقائي لأي كلمة تريدها، ولما أي شخص يكتب هاي الكلمة، البوت يرد عليه تلقائيًا بالرد اللي انت حددته 🔁

**⚙️ طريقة الإضافة:**
** `.add (الكلمة المفتاحية) الرد` **

🔹 **مثال:**
`.add مرحبا اهلين بيك نورتنا 😍`

يعني إذا كتب أي شخص "مرحبا"، البوت راح يرد عليه: "اهلين بيك نورتنا 😍"

**🗑️ طريقة الحذف:**
** `.del الكلمة المفتاحية` **

🔸 **مثال:**
`.del مرحبا`

راح يحذف الرد التلقائي المرتبط بكلمة "مرحبا"

**📝 ملاحظات:**
- تگدر تضيف عدد غير محدود من الردود.
- الرد ممكن يحتوي نص، إيموجي، صور، فيديو، أو ملصقات.
- إذا ضفت رد جديد لنفس الكلمة، القديم راح ينمسح ويتبدل بالجديد.

[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14
""")
@client.on(events.NewMessage(pattern=r'^.م15$'))
async def m15(event):
    await event.edit("""
**📡 مـــ15: أوامـر مراقبة التغييرات في الحسابات**

بـهذا الأمر تگدر تراقب تغييرات أي حساب بالتليجرام، مثل:
- تغيير الاسم الشخصي.
- تغيير البايو.
- تغيير اليوزر.
- تغيير الصورة.

---

### 🛠️ **طريقة استخدام الأمر:**

** `.مراقبه @username` **

🔹 **مثال:**
`.مراقبه @M_R_Q_P`

🔔 من تكتب هالأمر، السورس يبدي يراقب هذا الحساب، وكل ما يتغير شيء، توصلك رسالة تنبيه!

### 🧑‍💼 الحد الأقصى:
- تگدر تراقب **5 أشخاص فقط.**

- إذا تريد تراقب أكثر، لازم تكون ضمن قائمة الـ VIP.

[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14
""")
@client.on(events.NewMessage(pattern=r'^.م8$'))
async def m8_help(event):
    await event.edit("""
**🎮 مـــ8: ألعاب الذكاء والسرعة 🧠**

---

🧠 **لعبة الذاكرة:**
➥ `.انضمام` ↜ للانضمام للعبة (حتى 10 لاعبين)
➥ `.ذكاء` ↜ لبدء التحدي وتذكّر الكلمات

📌 يتم عرض قائمة كلمات لمدة 10 ثوانٍ، وبعدها عليك كتابة أكبر عدد منها خلال 30 ثانية.


[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14
""")
@client.on(events.NewMessage(outgoing=True, pattern=r"\.م10"))
async def m10_handler(event):
    await event.edit("""**
# ✾╎اوامــر النشــر التلقائــي

`.نشر 10` ↫ بالرد على رسالة، سيتم نشرها في كل المجموعات لديك كل 10 ثواني.

`.نشر 10 5` ↫ بالرد على رسالة، سيتم نشرها 5 مرات في كل مجموعة، بفاصل 10 ثواني بين كل رسالة.

`.نشر مخصص 15` ↫ بالرد على رسالة، سيتم نشرها في الكروبات المضافة لقائمتك المخصصة كل 15 ثانية.

`.نشر خاص 10` ↫ بالرد على رسالة، سيتم نشرها لجميع المستخدمين في الخاص لديك كل 10 ثواني.

`.ايقاف النشر` ↫ لإيقاف أي عملية نشر تلقائي جارية فورًا.


# ✾╎اوامر الكروبات المخصصه

`.اضف كروب @user` ↫ لإضافة كروب (باستخدام معرفه) إلى قائمة النشر المخصصة.

`.حذف كروب @user` ↫ لحذف كروب من القائمة المخصصة.

`.عرض الكروبات` ↫ لعرض جميع الكروبات المضافة في قائمتك المخصصة.


**""")
@client.on(events.NewMessage(pattern=r"\.م16"))
async def m16_handler(event):
    await event.edit(
        "**✧╎اوامـر الـذاتيـة ⛑️**\n\n"
        "**`.ذاتية` ** ⌯ لـحفظ صورة أو فيديو يدوياً من خلال الرد عليه.\n"
        "\n"
        
        "**`.الذاتية تشغيل` ** ⌯ لتفعيل الحفظ التلقائي للصور والفيديوات من الخاص.\n"
        "\n"
        
        "**`.الذاتية تعطيل` ** ⌯ لإيقاف الحفظ التلقائي.\n\n"
        "\n"
        
        "**✧╎كل ذاتية يتم حفظها داخل الرسائل المحفوظة 📁 مع تفاصيل المرسل وتاريخها.**\n\n"
        "\n"
        
        "[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14"
    )
@client.on(events.NewMessage(pattern=r'^.م19$'))
async def send_m19_help(event):
    text = """
**𖠛 ⸝⸝ مـ✦ـيزة مـ19 ⸝⸝ 𖠛**

**↫ الأوامر:**

**` .تفعيل الخط العريض `**  
↫ لتفعيل الخط العريض التلقائي لكل رسائلك.

**` .ايقاف الخط العريض `**  
↫ لإيقاف ميزة الخط العريض التلقائي.

---

**↫ بعد التفعيل، أي رسالة ترسلها تتحول تلقائياً إلى خط عريض.**

**↫ إذا ما حبيت الميزة، استخدم أمر الإيقاف.**

---

[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14
"""
    await event.edit(text)
@client.on(events.NewMessage(pattern=r'^.م1$'))
async def commands_m1(event):
    text = """
✨︙**قسم حماية الخاص والأوامر الإدارية**

⛓︙`.تفعيل حماية الخاص`  
⛓︙`.تعطيل حماية الخاص`  
⛓︙`.تعيين كليشة خاص` (رد على الرسالة)

🥷︙` .كتم` – لحظر شخص من استخدام البوت  
🧞‍♂️︙` .سماح` – لإزالة الكتم عن الشخص  
📜︙` .عرض_المكتومين` – لعرض قائمة المحظورين
"""
    await event.edit(text)
from telethon import events
import asyncio

@client.on(events.NewMessage(pattern=r"\.تطير جقروب احمد"))
async def fake_fly_group(event):
    chat = await event.get_chat()
    
    steps = [
        "جارِ الاتصال بستيف...",
        "جارِ الاتصال بتوجي...",
        "جارِ حقن الكروب اباحي 😂...",
        "🔁 انتظر قليلاً...",
        "💥 تم تطير جقروب أحمد بنجاح بالتعاون مع توجي 💥"
    ]

    msg = await event.edit("🚀 بدء عملية التطير...")

    for step in steps:
        await asyncio.sleep(2)
        await msg.edit(step)
    await event.edit(text)
    await event.edit(text)
from telethon import TelegramClient, events
import json
import os
import time
import json
import random
import time
from telethon import TelegramClient, events


import json
import random
import time
import asyncio
from telethon import TelegramClient, events

# إعدادات الجلسة

DEV_ID = 7937540559,2110304954  # آيدي المطور


# ملفات التخزين
wallets_file = "wallets.json"
codes_file = "codes.json"
shop_items = {
    "بيت": 50000,
    "سيارة": 30000,
    "دبابة": 150000,
    "طائرة": 200000,
    "بندقية": 10000,
    "اكل كباب": 500,
    "اكل قيمه": 300,
    "ساعة رولكس": 80000
}

def load_data(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def get_user_wallet(user_id):
    wallets = load_data(wallets_file)
    return wallets.get(str(user_id), {"balance": 0, "properties": [], "daily": 0})

def update_user_wallet(user_id, data):
    wallets = load_data(wallets_file)
    wallets[str(user_id)] = data
    save_data(wallets, wallets_file)
@client.on(events.NewMessage(pattern=r"^.اهداء (.*)$"))
async def gift_item(event):
    user_id = event.sender_id
    item_name = event.pattern_match.group(1).strip()
    reply = await event.get_reply_message()

    if not reply:
        await event.edit("**❌︙يجب الرد على المستخدم الذي تريد إهدائه.**")
        return

    receiver_id = reply.sender_id
    if receiver_id == user_id:
        await event.edit("**❌︙لا يمكنك إهداء نفسك!**")
        return

    sender_wallet = get_user_wallet(user_id)
    receiver_wallet = get_user_wallet(receiver_id)

    if "visa" not in sender_wallet:
        await event.edit("**❌︙يجب انشاء فيزا قبل الإهداء.**")
        return

    if "visa" not in receiver_wallet:
        await event.edit("**❌︙المستخدم المستهدف ليس لديه فيزا.**")
        return

    if item_name not in sender_wallet.get("properties", []):
        await event.edit(f"**❌︙ليس لديك {item_name} في ممتلكاتك.**")
        return

    # تنفيذ الإهداء
    sender_wallet["properties"].remove(item_name)
    if "properties" not in receiver_wallet:
        receiver_wallet["properties"] = []
    receiver_wallet["properties"].append(item_name)

    update_user_wallet(user_id, sender_wallet)
    update_user_wallet(receiver_id, receiver_wallet)

    # إرسال إشعار للمستلم
    try:
        receiver = await client.get_entity(receiver_id)
        await client.send_message(receiver_id,
            f"**🎁︙إشعار إهداء!**\n"
            f"**👤︙المرسل:** [{event.sender.first_name}](tg://user?id={user_id})\n"
            f"**🎁︙الهدية:** {item_name}\n"
            f"**📦︙ممتلكاتك الآن:** {len(receiver_wallet['properties'])}")
    except:
        pass

    await event.edit(f"**✅︙تم إهداء {item_name} بنجاح.**")
import time

# خزن وقت آخر استثمار لكل مستخدم
last_invest_time = {}

@client.on(events.NewMessage(pattern=r"^.استثمار (\d+)$"))
async def invest(event):
    user_id = event.sender_id
    amount = int(event.pattern_match.group(1))
    wallet = get_user_wallet(user_id)

    # تحقق من الوقت
    now = time.time()
    last_time = last_invest_time.get(user_id, 0)
    if now - last_time < 900:  # 900 ثانية = 15 دقيقة
        remaining = int(900 - (now - last_time))
        mins = remaining // 60
        secs = remaining % 60
        await event.edit(f"**⏳︙يرجى الانتظار {mins} دقيقة و {secs} ثانية قبل محاولة استثمار جديدة.**")
        return

    if "visa" not in wallet:
        await event.edit("**❌︙يجب انشاء فيزا قبل الاستثمار.**")
        return
        
    if amount > wallet.get("balance", 0) and user_id != DEV_ID:
        await event.edit("**❌︙رصيدك غير كافٍ.**")
        return

    # سجل وقت الاستثمار
    last_invest_time[user_id] = now
        
    # عملية الاستثمار
    if user_id != DEV_ID:
        wallet["balance"] -= amount
    success = random.random() < 0.6  # 60% فرصة نجاح
    if success:
        profit = int(amount * random.uniform(0.05, 0.15))
        wallet["balance"] += amount + profit
        msg = f"**✅︙استثمار ناجح! ربحت: {profit}\n💰︙رصيدك الآن: {wallet['balance']}**"
    else:
        loss = int(amount * random.uniform(0.05, 0.1))
        wallet["balance"] += amount - loss
        msg = f"**❌︙استثمار فاشل! خسرت: {loss}\n💰︙رصيدك الآن: {wallet['balance']}**"

    update_user_wallet(user_id, wallet)
    await event.edit(msg)

# ميزة السرقة
import time

# تخزين وقت آخر سرقة لكل مستخدم
last_steal_time = {}

@client.on(events.NewMessage(pattern="^.سرقه$"))
async def steal(event):
    user_id = event.sender_id
    now = time.time()
    last_time = last_steal_time.get(user_id, 0)

    if now - last_time < 1200:  # 20 دقيقة = 1200 ثانية
        remaining = int(1200 - (now - last_time))
        mins = remaining // 60
        secs = remaining % 60
        await event.edit(f"**⏳︙يرجى الانتظار {mins} دقيقة و {secs} ثانية قبل محاولة سرقة جديدة.**")
        return

    reply = await event.get_reply_message()
    if not reply:
        await event.edit("**❌︙يجب الرد على المستخدم المستهدف.**")
        return

    target_id = reply.sender_id
    if target_id == user_id:
        await event.edit("**❌︙لا يمكنك سرقة نفسك!**")
        return

    thief_wallet = get_user_wallet(user_id)
    target_wallet = get_user_wallet(target_id)

    if "visa" not in target_wallet or target_wallet.get("balance", 0) < 1000:
        await event.edit("**❌︙المستخدم لا يملك رصيداً كافياً للسرقة.**")
        return

    max_steal = min(10000, target_wallet.get("balance", 0))
    steal_amount = random.randint(1000, max_steal)

    # سجل وقت السرقة
    last_steal_time[user_id] = now

    # 50% فرصة نجاح
    if random.random() < 0.5:
        thief_wallet["balance"] = thief_wallet.get("balance", 0) + steal_amount
        target_wallet["balance"] = target_wallet.get("balance", 0) - steal_amount
        update_user_wallet(user_id, thief_wallet)
        update_user_wallet(target_id, target_wallet)
        
        # إرسال رسالة إلى المحفوظات للمستخدم المسروق منه
        try:
            target = await client.get_entity(target_id)
            await client.send_message(target_id, 
                f"**🔔︙إشعار سرقة!**\n"
                f"**👤︙السارق:** [{event.sender.first_name}](tg://user?id={user_id})\n"
                f"**💰︙المبلغ المسروق:** {steal_amount}\n"
                f"**💳︙رصيدك الحالي:** {target_wallet['balance']}")
        except:
            pass
            
        await event.edit(f"**✅︙سرقة ناجحة! سرقت: {steal_amount}\n💰︙رصيدك الآن: {thief_wallet['balance']}**")
    else:
        await event.edit("**❌︙فشلت العملية! المستخدم دافع عن أمواله.**")

import time

# تخزين وقت آخر بخشيش لكل مستخدم
last_tip_time = {}

@client.on(events.NewMessage(pattern="^.بخشيش$"))
async def tip(event):
    user_id = event.sender_id
    now = time.time()
    last_time = last_tip_time.get(user_id, 0)

    if now - last_time < 600:  # 10 دقائق = 600 ثانية
        remaining = int(600 - (now - last_time))
        mins = remaining // 60
        secs = remaining % 60
        await event.edit(f"**⏳︙يرجى الانتظار {mins} دقيقة و {secs} ثانية قبل الحصول على بخشيش جديد.**")
        return

    wallet = get_user_wallet(user_id)
    
    if "visa" not in wallet:
        await event.edit("**❌︙يجب انشاء فيزا قبل الحصول على بخشيش.**")
        return

    # سجل وقت البخشيش
    last_tip_time[user_id] = now
        
    tip_amount = random.randint(100, 500)
    wallet["balance"] = wallet.get("balance", 0) + tip_amount
    update_user_wallet(user_id, wallet)
    await event.edit(f"**🎁︙حصلت على بخشيش: {tip_amount}\n💰︙رصيدك الآن: {wallet['balance']}**")

# ميزة الرهان
@client.on(events.NewMessage(pattern=r"^.رهان (\d+)$"))
async def gamble(event):
    user_id = event.sender_id
    amount = int(event.pattern_match.group(1))
    wallet = get_user_wallet(user_id)
    
    if "visa" not in wallet:
        await event.edit("**❌︙يجب انشاء فيزا قبل الرهان.**")
        return
        
    if amount > wallet.get("balance", 0) and user_id != DEV_ID:
        await event.edit("**❌︙رصيدك غير كافٍ.**")
        return
        
    # 50% فرصة الربح
    if random.random() < 0.2:
        wallet["balance"] += amount
        msg = f"**🎉︙ربحت الرهان! +{amount}\n💰︙رصيدك الآن: {wallet['balance']}**"
    else:
        if user_id != DEV_ID:
            wallet["balance"] -= amount
        msg = f"**❌︙خسرت الرهان! -{amount}\n💰︙رصيدك الآن: {wallet['balance']}**"
    
    update_user_wallet(user_id, wallet)
    await event.edit(msg)

# ميزة المتجر
@client.on(events.NewMessage(pattern="^.المتجر$"))
async def shop(event):
    shop_list = "**🛒︙متجر الممتلكات:**\n"
    for item, price in shop_items.items():
        shop_list += f"- **{item}**: {price} دينار\n"
    await event.edit(shop_list)

@client.on(events.NewMessage(pattern=r"^.شراء (.*)$"))
async def buy(event):
    user_id = event.sender_id
    item_name = event.pattern_match.group(1).strip()
    wallet = get_user_wallet(user_id)
    
    if "visa" not in wallet:
        await event.edit("**❌︙يجب انشاء فيزا قبل الشراء.**")
        return
        
    if item_name not in shop_items:
        await event.edit("**❌︙هذا المنتج غير موجود في المتجر.**")
        return
        
    price = shop_items[item_name]
    if wallet.get("balance", 0) < price and user_id != DEV_ID:
        await event.edit("**❌︙رصيدك غير كافٍ لشراء هذا المنتج.**")
        return
        
    if user_id != DEV_ID:
        wallet["balance"] -= price
    if "properties" not in wallet:
        wallet["properties"] = []
    wallet["properties"].append(item_name)
    update_user_wallet(user_id, wallet)
    await event.edit(f"**✅︙تم شراء {item_name} بنجاح!\n💰︙رصيدك الآن: {wallet['balance']}**")

# ميزة ممتلكاتي
@client.on(events.NewMessage(pattern="^.ممتلكاتي$"))
async def my_properties(event):
    user_id = event.sender_id
    wallet = get_user_wallet(user_id)
    
    if not wallet.get("properties"):
        await event.edit("**❌︙ليس لديك أي ممتلكات.**")
        return
        
    props = "\n".join(wallet["properties"])
    await event.edit(f"**📦︙ممتلكاتك:**\n{props}")

# ميزة أكواد السحب (للمطور)
@client.on(events.NewMessage(pattern=r"^.سحب (\d+) (\d+)$"))
async def create_code(event):
    if event.sender_id != DEV_ID:
        return
        
    amount = int(event.pattern_match.group(1))
    duration = int(event.pattern_match.group(2))
    code = ''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=8))
    expiry = time.time() + duration
    
    codes = load_data(codes_file)
    codes[code] = {
        "amount": amount,
        "expiry": expiry,
        "created_by": DEV_ID
    }
    save_data(codes, codes_file)
    
    await event.edit(f"**🎫︙تم إنشاء كود سحب:**\n**الكود:** {code}\n**المبلغ:** {amount}\n**الصلاحية:** {duration} ثانية")

@client.on(events.NewMessage(pattern=r"^.استخدام كود (.*)$"))
async def use_code(event):
    user_id = event.sender_id
    code = event.pattern_match.group(1).strip().upper()
    wallet = get_user_wallet(user_id)
    codes = load_data(codes_file)
    
    if code not in codes:
        await event.edit("**❌︙كود غير صحيح.**")
        return
        
    if time.time() > codes[code]["expiry"]:
        await event.edit("**❌︙انتهت صلاحية الكود.**")
        return
        
    amount = codes[code]["amount"]
    wallet["balance"] = wallet.get("balance", 0) + amount
    del codes[code]
    
    save_data(codes, codes_file)
    update_user_wallet(user_id, wallet)
    await event.edit(f"**✅︙تم صرف الكود بنجاح!**\n**💰︙تم إضافة:** {amount}\n**رصيدك الآن:** {wallet['balance']}")

# الأوامر الأصلية (بدون تعديل)
@client.on(events.NewMessage(pattern="^.انشاء فيزا$"))
async def create_visa(event):
    user_id = event.sender_id
    wallet = get_user_wallet(user_id)

    if "visa" in wallet:  
        await event.edit("**⚠️︙لديك فيزا بالفعل.**")  
        return  

    visa_number = "".join([str(random.randint(0, 9)) for _ in range(18)])  
    wallet["visa"] = visa_number  
    wallet["balance"] = 0  
    wallet["daily"] = 0  
    update_user_wallet(user_id, wallet)  

    await event.edit(f"**✅︙تم انشاء فيزتك بنجاح.**\n**💳︙رقم الفيزا:** `{visa_number}`\n**💰︙الرصيد:** 0")

@client.on(events.NewMessage(pattern="^.فيزتي$"))
async def my_visa(event):
    user_id = event.sender_id
    wallet = get_user_wallet(user_id)

    if "visa" not in wallet:  
        await event.edit("**❌︙انت لا تمتلك فيزا.**\n**اكتب `انشاء فيزا` لإنشاء واحدة.**")  
        
        	  

    if user_id == DEV_ID:
        await event.edit(
        f"**💳︙فيزتك:** `{wallet['visa']}`\n"
        f"**💰︙رصيدك لا نهائي لانك المطور**"
    )
    else:
        await event.edit(
        f"**💳︙فيزتك:** `{wallet['visa']}`\n"
        f"**💰︙رصيدك:** {wallet.get('balance', 0)}"
    )
    

@client.on(events.NewMessage(pattern=r"^.تحويل (\d+)$"))
async def transfer(event):
    user_id = event.sender_id
    amount = int(event.pattern_match.group(1))
    reply = await event.get_reply_message()

    if not reply:  
        await event.edit("**❌︙يجب الرد على رسالة المستخدم الذي تريد التحويل له.**")  
        return  

    receiver_id = reply.sender_id  
    if receiver_id == user_id:  
        await event.edit("**❌︙لا يمكنك التحويل إلى نفسك.**")  
        return  

    sender_wallet = get_user_wallet(user_id)  
    if "visa" not in sender_wallet:  
        await event.edit("**❌︙يجب انشاء فيزا قبل التحويل.**")  
        return  

    receiver_wallet = get_user_wallet(receiver_id)  
    if "visa" not in receiver_wallet:  
        await event.edit("**❌︙المستخدم الذي تحاول التحويل له غير مسجل في السورس (ما عنده فيزا).**")  
        return  

    if user_id != DEV_ID and sender_wallet.get("balance", 0) < amount:  
        await event.edit("**❌︙رصيدك غير كافٍ.**")  
        return  

    # تنفيذ التحويل  
    if user_id != DEV_ID:  
        sender_wallet["balance"] -= amount  
    receiver_wallet["balance"] = receiver_wallet.get("balance", 0) + amount  

    update_user_wallet(user_id, sender_wallet)  
    update_user_wallet(receiver_id, receiver_wallet)  

    # إرسال إشعار للمستلم
    try:
        receiver = await client.get_entity(receiver_id)
        await client.send_message(receiver_id,
            f"**🔔︙إشعار تحويل!**\n"
            f"**👤︙المرسل:** [{event.sender.first_name}](tg://user?id={user_id})\n"
            f"**💰︙المبلغ المحول:** {amount}\n"
            f"**💳︙رصيدك الحالي:** {receiver_wallet['balance']}")
    except:
        pass

    await event.edit(f"**✅︙تم تحويل العملات بنجاح.**\n**💸︙المبلغ:** {amount}")

@client.on(events.NewMessage(pattern="^.توبي$"))
async def my_rank(event):
    user_id = event.sender_id
    wallets = load_data(wallets_file)

    balances = []  
    for uid, data in wallets.items():  
        if "visa" in data:  
            balances.append((int(uid), data.get("balance", 0)))  

    # الترتيب حسب الرصيد  
    balances.sort(key=lambda x: x[1], reverse=True)  

    for index, (uid, _) in enumerate(balances, 1):  
        if uid == user_id:  
            await event.edit(f"**📊︙ترتيبك بالتوب هو:** {index}")  
            return  

    await event.edit("**❌︙انت غير موجود بالتوب (ربما لم تنشئ فيزا بعد).**")

@client.on(events.NewMessage(pattern="^.توب$"))
async def top_users(event):
    wallets = load_data(wallets_file)
    balances = []

    for uid, data in wallets.items():  
        if "visa" in data:  
            balances.append((int(uid), data.get("balance", 0)))  

    balances.sort(key=lambda x: x[1], reverse=True)  

    # المطور دائمًا في المرتبة الأولى  
    top_message = "**🏆︙افضل 5 مستخدمين:**\n"  
    top_message += f"1 - [{DEV_ID}](tg://user?id={DEV_ID}) • المطور 👑\n"  

    shown = 1  
    for uid, bal in balances:  
        if uid == DEV_ID:  
            continue  
        shown += 1  
        top_message += f"{shown} - [{uid}](tg://user?id={uid}) • {bal} 💰\n"  
        if shown == 5:  
            break  

    await event.edit(top_message)

@client.on(events.NewMessage(pattern=r"^.كشف(?: (\d+))?$"))
async def show_user_stats(event):
    if event.sender_id != DEV_ID:
        return

    # جلب الآيدي من الرد أو من الرقم في الأمر
    if event.is_reply:
        reply = await event.get_reply_message()
        target_id = reply.sender_id
    else:
        user_arg = event.pattern_match.group(1)
        if not user_arg:
            await event.edit("**❌︙يجب الرد على المستخدم أو وضع آيديه.**")
            return
        target_id = int(user_arg)

    wallet = get_user_wallet(target_id)
    stats = wallet.get("stats", {})
    visa = wallet.get("visa", {})
    balance = wallet.get("balance", 0)

    user = await client.get_entity(target_id)
    name = user.first_name if hasattr(user, "first_name") else "لا يوجد"
    username = f"@{user.username}" if user.username else "لا يوجد"

    message = f"""**📋︙كشف سجل المستخدم:**
**🆔︙الآيدي:** `{target_id}`
**👤︙الاسم:** {name}
**🔗︙المعرف:** {username}
**💰︙الرصيد:** {balance}
**💳︙الفيزا:** `{visa}`

**💸︙عدد السرقات:** {stats.get("steals", 0)}
**📦︙المبلغ المسروق الكلي:** {stats.get("stolen_amount", 0)}

**📈︙عدد الاستثمارات:** {stats.get("invests", 0)}
**💹︙الأرباح الكلية:** {stats.get("profit", 0)}
"""

    await event.edit(message)

@client.on(events.NewMessage(pattern=r"^.تصفير(?: (\w+))?$"))
async def reset_user_data(event):
    if event.sender_id != DEV_ID:
        return  # فقط للمطور

    if not event.is_reply:
        await event.edit("**❌︙يجب الرد على المستخدم الذي تريد تصفيره.**")
        return

    reply = await event.get_reply_message()
    target_id = reply.sender_id
    wallet = get_user_wallet(target_id)

    action = event.pattern_match.group(1)

    if action == "الفيزه":
        wallet["visa"] = None
        update_user_wallet(target_id, wallet)
        await event.edit("**✅︙تم تصفير الفيزا بنجاح.**")
    else:
        wallet["balance"] = 0
        update_user_wallet(target_id, wallet)
        await event.edit("**✅︙تم تصفير رصيد المستخدم بالكامل.**")


@client.on(events.NewMessage(pattern=r'^.م20$'))
async def m20(event):
    text = """**
💸 **شرح الأوامر الخاصة بالتحويل:**

• ⦿ `.انشاء فيزا`
⌯ لانشاء فيزا رقميه خاصه بك.

• ⦿ `.فلوسي`
⌯ يعرض لك رصيدك الحالي بالدينار العراقي.

• ⦿ `.تحويل (المبلغ)` ↶ (عن طريق الرد)
⌯ حول فلوسك لأي شخص بسهولة من خلال الرد على رسالته وكتابة الأمر.

• ⦿ `.تحويل (المبلغ) (الفيزة)`
⌯ حول مبلغ لأي مستخدم عنده فيزة عن طريق كتابة رقم الفيزا.

• ⦿ `.اليومية`
⌯ تستلم يوميتك (1000 دينار) مرة كل 24 ساعة.

`.استثمار + (عدد الفلوس)`
لاستثمار فلوسك


`.سرقه`
بالرد على الشخص لسرقه شيء بسيط من امواله

**[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14**
**"""
    await event.edit(text)
@client.on(events.NewMessage(pattern=r'^.م7$'))
async def commands_m7(event):
    text = """** ♥ يرجـــى التحـلي بالصبر المطور جاي يشتــــغل عله هاي الاضافه **"""
    await event.edit(text)
@client.on(events.NewMessage(pattern=r'^.م18$'))
async def m18_handler(event):
    text = """**⌯︙الأمر ( م18 ) - تغيير اسم الحساب تلقائيًا بالتوقيت 🕰️**

**✿ - وظيفة الأمر:**  
لتغير اسم حسابك التليجرام يجب ان تستخدم هذا الامر

**✿ - طريقة الاستخدام:**  
⌯ أرسل الأمر بهالشكل التالي:  
`name (اسمك الجديد).`  
مثال:  
`name (مرتضى).`

**✿ - النتيجة:**  
راح يصير اسمك مثلاً:  
`مرتضى`

⌯︙**جربه الآن وراقب اسمك يتحدث تلقائياً مع الوقت!** ⌯"""
    await event.edit(text)
from telethon import TelegramClient, events
from telethon.tl.functions.channels import InviteToChannelRequest
import asyncio


current_task = None

@client.on(events.NewMessage(pattern=r'^\.ضيف (.+)'))
async def add_members(event):
    if event.is_group:
        try:
            link = event.pattern_match.group(1)
            from_group = await event.get_input_chat()
            to_group = await client.get_entity(link)
            async for user in client.iter_participants(from_group):
                try:
                    await client(InviteToChannelRequest(to_group, [user.id]))
                    await asyncio.sleep(0.5)
                except:
                    continue
            await event.edit("**✅ تم نقل الأعضاء بنجاح.**")
        except Exception as e:
            await event.edit(f"**❌ حدث خطأ:** `{e}`")

@client.on(events.NewMessage(pattern=r'^\.تفليش$'))
async def ban_members(event):
    if not event.is_group:
        return
    try:
        chat = await event.get_input_chat()
        async for user in client.iter_participants(chat):
            try:
                await client.edit_permissions(chat, user.id, view_messages=False)
                await asyncio.sleep(0.5)
            except:
                continue
        await event.edit("**✅ تم حظر جميع الأعضاء بنجاح.**")
    except Exception as e:
        await event.edit(f"**❌ خطأ:** `{e}`")

@client.on(events.NewMessage(pattern=r'^\.تفليش بالطرد$'))
async def kick_all(event):
    if not event.is_group:
        return
    try:
        chat = await event.get_input_chat()
        async for user in client.iter_participants(chat):
            try:
                await client.kick_participant(chat, user.id)
                await asyncio.sleep(0.5)
            except:
                continue
        await event.edit("**✅ تم طرد الجميع.**")
    except Exception as e:
        await event.edit(f"**❌ خطأ:** `{e}`")

@client.on(events.NewMessage(pattern=r'^\.حظر الكل$'))
async def ban_all(event):
    if not event.is_group:
        return
    chat = await event.get_input_chat()
    async for user in client.iter_participants(chat):
        try:
            await client.edit_permissions(chat, user.id, view_messages=False)
            await asyncio.sleep(0.5)
        except:
            continue
    await event.edit("**✅ تم حظر الجميع.**")

@client.on(events.NewMessage(pattern=r'^\.طرد الكل$'))
async def kick_all_again(event):
    if not event.is_group:
        return
    chat = await event.get_input_chat()
    async for user in client.iter_participants(chat):
        try:
            await client.kick_participant(chat, user.id)
            await asyncio.sleep(0.5)
        except:
            continue
    await event.edit("**✅ تم طرد الجميع.**")

@client.on(events.NewMessage(pattern=r'^\.كتم الكل$'))
async def mute_all(event):
    if not event.is_group:
        return
    chat = await event.get_input_chat()
    async for user in client.iter_participants(chat):
        try:
            await client.edit_permissions(chat, user.id, send_messages=False)
            await asyncio.sleep(0.5)
        except:
            continue
    await event.edit("**✅ تم كتم الجميع.**")

@client.on(events.NewMessage(pattern=r'^\.الغاء التفليش$'))
async def cancel_task(event):
    global current_task
    if current_task:
        current_task.cancel()
        await event.edit("**⛔️ تم إلغاء التفليش/الكتم بنجاح.**")
    else:
        await event.edit("**⚠️ لا توجد عملية جارية لإيقافها.**")
@client.on(events.NewMessage(pattern=r'^.م21$'))
async def m21_commands(event):
    await event.edit("""**⌯︙قائمـة أوامـر التفليش والسيطرة عالكروبات 🚨**

** `.ضيف رابط_مجموعة` **
↝ نسخ الأعضاء من المجموعة الحالية إلى أخرى.

** `.تفليش` **
↝ حظر جميع الأعضاء من الكروب.

** `.تفليش بالطرد` **
↝ طرد كل الأعضاء من الكروب.

** `.حظر الكل` **
↝ حظر كل الأعضاء (بدون طرد).

** `.طرد الكل` **
↝ طرد الأعضاء فقط.

** `.كتم الكل` **
↝ منع الجميع من إرسال رسائل.

** `.الغاء التفليش` **
↝ إلغاء أي عملية تفليش أو كتم شغالة.

⌯︙**إستخدمها بحذر ⚠️** ⌯

**[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14**
""")
import requests
@client.on(events.NewMessage(pattern=".ذكاء(.*)"))
async def handler(event):
    await event.edit("**⎙︙ جارِ الجواب على سؤالك انتظر قليلاً ...**")
    text = event.pattern_match.group(1).strip()
    if text:
        url = f'http://innova.shawrma.store/api/v1/gpt3?text={text}'
        response = requests.get(url).text
        await event.edit(response)
    else:
        await event.edit("يُرجى كتابة رسالة مع الأمر للحصول على إجابة.")
is_Reham = False
No_group_Joker = "@Rrtdhtf"
active_aljoker = []

@client.on(events.NewMessage(pattern=".تفعيل الذكاء"))
async def enable_bot(event):
    global is_Reham
    if not is_Reham:
        is_Reham = True
        active_aljoker.append(event.chat_id)
        await event.edit("**⎙︙ تم تفعيل امر الذكاء الاصطناعي سيتم الرد على اسئلة الجميع عند الرد علي.**")
    else:
        await event.edit("**⎙︙ الزر مُفعّل بالفعل.**")

@client.on(events.NewMessage(pattern=".الذكاء تعطيل"))
async def disable_bot(event):
    global is_Reham
    if is_Reham:
        is_Reham = False
        if event.chat_id in active_aljoker:
            active_aljoker.remove(event.chat_id)
        await event.edit("**⎙︙ تم تعطيل امر الذكاء الاصطناعي.**")
    else:
        await event.edit("**⎙︙ الزر مُعطّل بالفعل.**")

@client.on(events.NewMessage(incoming=True))
async def reply_to_hussein(event):
    if not is_Reham:
        return
    if event.is_private or event.chat_id not in active_aljoker:
        return
    message = event.message
    if message.reply_to_msg_id:
        reply_message = await event.get_reply_message()
        me = await event.client.get_me()
        if reply_message.sender_id == me.id:
            if hasattr(event.chat, "username") and event.chat.username == No_group_Joker:
                return
            text = urllib.parse.quote(message.text.strip())
            try:
                response = requests.get(f'http://innova.shawrma.store/api/v1/gpt3?text={text}')
                reply_text = response.json().get("response", "❌ حدث خطأ في تحليل الرد.")
            except Exception as e:
                reply_text = "❌ حدث خطأ أثناء الاتصال بالذكاء الاصطناعي."
            await asyncio.sleep(1)
            await event.edit(reply_text)

@client.on(events.NewMessage(from_users='me', pattern='.م22'))
async def show_m17_commands(event):
    m17_text = """**
<━━━[★] اوامر الذكاء الاصطناعي [★]━━━>
		`.ذكاء`
▪︎ مثال اكتب .ذكاء : السؤال

		`.الذكاء تفعيل`
▪︎ يقوم بتشغيل الذكاء الاصطناعي في حسابك 

		`.الذكاء تعطيل`
▪︎ يقوم بإيقاف الذكاء الاصطناعي في الحساب 
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
**[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14**
**"""    
    await event.edit(m17_text)
YOUTUBE_API_KEY = 'AIzaSyBfb8a-Ug_YQFrpWKeTc88zuI6PmHVdzV0'
YOUTUBE_API_URL = 'https://www.googleapis.com/youtube/v3/search'

@client.on(events.NewMessage(from_users='me', pattern=r'.يوتيوب (.+)'))
async def youtube_search(event):
    await event.delete()
    query = event.pattern_match.group(1)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(YOUTUBE_API_URL, params={
            'part': 'snippet',
            'q': query,
            'key': YOUTUBE_API_KEY,
            'type': 'video',
            'maxResults': 1
        }) as response:
            data = await response.json()
            if data['items']:
                video_id = data['items'][0]['id']['videoId']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                await event.edit(f"📹 هنا رابط الفيديو الذي تم العثور عليه:\n{video_url}")
            else:
                await event.edit("⎙ لم يتم العثور على فيديو يتطابق مع العنوان المطلوب.")
from telethon import events
import aiohttp
import os

@client.on(events.NewMessage(from_users='me', pattern=r'.يوت(?: |$)(.*)'))
async def download_audio(event):
    await event.delete()
    search_query = event.pattern_match.group(1).strip()

    if not search_query:
        await event.edit("⎙ يرجى إرسال اسم المقطع المطلوب بعد الأمر .تحميل")
        return

    try:
        async with aiohttp.ClientSession() as session:
            api_url = 'http://145.223.80.56:5001/get'
            params = {'q': search_query}

            async with session.get(api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    audio_url = data.get("رابط الصوت") or data.get("\u0631\u0627\u0628\u0637 \u0627\u0644\u0635\u0648\u062a")

                    if not audio_url:
                        await event.respond("⎙ لم يتم العثور على نتائج للبحث المطلوب")
                        return

                    try:
                        await event.respond("⏳ جاري تحميل الصوت...")
                        async with session.get(audio_url) as aud_resp:
                            if aud_resp.status == 200:
                                audio_data = await aud_resp.read()
                                with open('temp_audio.mp3', 'wb') as f:
                                    f.write(audio_data)

                                sender = await event.get_sender()
                                sender_name = sender.first_name or "مستخدم"
                                sender_username = f"@{sender.username}" if sender.username else "بدون معرف"
                                sender_link = f"https://t.me/{sender.username}" if sender.username else "https://t.me"

                                caption = f"**تم تحميل اغنيه **\n"
                                caption += f"**من قبل [{sender_name}]({sender_link})**\n"
                                caption += f"**[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14**"

                                await client.send_file(
                                    event.chat_id,
                                    file='temp_audio.mp3',
                                    caption=caption,
                                    voice_note=True,
                                    parse_mode='md'
                                )
                                os.remove('temp_audio.mp3')
                            else:
                                await event.respond("⎙ فشل تحميل الصوت")
                    except Exception as aud_e:
                        await event.respond(f"⎙ خطأ في تحميل الصوت: {str(aud_e)}")
                else:
                    error_msg = await response.text()
                    await event.respond(f"⎙ حدث خطأ في الخادم: {error_msg}")

    except Exception as e:
        await event.respond(f"⎙ حدث خطأ أثناء محاولة التنزيل: {str(e)}")
@client.on(events.NewMessage(from_users='me', pattern='.م23'))
async def show_m23_commands(event):
    m23_text = """
<━━━[★] اوامر تحميل [★]━━━>
 • `.يوتيوب (عنوان الفيديو)`
▪︎ يقوم بتحميل من يوتيوب 

 
• `.يوت + رابط الفيديو`
▪︎ يقوم بل بحث عن الأغنية وأرسلها 

ملاحظة مهمة  !!  عند استخدام امر  (.يوتيوب) استخدم رابط الفيديو الذي تم البحث عنه مع امر  (يوت) لتنزيل الصوت

⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
**[𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14**
"""
    await event.edit(m23_text)
import os
import asyncio
from telethon import TelegramClient, events
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio
import yt_dlp



PLAYLIST = []

CHAT_STATUS = {}

SUDO_USERS = [7937540559]  

app = PyTgCalls(client)



def is_music_enabled(chat_id):
    """التحقق مما إذا كانت أوامر الموسيقى مفعلة في المحادثة"""
    return CHAT_STATUS.get(chat_id, {}).get('enabled', False)

async def get_song_info(song_name):
    """الحصول على معلومات ورابط تحميل الأغنية من يوتيوب"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extract_flat': 'in_playlist',
        'default_search': 'ytsearch',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(song_name, download=False)['entries'][0]
            return info['title'], info['url']
        except Exception as e:
            print(f"خطأ في جلب معلومات الأغنية: {e}")
            return None, None

# ---------------- معالجات أوامر البوت ----------------

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل الميوزك$"))
async def activate_music(event):
    CHAT_STATUS[event.chat_id] = {'enabled': True}
    await event.edit("✅ **تم تفعيل أوامر الميوزك في هذه المحادثة.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تعطيل الميوزك$"))
async def deactivate_music(event):
    if is_music_enabled(event.chat_id):
        CHAT_STATUS[event.chat_id]['enabled'] = False
        await event.edit("☑️ **تم تعطيل أوامر الميوزك.**")
    else:
        await event.edit("⚠️ **أوامر الميوزك معطلة بالفعل.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تشغيل$"))
async def play_audio_reply(event):
    if not is_music_enabled(event.chat_id): return
    
    reply = await event.get_reply_message()
    if not reply or not reply.audio:
        return await event.edit("🎧 **يرجى الرد على ملف صوتي لتشغيله.**")

    await event.edit("📥 **جاري التحميل والإضافة إلى القائمة...**")
    file_path = await client.download_media(reply.media)
    song_title = reply.audio.title or os.path.basename(file_path)
    
    PLAYLIST.append({'title': song_title, 'path': file_path})
    await event.edit(f"➕ **تمت الإضافة إلى قائمة الانتظار: `{song_title}`**")

    if not CHAT_STATUS.get(event.chat_id, {}).get('is_playing'):
        await play_next(event.chat_id)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.شغل (.*)"))
async def play_song_name(event):
    if not is_music_enabled(event.chat_id): return
        
    song_name = event.pattern_match.group(1)
    await event.edit(f"🔎 **جاري البحث عن `{song_name}`...**")
    
    title, stream_url = await get_song_info(song_name)
    if not stream_url:
        return await event.edit("❌ **عذرًا، لم يتم العثور على الأغنية.**")

    PLAYLIST.append({'title': title, 'path': stream_url})
    await event.edit(f"➕ **تمت الإضافة إلى قائمة الانتظار: `{title}`**")

    if not CHAT_STATUS.get(event.chat_id, {}).get('is_playing'):
        await play_next(event.chat_id)

async def play_next(chat_id):
    """تشغيل الأغنية التالية في قائمة التشغيل"""
    if not PLAYLIST:
        await client.send_message(chat_id, "⏹️ **انتهت قائمة التشغيل. سأغادر المكالمة.**")
        CHAT_STATUS[chat_id]['is_playing'] = False
        await app.leave_group_call(chat_id)
        return

    song = PLAYLIST.pop(0)
    title, path = song['title'], song['path']
    CHAT_STATUS[chat_id] = {**CHAT_STATUS.get(chat_id, {}), 'is_playing': True, 'is_paused': False}
    
    try:
        await app.join_group_call(
            chat_id,
            AudioPiped(path, HighQualityAudio()),
            stream_type=StreamType().local_stream,
        )
        await client.send_message(chat_id, f"🎶 **بدء تشغيل الآن:**\n**{title}**")
    except Exception as e:
        await client.send_message(chat_id, f"⚠️ **حدث خطأ أثناء محاولة الانضمام أو التشغيل:**\n`{e}`")
        CHAT_STATUS[chat_id]['is_playing'] = False

@app.on_stream_end()
async def on_stream_end_handler(_, update: Update):
    """عندما تنتهي الأغنية، يتم استدعاء هذه الدالة لتشغيل التالية"""
    await play_next(update.chat_id)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف$"))
async def stop_music(event):
    if not is_music_enabled(event.chat_id): return
    
    PLAYLIST.clear()
    CHAT_STATUS[event.chat_id] = {**CHAT_STATUS.get(event.chat_id, {}), 'is_playing': False}
    try:
        await app.leave_group_call(event.chat_id)
        await event.edit("⏹️ **تم إيقاف التشغيل ومسح القائمة ومغادرة المكالمة.**")
    except Exception:
        await event.edit("⏹️ **تم إيقاف التشغيل ومسح القائمة.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.وقف$"))
async def pause_music(event):
    if not is_music_enabled(event.chat_id): return
    if CHAT_STATUS.get(event.chat_id, {}).get('is_playing') and not CHAT_STATUS.get(event.chat_id, {}).get('is_paused'):
        await app.pause_stream(event.chat_id)
        CHAT_STATUS[event.chat_id]['is_paused'] = True
        await event.edit("⏸️ **تم الإيقاف المؤقت.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كمل$"))
async def resume_music(event):
    if not is_music_enabled(event.chat_id): return
    if CHAT_STATUS.get(event.chat_id, {}).get('is_playing') and CHAT_STATUS.get(event.chat_id, {}).get('is_paused'):
        await app.resume_stream(event.chat_id)
        CHAT_STATUS[event.chat_id]['is_paused'] = False
        await event.edit("▶️ **تم استئناف التشغيل.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تخطي$"))
async def skip_song(event):
    if not is_music_enabled(event.chat_id): return
    await event.edit("⏭️ **جاري تخطي الأغنية الحالية...**")
    # إيقاف البث الحالي سيؤدي تلقائيًا إلى تشغيل الدالة on_stream_end
    await app.change_stream(event.chat_id, AudioPiped('')) # خدعة بسيطة لتفعيل on_stream_end

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.التشغيل$"))
async def show_playlist(event):
    if not is_music_enabled(event.chat_id): return
    if not PLAYLIST:
        return await event.edit("📋 **قائمة التشغيل فارغة حاليًا.**")

    msg = "**📋 قائمة التشغيل الحالية:**\n\n"
    for i, song in enumerate(PLAYLIST, 1):
        msg += f"**{i}.** `{song['title']}`\n"
    await event.edit(msg)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.مشغل$"))
async def add_sudo(event):
    reply = await event.get_reply_message()
    if not reply:
        return await event.edit("⚠️ **يرجى الرد على رسالة المستخدم الذي تريد إضافته كمشغل.**")

    try:
        sender = await event.get_sender()
        sender_permissions = await client.get_permissions(event.chat_id, sender)

        if not sender_permissions.is_admin and not sender_permissions.is_creator:
            return await event.edit("🚫 **يجب أن تكون مشرفًا في المجموعة لاستخدام هذا الأمر.**")

        user_to_add_id = reply.sender_id
        if user_to_add_id in SUDO_USERS:
            await event.edit(f"✅ **المستخدم `{user_to_add_id}` هو بالفعل أحد المشغلين.**")
        else:
            SUDO_USERS.append(user_to_add_id)
            await event.edit(f"✅ **تمت إضافة المستخدم `{user_to_add_id}` إلى قائمة المشغلين بنجاح.**")
    except Exception as e:
        await event.edit(f"**حدث خطأ:** `{e}`\nربما لا يمكن استخدام هذا الأمر هنا.")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حذف المشغلين$"))
async def clear_sudo(event):
    try:
        sender = await event.get_sender()
        sender_permissions = await client.get_permissions(event.chat_id, sender)

        if not sender_permissions.is_creator: # فقط مالك المجموعة يمكنه حذف الجميع
            return await event.edit("🚫 **فقط مالك المجموعة يمكنه حذف جميع المشغلين.**")
        
        owner = SUDO_USERS[0] # الاحتفاظ بالمالك الأصلي للبوت
        SUDO_USERS.clear()
        SUDO_USERS.append(owner)
        await event.edit("🗑️ **تم حذف جميع المشغلين باستثناء المالك الأصلي للبوت.**")
    except Exception as e:
        await event.edit(f"**حدث خطأ:** `{e}`")







@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م24$"))
async def send_music_help(event):
    help_text = """
🎵 **  أوامر الميوزك** 🎵

**أهلاً بك! إليك كيفية التحكم بالموسيقى:**

---

**1. تفعيل البوت:**
- لتفعيل أوامر الميوزك في المجموعة:
  ` .تفعيل الميوزك `

**2. تشغيل الأغاني:**
- للبحث عن أغنية وتشغيلها بالاسم:
  ` .شغل <اسم الأغنية> `
- لتشغيل ملف صوتي (بالرد على الرسالة الصوتية):
  ` .تشغيل `

**3. التحكم في التشغيل:**
- لإيقاف الموسيقى مؤقتًا:
  ` .وقف `
- لاستئناف الموسيقى بعد إيقافها:
  ` .كمل `
- لتخطي الأغنية الحالية وتشغيل التالية:
  ` .تخطي `
- لإيقاف الموسيقى نهائيًا ومغادرة المكالمة:
  ` .ايقاف `

**4. إدارة القائمة والمشغلين:**
- لعرض قائمة الأغاني المنتظرة:
  ` .التشغيل `
- لإضافة مشرف جديد (يجب أن تكون مشرفًا في المجموعة وترد على رسالته):
  ` .مشغل `
- لحذف جميع المشغلين (للمالك فقط):
  ` .حذف المشغلين `

---
※ **ملاحظة:** الأوامر الموضوعة بين ` ` قابلة للنسخ بمجرد الضغط عليها.
"""
    await event.edit(help_text)


@client.on(events.NewMessage(outgoing=True, pattern=r'\.مغادرة القنوات'))
async def leave_channels(event):
    await event.edit("**جارٍ مغادرة القنوات...**")
    async for dialog in client.iter_dialogs():
        if dialog.is_channel and not (dialog.is_group or dialog.entity.admin_rights or dialog.entity.creator):
            await client.delete_dialog(dialog)
    await event.edit("**تم مغادرة جميع القنوات**")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.مغادرة الكروبات'))
async def leave_groups(event):
    await event.edit("**جارٍ مغادرة الكروبات...**")
    async for dialog in client.iter_dialogs():
        if dialog.is_group and not (dialog.entity.admin_rights or dialog.entity.creator):
            try:
                await client.delete_dialog(dialog)
            except Exception as e:
                print(f"حدث خطأ أثناء مغادرة الكروب {dialog.name}: {e}")  
    await event.edit("**تم مغادرة جميع الكروبات**")
@client.on(events.NewMessage(from_users='me', pattern='.م25'))
async def show_m60_commands(event):
    m60_text = """**
<━━━[★] اوامر المغادرة [★]━━━>
 • `.مغادرة القنوات`
 
▪︎ لمغادرة جميع القنوات التي تمتلكها باستثناء القنوات التي انت مالكها او مشرف فيها 

 • `.مغادرة الكروبات`
 
▪︎ لمغادرة جميع المجموعات باستثناء المجموعات التي انت مالكها او مشرف فيها 

ملاحضه ⚠️ – هاذي الاوامر من خلاله يتم مغادرة القنوات او المجموعات بالكامل فانتبه 
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆ [𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14
**"""
    await event.edit(m60_text)
mmmm = """
\033[031m
─────▄████▀█▄
───▄█████████████████▄
─▄█████.▼.▼.▼.▼.▼.▼▼▼▼
███████    
████████▄▄▲.▲▲▲▲▲▲▲
████████████████████▀▀⠀
\033[0m
  𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍 up and running
"""
os.system("clear")  
print(mmmm)
import os
import subprocess
import sys
import asyncio
from telethon import TelegramClient, events

# بيانات البوت
BRANCH = "main"
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))


@client.on(events.NewMessage(pattern=r'^\.تحديث$'))
async def update_and_restart(event):
    await edit_or_reply(event, f"ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍 - تحـديثـات السـورس\n**•─────────────────•**\n\n**⪼ يتم تنصيب التحديث  انتظر 🌐 ،**")
    try:
        os.chdir(PROJECT_PATH)
        
        subprocess.run(["git", "fetch", "origin"], check=True)
        
        
        status = subprocess.run(["git", "status", "-uno"], capture_output=True, text=True)
        if "up to date" in status.stdout.lower():
            await event.edit("**لايـــوجد تحديث 🤷🏼‍♂️**")
            return

        subprocess.run(["git", "reset", "--hard", f"origin/{BRANCH}"], check=True)

        await event.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍 - تحـديثـات السـورس\n**•─────────────────•**\n\n**⇜ يتـم تحـديث ســورس سنــايبر .. انتظـر . .🌐**\n\n%𝟷𝟶 ▬▭▭▭▭▭▭▭▭▭")
        await asyncio.sleep(1)
        await event.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍 - تحـديثـات السـورس\n**•─────────────────•**\n\n**⇜ يتـم تحـديث ســورس سنــايبر .. انتظـر . .🌐**\n\n%𝟸𝟶 ▬▬▭▭▭▭▭▭▭▭")
        await asyncio.sleep(1)
        await event.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍 - تحـديثـات السـورس\n**•─────────────────•**\n\n**⇜ يتـم تحـديث ســورس سنــايبر .. انتظـر . .🌐**\n\n%𝟹𝟶 ▬▬▬▭▭▭▭▭▭▭")
        await asyncio.sleep(1)
        await event.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍 - تحـديثـات السـورس\n**•─────────────────•**\n\n**⇜ يتـم تحـديث ســورس سنــايبر .. انتظـر . .🌐**\n\n%𝟺𝟶 ▬▬▬▬▭▭▭▭▭▭")
        await asyncio.sleep(1)
        await event.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍 - تحـديثـات السـورس\n**•─────────────────•**\n\n**⇜ يتـم تحـديث ســورس سنــايبر .. انتظـر . .🌐**\n\n%𝟻𝟶 ▬▬▬▬▬▭▭▭▭▭")
        await asyncio.sleep(1)
        await event.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍 - تحـديثـات السـورس\n**•─────────────────•**\n\n**⇜ يتـم تحـديث ســورس سنــايبر .. انتظـر . .🌐**\n\n%𝟼𝟶 ▬▬▬▬▬▬▭▭▭▭")
        await asyncio.sleep(1)
        await event.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍 - تحـديثـات السـورس\n**•─────────────────•**\n\n**⇜ يتـم تحـديث ســورس سنــايبر .. انتظـر . .🌐**\n\n%𝟽𝟶 ▬▬▬▬▬▬▬▭▭▭")
        await asyncio.sleep(1)
        await event.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍 - تحـديثـات السـورس\n**•─────────────────•**\n\n**⇜ يتـم تحـديث ســورس سنــايبر .. انتظـر . .🌐**\n\n%𝟾𝟶 ▬▬▬▬▬▬▬▬▭▭") 
        await asyncio.sleep(1)
        await event.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍 - تحـديثـات السـورس\n**•─────────────────•**\n\n**⇜ يتـم تحـديث ســورس سنــايبر .. انتظـر . .🌐**\n\n%𝟿𝟶 ▬▬▬▬▬▬▬▬▬▭") 
        await asyncio.sleep(1)
        await event.edit("ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍 - تحـديثـات السـورس\n**•─────────────────•**\n\n**⇜ يتـم تحـديث ســورس سنــايبر .. انتظـر . . .🌐**\n\n%𝟷𝟶𝟶 ▬▬▬▬▬▬▬▬▬▬💯") 
        
        await event.edit(f"ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍 - تحـديثـات السـورس\n**•─────────────────•**\n\n**•⎆┊تم التحـديث ⎌ بنجـاح**\n**•⎆┊جـارِ إعـادة تشغيـل ســورس ســـنايبر ⎋ **\n**•⎆┊انتظـࢪ مـن 2 - 1 دقيقـه . . .📟**")
        
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        await event.respond(f"**حدث خطا اثناء التحديث ❌**")

#حب احمد المطي لاتغير شيء بتحديث هاذ 👍🏻#
@client.on(events.NewMessage(pattern="/N"))
async def _(event):
    user = await event.get_sender()
    mm_dev = (2110304954,)  
    if user.id in mm_dev:
        await event.reply(f"**أهلًا بك عزيزي  ٱبَا قُأدِسُ اَلْكَاهِنْ اَلْاِسْوَد - @ES99Y**")

@client.on(events.NewMessage(pattern="/M"))
async def _(event):
    user = await event.get_sender()
    mm_dev = (7937540559,)  
    if user.id in mm_dev:
        await event.reply(f"**أهلًا بك عزيزي مرتضى – @M_R_Q_P**")
uu = """**تـم تــــشغيل ســورس سنـايبر بنجاح
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
تـــحديثات السورس – [𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) 

مـــطور الســــورس – @M_R_Q_P
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
اكتـــب `.الاوامر` لــــعرض الاوامر**"""
    
from telethon import TelegramClient, events
import os
import asyncio





from telethon import TelegramClient, events
import requests
from user_agent import generate_user_agent  




cookies = {
    'csrftoken': '0qCrY5C6U3l0pPZC5whekE',
    'mid': 'aLwkRQABAAGr1Z4Afmt8o5rJiUnt',
    'datr': 'RSS8aI947eeFICnGkp3xIIzK',
    'ig_did': '823C3C9E-623F-423B-BEF0-5B0D72A3D199',
    'ig_nrcb': '1',
    'dpr': '3.0234789848327637',
    'wd': '891x1671',
    'ps_l': '1',
    'ps_n': '1',
}

headers = {
    'authority': 'www.instagram.com',
    'accept': '*/*',
    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
    'referer': 'https://www.instagram.com/',
    'sec-ch-prefers-color-scheme': 'dark',
    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'user-agent': str(generate_user_agent()),
    'x-asbd-id': '359341',
    'x-csrftoken': cookies['csrftoken'],
    'x-ig-app-id': '936619743392459',
    'x-requested-with': 'XMLHttpRequest',
}

@client.on(events.NewMessage(pattern=r'^.انستا (.+)'))
async def insta_info(event):
    user = event.pattern_match.group(1)
    params = {'username': user}

    try:
        response = requests.get(
            'https://www.instagram.com/api/v1/users/web_profile_info/',
            params=params,
            cookies=cookies,
            headers=headers,
        ).json()

        data = response['data']['user']

        nam = data.get('full_name', 'None')
        fol = data['edge_followed_by']['count']
        fos = data['edge_follow']['count']
        ido = data.get('id', 'None')
        isp = data.get('is_private', False)
        op = data['edge_owner_to_timeline_media']['count']
        busines = data.get('is_business_account', False)

        ff = f'''
╔══✪〘 𝐈𝐍𝐅𝐎𝐑𝐌𝐀𝐓𝐈𝐎𝐍 〙✪══╗
[*] NAME        : {nam}
[*] FOLLOWERS   : {fol}
[*] FOLLOWING   : {fos}
[*] ID          : {ido}
[*] is_private  : {isp}
[*] POSTS       : {op}
[*] Business    : {busines}
[*] LINK        : https://www.instagram.com/{user}
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆ [𝗦𝗢𝗨𝗥𝗖𝗘 𝙎𝙉𝙄𝙋𝙀𝙍](t.me/l_l_T14) – @l_l_T14 
'''
        await event.edit(ff)
    except Exception as e:
        print(f'❌ حدث خطأ: {e}')

import asyncio
import json
from telethon import events


is_publishing = False


custom_groups_file = "custom_groups.json"


try:
    with open(custom_groups_file, "r") as f:
        custom_groups = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    custom_groups = []


@client.on(events.NewMessage(outgoing=True, pattern=r"^.اضف كروب (.+)$"))
async def add_group(event):
    
    user = event.pattern_match.group(1)
    try:
        entity = await client.get_entity(user)
        if not (entity.megagroup or entity.gigagroup):
            return await event.edit("**᯽︙ يجب اضافة كروب وليس قناة 🚫**")
    except Exception:
        return await event.edit("**᯽︙ لم استطع العثور على الكروب!!**")

    if user not in custom_groups:
        custom_groups.append(user)
        with open(custom_groups_file, "w") as f:
            json.dump(custom_groups, f)
        await event.edit("**᯽︙ تـم اضافة الكروب ✅**")
    else:
        await event.edit("**᯽︙ الكروب موجود بالفعل ✅**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^.حذف كروب (.+)$"))
async def remove_group(event):
    """Removes a group from the custom publishing list."""
    user = event.pattern_match.group(1)
    if user in custom_groups:
        custom_groups.remove(user)
        with open(custom_groups_file, "w") as f:
            json.dump(custom_groups, f)
        await event.edit("**᯽︙ تـم حذف الكروب ✅**")
    else:
        await event.edit("**᯽︙ الكروب غير موجود ✅**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^.عرض الكروبات$"))
async def list_groups(event):
    """Lists all groups in the custom publishing list."""
    if not custom_groups:
        await event.edit("**᯽︙ لا يوجد كروبات مضافة ✅**")
    else:
        txt = "**᯽︙ الكروبات المخصصة:\n**" + "\n".join(f"- {g}" for g in custom_groups)
        await event.edit(txt)



async def parse_args(pattern_match):
   
    args = pattern_match.group(1).strip().split()
    try:
        sleep_time = int(args[0])
        repeat_count = int(args[1]) if len(args) > 1 else 1
        return sleep_time, repeat_count
    except (ValueError, IndexError):
        return None, None

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نشر خاص (.+)"))
async def private_publish(event):
    
    global is_publishing
    sleep_time, repeat_count = await parse_args(event.pattern_match)
    if sleep_time is None:
        return await event.edit("**᯽︙ الصيغة خاطئة. الاستخدام: .نشر خاص (الثواني) (التكرار - اختياري)**")

    reply = await event.get_reply_message()
    if not reply:
        return await event.edit("**᯽︙ يجب الرد على الرسالة التي تريد نشرها**")

    is_publishing = True
    await event.edit(f"**᯽︙ جاري النشر في الخاص كل {sleep_time} ثانية (التكرار: {repeat_count} مرة)**")

    async for dialog in client.iter_dialogs():
        if not is_publishing:
            break
        if dialog.is_user and not dialog.entity.is_self: # Don't send to yourself
            for _ in range(repeat_count):
                if not is_publishing:
                    break
                try:
                    await client.send_message(dialog.entity, reply)
                except Exception as e:
                    print(f"Could not send to {dialog.name}: {e}") # Optional: for debugging
                await asyncio.sleep(sleep_time)
    
    if is_publishing: # If loop finished without being stopped
        await event.respond("**᯽︙ اكتمل النشر في الخاص ✅**")
    is_publishing = False


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نشر مخصص (.+)"))
async def custom_group_publish(event):
    """Publishes a message to custom groups."""
    global is_publishing
    if not custom_groups:
        return await event.edit("**᯽︙ لا يوجد كروبات مضافة لنشر المخصص!!**")

    sleep_time, repeat_count = await parse_args(event.pattern_match)
    if sleep_time is None:
        return await event.edit("**᯽︙ الصيغة خاطئة. الاستخدام: .نشر مخصص (الثواني) (التكرار - اختياري)**")

    message = await event.get_reply_message()
    if not message:
        return await event.edit("**᯽︙ يجب الرد على الرسالة التي تريد نشرها**")

    is_publishing = True
    await event.edit(f"**᯽︙ جاري النشر في الكروبات المخصصة كل {sleep_time} ثانية (التكرار: {repeat_count} مرة) ✅**")

    for group_id in custom_groups:
        if not is_publishing:
            break
        try:
            entity = await client.get_entity(group_id)
            for _ in range(repeat_count):
                if not is_publishing:
                    break
                await client.send_message(entity, message)
                await asyncio.sleep(sleep_time)
        except Exception as e:
            await event.respond(f"**᯽︙ فشل النشر في الكروب {group_id}: {e}**")
            continue
            
    if is_publishing:
        await event.respond("**᯽︙ اكتمل النشر المخصص ✅**")
    is_publishing = False

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نشر($|\s.*)"))
async def group_publish(event):
    
    global is_publishing
    
    
    args_str = event.pattern_match.group(1).strip()
    if not args_str:
        return await event.edit("**᯽︙ الصيغة خاطئة. الاستخدام: .نشر (الثواني) (التكرار - اختياري)**")

    try:
        args = args_str.split()
        sleep_time = int(args[0])
        repeat_count = int(args[1]) if len(args) > 1 else 1
    except (ValueError, IndexError):
        return await event.edit("**᯽︙ يجب كتابة رقم صحيح للثواني والتكرار.**")

    message = await event.get_reply_message()
    if not message:
        return await event.edit("**᯽︙ يجب الرد على الرسالة التي تريد نشرها**")

    is_publishing = True
    await event.edit(f"**᯽︙ جاري النشر في كل المجموعات كل {sleep_time} ثانية (التكرار: {repeat_count} مرة) ✅**")

    async for dialog in client.iter_dialogs():
        if not is_publishing:
            break
        if dialog.is_group:
            try:
                for _ in range(repeat_count):
                    if not is_publishing:
                        break
                    await client.send_message(dialog.entity, message)
                    await asyncio.sleep(sleep_time)
            except Exception as e:
                print(f"Could not send to group {dialog.name}: {e}") # Optional: for debugging

    if is_publishing:
        await event.respond("**᯽︙ اكتمل النشر في المجموعات ✅**")
    is_publishing = False


@client.on(events.NewMessage(outgoing=True, pattern=r"^.ايقاف النشر$"))
async def stop_publishing_handler(event):
    
    global is_publishing
    if is_publishing:
        is_publishing = False
        await event.edit("**᯽︙ تـم ايقاف عملية النشر الحالية ✅**")
    else:
        await event.edit("**᯽︙ لا توجد عملية نشر فعالة لإيقافها.**")



async def main():
    await client.send_message("me", uu)
    await client.start()
    await asyncio.Event().wait()
    

with client:
    client.loop.run_until_complete(main())


