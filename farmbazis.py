import logs
import requests
import time

class FarmBazis:
    web_api_session = None
    session = None
    account = None

    def auth(self, p_account):
        self.account = p_account
        self.session = requests.Session()
        if self.account['user_id'] == '':
            url = f"https://api.farmbazis.ru/Login?customerId={self.account['customer_id']}&password={self.account['password']}"
        else:
            url = f"https://api.farmbazis.ru/Login?userId={self.account['user_id']}&password={self.account['password']}"
        response = self.session.get(url)
        if response:
            response_json = response.json()
            status = response_json['status']
            if status == '0':
                result = True
                self.web_api_session = response_json['sessionId']
            else:
                logs.write_log(f"не удалось авторизоваться  {self.account['desc']}")
                result = False
        else:
            logs.write_log(f"не удалось авторизоваться  {self.account['desc']}")
            result = False
        return result

    def logout(self):
        url = "https://api.farmbazis.ru/Logout"
        self.session.get(url, headers={'WebApiSession': self.web_api_session})
        self.session.close()

    def api_request(self, url, sleep_):
        obj = None
        response = self.session.get(url, headers={'WebApiSession': self.web_api_session})
        if sleep_ is not None:
            time.sleep(1)
        if response:
            response_json = response.json()
            if response_json['status'] == '0':
                obj = response_json
            else:
                logs.write_log(f'Ошибка получения данных {url}')
        else:
            logs.write_log(f'Ошибка получения данных {url}')
        return obj

    def get_dep(self):
        print('выгружаем подразделения')
        dep = {}
        url = f'https://api.farmbazis.ru/BranchList'
        response = self.session.get(url, headers={'WebApiSession': self.web_api_session})
        if response:
            response_json = response.json()
            if response_json['status'] == '0':
                for item in response_json['items']:
                    if item['address'] == '':
                        dep[item['branchId']] = item['branch']
                    else:
                        dep[item['branchId']] = item['address']
            else:
                logs.write_log(f"Ошибка пполучения справочника подразделений {self.account['desc']}")
                dep = False
        else:
            logs.write_log(f"Ошибка получения справочника подразделений {self.account['desc']}")
            dep = False
        return dep


    def get_sales(self, filename, date_from, date_to, dep, type_receipt):
        upd_count = '0'
        fl_continue = True
        while fl_continue:
            url = f"https://api.farmbazis.ru/GoodsMoveOut?customerId={self.account['customer_id']}&updCount={upd_count}&" \
                  f"docTypeId={type_receipt}&dateType=1&d1={date_from}&d2={date_to}"
            response = self.api_request(url, '1')
            if response == None:
                continue
            if upd_count == response['updCount']:
                fl_continue = False
            else:
                fl_continue = True
            upd_count = response['updCount']
            docs = response['document']
            for doc in docs:
                if doc['isDisable'] == True:
                    continue
                for row in doc['row']:
                    if row['isDisable'] == True:
                        continue
                    if doc['branchId'] in dep:
                        store = dep[doc['branchId']].replace("'", ' ')
                    else:
                        store = doc['branchId'].replace("'", ' ')
                    sum_rozn_doc = doc['sumRoznWNDS']
                    num_kkm = doc['deviceId']
                    zavod_kkm = doc['fullDeviceId']
                    sum_disc = doc['sumDiscount']
                    id_rec = doc['localNaklTitleRId']
                    fn = doc['FNFactoryNumber']
                    fpd = doc['FNFiscalSign']
                    fd = doc['FNDocumentNumber']
                    dt_rec = doc['FNDocumentDate']
                    sum_rozn_row = row['sumRoznWNDS']
                    id_good = row['regId']
                    naim = row['tovName']
                    manuf = row['fabr']
                    fix_price = row['fixedPrice']
                    quantity = row['quantity']
                    id_disc = row['discountId']
                    num_doc = doc['naklTitleRId']
                    with open(filename, 'a') as fw:
                        fw.write(f"{store}|{sum_rozn_doc}|{num_kkm}|{zavod_kkm}|{id_disc}|{sum_disc}|{id_rec}|{fn}|{fpd}|"
                                 f"{fd}|{dt_rec}|{sum_rozn_row}|{id_good}|{naim}|{manuf}|{fix_price}|"
                                 f"{quantity}|{id_disc}|{num_doc}")
                        fw.write("\n")
