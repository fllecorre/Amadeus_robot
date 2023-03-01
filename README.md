# Parallelization using Pabot Library

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
- [Pabot](https://github.com/robotframework/robotframework)


## **How to**

---

### *How to run the tests in parallel*

- Run tests cases in parallel : 
    - > `pabot --testlevelsplit --outputdir results --variable PHASE:dev tests/suite1.robot`

- Run tests suites in parallel :  :  
    - > `pabot --outputdir results --variable PHASE:dev tests`

- Run test suites and test cases in parallel : 
    - > `pabot --testlevelsplit --outputdir results --variable PHASE:dev  tests`

- Run test cases in 2 parallel executors :
    - > `pabot --processes 2 --testlevelsplit --outputdir results --variable PHASE:dev tests`

- Run one suite sequentially and the other test cases in parallel :
    - > `pabot --ordering .pabotsuitenames-ordering --testlevelsplit --outputdir results --variable PHASE:DEV Tests`
---


