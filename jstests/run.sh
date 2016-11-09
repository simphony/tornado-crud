python application.py &
pid=${!}
sleep 3
echo "Started server with pid $pid"
`npm bin`/node-qunit-phantomjs "http://127.0.0.1:12345/tests.html"
retcode=$?
echo "Killing pid $pid"
kill $pid
exit $retcode
