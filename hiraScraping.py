# from pydoc import doc
# import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
import time

default_value = ""

# dictionary {"전문의과목명" : 수}
dic_specialistPart_count = { \
    "내과" : default_value, \
    "신경과" : default_value, \
    "정신건강의학과" : default_value, \
    "외과" : default_value, \
    "정형외과" : default_value, \
    "신경외과" : default_value, \
    "흉부외과" : default_value, \
    "성형외과" : default_value, \
    "마취통증의학과" : default_value, \
    "산부인과" : default_value, \
    "소아청소년과" : default_value, \
    "안과" : default_value, \
    "이비인후과" : default_value, \
    "피부과" : default_value, \
    "비뇨의학과" : default_value, \
    "비뇨기과" : default_value, \
    "영상의학과" : default_value, \
    "방사선종양학과" : default_value, \
    "병리과" : default_value, \
    "진단검사의학과" : default_value, \
    "결핵과" : default_value, \
    "재활의학과" : default_value, \
    "핵의학과" : default_value, \
    "가정의학과" : default_value, \
    "응급의학과" : default_value, \
    "직업환경의학과" : default_value, \
    "예방의학과" : default_value, \
    "치과" : default_value, \
    "구강악안면외과" : default_value, \
    "치과보철과" : default_value, \
    "치과교정과" : default_value, \
    "소아치과" : default_value, \
    "치주과" : default_value, \
    "치과보존과" : default_value, \
    "구강내과" : default_value, \
    "영상치의학과" : default_value, \
    "구강악안면방사선과" : default_value, \
    "구강병리과" : default_value, \
    "예방치과" : default_value, \
    "통합치의학과" : default_value, \
    "한방내과" : default_value, \
    "한방부인과" : default_value, \
    "한방소아과" : default_value, \
    "한방안·이비인후·피부과" : default_value, \
    "한방안이비인후피부과" : default_value, \
    "한방신경정신과" : default_value, \
    "침구과" : default_value, \
    "한방재활의학과" : default_value, \
    "사상체질과" : default_value, \
    "한방응급" : default_value, }

# dictionary value 초기화 함수
def set_dic_value(dic_input, value):
    for dic_key in dic_input:
        dic_input[dic_key] = value

browser = webdriver.Chrome() # 같은경로에 chromedriver.exe 있어야 함
url = "https://www.hira.or.kr/rd/hosp/getHospList.do?pgmid=HIRAA030002000000#tab01"
browser.get(url)

# "병원 규모별" 클릭
browser.find_element_by_xpath('//*[@id="typeTab01"]').click()
# 병원규모 탭 나올 때까지 최대 10초 대기
try:
    WebDriverWait(browser,10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="hospTypeList"]')))
except:
    browser.quit()
    
# "병원 규모" 선택 (ex 요양병원 == li[1]) # 추후 사용자에게 입력받도록 변경
elem = browser.find_element_by_xpath('//*[@id="hospTypeList"]/li[2]/a')
elem.click()
filename = "심평원크롤링_2022_{}.csv".format(elem.text)
# 병원 클릭 후 상세 분야 탭 나올 때까지 최대 10초 대기
try:
    WebDriverWait(browser,10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="hosp-form"]/div/div[2]/div[2]/div[1]/div[2]/ul/li[1]/label')))
except:
    browser.quit()

# "전체선택" 클릭
browser.find_element_by_xpath('//*[@id="hosp-form"]/div/div[2]/div[2]/div[1]/div[2]/ul/li[1]/label').click()
# "검색" 클릭
browser.find_element_by_xpath('//*[@id="hosp-form"]/div/div[1]/a').click()
# 검색 로딩시간 최대 10초 대기
try:
    WebDriverWait(browser,10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="hosp-form"]/div/div[2]/div[2]/div[1]/div[4]/div/table/tbody/tr[1]')))
except:
    browser.quit()

# 스크롤 다운 프로세스
# 페이지 내 스크롤있는 div class element 저장 
itemList = browser.find_element_by_class_name("result-list-wrap")

# 검색된 병원 개수 확인
# hospital_num = browser.find_element_by_class_name("pointB").text[0:-1]
hospital_num = browser.find_element_by_xpath('//*[@id="searchResultTitle"]/strong').text[0:-1]
# 숫자에 따옴표(,) 있으면 제거 (따옴표 한개 있을 때만 가능)
if hospital_num.find(',') >= 0:
    hospital_num = hospital_num[:hospital_num.find(',')] + hospital_num[hospital_num.find(',') + 1:]

while True:
    # div class 스크롤을 가장 아래로 내림
    browser.execute_script("arguments[0].scrollBy(0, document.body.scrollHeight)", itemList)
    # 페이지 로딩 대기
    time.sleep(0.2)
    # 페이지 파싱
    soup = BeautifulSoup(browser.page_source, "lxml")
    # 검색된 병원들 find
    hospitals = soup.find("table", attrs={"class":"result-list"}).find("tbody").find_all("tr")
    # 병원 개수 저장
    curr_hospital_count = len(hospitals)
    print("현재 병원 개수: " + str(curr_hospital_count))
    # 병원 개수 확인하여 루프 탈출
    if int(hospital_num) <= curr_hospital_count:
        break

# 검색된 병원들 하나하나 클릭 및 데이터 저장
# 일반병원 버젼 타이틀 (요양병원 / 일반병원 / 치과 / 한방 네 가지 분류 타이틀 만들어야 함)
# 엑셀 첫 줄 생성 및 write
list_defaultInfo = "번호	병원명	주소	전화번호	병원구분	홈페이지	설립구분	일반입원실_상급	일반입원실_일반	중환자실_성인	중환자실_소아	중환자실_신생아	정신과개방_상급	정신과개방_일반	정신과폐쇄_상급	정신과폐쇄_일반	격리병실	무균치료실	분만실	수술실	응급실	물리치료실	총원(의사+치과의사+한의사)   의사    치과의사    한의사".split()
list_firstLine = list_defaultInfo + list(dic_specialistPart_count.keys())
f = open(filename, "w", encoding="utf-8-sig", newline="") # 엑셀에서 한글 깨질 경우 인코딩: utf-8-sig 
writer = csv.writer(f)
writer.writerow(list_firstLine)

# 각 병원 정보 긁어오기... 두둥
for idx, hospital in enumerate(hospitals):
    set_dic_value(dic_specialistPart_count, "") # 진료과별 전문의 수 초기화
    hospital_name = hospital.td.get_text()
    print("{0}. {1}".format(idx+1, hospital_name))
    
    hospital_data = list() # 병원 데이터 리스트 생성
    hospital_data.append(str(idx+1)) # 번호 
    hospital_data.append(hospital_name) # 병원명   
    
    try:
        browser.find_element_by_link_text(hospital_name).click() # 병원 클릭
    except:
        print("find_element_by_link_text 에러 발생 {}".format(hospital_name))
        writer.writerow(hospital_data)
        continue
    
    # 클릭 후 데이터 로딩 최대 10초 대기
    try:
        WebDriverWait(browser,10).until(EC.text_to_be_present_in_element((By.ID,'hospNm'),hospital_name))
    except:
        print("WebDriverWait 에러 발생 ({})".format(hospital_name))
    # 기본정보 스크래핑
    # 기본정보 클릭
    # browser.find_element_by_xpath('//*[@id="container"]/div[1]/div[2]/div/div[2]/div[1]/ul/li[1]/a').click()
    # time.sleep(0.3) # 클릭 후 데이터 로딩 대기
    
    soup = BeautifulSoup(browser.page_source, "lxml")
    data_blocks = soup.find("div", attrs={"class":"section_default hosp-search-view"})
    
    # 1. 기본정보 추출 # 주소, 전화번호, 홈페이지, 설립구분 등
    default_info_tr1 = data_blocks.find("table", attrs = {"summary":"기본정보 주소, 전화번호, 병원구분, 홈페이지, 설립구분에 대한 설명입니다."}).tbody.tr
    default_info_tr2 = default_info_tr1.find_next_sibling("tr")
    
    for td_info in default_info_tr1.find_all("td"):
        hospital_data.append(td_info.get_text())
    
    for td_info in default_info_tr2.find_all("td"):
        hospital_data.append(td_info.get_text())

    # 2. 시설 및 운영정보 추출 # 입원실 등
    facility_info1_tr = data_blocks.find("table", attrs = {"summary":"기본정보 병상수, 일반입원실, 정신과폐쇄, 정신과개방에 대한 정보입니다."}).tbody.tr.find_next_sibling("tr").find_next_sibling("tr")
    facility_info2_tr = data_blocks.find("table", attrs = {"summary":"격리병실, 무균치료실, 분만실, 수술실, 읍글실, 물리치료실에 대한 정보입니다."}).tbody.tr.find_next_sibling("tr")
    
    for td_info in facility_info1_tr.find_all("td"):
        data = td_info.get_text()
        if data == "0": # 값이 0일 경우 default_value 값 입력
            data = default_value
        hospital_data.append(data)

    for td_info in facility_info2_tr.find_all("td"):
        data = td_info.get_text()        
        if data == "0": # 값이 0일 경우 default_value 값 입력
            data = default_value
        hospital_data.append(data)        

    # 3. 진료과목 및 의사 현황
    text_info = data_blocks.find("td", attrs = {"class":"txtL"}).text
    # 총원 (의사+치과의사+한의사) 정규식 어렵
    # total_num = re.findall("(?<=인원: )(.*)(?=명)", text_info)[0]
    total_num = text_info[text_info.find("인원:")+3 : text_info.find("명")].strip()
    if total_num == "0":
        total_num = default_value
    hospital_data.append(total_num)

    # 의사 수 추출
    # doctor_num = re.findall("(?<=의사: )(.*)(?=, 치과의사)", text_info)[0]
    doctor_num = text_info[text_info.find("의사:")+3 : text_info.find(", 치과의사")].strip()
    if doctor_num == "0":
        doctor_num = default_value
    hospital_data.append(doctor_num)
    
    # 치과의사 수 추출
    #detist_num = re.findall("(?<=치과의사: )(.*)(?=, 한의사)", text_info)[0]
    detist_num = text_info[text_info.find("치과의사:")+5 : text_info.find(", 한의사")].strip()
    if detist_num == "0":
        detist_num = default_value
    hospital_data.append(detist_num)    
    
    # 한의사 수 추출
    #kdm_num = re.findall("(?<=한의사: )(.*)(?=\)전문의상세보기)", text_info)[0]
    kdm_num = text_info[text_info.find("한의사:")+4 : text_info.find(")")].strip()
    if kdm_num == "0":
        kdm_num = default_value
    hospital_data.append(kdm_num)   

    # 진료과목별 전문의 숫자
    mediPartValues = data_blocks.find("tr", attrs = {"id":"medicalSubjectList2"}).td.ul
    etcPart_num = 0
    for mediPartValue in mediPartValues:
        tempText = mediPartValue.get_text()
        
        partName = tempText[:tempText.find('(')].strip() # 진료과목명 추출
        partNum = tempText[tempText.find('(')+1 : tempText.find(')')].strip() # 숫자 추출
        if partNum == "0":
            partNum = default_value
        try:
            dic_specialistPart_count[partName] = partNum
        except: # dictionary에 partName key가 없을 경우
            etcPart_num = etcPart_num + partNum
            print("{}({})은 dictionary에 없는 진료과목. (누적 미소속 전문의 수: {})",partName, partNum, etcPart_num)

    # 진료과목별 전문의 수 리스트에 추가
    hospital_data = hospital_data + list(dic_specialistPart_count.values())
    # csv 파일에 병원 정보 쓰기    
    writer.writerow(hospital_data)

f.close()
time.sleep(3)
browser.quit()