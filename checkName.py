from bs4 import BeautifulSoup as BS
import re


def checkUsername(htmlSource):
    closeStatus = False
    try:
        #soup = BS(htmlSource, "lxml")
        soup = BS(open(htmlSource,encoding="utf8"), "lxml")

        #Username
        tables = soup.find_all('table',{'id':'TBTopTable'})
        rowData = [tr for tr in tables[0].find_all('tr')]

        td = rowData[1].find_all('td')

        for eachtd in td:
            if eachtd:
                data = [each.parent.find('font').findNext('font') for each in eachtd]
                return (data[0].text.replace('User ', '').replace('may have pending personal tasks.', '').strip())


    except Exception as e:
        print(e)


username = checkUsername('checkName.html')
username = (re.sub(r'\([^)]*\)', '', username))
print(username)

'''
<td align="left" valign="middle" bgcolor="#bb00cc"><font face="Arial" size="1" color="#FFFFCC"><b>AMO QA, Inc. GCH version 4.3</b>
</font><br><font face="Verdana" size="2" color="#FFFFFF">User Prashanth Kumar B (<a href="main.aspx?WCI=Main&WCE=DeptTasks&WCU=s%3DLIRHALUFFRGY9E5D81GELL4F051TJ129">
<font face="Verdana" size="2" color="#FFFFFF">Asia Pacific</font></a>)<br>may have pending <a href="main.aspx?WCI=Main&WCE=PersTasks&WCU=s%3DLIRHALUFFRGY9E5D81GELL4F051TJ129"><font face="Verdana" size="2" color="#FFFFFF">personal tasks</font></a>.</font></td>
'''