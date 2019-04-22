from pathlib import Path
import os,sys, inspect
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import urllib3
import subprocess
from subprocess import Popen
import time
import re
import steps


current_folder = os.getcwd()

class Product:
    no_of_products = 0
    def __init__(self,productType,productFormula,serialNum,productCWID):
        self.productType = productType
        self.productFormula = productFormula
        self.serialNum = serialNum
        self.productCWID = productCWID
        Product.no_of_products += 1

def checkCM(htmlSource):
    soup = BS(htmlSource, "lxml")
    bold = soup.find_all('b')
    for eachText in bold:
        if eachText.text.strip() == 'Complaint Manager Home Page':
            return True
    return False

def checkSession(htmlSource):
    soup = BS(htmlSource, "lxml")
    try:
        tables = soup.find_all('table',{'id':'TBLoginForm'})
        data = ''
        td = [tr.find_all('td', {'class':'msgfield'}) for tr in tables[0].find_all('tr')]
        for eachtd in td:
            if eachtd:
                data = eachtd[0].text.strip()
                print(data)
        print("sessionFalse")
        return False, data

    except:
        print("sessionTrue")
        return True, 'None'

def checkUsername(htmlSource):
    closeStatus = False
    try:
        soup = BS(htmlSource, "lxml")
        #soup = BS(open(htmlSource,encoding="utf8"), "lxml")

        #Username
        tables = soup.find_all('table',{'id':'TBTopTable'})
        rowData = [tr for tr in tables[0].find_all('tr')]

        td = rowData[1].find_all('td')

        for eachtd in td:
            if eachtd:
                data = [each.parent.find('font').findNext('font') for each in eachtd]
                userName = data[0].text.strip().replace('User ', '').replace('may have pending personal tasks.', '')
                userName = re.sub(r'\([^)]*\)', '', userName)
                return userName[:-1]


    except Exception as e:
        print(e)
        return 'Error'


def actionSubmit(browser,ID):
    browser.find_element_by_id('CTRLRECORDTYPE2').click() #Action Radio
    browser.find_element_by_xpath('//*[@id="CTRLRECORDIDTO"]').send_keys(ID) #CWID 
    browser.find_element_by_xpath('//*[@id="CTRLSubmitCommonPageTop"]').click() #Submit
    return browser
    
def getCFDetails(htmlSource):
    username = 'no user'
    RPC = 'no RPC'
    PTC = 'no PTC'
    RDPC = 'No RDPC'
    malfunction_code = 'No Malfunc'
    medical_event = 'No ME'
    pREflag = False
    step = 'No Step'
    productLine = 'No pLine'
    productType = 'No ptype'
    productFormula = 'No pformula'
    serialNum = 'No ser'
    productCWID = 'No prodCWID'
    productCount = False
    fieldServiceFlag = False
    fieldServiceStatus = 'no FSE'
    RDTFlag = False
    IR = False
    IRstep = 'No IRStep'
    IRnum = 'No IRNum'
    productList = dict()

    try:
        soup = BS(htmlSource, "lxml")
        #soup = BS(open(htmlSource,encoding="utf8"), "lxml")
        center = soup.find_all('center')
        tables = soup.find_all('table',{'id':'TBCALogForm'})

        username = checkUsername(htmlSource)

        #Medical event
        td = [tr.find_all('td', {'id':'TDStandardText069'}) for tr in tables[0].find_all('tr')]
        for eachtd in td:
            if eachtd:
                data = [each.find('font') for each in eachtd]
        medical_event = data[0].text.strip()

        #Current step
        td = [tr.find_all('td', {'id':'TDStandardText003'}) for tr in tables[0].find_all('tr')]
        
        for eachtd in td:
            if eachtd:
                data = [each.find('font') for each in eachtd]
        step = data[0].text.strip()

        #Reported Patient Code
        td = [tr.find_all('td', {'id':'TDStandardMemo018'}) for tr in tables[0].find_all('tr')]
        for eachtd in td:
            if eachtd:
                data = [each.find('font') for each in eachtd]
        RPC = data[0].text.strip()
        

        #RDPC
        td = [tr.find_all('td', {'id':'TDStandardMemo013'}) for tr in tables[0].find_all('tr')]
        for eachtd in td:
            if eachtd:
                data = [each.find('font') for each in eachtd]
        RDPC = data[0].text.strip()

        #Malfunction Code
        td = [tr.find_all('td', {'id':'TDStandardMemo020'}) for tr in tables[0].find_all('tr')]
        for eachtd in td:
            if eachtd:
                data = [each.find('font') for each in eachtd]
        malfunction_code = data[0].text.strip()

        #Patient Treatment Code
        td = [tr.find_all('td', {'id':'TDStandardMemo019'}) for tr in tables[0].find_all('tr')]
        for eachtd in td:
            if eachtd:
                data = [each.find('font') for each in eachtd]
        PTC = data[0].text.strip()


        #Product Line
        td = [tr.find_all('td', {'id':'TDStandardText011'}) for tr in tables[0].find_all('tr')]
        for eachtd in td:
            if eachtd:
                data = [each.find('font') for each in eachtd]
        productLine = data[0].text.strip()

        #Product
        try:
            p_tag = soup.find(text='Products').parent
            font_tag = p_tag.parent
            center_tag = font_tag.parent
            next_center_tag = center_tag.findNext('center').findNext('center')
            tables = next_center_tag.find_all('table',{'id':'TBGenericRecs0'})

            
            prodCount = [tr for tr in tables[0].find_all('tr')]
            print(len(prodCount))

            for i in range(1, len(prodCount)):
                print('i',i)
                td = [tr.find_all('td', {'id':'TDRowItem{}6'.format(i)}) for tr in tables[0].find_all('tr')]
                td1 = [tr.find_all('td', {'id':'TDRowItem{}4'.format(i)}) for tr in tables[0].find_all('tr')]
                td2 = [tr.find_all('td', {'id':'TDRowItem{}9'.format(i)}) for tr in tables[0].find_all('tr')]
                td3 = [tr.find_all('td', {'id':'TDRowItem{}1'.format(i)}) for tr in tables[0].find_all('tr')]

                for eachtd, eachtd1, eachtd2, eachtd3 in zip(td,td1,td2,td3):
                    
                    if (eachtd, eachtd1, eachtd2, eachtd3):
                        data = [each.find('font') for each in eachtd if each]
                        data1 = [each.find('font') for each in eachtd1]
                        data2 = [each.find('font') for each in eachtd2]
                        data3 = [each.find('font') for each in eachtd3]

                        if data:
                            productFormula = data[0].text.strip()

                        if data1:
                            productType = data1[0].text.strip()

                        if data2:
                            serialNum = data2[0].text.strip()

                        if data3:
                            productCWID = data3[0].text.strip()
                                 
                #print(productFormula,productType,serialNum,productCWID)        
                productList[i] = Product(productType,productFormula,serialNum,productCWID)

                    
        except AttributeError:
            productFormula = 'No pFormula'
            productType = 'No pType'
            serialNum = 'No ser'
            productCWID = 'No prodCWID'
            productCount = False

        #pRE
        try:
            pREflag = False
            p_tag = soup.find(text='pREs').parent
            font_tag = p_tag.parent
            center_tag = font_tag.parent
            next_center_tag = center_tag.findNext('center').findNext('center')
            pREtables = next_center_tag.find('table',{'id':'TBGenericRecs0'})
            pREtr = pREtables.find_all('tr')

            for i in range(1, len(pREtr)):
                pREtd = [eachtd for eachtd in pREtr[i].find_all('td')]
                data = [item.text.strip() for item in pREtd]
                for j in range(3,13):
                    if data[j].lower() == 'Yes'.lower():
                        pREflag = True

        except AttributeError:
            pREflag = False

        #RDT Check

        try:
            RDT_tag = soup.find(text='---  Reportability Decision Trees  ---').parent
            RDTFlag = True


        except AttributeError:
            RDTFlag = False

        except Exception as e:
            print(e)
        
        #Field Service
        try:
            ir_tag = soup.find('font', face="Verdana", size="2", text='Field Service').parent
            next_center_tag = ir_tag.findNext('center').findNext('center')
            tables = next_center_tag.find_all('table',{'id':'TBGenericRecs0'})
            td = [tr.find_all('td', {'id':'TDRowItem12'}) for tr in tables[0].find_all('tr')]
            for eachtd in td:
                if eachtd:
                    data = [each.find('font') for each in eachtd]
            fieldServiceStatus = data[0].text.strip()
            fieldServiceFlag = True

        except AttributeError:
            fieldServiceFlag = False
            fieldServiceStatus = 'No FSE'

        #Investigation report
        try:
            ir_tag = soup.find(text='Investigation Requests').parent
            font_tag = ir_tag.parent
            center_tag = font_tag.parent
            next_center_tag = center_tag.findNext('center').findNext('center')
            tables = next_center_tag.find_all('table',{'id':'TBGenericRecs0'})
            td = [tr.find_all('td', {'id':'TDRowItem11'}) for tr in tables[0].find_all('tr')]
            td1 = [tr.find_all('td', {'id':'TDRowItem13'}) for tr in tables[0].find_all('tr')]
            for eachtd, eachtd1 in zip(td,td1):
                if (eachtd,eachtd1):
                    data = [each.find('font') for each in eachtd]
                    data1 = [each.find('font') for each in eachtd1]
            IRnum = data[0].text.strip()
            IRstep = data1[0].text.strip()
            IR = True
        except AttributeError:
            IR = False
            IRstep = 'XX'
            IRnum = 'XXXX'
        
        return(True,username,RPC,RDPC,malfunction_code,PTC,medical_event,pREflag,step,productLine,productList,fieldServiceFlag,fieldServiceStatus,RDTFlag,IR,IRstep,IRnum)
    
    except Exception as err:
        print('Here error',err)
        return(False, username,RPC,RDPC,malfunction_code,PTC,medical_event,pREflag,step,productLine,productList,fieldServiceFlag,fieldServiceStatus,RDTFlag,IR,IRstep,IRnum)


def Login(url, site):
    pjs_file = '\\\\'.join(os.path.join(current_folder,"phantomjs.exe").split('\\'))
    print(pjs_file)

    fileFlag = True
    userName = ''
    my_file = Path(pjs_file)
    if not my_file.is_file():
        fileFlag = False
        print('fileError')
        return ('phantomjs.exe file not found',None, False,fileFlag)

    print(url)
    #url = 'http://cwqa/CATSWebNET/'

    while True:
        try :
            browser = webdriver.PhantomJS(executable_path = pjs_file, desired_capabilities={'phantomjs.page.settings.resourceTimeout': '5000'})
            browser.implicitly_wait(3)
            browser.set_page_load_timeout(100) 
            browser.get(url)

            if site == 'CWPROD':
                browser.get('http://cwprod/CATSWebNET/')

            elif site == 'CWQA':
                browser.get('http://cwqa/CATSWebNET/')

            elif site == 'CWDEV':
                browser.get('https://cwdev.jnj.com/catswebnet/')
            
            sessionFlag, returnMsg = checkSession(browser.page_source)


            if not sessionFlag:
                current_url = browser.current_url
                browser.quit()
                return ('Session expired. Please enter your logged in url', userName, current_url, sessionFlag, fileFlag)

            userName = checkUsername(browser.page_source)
            
            if site == 'CWPROD':
                userName+=' (Prod)'
            elif site == 'CWQA':
                userName+=' (QA)'
            elif site == 'CWDEV':
                userName+=' (Dev)'
            print(browser.current_url)
            return ('Please enter your login information:', userName, browser.current_url, True, fileFlag)

              
        except (urllib3.exceptions.TimeoutError, urllib3.exceptions.ReadTimeoutError): 
            browser.quit()
            print("Page load Timeout Occured. Quiting !!!")
            continue
            #return ('Page load Timeout Occured. Please try again',None, False)

        except Exception as e:
            print(e)
            continue


def preview(CFnum, main_url):
    print('Preview: ',preview)
    pjs_file = '\\\\'.join(os.path.join(current_folder,"chromedriver.exe").split('\\'))
    batch_file = '\\\\'.join(os.path.join(current_folder,"killChrome.bat").split('\\'))

    my_file = Path(batch_file)

    fileFlag = True
    my_file = Path(pjs_file)
    if not my_file.is_file():
        fileFlag = False
        print('fileError')
        return False, False, 'chromedriver.exe file not found', fileFlag

    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("disable-extensions")
    browser = webdriver.Chrome(pjs_file, chrome_options=chrome_options)
    #main_url = 'http://cwqa/CATSWebNET/main.aspx?WCI=Main&WCE=ViewDashboard&WCU=s%3dU3ABTU2E6N0KP5NMIJHLMQD87GJ7QCIG%7c*~r%3dComplaint%20Owner%20Home%20Page%7c*~q%3d1%7c*~g%3d0'
    
    while True:
        try:
            browser.implicitly_wait(3)
            browser.set_page_load_timeout(100)
            browser.get(main_url)

            sessionFlag, returnMsg = checkSession(browser.page_source)
            if not sessionFlag:
                if returnMsg == 'Your CATSWeb V7 session does not exist.  Please enter your login information:':
                    return sessionFlag, False, 'Your CATSWeb V7 session expired!', fileFlag
           
            print(browser.current_url)

            CM = checkCM(browser.page_source)
            if CM:
                browser.find_element_by_xpath('//*[@id="TDDisplayPart004"]/font/a/font').click() #Load Complaint Owner Home page

            browser = actionSubmit(browser,CFnum)
            return sessionFlag,True, 'None', fileFlag

        except (urllib3.exceptions.TimeoutError, urllib3.exceptions.ReadTimeoutError) as err1:
            print('Read Timeout Error')
            print('Err1', err1)
            continue
            #return sessionFlag, False, 'Read Timeout Error!'

        except Exception as err2:
            print('Err2 ',err2)
            continue


def complaintProcess(CFnum, url):
    print('inside complaintProcess', CFnum, url)
    pjs_file = '\\\\'.join(os.path.join(current_folder,"phantomjs.exe").split('\\'))
    statusMsg = '' 
    statusFlag = False
    fileFlag = True
    
    my_file = Path(pjs_file)
    if not my_file.is_file():
        fileFlag = False
        print('fileError')
        return False, CFnum, 'phantomjs.exe file not found', False, fileFlag
    
    print(pjs_file)
   
    '''
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("disable-extensions")
    '''

    
    while True:
        try:
            print('Not Here')
            browser = webdriver.PhantomJS(executable_path = pjs_file, desired_capabilities={'phantomjs.page.settings.resourceTimeout': '5000'})
            #browser = webdriver.Chrome(pjs_file, chrome_options=chrome_options)
            browser.implicitly_wait(3)
            browser.set_page_load_timeout(100)

            browser.get(url)

            sessionFlag, returnMsg = checkSession(browser.page_source)
            if not sessionFlag:
                return False, CFnum, 'session expired!', False, fileFlag
                    
            print(browser.current_url)

            CM = checkCM(browser.page_source)
            if CM:
                browser.find_element_by_xpath('//*[@id="TDDisplayPart004"]/font/a/font').click()

            browser = actionSubmit(browser,CFnum)
            print("Printed")
            (flag,username,RPC,RDPC,malfunction_code,PTC,medical_event,pREflag,current_step,productLine,productList,fieldServiceFlag,fieldServiceStatus,RDTFlag,IR,IRstep,IRnum) = getCFDetails(browser.page_source)
            print(flag, username,RPC,RDPC,malfunction_code,PTC,medical_event,pREflag,current_step,productLine,productList,fieldServiceFlag,fieldServiceStatus,RDTFlag,IR,IRstep,IRnum)
            print('PTC ', PTC)
            print('RPC ',RPC)
            break

        except (urllib3.exceptions.TimeoutError, urllib3.exceptions.ReadTimeoutError):
            print('Read Timeout Error')
            browser.quit()
            continue
            #return (True, CFnum, 'Read Timeout Error', False)

        except NoSuchElementException as allError:
            print('Page load ', browser.current_url)
            browser.quit()
            print(allError)
            return (True, CFnum, 'Page load error', False, fileFlag)

        except Exception as e:
            print('new error ',e)
            continue

    process_steps = {
                        '050':steps.step90,
                        '090':steps.step140,
                        '140':steps.step999
                    }

    if not flag:
        browser.quit()
        return (True, CFnum,'This is not a valid complaint folder number', False, fileFlag)

    elif current_step == '999':
        browser.quit()
        return (True, CFnum, 'Complaint folder already closed - step {}'.format(current_step), False, fileFlag)

    elif current_step == '020' or current_step == '030':
        browser.quit()
        return (True, CFnum,'Error! The current step is {}. Please move CF to step 40/50'.format(current_step), False, fileFlag)

    elif medical_event.lower() == 'Yes'.lower():
        browser.quit()
        return (True, CFnum,'Medical event is Yes. Cannot process', False, fileFlag)

    elif len(productList) == 0:
        browser.quit()
        return (True, CFnum,'No Product record found', False, fileFlag)

    elif len(RDPC) == 0:
        browser.quit()
        return (True, CFnum, 'Error! Please select atleast one RDPC', False, fileFlag)

    elif len(malfunction_code) == 0:
        browser.quit()
        return (True, CFnum,'Please select a malfunction code', False, fileFlag)

    elif malfunction_code.lower() != 'Not a Reportable Malfunction'.lower():
        browser.quit()
        return (True, CFnum,'Cannot close CF with a Malfunction code', False, fileFlag)

    elif RPC.lower() != 'Not applicable'.lower():
        browser.quit()
        return (True, CFnum,'Cannot close CF with a Reported Patient Code', False, fileFlag)

    elif PTC.lower() != 'Not applicable'.lower():
        browser.quit()
        return (True, CFnum,'Cannot close CF with a Patient Treatment Code', False, fileFlag)

    elif fieldServiceFlag and (fieldServiceStatus.lower() != 'Closed'.lower()):
        browser.quit()
        return (True, CFnum,'Please close the Field Service Record', False, fileFlag)

    elif pREflag:
        browser.quit()
        return (True, CFnum,'pRE is YES. Cannot close', False, fileFlag)

    elif IR and IRstep != '999':
        browser.quit()
        return (True, CFnum, 'IR still open in step {}'.format(IRstep), False, fileFlag)

    elif RDTFlag:
        browser.quit()
        return (True, CFnum, 'RDT present. Cannot close', False, fileFlag)

    elif productList:
        print('passed')
        for count, product in enumerate(productList):
            if len(productList[count+1].productFormula) == 0 or productList[count+1].productFormula.lower() == 'unknown':
                browser.quit()
                return (True, CFnum, 'Error! Formula/Model Number not found. Please update/close manually', False, fileFlag)

            elif len(productList[count+1].productType) == 0 or productList[count+1].productType.lower() == 'unknown':
                browser.quit()
                return (True, CFnum, 'Error! Product Type not found. Please update/close manually', False, fileFlag) 


    #Complaint Processing
        try:
            if not IR and productLine == 'IOL':
                if current_step == '140':
                    CFnum, statusMsg, statusFlag = process_steps[current_step](browser, CFnum, RDPC=RDPC, productLine=productLine, productList = productList, username=username,IR=IR,IRnum=IRnum)
                else:
                    CFnum, statusMsg, statusFlag = process_steps['090'](browser, CFnum, RDPC=RDPC, productLine=productLine, productList = productList, username=username,IR=IR,IRnum=IRnum)
                    
                browser.quit()
                return (True, CFnum, statusMsg, statusFlag, fileFlag) 

            elif len(productList) == 1:
                print('Single Product')

                if not IR and ((productLine == 'Phaco' and productList[1].productType == 'Disposable Tubing') or (productLine == 'LVC' and productList[1].productType == 'Patient Interface')) and re.search('[a-zA-Z]', productList[1].serialNum):
                    print('Inside Phaco part')
                    if current_step == '140':
                        CFnum, statusMsg, statusFlag = process_steps[current_step](browser, CFnum, RDPC=RDPC, productLine=productLine, productList = productList, username=username,IR=IR,IRnum=IRnum)
                    else:
                        CFnum, statusMsg, statusFlag = process_steps['090'](browser, CFnum, RDPC=RDPC, productLine=productLine, productList = productList, username=username,IR=IR,IRnum=IRnum)
                        
                    browser.quit()
                    return (True, CFnum, statusMsg, statusFlag, fileFlag)


                elif not IR and productList[1].productType == 'Patient Interface' and ((productList[1].serialNum[0] == '6' and RDPC == 'Suction - lack prior to laser fire') or re.search('[a-zA-Z]', productList[1].serialNum) or (productList[1].serialNum[0] != '6' and RDPC != 'Suction - lack prior to laser fire')):
                    if current_step == '140':
                        CFnum, statusMsg, statusFlag = process_steps[current_step](browser, CFnum, RDPC=RDPC, productLine=productLine, productList = productList, username=username,IR=IR,IRnum=IRnum)
                    else:
                        CFnum, statusMsg, statusFlag = process_steps['090'](browser, CFnum, RDPC=RDPC, productLine=productLine, productList = productList, username=username,IR=IR,IRnum=IRnum)
                    
                    browser.quit()
                    return (True, CFnum, statusMsg, statusFlag, fileFlag)
    
            
                elif not IR and ((RDPC == 'Failure to Capture' or RDPC == 'Loss of Capture') and (productList[1].productFormula == 'LOI' or productList[1].productFormula == '0180-1201' or productList[1].productFormula == 'LOI-12' or productList[1].productFormula == 'LOI-14' or productList[1].productFormula == '0180-1401' or productList[1].productFormula == 'LOI-12-BP' or productList[1].productFormula == 'LOI-BP' or productList[1].productFormula == 'LOI-F'))\
                or ((RDPC == 'Fluid Catchment Filled') and (productList[1].productFormula == 'LOI' or productList[1].productFormula == 'LOI-12' or productList[1].productFormula == 'LOI-12-BP' or productList[1].productFormula == 'LOI-BP' or productList[1].productFormula == 'LOI-F')):
                    print('Inside LOI part')
                    if current_step == '140':
                        CFnum, statusMsg, statusFlag = process_steps[current_step](browser, CFnum, RDPC=RDPC, productLine=productLine, productList = productList, username=username,IR=IR,IRnum=IRnum)
                    else:
                        CFnum, statusMsg, statusFlag = process_steps['090'](browser, CFnum, RDPC=RDPC, productLine=productLine, productList = productList, username=username,IR=IR,IRnum=IRnum)
                        
                    browser.quit()
                    return (True, CFnum, statusMsg, statusFlag, fileFlag)  


                else:
                    print('Inside Other')
                    CFnum, statusMsg, statusFlag = process_steps[current_step](browser, CFnum, RDPC=RDPC, productLine=productLine, productList = productList, username=username,IR=IR,IRnum=IRnum)
                    print(CFnum, statusMsg, statusFlag)
                    browser.quit()
                    return (True, CFnum, statusMsg, statusFlag, fileFlag)

            else:
                print('Multiple product')
                CFnum, statusMsg, statusFlag = process_steps[current_step](browser, CFnum, RDPC=RDPC, productLine=productLine, productList = productList, username=username,IR=IR,IRnum=IRnum)
                print(CFnum, statusMsg, statusFlag)
                browser.quit()
                return (True, CFnum, statusMsg, statusFlag, fileFlag)


        except KeyError:
            browser.quit()
            return (True, CFnum, 'This file cannot be closed as Investigation Not Required', False, fileFlag)  

    

        
