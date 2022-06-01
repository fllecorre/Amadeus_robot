1. Create card ( Rest, Cry, Wbs)
2. Integrate + call VCN generator to generate report
3. handle FTP connection to linux machines to perform actions on file
4. Place the created report in the Inbox ( Access to machine) 
5. Check file is Processed / Rejected ( Access to machine )
6. Check BOM (Get card bom with QA Proxy)
7. Check Get card display ( transactions available)
8. Run Job to generate appevents  ( find equivalent to CAPLAQ)
9. Integrate XPP Reporting checks using XPP Apis and libs ( Rest + Python 2.7 libs rework) 
10. XPP configuration + report file clean up 

Repo architecture :
1. Resource (Components | Libs )
2. tests 