*** Settings ***
Resource    ../models/REST_API_Model.robot
Resource    ../models/Kafka_Model.robot
Resource    ../models/AppEvent_Model.robot
Resource    ../models/Databricks_Model.robot
Variables   ../resources/test_users.py

*** Variables ***
${PHASE}    dev

*** Test Cases ***
Check AppEvent Enrichment Job Status
    ${run}    Get Latest Run For A Single Job    992622768224316
    Log    ${run}
    Check Run Status    ${run}    RUNNING    992622768224316

Check Exchange Rate Notebook Output
    ${run_id}    Run Job With Parameter    948537256776744   EUR
    ${output}    Get Run Output    ${run_id}
    Should Not Be True    '${output}' == 'No exchange rates available!'    msg=No exchange rates available!
