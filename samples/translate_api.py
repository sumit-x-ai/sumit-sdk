# initialize API
from sumit_sdk.api import APIClient
from sumit_sdk.translate_api import TranslateAPI

api = APIClient("/home/kobi/PycharmProjects/pythonPostman/commons/apisa-yishay-dev.json", "dev")  # create client
translate = TranslateAPI(api)

texts = ["אני רוצה לתרגם כל מיני משפטים.", "Sometimes I want to translate from English to Hebrew.",
         "Và đôi khi tôi sẽ muốn có một bản dịch từ tiếng Việt sang tiếng Do Thái.", "我这样做时没有给出源语言。"]
lang_trget = ["he", "en", "ar"]

he = []
for line in texts:
    payload = translate.build_request(line, lang_trget)
    res = translate.execute(payload)
    # print(res)
    he.append(res['results']['he'])

print("--------RES_1----------")
print(" ".join(he))
print("------------------")
# break
texts = """לפעמים נרצה להגביל את מספר התווים של הטקסט המתורגם שנקבל חזרה,
            בגלל שהתרגום לאנגלית יהיה ארוך יותר מבעברית.
            לכן נבקש לתקצר את התרגום.
             כאן לדוגמא אבקש שמספר התוים לא יהיה גדול יותר ממספר התווים של הטקסט הזה.
             *** שים לב - התקציר אומנם יחרוג מהמגבלה אך עדיין יקצר את התרגום.
             בחלק הבא, נעשה את אותו התרגום ללא המגבלה."""
en_limit = []
payload = translate.build_request(texts, lang_trget, out_length_limit=len(texts))
res = translate.execute(payload)
# print(res)
en_limit.append(res['results']['en'])

print("--------RES_2----------")
print(" ".join(en_limit))
print(f"מספר התווים: {len(" ".join(en_limit).split())}")
print("------------------")

en = []
payload = translate.build_request(texts, lang_trget)
res = translate.execute(payload)
# print(res)
en.append(res['results']['en'])

print("-------RES_3-----------")
print(" ".join(en))
print(f"מספר התווים: {len(" ".join(en).split())}")
print("------------------")
