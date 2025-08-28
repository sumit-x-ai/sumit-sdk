# initialize API
from sumit_sdk.api import APIClient
from sumit_sdk.translate_subtitles import TranslateSubtitles

api = APIClient("api-sa.json")
translate_sub = TranslateSubtitles(api)

input_language = "he-IL"  # The language you would like the summary to be in.
output_language = "en-US"  # The language you would like the results.
filename = "a01.json"  # The path of the file that will appear in the storage.
output_filename = "aaa.json"  # The path of the file that will save the result in the storage.

lines_num = 2
max_chars = 36
rephrase = True

payload = translate_sub.build_request(output_language, input_lang=input_language, input_blob_path=filename,
                                      output_blob_path=output_filename, lines_num=lines_num, max_chars=max_chars,
                                      rephrase=rephrase)
res = translate_sub.execute(payload)
print(res)
