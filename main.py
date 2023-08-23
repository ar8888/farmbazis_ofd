import farmbazis
import datetime
import time
import os
import sqlite3


def get_params():
    print("Укажите период. Формат даты ввода ДД.ММ.ГГГГ, например 01.01.2022", "Период может быть не больше 31 дня")
    while True:
        date_from = input("Введите дату начала периода: ")
        date_to = input("Введите дату окончания периода: ")
        date_from_obj = datetime.datetime.strptime(date_from, '%d.%m.%Y').date()
        date_to_obj = datetime.datetime.strptime(date_to, '%d.%m.%Y').date()
        date_from_str = str(date_from_obj)+"%2000:00:00.000"
        date_to_str = str(date_to_obj)+"%2023:59:59.000"
        diff = date_to_obj - date_from_obj
        if date_from_obj > date_to_obj:
            print('Дата начала периода должна быть меньше или равно дате окончания периода')
        elif diff.days > 30:
            print('Период может быть не больше 31 дня')
        else:
            break
    metka = int(time.time())
    filename = f'report_{date_from}_{date_to}_{metka}.txt'
    with open(filename, 'a') as fw:
        header = "Аптека|СуммаРозничнаяЧек|НомерККМ|ЗаводскойККМ|НомерДисконта|СуммаСкидкиПоЧеку|ИДЧека|ФН|" \
                 "ФПД|ФД|ДатаВремяЧека|СуммаРозничная|КодТовара|Наименование|Производитель|ФиксЦена|Кол-во|ИДСкидки|ВнутрНомерДок"
        fw.write(header+"\n")
    return {'date_from': date_from_str, 'date_to': date_to_str, 'filename': filename}


def get_accounts():
    accounts = []
    if os.path.isfile("db.db") is False:
        print("Отсутствует файл db.db Программа будет завершена")
        input("Нажмите любую клавишу")
        exit()
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    sql_text = "select * from `accounts`"
    cursor.execute(sql_text)
    rows = cursor.fetchall()
    for row in rows:
        accounts.append({'user_id': row[0], 'customer_id': row[1], 'password' : row[2], 'desc': row[3]})
    cursor.close()
    conn.close()
    return accounts


params = get_params()
accounts = get_accounts()
for account in accounts:
    fb = farmbazis.FarmBazis()
    if fb.auth(account) is True:
        #clear_data()
        print(f"выгружаем из кабинета {account['desc']}")
        dep = fb.get_dep()
        if not dep:
            print(f"Не обнаружены отделы. Пропускаем выгрузку отчета из аккаунта")
            continue
        fb.get_sales(params['filename'], params['date_from'], params['date_to'], dep, 3)  # наличка
        fb.get_sales(params['filename'], params['date_from'], params['date_to'], dep, 12)  # банковская
        fb.logout()

input("Программа завершила работу.")
