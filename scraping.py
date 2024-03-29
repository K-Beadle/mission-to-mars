# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt



def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary 
    data = { 
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(browser),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemispheres(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data


# ### Article NASA mars news site
def mars_news(browser):

    # Visit the mars NASA news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for laoding the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    # Add try/except for error handling
    try:

        slide_elem = news_soup.select_one('div.list_text')
        # slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first 'a' tag and save it as 'new_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


# ### Featured Images
def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com/'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:

        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url


# ### Mars Facts
def mars_facts(browser):

    try:
        # use 'read_html' to scrape the facts table into a dataframe  
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)    

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

def hemispheres(browser):
    # Use browser to visit the URL
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # Write code to retrieve the image urls and titles for each hemisphere.
    # Create a for loop to loop through each hemisphere link

    for i in range(4):
        hemisphere_dict = {}
        
        # select the hemisphere
        hemisphere = browser.find_by_css('.thumb', wait_time=2)[i]
        hemisphere.click()
        
        # follow the path to the jpg title and link
        html = browser.html
        hemisphere_soup = soup(html, 'html.parser')
        hemisphere_list = hemisphere_soup.find('ul')
        hemisphere = hemisphere_list.find('li')
        img_link = hemisphere.find('a')['href']

        # create an absolute URL
        image_link = f'https://marshemispheres.com/{img_link}'
        # get the text from the hemisphere title
        hemisphere_title = hemisphere_soup.find('h2', class_='title').text
        
        # add img and title to dictionary
        hemisphere_dict["img_url"] = img_link
        hemisphere_dict["title"] = hemisphere_title
        
        # add dictionary to the list
        hemisphere_image_urls.append(hemisphere_dict)
        browser.back()

    # Quit the browser
    browser.quit()

    return hemisphere_image_urls


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())