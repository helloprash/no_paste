from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import urllib3
import re
from time import sleep

def actionSubmit(browser,ID):
    browser.find_element_by_id('CTRLRECORDTYPE2').click() #Action Radio
    browser.find_element_by_xpath('//*[@id="CTRLRECORDIDTO"]').send_keys(ID) #CWID 
    browser.find_element_by_xpath('//*[@id="CTRLSubmitCommonPageTop"]').click() #Submit

def selectMultiple(browser, xpath, selectList):
    select = Select(browser.find_element_by_xpath(xpath))
    if select.is_multiple:
        select.deselect_all()
    for eachItem in selectList:
        select.select_by_value(eachItem)
    del select

def currentStep(htmlSource):
    soup = BS(htmlSource, "lxml")
    #soup = BS(open(htmlSource,encoding="utf8"), "lxml")
    center = soup.find_all('center')
    tables = soup.find_all('table',{'id':'TBCALogForm'})

    td = [tr.find_all('td', {'id':'TDStandardText003'}) for tr in tables[0].find_all('tr')]
        
    for eachtd in td:
        if eachtd:
            data = [each.find('font') for each in eachtd]
    step = data[0].text.strip()

    return step

def getpRE(htmlSource):
    soup = BS(htmlSource, "lxml")
    table = soup.find_all('table', {'id':'TBGenericRecs0'})
    tr = table[0].find_all('tr')
    links = tr[1].find_all('a');
    for link in links:
        print(link.text.strip())
        return link.text.strip()

def checkClosure(htmlSource):
    closeStatus = False
    closeMsg = ''
    try:
        soup = BS(htmlSource, "lxml")
        #soup = BS(open(htmlSource,encoding="utf8"), "lxml")
        center = soup.find_all('center')

        #Current step
        tables = soup.find_all('table',{'id':'TBCALogForm'})
        td = [tr.find_all('td', {'id':'TDStandardText003'}) for tr in tables[0].find_all('tr')]
        for eachtd in td:
            if eachtd:
                data = [each.find('font') for each in eachtd]
        step = data[0].text.strip()

        if step == '999':
            closeStatus = True
            closeMsg = 'Closed'
        else:
            tables = soup.find_all('table',{'id':'TBFancyMsgTypeCommon'})

            for ultag in soup.find_all('ul'):
                for litag in ultag.find_all('li'):
                    if "You are not authorized to close this complaint at this time" in litag.text: 
                        closeStatus = False
                        closeMsg = 'You are not authorized to close this complaint'
        
        print('Inside fucntion:', closeMsg, closeStatus)
        return closeMsg, closeStatus


    except Exception as e:
        return e, False

def checkValidation(htmlSource):
    try:
        soup = BS(htmlSource, "lxml")
        #soup = BS(open(htmlSource,encoding="utf8"), "lxml")

        #Username
        tables = soup.find_all('table',{'id':'TBFancyMsgTypeCommon'})
        
        if len(tables) == 0:
            print('No Fancy')
            if currentStep(htmlSource) == '999':
                return True, 'Closed'

        print('Found table')
        tableRow = [tr for tr in tables[0].find_all('tr')]
        
        tableData1 = [td for td in tableRow[0].find_all('td')]
        tableData2 = [td for td in tableRow[1].find_all('td')]

        returnMsg = None
        if tableData1[0].text.strip() == 'Validation Error':
            if 'When the complaint folder has one or more open items,'.lower() in tableData2[0].text.strip().lower():
                returnMsg = 'Please close the open items'
            elif 'You are not authorized to close this complaint at this time'.lower() in tableData2[0].text.strip().lower():
                returnMsg = 'You are not authorized to close this complaint'
            else:
                returnMsg = tableData2[0].text.strip()
        else:
            return True, None
        
        return False, returnMsg
        
        
    except Exception as e:
        print(e)
        

def step90(browser,CFnum, RDPC = 'XXXX', productLine='XXX', productList = 'XXXX', username = 'XXXX',IR = False,IRnum = 'XXXX'):
    url = browser.current_url
    while True:    
        try:
            if browser.current_url != url:
                browser.get(url)
            actionSubmit(browser,CFnum)
            print('Here 090')
            step = currentStep(browser.page_source)
            print(step)
            if step == '090':
                break


            browser.find_element_by_xpath('//*[@id="TBTopTable"]/tbody/tr[3]/td/font/b/a[1]/font/b').click() #Edit 
            try:
                selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Investigation Required - Service Completed']) #Workflow Decision
            except NoSuchElementException:
                selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Investigation Requests Completed'])

            selectMultiple(browser,'//*[@id="CTRLStandardMemo015"]', ['']) #Next Action
            browser.find_element_by_xpath('//*[@id="CTRLStandardDate008"]').clear() #Next Action date
            browser.find_element_by_xpath('//*[@id="CTRLSUBMIT"]').click() #Submit

            CFnum, closeMsg, closeFlag = step140(browser, CFnum, RDPC=RDPC, productList = productList, username=username,IR=IR,IRnum=IRnum)
            return CFnum, closeMsg, closeFlag

        except (urllib3.exceptions.TimeoutError, urllib3.exceptions.ReadTimeoutError) as e:
            print(e)
            print('Read Timeout step 50-90', browser.current_url)
            continue
            #return CFnum, 'Read Timeout Error', False

        except NoSuchElementException as e:
            print('Page load ', browser.current_url)
            print(e)
            continue
            #return CFnum, 'Page load error', False

        except Exception as e:
            return CFnum, e, False

    CFnum, closeMsg, closeFlag = step140(browser, CFnum, RDPC=RDPC, productList = productList, username=username,IR=IR,IRnum=IRnum)
    return CFnum, closeMsg, closeFlag


def step140(browser,CFnum, RDPC = 'XXXX', productLine='XXX', productList = 'XXXX', username = 'XXXX',IR = False,IRnum = 'XXXX'):
    url = browser.current_url
    while True:
        try:
            ifNoExplain = 'XXXX'
            CAR_comments = 'XXXX'
            CA = 'XXXX'
            OtherDetails = 'XXXX'


            #Step 140
            print('Here 140')
            if browser.current_url != url:
                browser.get(url)
            actionSubmit(browser,CFnum)
            pRE(browser,CFnum,productList)

            step = currentStep(browser.page_source)
            print(step)
            if step == '140':
                break

            #get incident date
            soup = BS(browser.page_source, "lxml")
            tables = soup.find_all('table',{'id':'TBCALogForm'})
            td = [tr.find_all('td', {'id':'TDStandardDate001'}) for tr in tables[0].find_all('tr')]
            for eachtd in td:
                if eachtd:
                    data = [each.find('font') for each in eachtd]
            incident_date = data[0].text.strip()

            print(incident_date)

            #get CAR 
            print('Inside IR')
            if IR:
                actionSubmit(browser,IRnum)
                soup = BS(browser.page_source, "lxml")
                #soup = BS(open('CAR.html',encoding="utf8"), "lxml")
                center = soup.find_all('center')
                tables = soup.find_all('table',{'id':'TBCALogForm'})

                #CAR Comments
                td = [tr.find_all('td', {'id':'TDMemo2'}) for tr in tables[0].find_all('tr')]
                for eachtd in td:
                    if eachtd:
                        data = [each.find('font') for each in eachtd]
                CAR_comments = data[0].text.strip()

                #Will C/A be taken at mfr site?
                td = [tr.find_all('td', {'id':'TDStandardText025'}) for tr in tables[0].find_all('tr')]
                for eachtd in td:
                    if eachtd:
                        data = [each.find('font') for each in eachtd]
                CA = data[0].text.strip()

                #If No, Explain
                if CA.lower() == 'no':
                    td = [tr.find_all('td', {'id':'TDStandardMemo018'}) for tr in tables[0].find_all('tr')]
                    for eachtd in td:
                        if eachtd:
                            data = [each.find('font') for each in eachtd]
                    ifNoExplain = data[0].text.strip()

                #Other Details
                td = [tr.find_all('td', {'id':'TDStandardText068'}) for tr in tables[0].find_all('tr')]
                for eachtd in td:
                    if eachtd:
                        data = [each.find('font') for each in eachtd]
                OtherDetails = data[0].text.strip()

                print(ifNoExplain, CAR_comments, CA, OtherDetails)

                actionSubmit(browser,CFnum)

            
            browser.find_element_by_xpath('//*[@id="TBTopTable"]/tbody/tr[3]/td/font/b/a[1]/font/b').click() #Edit

            if len(incident_date) == 0 or incident_date == '12/31/2999': 
                browser.find_element_by_xpath('//*[@id="CTRLStandardDate001"]').clear() #Incident date
                selectMultiple(browser,"//select[contains(@id,'CTRLShortText2')]",['Unknown, not provided']) #Incident date
            else:
                selectMultiple(browser,"//select[contains(@id,'CTRLShortText2')]",['Known']) #Incident date
                
            summary = '\n\nThis complaint meets the criteria for no further investigation per Johnson & Johnson Surgical Vision Complaint Handling procedures. There is no indication of injury, and this event has been assessed as not being reportable. These types of complaints will continue to be monitored through tracking and trending.'
            Product_Deficiency_Identified = 'No'
            Complaint_trend_similar = 'Yes'
            Internal_CAPA_requested = 'No'
            Reason_for_no_CAPA = 'Product Deficiency not identified'

            if not IR and productLine == 'IOL':
                selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Investigation Not Required']) #Workflow decision
                selectMultiple(browser,'//*[@id="CTRLStandardText022"]',['Per SOP']) #Reason Code

            elif IR:
                selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Request Review of Resolved Complaint']) #Workflow decision
                initial_report = '''\n\nSUMMARY OF REPORTED EVENT:
        It was reported that there was a {}. No patient contact was reported.
        '''.format(RDPC)

                summary = '''EVENT DESCRIPTION:
        Refer to ‘Summary of Reported Event’ within the Initial Report

        INVESTIGATION RESULTS:
        Refer to CATSWeb Investigation Request # {0}

        CONCLUSION:
        Refer to CATSWeb Investigation Request # {0}
        '''.format(IRnum)

                #browser.find_element_by_xpath("//textarea[contains(@id,'CTRLStandardMemo001')]").send_keys(initial_report) #initial report

                if ifNoExplain.lower() == 'Known issue - already addressed in a Corrective Action'.lower() and len(CAR_comments) != 0:
                    Product_Deficiency_Identified = 'Yes'
                    Reason_for_no_CAPA = 'Deficiency already investigated (provide REF # in Precedent CAPA Number field)'
                    if 'CAPA'.lower() in CAR_comments.lower() or 'NR'.lower() in CAR_comments.lower() or 'pER'.lower() in CAR_comments.lower():
                        browser.find_element_by_xpath("//input[@id='CTRLStandardText059']").send_keys(CAR_comments)

                if 'Design'.lower() in OtherDetails.lower():
                    selectMultiple(browser,'//*[@id="CTRLStandardText024"]', ['DESIGN DEFICIENCY'])

                elif 'Manufacturing'.lower() in OtherDetails.lower() or 'Mfg'.lower() in OtherDetails.lower():
                    selectMultiple(browser,'//*[@id="CTRLStandardText024"]', ['MANUFACTURING DEFICIENCY'])

                

            elif len(productList) == 1:
                print('Single Product')
                if (not IR and (RDPC == 'Failure to Capture' or RDPC == 'Loss of Capture') and (productList[1].productFormula == 'LOI' or productList[1].productFormula == '0180-1201' or productList[1].productFormula == 'LOI-12' or productList[1].productFormula == 'LOI-14' or productList[1].productFormula == '0180-1401' or productList[1].productFormula == 'LOI-12-BP' or productList[1].productFormula == 'LOI-BP' or productList[1].productFormula == 'LOI-F')) \
            or (not IR and (RDPC == 'Fluid Catchment Filled') and (productList[1].productFormula == 'LOI' or productList[1].productFormula == 'LOI-12' or productList[1].productFormula == 'LOI-12-BP' or productList[1].productFormula == 'LOI-BP' or productList[1].productFormula == 'LOI-F')):
                    print('LOI 140')
                    if not IR:
                        selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Investigation Not Required']) #Workflow decision
                        selectMultiple(browser,'//*[@id="CTRLStandardText022"]',['Per SOP']) #Reason Code
                    else:
                        selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Request Review of Resolved Complaint']) #Workflow decision
                        
                    Reason_for_no_CAPA = 'Other, describe in CAPA Comments'
                    no_CAPA_comments = 'Previously Investigated Complaint per LIB90002'
                    browser.find_element_by_xpath("//textarea[@id='CTRLStandardMemo014']").clear() #Other(Reason for no CAPA comments)
                    browser.find_element_by_xpath("//textarea[@id='CTRLStandardMemo014']").send_keys(no_CAPA_comments)


                elif not IR and ((productLine == 'Phaco' and productList[1].productType == 'Disposable Tubing') or (productLine == 'LVC' and productList[1].productType == 'Patient Interface')) and re.search('[a-zA-Z]', productList[1].serialNum):
                    print('Inside Phaco part')
                    if not IR:
                        selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Investigation Not Required']) #Workflow decision
                        selectMultiple(browser,'//*[@id="CTRLStandardText022"]',['Per SOP']) #Reason Code
                    else:
                        selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Request Review of Resolved Complaint']) #Workflow decision


                elif not IR and RDPC == 'Suction - lack prior to laser fire' and (productList[1].productType == 'Patient Interface') and (productList[1].serialNum[0] == '6'):
                    print('PI 140')
                    if not IR:
                        selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Investigation Not Required']) #Workflow decision
                        selectMultiple(browser,'//*[@id="CTRLStandardText022"]',['Per SOP']) #Reason Code
                    else:
                        selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Request Review of Resolved Complaint']) #Workflow decision

                    Complaint_trend_similar = 'Other (explain in comments)'
                    complaint_trend_comments = 'CAPA-008898 was opened to address this issue'
                    precedent_CAPA = 'CAPA-008898'
                    browser.find_element_by_xpath("//textarea[@id='CTRLStandardMemo016']").clear() #Complaint trend comments
                    browser.find_element_by_xpath("//textarea[@id='CTRLStandardMemo016']").send_keys(complaint_trend_comments)
                    browser.find_element_by_xpath("//input[@id='CTRLStandardText059']").clear() #precedent CAPA
                    browser.find_element_by_xpath("//input[@id='CTRLStandardText059']").send_keys(precedent_CAPA)

                elif not IR and productList[1].productType == 'Patient Interface' and (re.search('[a-zA-Z]', productList[1].serialNum) or (productList[1].serialNum[0] != '6' and RDPC != 'Suction - lack prior to laser fire')):
                    selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Investigation Not Required']) #Workflow decision
                    selectMultiple(browser,'//*[@id="CTRLStandardText022"]',['Per SOP']) #Reason Code

                else:
                    selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Request Review of Resolved Complaint']) #Workflow decision


            elif len(productList) > 1:
                print('Multiple Product')
                selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Request Review of Resolved Complaint']) #Workflow decision
                
            browser.find_element_by_xpath('//*[@id="CTRLStandardMemo004"]').clear() #Final/Summary Report
            browser.find_element_by_xpath('//*[@id="CTRLStandardMemo004"]').send_keys(summary)
            selectMultiple(browser,'//*[@id="CTRLStandardText002"]',[Product_Deficiency_Identified]) #Product Deficiency Identified?
            print('Product_Deficiency_Identified ',Product_Deficiency_Identified)
            selectMultiple(browser,'//*[@id="CTRLStandardText018"]', [Complaint_trend_similar]) #Complaint trend similar?
            print('Complaint_trend_similar ',Complaint_trend_similar)
            selectMultiple(browser,'//*[@id="CTRLStandardText054"]', [Internal_CAPA_requested]) #Internal CAPA requested
            print('Internal_CAPA_requested ',Internal_CAPA_requested)
            selectMultiple(browser,'//*[@id="CTRLStandardText058"]', [Reason_for_no_CAPA]) #Reason for no CAPA
            print('Reason_for_no_CAPA ',Reason_for_no_CAPA)
            
            checkbox = browser.find_element_by_xpath('//*[@id="CTRLStandardYesNo020"]') #Complaint ready for closing
            if checkbox.is_selected():
                pass
            else:
                checkbox.click()
                    
            selectMultiple(browser,'//*[@id="CTRLStandardText049"]', [username])
            browser.find_element_by_xpath('//*[@id="CTRLReasonForEdit"]').clear() #Reason for edit
            browser.find_element_by_xpath('//*[@id="CTRLReasonForEdit"]').send_keys('RTC')
            selectMultiple(browser,'//*[@id="CTRLStandardMemo015"]', ['Closer Review in Process']) #Next Action
            browser.find_element_by_xpath('//*[@id="CTRLStandardDate008"]').clear() #Next Action date
            browser.find_element_by_xpath('//*[@id="CTRLSUBMIT"]').click() #Submit
            print('Submitted')
            CFnum, closeMsg, closeFlag = step999(browser, CFnum, RDPC=RDPC, productList = productList, username=username,IR=IR,IRnum=IRnum)
            return CFnum, closeMsg, closeFlag

        except (urllib3.exceptions.TimeoutError, urllib3.exceptions.ReadTimeoutError) as e:
            print(e)
            print('Read Timeout 90-140', browser.current_url)
            continue
            #return CFnum, 'Read Timeout Error', False

        except NoSuchElementException as e:
            print('Page load ', browser.current_url)
            print(e)
            continue
            #return CFnum, 'Page load error', False

        except Exception as e:
            return CFnum, e, False

    CFnum, closeMsg, closeFlag = step999(browser, CFnum, RDPC=RDPC, productList = productList, username=username,IR=IR,IRnum=IRnum)
    return CFnum, closeMsg, closeFlag

def step999(browser,CFnum, RDPC = 'XXXX', productLine='XXX', productList = 'XXXX', username = 'XXXX',IR = False,IRnum = 'XXXX'):
    url = browser.current_url
    while True:    
        try:
            if browser.current_url != url:
                browser.get(url)
            actionSubmit(browser,CFnum)
            print('Here 999')
            step = currentStep(browser.page_source)
            print(step)
            if step == '999':
                break

            browser.find_element_by_xpath('//*[@id="TBTopTable"]/tbody/tr[3]/td/font/b/a[1]/font/b').click() #Edit
            selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Close Complaint']) #Workflow Decision
            selectMultiple(browser,'//*[@id="CTRLStandardMemo015"]', ['']) #Next Action
            browser.find_element_by_xpath('//*[@id="CTRLStandardDate008"]').clear() #Next Action date
            browser.find_element_by_xpath('//*[@id="CTRLSUBMIT"]').click() #Submit

            sleep(3)
            #closeMsg, closeFlag = checkClosure(browser.page_source)
            closeFlag, closeMsg = checkValidation(browser.page_source)

            print('Inside 999 func', CFnum, closeMsg, closeFlag)
            return CFnum, closeMsg, closeFlag

        except (urllib3.exceptions.TimeoutError, urllib3.exceptions.ReadTimeoutError) as e:
            print(e)
            print('Read Timeout 140-999', browser.current_url)
            continue
            #return CFnum, 'Read Timeout Error', False
        
        except NoSuchElementException as e:
            print('Page load ', browser.current_url)
            print(e)
            continue
            #return CFnum, 'Page load error', False    
        
        except Exception as e:
            print('CATSWeb Error ',e)
            return CFnum, 'CatsWeb Error', False

    sleep(3)
    #closeMsg, closeFlag = checkClosure(browser.page_source)
    
    closeFlag, closeMsg = checkValidation(browser.page_source)
    
    print('Inside 999 func', CFnum, closeMsg, closeFlag)
    return CFnum, closeMsg, closeFlag
    

def pRE(browser,CFnum,productList):

    pREID = getpRE(browser.page_source)
    if pREID:
        actionSubmit(browser,pREID)
        browser.find_element_by_xpath('//*[@id="TBTopTable"]/tbody/tr[3]/td/font/b/a[1]/font/b').click() #Edit 
    
        #Select all dropdown ,'009','017','018','019','020'
        xpathList = ['021','006','007','008']
        for eachXpath in xpathList:
            xpath = '//*[@id="CTRLStandardText{}"]'.format(eachXpath)
            selectMultiple(browser,xpath, ['No'])
        
        comments = 'With the information available at the time of this assessment, there is no indication that the event associated with this pRE is considered potentially reportable.'
        browser.find_element_by_xpath('//*[@id="CTRLStandardMemo003"]').clear()
        browser.find_element_by_xpath('//*[@id="CTRLStandardMemo003"]').send_keys(comments)
        browser.find_element_by_xpath('//*[@id="CTRLReasonForEdit"]').clear()
        browser.find_element_by_xpath('//*[@id="CTRLReasonForEdit"]').send_keys('pRE')
        browser.find_element_by_xpath('//*[@id="CTRLSUBMIT"]').click() #Submit

    for count, product in enumerate(productList):
        print(productList[count+1].productCWID)
        if not productRefresh(browser, productList[count+1].productCWID):
            return CFnum, 'Please select product manufacturer', False

    actionSubmit(browser,CFnum)

def productRefresh(browser, productCWID):
    if productCWID:
        print('Here productRefresh')
        actionSubmit(browser,productCWID)

        soup = BS(browser.page_source, "lxml")
        tables = soup.find_all('table',{'id':'TBCALogForm'})
        td = [tr.find_all('td', {'id':'TDStandardText033'}) for tr in tables[0].find_all('tr')]
        for eachtd in td:
            if eachtd:
                data = [each.find('font') for each in eachtd]
        prodMfr = data[0].text.strip()
        print(prodMfr+' '+str(len(prodMfr)))
        if len(prodMfr) == 0:
            return False

        browser.find_element_by_xpath('//*[@id="TBTopTable"]/tbody/tr[3]/td/font/b/a[1]/font/b').click() #Edit 
        browser.find_element_by_xpath('//*[@id="CTRLRELOAD"]').click() #Refresh product manufacturer
        browser.find_element_by_xpath('//*[@id="CTRLReasonForEdit"]').send_keys('Updated Mfr')
        browser.find_element_by_xpath('//*[@id="CTRLSUBMIT"]').click() #Submit
        #actionSubmit(browser,CFnum)
        return True
        
