# coding: utf-8
import json
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = 'https://w5.linguaporta.jp/user/seibido/'


def main():
    # ブラウザ起動

    driver = webdriver.Chrome()
    driver.get(URL)
    driver.execute_script("document.body.style.zoom='100%'")
    wait = WebDriverWait(driver, 10)

    user_data = get_user_data()

    login(driver, user_data)

    to_study_unit_page(driver, wait)

    now = to_user_data_page(driver, user_data)

    if user_data["mode"] == 1:
        solve_unit(driver, wait, user_data, now)

    else:
        find_unit(driver, wait, user_data, now)


def login(driver: WebDriver, user_data: dict):
    driver.find_element(By.NAME, "id").send_keys(user_data["id"])
    driver.find_element(By.NAME, "password").send_keys(user_data["pass"])
    driver.find_element(By.ID, "btn-login").click()
    print('ログイン成功')


def to_study_unit_page(driver: WebDriver, wait: WebDriverWait):
    study_element = wait.until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'menu-study')))
    study_element.click()
    print("studyページ")

    # 違うunitの場合要修正
    driver.execute_script("arguments[0].click();", driver.find_element(
        By.CLASS_NAME, 'btn-reference-select'))
    print("unitページ")


def to_next_page(driver: WebDriver, next_page: int):
    if (next_page > 20):
        next_page = next_page % 20 + 1

    next_button_xpath = "/html/body/div[2]/div/div/div[2]/a[" + \
        str(next_page) + "]"
    to_next_page_button = driver.find_element(By.XPATH, next_button_xpath)
    to_next_page_button.click()


def to_user_data_page(driver: WebDriver, user_data: dict):
    now = 1
    while now < user_data["page"]:
        to_next_page(driver, now)
        now += 1
    print(str(now) + "ページ目にいます")
    return now


def to_learning(driver: WebDriver, index: int):
    try:
        learning_xpath = "/html/body/div[2]/div/div/div[1]/div[" + \
            str(index+1) + "]/div[1]/div/input"
        element_learning = driver.find_element(By.XPATH, learning_xpath)
        driver.execute_script("arguments[0].click();", element_learning)
        return False
    except NoSuchElementException:
        return True


def to_next_question(driver: WebDriver, wait: WebDriverWait):
    time.sleep(1.5)
    next_question_xpath = "/html/body/div[2]/div/div/table/tbody/tr[4]/td/div/form/input[1]"
    next_question_element = wait.until(
        EC.visibility_of_element_located((By.XPATH, next_question_xpath)))

    driver.execute_script(
        "arguments[0].click();", next_question_element)

    print("次の問題に行きます")


def solve_unit(driver: WebDriver, wait: WebDriverWait, user_data: dict, now: int):
    unit_indexes = []
    allDone = False
    while not allDone:

        if str(now) not in user_data["history"]:
            user_data["history"][str(now)] = {}

        if now % 2 == 1:
            unit_indexes = [1, 2, 4, 5, 6, 8, 9, 10]
            session_type = 0
        else:
            unit_indexes = [2, 3, 4, 6, 7, 8, 10]
            session_type = 2

        if user_data["page"] == 6:
            allDone = True
            unit_indexes = [2, 3, 4, 6]

        for index in unit_indexes:
            print("{}ページ {}ユニット目".format(user_data["page"], index))

            if str(index) not in user_data["history"][str(now)]:
                user_data["history"][str(now)][str(index)] = {}

            is_session = to_learning(driver, index)

            if not is_session:
                if session_type == 0:
                    user_data = solve_session_0(
                        driver, wait, user_data, now, index)
                else:
                    user_data = solve_session_12(
                        driver, wait, user_data, now, index, session_type)

            session_type = (session_type + 1) % 3

            if index == 10:
                to_next_page(driver, now)
                user_data["page"] += 1
                now += 1

            save_user_data(user_data)


def find_unit(driver: WebDriver, wait: WebDriverWait, user_data: dict, now: int):
    unit_indexes = []
    allDone = False
    while not allDone:

        if str(now) not in user_data["history"]:
            user_data["history"][str(now)] = {}

        if now % 2 == 1:
            unit_indexes = [3, 7]
        else:
            unit_indexes = [1, 5, 9]

        if user_data["page"] == 6:
            allDone = True
            unit_indexes = [1, 5]

        for index in unit_indexes:
            print("{}ページ {}ユニット目".format(user_data["page"], index))

            if str(index) not in user_data["history"][str(now)]:
                user_data["history"][str(now)][str(index)] = {}

            is_session = to_learning(driver, index)

            if not is_session:
                user_data = find_session_ans(
                    driver, wait, user_data, now, index)

            if index > 6:
                to_next_page(driver, now)
                user_data["page"] += 1
                now += 1

            save_user_data(user_data)


def solve_session_12(driver: WebDriver, wait, user_data: dict, page: int, index: int, session_type: int):
    while (True):
        time.sleep(1)
        print("----------------------")

        question_xpath = "/html/body/div[2]/div/div/table/tbody/tr[4]/td/form/b"
        if len(driver.find_elements(By.XPATH, question_xpath)) == 0:
            break
        question_element = driver.find_element(By.XPATH, question_xpath)
        question_num = int(question_element.text.replace("問題番号：", ""))

        print("問題番号:", question_num)

        input_xpath = ["/html/body/div[2]/div/div/table/tbody/tr[4]/td/form/div[2]/div[3]/div/input[1]",
                       "/html/body/div[2]/div/div/table/tbody/tr[4]/td/form/div/div[3]/div/input",
                       "/html/body/div[2]/div/div/table/tbody/tr[4]/td/form/div[2]/div[2]/div/input"]

        input_element = driver.find_element(
            By.XPATH, input_xpath[session_type])

        submit_xpath = "/html/body/div[2]/div/div/table/tbody/tr[4]/td/form/input[3]"
        submit_element = driver.find_element(By.XPATH, submit_xpath)

        # 過去にデータがあるか確認
        if str(question_num) not in user_data["history"][str(page)][str(index)]:

            while (True):
                time.sleep(2)

                to_answer_class = "btn-answer-view"
                if len(driver.find_elements(By.CLASS_NAME, to_answer_class)) > 0:
                    to_answer_element = driver.find_element(
                        By.CLASS_NAME, to_answer_class)

                    driver.execute_script(
                        "arguments[0].click();", to_answer_element)

                    answer_xpath = ["",
                                    "/html/body/div[2]/div/div/table/tbody/tr[4]/td/form[1]/div/div[3]/input",
                                    "/html/body/div[2]/div/div/table/tbody/tr[4]/td/form[1]/div[2]/div[2]/input"]
                    answer_element = driver.find_element(
                        By.XPATH, answer_xpath[session_type])
                    answer_taxt = answer_element.get_attribute("value")
                    answer_taxt = answer_taxt.strip()

                    print("回答:{} を得ました".format(answer_taxt))
                    update_ans_list(user_data, page, index,
                                    question_num, answer_taxt)

                    to_next_question(driver, wait)

                    break
                else:
                    try:
                        if session_type == 0:
                            driver.execute_script(
                                "arguments[0].click();", input_element)
                        else:
                            input_element.send_keys("hoge")

                        driver.execute_script(
                            "arguments[0].click();", submit_element)
                    except:
                        try:
                            driver.find_element(
                                By.ID, "tabindex1").send_keys("hoge")
                            driver.execute_script(
                                "arguments[0].click();", driver.find_element(By.ID, "ans_submit"))
                        except:
                            print("例外が発生しました、手動で回答してください")
                            input()
                            exit()

                    print("過去に回答がなかったため回答を見ます")
        else:
            history_answer = user_data["history"][str(
                page)][str(index)][str(question_num)]
            input_element.send_keys(history_answer)
            driver.execute_script("arguments[0].click();", submit_element)

            print("問題の解答に成功しました")

            try:
                to_next_question(driver, wait)
            except:
                return_unit_class = "btn-return-units"
                return_unit_element = driver.find_element(
                    By.CLASS_NAME, return_unit_class)
                driver.execute_script(
                    "arguments[0].click();", return_unit_element)
                print("unitが終了しました")

    return user_data


def solve_session_0(driver: WebDriver, wait, user_data: dict, page: int, index: int):
    while (True):
        time.sleep(1)
        print("----------------------")

        question_xpath = "/html/body/div[2]/div/div/table/tbody/tr[4]/td/form/b"
        if len(driver.find_elements(By.XPATH, question_xpath)) == 0:
            break
        question_element = driver.find_element(By.XPATH, question_xpath)
        question_num = int(question_element.text.replace("問題番号：", ""))

        print("問題番号:", question_num)

        input_xpath = "/html/body/div[2]/div/div/table/tbody/tr[4]/td/form/div[2]/div[3]/div/input[1]"
        input_element = driver.find_element(By.XPATH, input_xpath)

        submit_xpath = "/html/body/div[2]/div/div/table/tbody/tr[4]/td/form/input[3]"
        submit_element = driver.find_element(By.XPATH, submit_xpath)

        now_value = ""

        # 過去にデータがあるか確認
        if str(question_num) not in user_data["history"][str(page)][str(index)]:

            while (True):
                time.sleep(2)

                to_answer_class = "btn-answer-view"
                ans_msg_id = "true_msg"
                if len(driver.find_elements(By.CLASS_NAME, to_answer_class)) > 0:
                    to_answer_element = driver.find_element(
                        By.CLASS_NAME, to_answer_class)

                    driver.execute_script(
                        "arguments[0].click();", to_answer_element)

                    answer_xpath = "/html/body/div[2]/div/div/table/tbody/tr[4]/td/form[1]/div[2]/div[4]/div"
                    answer_element = driver.find_element(
                        By.XPATH, answer_xpath)
                    answer_taxt = answer_element.text
                    answer_taxt = answer_taxt.strip("正解：")

                    print("回答:{} を得ました".format(answer_taxt))
                    update_ans_list(user_data, page, index,
                                    question_num, answer_taxt)

                    to_next_question(driver, wait)

                    break

                elif len(driver.find_elements(By.ID, ans_msg_id)) > 0:

                    print("正解してしまいました")
                    print("回答:{} を得ました".format(now_value))
                    update_ans_list(user_data, page, index,
                                    question_num, now_value)

                    to_next_question(driver, wait)
                    break

                else:
                    driver.execute_script(
                        "arguments[0].click();", input_element)
                    driver.execute_script(
                        "arguments[0].click();", submit_element)

                    now_value = input_element.get_attribute("value")

                    print("過去に回答がなかったため回答を見ます")
        else:
            history_answer = user_data["history"][str(
                page)][str(index)][str(question_num)]

            radio_id_list = ["answer_0_0", "answer_0_1",
                             "answer_0_2", "answer_0_3"]
            radio_element_list = [driver.find_element(
                By.ID, id) for id in radio_id_list]
            radio_text_list = [element.get_attribute(
                "value") for element in radio_element_list]

            print(radio_text_list)
            print(history_answer)

            ans_index = radio_text_list.index(history_answer)
            driver.execute_script(
                "arguments[0].click();", radio_element_list[ans_index])
            driver.execute_script("arguments[0].click();", submit_element)

            print("問題の解答に成功しました")

            try:
                to_next_question(driver, wait)

            except:
                return_unit_class = "btn-return-units"
                return_unit_element = driver.find_element(
                    By.CLASS_NAME, return_unit_class)
                driver.execute_script(
                    "arguments[0].click();", return_unit_element)
                print("unitが終了しました")

    return user_data


def find_session_ans(driver: WebDriver, wait, user_data: dict, page: int, index: int):
    while (True):
        time.sleep(1)
        print("----------------------")

        question_xpath = "/html/body/div[2]/div/div/table/tbody/tr[4]/td/b"
        if len(driver.find_elements(By.XPATH, question_xpath)) == 0:
            break
        question_element = driver.find_element(By.XPATH, question_xpath)
        question_num = int(question_element.text.replace("問題番号：", ""))

        print("問題番号:", question_num)

        # 過去にデータがあるか確認
        if str(question_num) not in user_data["history"][str(page)][str(index)]:

            while (True):
                time.sleep(2)

                to_answer_class = "btn-answer-view"
                if len(driver.find_elements(By.CLASS_NAME, to_answer_class)) > 0:
                    to_answer_element = driver.find_element(
                        By.CLASS_NAME, to_answer_class)

                    driver.execute_script(
                        "arguments[0].click();", to_answer_element)

                    answer_xpath = "/html/body/div[2]/div/div/table/tbody/tr[4]/td/form[1]/div/div[3]"
                    answer_element = driver.find_element(
                        By.XPATH, answer_xpath)
                    answer_taxt = answer_element.text
                    answer_taxt = answer_taxt.strip("正解：")

                    print("回答:{} を得ました".format(answer_taxt))
                    update_ans_list(user_data, page, index,
                                    question_num, answer_taxt)

                    to_next_question(driver, wait)

                    break

                else:
                    driver.execute_script("window.scrollBy(0, 300);")

                    first_selection_id = "D0"
                    first_selection_element = driver.find_element(
                        By.ID, first_selection_id)

                    input_id = "Drop0"
                    input_element = driver.find_element(By.ID, input_id)

                    actions = ActionChains(driver)
                    actions.drag_and_drop(
                        first_selection_element, input_element)
                    actions.perform()

                    time.sleep(1)

                    submit_id = "ans_submit"
                    submit_element = driver.find_element(By.ID, submit_id)

                    driver.execute_script(
                        "arguments[0].click();", submit_element)

                    print("過去に回答がなかったため回答を見ます")
        else:
            print("解答が存在する問題です")

            try:
                driver.execute_script("window.scrollBy(0, 300);")

                first_selection_id = "D0"
                first_selection_element = driver.find_element(
                    By.ID, first_selection_id)

                input_id = "Drop0"
                input_element = driver.find_element(By.ID, input_id)

                actions = ActionChains(driver)
                actions.drag_and_drop(
                    first_selection_element, input_element)
                actions.perform()

                time.sleep(1)

                submit_id = "ans_submit"
                submit_element = driver.find_element(By.ID, submit_id)

                driver.execute_script(
                    "arguments[0].click();", submit_element)

                if len(user_data["history"][str(page)][str(index)]) == 20:
                    print(1/0)
                to_next_question(driver, wait)

            except:
                return_unit_class = "btn-return-units"
                return_unit_element = driver.find_element(
                    By.CLASS_NAME, return_unit_class)
                driver.execute_script(
                    "arguments[0].click();", return_unit_element)
                print("unitが終了しました")

    return user_data


def get_user_data():
    with open("user_data.json", encoding="utf-8") as data:
        user_data = json.load(data)
        if not (user_data["id"] and user_data["pass"]):
            print("user_data.jsonにidとpasswordを記述してください")
            exit()
        if not user_data["page"]:
            print("user_data.jsonに問題のpageを記述してください")
        if not user_data["mode"]:
            print("user_data.jsonにmodeを記述してください。")
            print("1が「単語・語句の意味」「空所補充」「音声を聞いて読み取り」")
            print("2が単語並び替え")
            print("2は回答収集のみです")

    return user_data


def save_user_data(user_data: dict):
    data_file = open("user_data.json", mode="w", encoding="utf-8")
    json.dump(user_data, data_file, indent=2, ensure_ascii=False)
    data_file.close()


def update_ans_list(user_data, page, index, question_num, ans):

    user_data["history"][str(page)][str(
        index)][str(question_num)] = ans

    answer_list = sorted(user_data["history"][str(
        page)][str(index)].items(), key=lambda x: int(x[0]))

    user_data["history"][str(page)][str(
        index)] = dict(answer_list)

    save_user_data(user_data)


if __name__ == "__main__":
    main()
