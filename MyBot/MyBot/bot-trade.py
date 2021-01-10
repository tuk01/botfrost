import discord
from discord.ext import commands
import httplib2
import apiclient
import time
from oauth2client.service_account import ServiceAccountCredentials
import os

CREDENTIALS_FILE = 'Bot discord trade-7918af75fdd8.json'
spreadsheet_id = '1bvgHWWdi3i8bxl1GQOMZeHUVp4NKrP9rzrcV3fv4KhI'
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)
client = commands.Bot(command_prefix="/")
client.remove_command('help')


@client.event
async def on_command_error(ctx, error):
    pass


@client.command()
@commands.has_permissions(administrator=True)
async def add(ctx, arg1):
    await ctx.send("Ожидание ответа сервера...")
    traders = ctx.message.author.mention
    nick = arg1

    values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range='A1:A9999',
                                                 majorDimension='COLUMNS').execute()
    values = values["values"]

    ar = len(values[0]) + 1
    if (nick in values[0]) == True:
        await ctx.send(
            f"{traders}, ник '{nick}', уже занят и находится в базе данных. Проверьте правильность написания.")
    else:
        list_value = []
        list_value.append(nick)
        list_value.append("None")
        list_value.append(f"{ar};")
        list_value.append(f"0;")
        list_value.append(0)
        list_value.append(0)
        list_value.append(0)
        service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                    body={"valueInputOption": "USER_ENTERED", "data": [
                                                        {"range": f"A{ar}:G{ar}",
                                                         "majorDimension": "ROWS",
                                                         "values": [list_value]},
                                                    ]}).execute()
        await ctx.send(
            f'Ник: "{arg1}" был зарегестрирован в статистике администратором: {traders}. Теперь другие игроки могут оставлять о нём отзывы. \n\n Если вы являетесь игроком с этим ником обратитесь к одному из Администраторов! ')


@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def clear(ctx, arg=10):
    if arg > 50:
        arg = 50
    await ctx.channel.purge(limit=arg + 1)
    time.sleep(0.1)
    await ctx.send("Очистка завершена. {0}".format(str(ctx.message.author.name)))


@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def nullify(ctx, arg):
    try:
        nick = arg
        values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range='A1:A9999',
                                                     majorDimension='COLUMNS').execute()
        values = values["values"]
        if (nick in values[0]) == True:
            arg = (values[0]).index(str(nick)) + 1
            values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=f'C{arg}:D{arg}',
                                                         majorDimension='COLUMNS').execute()
            values = values["values"]
            ind = ((values[0])[0]).split(";")
            ar = ((values[1])[0]).split(";")
            del ind[len(ind) - 1]
            del ar[len(ar) - 1]
            for i in range(len(ind)):
                i_ = ind[i]
                a_ = ar[i]
                if a_ == "0":
                    pass
                else:
                    values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=f'E{i_}',
                                                                 majorDimension='COLUMNS').execute()
                    values = int(((values["values"])[0])[0])
                    if a_ == "+":
                        val = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=f'F{i_}',
                                                                  majorDimension='COLUMNS').execute()
                        val = int(((val["values"])[0])[0])
                        val -= 1
                        values -= 1
                        service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                                    body={"valueInputOption": "USER_ENTERED", "data": [
                                                                        {"range": f"E{i_}",
                                                                         "majorDimension": "ROWS",
                                                                         "values": [[values]]},
                                                                        {"range": f"F{i_}",
                                                                         "majorDimension": "ROWS",
                                                                         "values": [[val]]},
                                                                    ]}).execute()
                    elif a_ == "-":
                        val = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=f'G{i_}',
                                                                  majorDimension='COLUMNS').execute()
                        val = int(((val["values"])[0])[0])
                        values += 1
                        val -= 1
                        service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                                    body={"valueInputOption": "USER_ENTERED", "data": [
                                                                        {"range": f"E{i_}",
                                                                         "majorDimension": "ROWS",
                                                                         "values": [[values]]},
                                                                        {"range": f"G{i_}",
                                                                         "majorDimension": "ROWS",
                                                                         "values": [[val]]},
                                                                    ]}).execute()
                    else:
                        await ctx.send("Непредвиденная ошибка в Базе данных. Обратитесь к управляющему сервера")
                        break

            text = []
            text.append(f"{ind[0]};")
            text.append(f"{ar[0]};")
            service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                        body={"valueInputOption": "USER_ENTERED", "data": [
                                                            {"range": f"C{arg}:D{arg}",
                                                             "majorDimension": "ROWS",
                                                             "values": [text]},
                                                        ]}).execute()
            await ctx.send("Анулирование прошло успешно.")
        else:
            await ctx.send("Такого ника не найдено!")
    except:
        await ctx.send("Необходимо два аргумента!")


@client.command()
async def comment(ctx, *arg1):
    await ctx.send("Ожидание ответа сервера...")
    traders = ctx.message.author.mention
    try:
        nick, vals = arg1[0], arg1[1]

        values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range='B1:B9999',
                                                     majorDimension='COLUMNS').execute()
        values = values["values"]
        if (traders in values[0]) == True:
            ar = (values[0]).index(str(traders)) + 1
            values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range='A1:A9999',
                                                         majorDimension='COLUMNS').execute()
            values = values["values"]
            if (nick in values[0]) == True:
                arg = (values[0]).index(str(nick)) + 1
                values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=f'C{ar}',
                                                             majorDimension='COLUMNS').execute()
                values = (((values["values"])[0])[0]).split(";")
                del values[len(values) - 1]
                if (str(arg) in values) != True:
                    values.append(arg)
                    znach = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=f'D{ar}',
                                                                majorDimension='COLUMNS').execute()
                    znach = (((znach["values"])[0])[0]).split(";")
                    del znach[len(znach) - 1]
                    if (vals == "+" or vals == "-") == True:
                        znach.append(vals)
                        reit = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=f'E{arg}:G{arg}',
                                                                   majorDimension='COLUMNS').execute()
                        reits = int(((reit["values"])[0])[0])
                        plus = int(((reit["values"])[1])[0])
                        minus = int(((reit["values"])[2])[0])

                        if vals == "+":
                            reits += 1
                            plus += 1
                        else:
                            reits -= 1
                            minus += 1
                        list_value = "{0};".format(str(";".join(map(str, values))))
                        list_val = "{0};".format(str(";".join(map(str, znach))))
                        service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                                    body={"valueInputOption": "USER_ENTERED", "data": [
                                                                        {"range": f"C{ar}:D{ar}",
                                                                         "majorDimension": "ROWS",
                                                                         "values": [[list_value, list_val]]},
                                                                        {"range": f"E{arg}:G{arg}",
                                                                         "majorDimension": "ROWS",
                                                                         "values": [[reits, plus, minus]]},
                                                                    ]}).execute()
                        await ctx.send(f"Отзыв оставлен {traders}")
                    else:
                        await ctx.send(
                            f"Ошибка в формате заполнения коментария! Коментарий должен содержать только '/comment *Ник* + или - (в зависимости от комаентария: положительный или отрецательный)'")
                else:
                    await ctx.send(f"Вы уже оставляли отзыв этому пользователю!")
            else:
                await ctx.send(f"Игрока с ником {nick} не существует {traders}, проверьте правильность ввода!")
        else:
            await ctx.send(f"Только зарегестрированные пользователи могут оставлять отзывы")
    except:
        await ctx.send(f"Должно быть два аргумента у команды. Проверьте правильность написания.")


@client.command()
async def statistics(ctx):
    top = []
    values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range='E1:E9999',
                                                 majorDimension='COLUMNS').execute()
    values = (values["values"])[0]
    ni = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range='A1:A9999',
                                             majorDimension='COLUMNS').execute()
    ni = (ni["values"])[0]
    del values[0]
    del ni[0]
    for i in range(len(values)):
        values[i] = int(values[i])
    val = (sorted(values))[::-1]
    for i in val:
        if i < 0:
            break
        else:
            ind = values.index(i)
            top.append((ni[ind], values[ind]))
            values[ind] = None
    text = []
    t = "Номер в топе:   Ник игрока:      Рейтинг:"
    text.append(t)
    for i in range(len(top)):
        nick, rey = top[i]
        prob = 21 - len(nick) - len(str(rey))
        probel = ""
        for a in range(prob):
            probel += " "
        if i + 1 < 10:

            t = f"№ {i + 1}             {nick}{probel}{rey}"
            text.append(t)
        else:
            t = f"№ {i + 1}            {nick}{probel}{rey}"
            text.append(t)
    text = "\n".join(map(str, text))
    await ctx.send(f"""```css\n{text}```""")


@client.command()
async def help(ctx):
    await ctx.send("""
    Команды.
    
    Внимание! Пишите все ники в скобках ибо если ваш ник состоит из двух слов зарегестрируется лишь первое слово вашего ника и вам придёться обратиться к администрации. 
    
    Для администрации:
        1. /add "*ник игрока*" - добавляет ник игрока в статистику в случае, если игрок отсуцтвует в базе данных, но на игрока приходят жалобы.
        2. /clear *количество сообщений* - удаляет необходимое количество сообщений.
        3. /nullify "*ник игрока*" - возможность анулировать все отзывы игрока(Использовать в крайних случаях).
    Для зарегистрированных пользователей:
        1. /comment "*Ник игрока*" (+ или -, если после торговли игрок вас не обманул ставте +, а иначе ставте -) - Позволяет оставить отзыв об игроке повысив или понизив его рейтинг среди других торговцев. Только один раз на каждого торговца!
        2. /statistics - позволяет увидеть 50 лучших торговцев
    Для всех пользователей.
        1. /help - Все команды и их описание.
        3. /record "*Свой ник*" - регестрирует участника в общую базу данных, открывает доступ к новым командам. Ник должен быть записан в скобках, пример: /record "Большой бильбо"
        2. /check "*ник игрока*" - проверяет рейтинг игрока с таким ником. \n\n Внимание! Не лучшая идея торговать с людьми, у которых низкий рейтинг! Если они обманывали других, то могут обмануть и вас!

По любы вопросам можно обращаться к администрации сервера для решения возникши проблем. И несоветуем торговать с игроками ников которых нет в статистике!
    """)


@client.command()
async def record(ctx, arg1):
    await ctx.send("Ожидание ответа сервера...")
    traders = ctx.message.author.mention
    nick = arg1

    values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range='A1:A9999',
                                                 majorDimension='COLUMNS').execute()
    values = values["values"]
    aut_trade = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range='B1:B9999',
                                                    majorDimension='COLUMNS').execute()
    aut_trade = aut_trade["values"]

    ar = len(values[0]) + 1
    if (nick in values[0]) == True:
        await ctx.send(
            f"Ваш ник '{nick}', уже занят {traders} и находится в базе данных. В случае если вы точно не регестрировались - обратитесь к администратору: в некоторых случаях они могут добавлять ники в статистику без ведома автора.")
    elif (str(traders) in aut_trade[0]) == True:
        await ctx.send(
            f"Вы уже зарегестрировали один аккаунт {traders}, если вы опечатались в нике при регестрации обратитесь к администратору.")
    else:
        list_value = []
        list_value.append(nick)
        list_value.append(traders)
        list_value.append(f"{ar};")
        list_value.append("0;")
        list_value.append(0)
        list_value.append(0)
        list_value.append(0)
        service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                    body={"valueInputOption": "USER_ENTERED", "data": [
                                                        {"range": f"A{ar}:G{ar}",
                                                         "majorDimension": "ROWS",
                                                         "values": [list_value]},
                                                    ]}).execute()
        await ctx.send(
            f'{traders} вы были добавлены в статистику под ником: "{nick}". Теперь вы можете торговать и повышать свой рейтинг довереного торговца.')


@client.command()
async def check(ctx, arg1):
    nick = arg1
    values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range='A1:A9999',
                                                 majorDimension='COLUMNS').execute()
    values = (values["values"])[0]
    if (nick in values) == True:
        arg = values.index(nick) + 1
        values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=f'A{arg}:G{arg}',
                                                     majorDimension='COLUMNS').execute()
        values = (values["values"])
        nick = (values[0])[0]
        ID = str((values[1])[0])
        stat = int((values[4])[0])
        su = int((values[5])[0])
        raz = int((values[6])[0])
        res = {stat == 0 and su == 0 and raz == 0: "Торговец новичёк, статистика чиста.",
               stat == 0 and su != 0 and raz != 0: "Игрок подозрителен... Но решение за вами.",
               stat >= 1: "Игрок похож на чесного торговца. Думаю с таким можно поторговать.",
               stat < 0 and stat >= -2: "Статистика плоховата, но это ещё не о всём говорит. Решайте сами.",
               stat < -2: "Игрок очень похож на кидалу. Поищите торговца с лучшей статистикой.",
               stat <= -10: "Явный кидок! Не стоит даже пробовать торговать с таким.",
               stat >= 10: "Игрок судя по рейтингу явно чист. Можно торговать."}[True]
        await ctx.send(f"""```css\n
Ник торговца: {nick}
ID торговца: {ID} ==> Скопируйте его и вставте в текстовое поле если хотите упомянуть и найти торговца(Пример: <@999999999999999999>).
Рейтинг торговца: {stat} ==> Чем выше значение тем меньше шанс того, что игрок вас обманет.
Положительных отзывов: {su} ==> Количество положительных отзывов на игрока.
Отрицательных отзывов: {raz} ==> Количество Отрицательных отзывов на игрока.
Заключение: {res}```""")
    else:
        await ctx.send("короче вот статистика этого додика")


@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.message.author.mention} указаны не все аргументы команды.")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{ctx.message.author.mention} у вас недостаточно прав для этой команды!")
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"{ctx.message.author.mention} такой команды не существует.")


@client.event
async def on_ready():
    channel = client.get_channel(int(733230754817114166))
    await channel.send("Напишите команду /help чтоб увидеть на что я способен!")

token = os.environ.get("bot_token")
client.run(str(tok+en))

"NzkzMDU1MTA5NTg3NTMzODM0.X-msIA.oCkvUVO-bQ3jBjGXIi1RJCCDaOs"