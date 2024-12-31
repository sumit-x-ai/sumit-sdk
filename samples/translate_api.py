# initialize API
from sumit_sdk.api import APIClient
from sumit_sdk.translate_api import TranslateAPI

api = APIClient("api-sa-prod.json")  # create client
translate = TranslateAPI(api)

texts = ["אני רוצה לתרגם כל מיני משפטים.", "Sometimes I want to translate from English to Hebrew.",
         "Và đôi khi tôi sẽ muốn có một bản dịch từ tiếng Việt sang tiếng Do Thái.", "我这样做时没有给出源语言。"]
lang_trget = ["he", "en", "ar"]

# translate sentences to multiple languages, without specify the origin language
he = []
for line in texts:
    payload = translate.build_request(line, lang_trget)
    res = translate.execute(payload)
    # if you 
    # print(res)
    he.append(res['results']['he'])

print("--------RES_1: Hebrew translation----------")
print(" ".join(he))
print("-------------------------------------------")

texts = """לפעמים נרצה להגביל את מספר התווים של הטקסט המתורגם שנקבל חזרה,
            בגלל שהתרגום לאנגלית יהיה ארוך יותר מבעברית.
            לכן נבקש לתקצר את התרגום.
             כאן לדוגמא אבקש שמספר התוים לא יהיה גדול יותר ממספר התווים של הטקסט הזה.
             בחלק הבא, נעשה את אותו התרגום ללא המגבלה."""
lang_trget = ["en"]

payload = translate.build_request(texts, lang_trget, out_length_limit=len(texts))
res = translate.execute(payload)
# print(res)
en_limit = res['results']['en']

print("--------RES_2----------")
print(en_limit)
print(f"string length: {len(en_limit)}, original input length: {len(texts)}")
print("------------------")

payload = translate.build_request(texts, lang_trget)
res = translate.execute(payload)
# print(res)
en = res['results']['en']

print("-------RES_3-----------")
print(en)
print(f"string length: {len(en)}")
print("------------------")
