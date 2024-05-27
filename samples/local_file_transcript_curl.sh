# API endpoints:
api_url=https://api.sumit-labs.com
login_ep=login
upload_ep=storage/upload
download_ep=storage/download
transcript=v3/transcript
transcript_status=get_status

credential_file=api-sa.json # your API credentials file

# files:
local_file=test.wav
remote_file=test.wav
transcript_file=test.json
flat_transcript_file=test_flat.json
language="he-IL"

# STEP 1:

# login and get token
resp=$(curl -X POST -H "Content-Type: application/json" -d @$credential_file $api_url/$login_ep)
# return:
# {"request": {"company": "xxx", "domain": "xxx", "email": "xxx", "user": "xxx"}, "success": true, "token": "YOUR.SECRET.TOKEN"}
# take the token from the response
token=$(echo $resp | jq ".token" | sed s/\"//g)
headers="Authorization: Bearer $token"

# get upload link
payload="{\"filename\": \"$remote_file\"}"
resp=$(curl -X POST -H "Content-Type: application/json" -H "$headers" -d "$payload" $api_url/$upload_ep)
# return:
# {"request": {"filename": "test.wav"}, "signed_url": "https://xxxxx/....d267dd0c", "success": true}
# take the url
dest_url=$(echo $resp | jq ".signed_url" | sed s/\"//g)

# upload - "--upload-file" is PUT request for a binary file
curl $dest_url --upload-file $local_file

# send to transcript:
payload="{\"path\": \"$remote_file\", \"output_path\": \"$transcript_file\", \"lang\": \"$language\", \"model\": \"he_gen_v2\", \"flat_output_path\": \"$flat_transcript_file\"}"
resp=$(curl -X POST -H "Content-Type: application/json" -H "$headers" -d "$payload" $api_url/$transcript)
echo $resp
task_id=$(echo $resp | jq ".response.job_id" | sed s/\"//g)
echo "follow task_id: $task_id"

# STEP 2:

# check for status...
payload="{\"id\": \"$task_id\"}"
resp=$(curl -X POST -H "Content-Type: application/json" -H "$headers" -d "$payload" $api_url/$transcript_status)
echo $resp

# STEP 3:

# download transcription:
# get download link
payload="{\"filename\": \"$transcript_file\"}"  # replace to $flat_transcript_file for the flat version of the transcript
resp=$(curl -X POST -H "Content-Type: application/json" -H "$headers" -d "$payload" $api_url/$download_ep)
src_url=$(echo $resp | jq ".url" | sed s/\"//g)
curl -o $transcript_file $src_url
