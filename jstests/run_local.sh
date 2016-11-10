#!/bin/bash
# Runs the tests locally in the browser. Note that it leaves the server running
python application.py &
pid=${!}
sleep 3
echo "Started server with pid $pid"
open "http://127.0.0.1:12345/tests.html"
