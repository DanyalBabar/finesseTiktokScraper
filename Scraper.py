from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import time
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import csv
import datetime


class Scraper:
    END_OF_RESULTS_CLASS = "DivNoMoreResultsContainer"
    VIDEO_RESULT_CONTAINER_CLASS = "DivItemContainerForSearch"
    VIDEO_VIEW_COUNT_CLASS = "StrongVideoCount"

    VIDEO_PLAYER_CONTAINER_CLASS = "DivPlayerContainer"
    VIDEO_BUTTON_CONTAINER_CLASS = "DivActionItemContainer"
    VIDEO_DESCRIPTION_CONTAINER_CLASS = 'h1[data-e2e="browse-video-desc"]'
    VIDEO_DATE_CONTAINER_CLASS = "SpanOtherInfos"

    REPLY_BUTTON_CLASS = "PReplyActionText"
    COMMENT_CONTAINER_CLASS = "PCommentText"

    def __init__(self) -> None:
        pass

    # Convert TikTok number abbreviation to int
    # e.g. 2.1K -> 2100
    def tiktokCountToInt(self, text: str) -> int:
        # print("tiktokCountToInt", text)
        try:
            multiplier = 1

            if text[-1] == "M":
                multiplier = 1000000
            elif text[-1] == "K":
                multiplier = 1000

            if text[-1].isalpha():
                text = text[:-1]
            return int(float(text) * multiplier)
        except:
            # print("EXCEPT:", text)
            return 0

    # Convert Tiktok date to datetime
    # Dates of today are formatted Xh ago
    # Dates of the current year are formatted to mm-dd
    # Dates of previous years are formatted to yyyy-mm-dd
    def tiktokDateToDatetime(self, text: str) -> datetime.date:
        # print("tiktokDateToDatetime", text)
        dateToday = datetime.datetime.today()

        if "h" in text:
            return dateToday
        if "d" in text:
            return dateToday - datetime.timedelta(days=int(text[0]))

        text = text.split("-")

        year = datetime.date.today().year
        month = 0
        day = 0

        if len(text) == 3:
            year = int(text[0])
            text = text[1:]

        month = int(text[0])
        day = int(text[1])

        return datetime.date(year, month, day)

    # Scrape from the "trending" page of a particular search query and write
    # the post links and the likes of each post to a target csv file
    def scrapePostLinks(self, searchQuery, targetCsvFile):
        print("Scraper starting! Query:", searchQuery)
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option("useAutomationExtension", False)
        driver = webdriver.Chrome(options=options)

        stealth(
            driver,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        url = "https://www.tiktok.com/search?q={}".format(searchQuery)
        driver.get(url)
        print("Driver successfully loaded Tiktok")
      
        while True:
            driver.execute_script("window.scrollBy(0, window.innerHeight);")

            if driver.find_elements(
                By.CSS_SELECTOR, '[class*="{}"]'.format(Scraper.END_OF_RESULTS_CLASS)
            ):
                break

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    '[class*="{}"]'.format(Scraper.VIDEO_RESULT_CONTAINER_CLASS),
                )
            )
        )
        videoDivs = driver.find_elements(
            By.CSS_SELECTOR,
            '[class*="{}"]'.format(Scraper.VIDEO_RESULT_CONTAINER_CLASS),
        )
        postLinks = []

        for div in videoDivs:
            anchorElements = div.find_elements(By.TAG_NAME, "a")
            for anchor in anchorElements:
                href = anchor.get_attribute("href")
                if href and "tiktok.com/" in href:
                    postUrl = href
                    break

            postViews = self.tiktokCountToInt(
                div.find_element(
                    By.CSS_SELECTOR,
                    '[class*="{}"]'.format(Scraper.VIDEO_VIEW_COUNT_CLASS),
                ).text
            )
            postLinks.append([postUrl, postViews])

        with open(targetCsvFile, "w", newline="", encoding="utf-8") as postFile:
            postFileWriter = csv.writer(postFile)
            for postUrl, postViews in postLinks:
                print(postUrl)
                postAccount = ""
                postLikes = 0
                postCommentCount = 0
                postComments = []
                postSaved = 0
                postShared = 0
                postCaption = ""
                postHashtags = []
                postDate = None
                postDateCollected = datetime.date.today()

                postAccount = postUrl.split("/")[3][1:]

                driver.get(postUrl)
                time.sleep(1)
                try:
                    closeModalButton = driver.find_element(
                        By.CSS_SELECTOR, '[class*="{}"]'.format("DivCloseWrapper")
                    )
                    if closeModalButton:
                        # print("Got here")
                        WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable(closeModalButton)
                        )
                        # closeModalButton.click()
                        ActionChains(driver).move_to_element(
                            closeModalButton
                        ).click().perform()
                    # print("HER")
                except NoSuchElementException:
                    pass

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            '[class*="{}"]'.format(
                                Scraper.VIDEO_PLAYER_CONTAINER_CLASS
                            ),
                        )
                    )
                )
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            '[class*="{}"]'.format(
                                Scraper.VIDEO_BUTTON_CONTAINER_CLASS
                            ),
                        )
                    )
                )

                buttonContainer = driver.find_element(
                    By.CSS_SELECTOR,
                    '[class*="{}"]'.format(Scraper.VIDEO_BUTTON_CONTAINER_CLASS),
                )
                postMetricElements = buttonContainer.find_elements(
                    By.TAG_NAME, "strong"
                )

                postLikes = self.tiktokCountToInt(postMetricElements[0].text)
                postCommentCount = self.tiktokCountToInt(postMetricElements[1].text)
                postSaved = self.tiktokCountToInt(postMetricElements[2].text)
                postShared = self.tiktokCountToInt(postMetricElements[3].text)

                descriptionContainer = driver.find_element(
                    By.CSS_SELECTOR, Scraper.VIDEO_DESCRIPTION_CONTAINER_CLASS
                )
                try:
                    captionElement = descriptionContainer.find_element(
                        By.TAG_NAME, "span"
                    )
                    postCaption = captionElement.text
                except:
                    postCaption = ""

                try:
                    hashtagElements = descriptionContainer.find_elements(
                        By.TAG_NAME, "a"
                    )
                    for hashtagElement in hashtagElements:
                        hashtag = hashtagElement.text[1:]
                        if hashtag:
                            postHashtags.append(hashtag)
                except:
                    postHashtags = []

                dateContainer = driver.find_element(
                    By.CSS_SELECTOR,
                    '[class*="{}"]'.format(Scraper.VIDEO_DATE_CONTAINER_CLASS),
                )
                postDate = self.tiktokDateToDatetime(
                    dateContainer.find_elements(By.TAG_NAME, "span")[2].text
                )

                # scrape up to 20 non-reply comments
                realCommentCount = postCommentCount
                loadedComments = []
                driver.execute_script("window.scrollBy(0, window.innerHeight);")
                seenReplyButtons = set()

                while len(loadedComments) < min(20, realCommentCount):
                    # print("loadedComments : realComments", len(loadedComments), "/", realCommentCount)

                    loadedComments = driver.find_elements(
                        By.CSS_SELECTOR,
                        '[class*="{}"]'.format(Scraper.COMMENT_CONTAINER_CLASS),
                    )
                    replyButtons = driver.find_elements(
                        By.CSS_SELECTOR,
                        '[class*="{}"]'.format(Scraper.REPLY_BUTTON_CLASS),
                    )

                    for button in replyButtons:
                        if button not in seenReplyButtons:
                            if button.text != "Hide":
                                totalReplies = int(button.text.split(" ")[1])
                                realCommentCount -= totalReplies
                            seenReplyButtons.add(button)

                    driver.execute_script("window.scrollBy(0, window.innerHeight);")
                    driver.execute_script("window.scrollBy(0, window.innerHeight);")
                    time.sleep(0.15)

                for comment in loadedComments:
                    # print("comment", comment)
                    postComments.append(comment.text)

                postFileWriter.writerow(
                    [
                        postUrl,
                        postAccount,
                        postViews,
                        postLikes,
                        postCommentCount,
                        postComments,
                        postSaved,
                        postShared,
                        postCaption,
                        postHashtags,
                        postDate,
                        postDateCollected,
                    ]
                )

        driver.quit()


s = Scraper()
s.scrapePostLinks("fashion", "postLinks.csv")
