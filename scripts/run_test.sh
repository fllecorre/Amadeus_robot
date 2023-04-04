echo $CERT
echo $CKEY

robot --variable cert_filepath:${CERT} --variable key_filepath:${CKEY} --exclude windows -x result.xml -o report.xml tests/cyberark_tests.robot



