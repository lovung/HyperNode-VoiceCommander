source env/bin/activate
start_time=`date +%s`
python3 GoogleCloudPlatform/speech/cloud-client/transcribe.py Hello.wav
end_time=`date +%s`
echo execution time was `expr $end_time - $start_time` s.

# start_time=`date +%s`
# python3 GoogleCloudPlatform/speech/cloud-client/transcribe_async.py Hello.wav
# end_time=`date +%s`
# echo execution time was `expr $end_time - $start_time` s.

# start_time=`date +%s`
# python3 GoogleCloudPlatform/speech/cloud-client/transcribe_streaming.py Hello.wav
# end_time=`date +%s`
# echo execution time was `expr $end_time - $start_time` s.

start_time=`date +%s`
python3 GoogleCloudPlatform/speech/cloud-client/transcribe_streaming_mic.py
end_time=`date +%s`
echo execution time was `expr $end_time - $start_time` s.
