# Test for MVP Post Processing of AppEvents

## **Prerequisites**

---

- Python version >= 3.6 (added to PATH)

- Robot Framework environment installed :
    - pip install -r requirements.txt

## **Documentation**

---

### *Official documentation*
- [Robot Framework web site](https://robotframework.org/)
- [Robot Framework documentation](https://robotframework.org/robotframework/)
- [Robot Framework github](https://github.com/robotframework/robotframework)


## **How to**

---

### *How to run the tests in command lines*

- Run a specific test case : 
    - > `robot --outputdir results --variable PHASE:dev --test 01_Kafka_Unprocessed_Topic_Test tests/kafka_topics_tests.robot`

- Run a specific test suite (= all the test cases of the suite) :  
    - > `robot --outputdir results --variable PHASE:dev --include ready tests/enrichment_tests.robot`

- Run the whole folder (= all the test suites) : 
    - > `robot --outputdir results --variable PHASE:dev --include ready tests`

---

### *How to solve timezone issue on unix machine*

- TZ='Europe/Paris'; export TZ