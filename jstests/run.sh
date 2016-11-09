python application.py &
pid=${!}
sleep 3
echo "Started server with pid $pid"
python -m unittest selenium_testrunner.py
retcode=$?
echo "Killing pid $pid"
kill $pid
exit $retcode
