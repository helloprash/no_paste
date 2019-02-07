from bs4 import BeautifulSoup as BS


def checkClosure(htmlSource):
    closeStatus = False
    closeMsg = ''
    try:
        #soup = BS(htmlSource, "lxml")
        soup = BS(open(htmlSource,encoding="utf8"), "lxml")
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
                
        return closeMsg, closeStatus


    except Exception as e:
        return e, False


print(checkClosure('check999.html'))
#print(check999('999.html'))