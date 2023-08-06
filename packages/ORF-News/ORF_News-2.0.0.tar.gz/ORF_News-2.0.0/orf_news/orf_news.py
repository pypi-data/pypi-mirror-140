from bs4 import BeautifulSoup
import asyncio
import aiohttp
from datetime import datetime

class ORF_News:
    def __init__(self):
        pass
    
    #! Creates Dictionary for post
    def make_dict(self, topic, post_headline, post_id, post_link, detailed_post_text, post_date):
        try:
            # create post dictionary
            post_json = {}
            # add all values of post to dictionary
            post_json['topic'] = topic
            post_json['post_headline'] = post_headline
            post_json['post_id'] = post_id
            post_json['post_link'] = post_link
            post_json['detail_post_text'] = detailed_post_text
            post_json['post_date'] = str(post_date)
            post_json['current_date'] = str(datetime.now().replace(microsecond=0))
            
            # return post dictionary
            return post_json
        
        except Exception as e:
            raise e

    #! Get Dictionary of all avaible topics
    async def getTopics(self):
        # Create session
        async with aiohttp.ClientSession() as session:
            # Call session
            async with session.get("https://orf.at/") as r:
                try:
                    # make soup of website
                    soup = BeautifulSoup(await r.text(), features="html.parser")
                    
                    # find all topics in soup
                    topics = soup.find_all("div", {"class": "ticker-ressort"})
                    
                    # create topic dictionary
                    topic_dict = {}
                    
                    for topic in topics:
                        # scrape topic name of soup
                        topic_names = topic.find("h2", {"class": "ticker-ressort-title"}).text
                        # add to topic dictionary
                        topic_dict[topic_names] = topic["class"][1]
                        
                    # return topic dictionary
                    return topic_dict
                
                except Exception as e:
                    raise e

    #! Get newest post of topic
    async def getTopPost(self, topic):
        # Create session
        async with aiohttp.ClientSession() as session:
            # Call session
            async with session.get("https://orf.at/") as r:
                try:
                    # make soup of website
                    soup = BeautifulSoup(await r.text(), features="html.parser")
                    
                    # find post in soup
                    post_soup = soup.find("div", {"class": topic})
                    
                    #if post exsists
                    if post_soup:
                        # scrape post article
                        post_article = post_soup.find("article", {"class": "ticker-story"})
                        # scrape post object
                        post_obj = post_article.find("a")
                        # scrape post headline
                        post_headline = post_obj.text.strip()
                        # scrape post post_link
                        post_link = post_obj["href"]
                        # scrape post id
                        post_id = int(post_obj["id"].replace("story", ""))
                        
                        # scrape details of post in post_soup
                        detailed_post_soup = soup.find("div", {"id": f"ticker-story-text-{post_id}"})
                        # scrape detailed post object
                        detailed_post_obj = detailed_post_soup.find("p")
                        # scrape detailed post text
                        detailed_post_text = detailed_post_obj.text.strip()
                        
                    else:
                        # if no posts exsists
                        raise ValueError(f"No posts with {topic} as topic")

                except Exception as e:
                    raise e

            # call session for post meta data
            async with session.get(f"https://orf.at/stories/{post_id}") as r:
                try:
                    # make soup of website
                    soup = BeautifulSoup(await r.text(), features="html.parser")
                    # scrape meta of soup
                    post_meta = soup.find("div", {"class": "print-only"})
                    # scrape post date of meta 
                    post_date = post_meta.text.strip() # 25.02.2022 19.07
                    # convert post date to datime object
                    post_date = datetime.strptime(post_date, '%d.%m.%Y %H.%M')
                    
                except Exception as e:
                    raise e
                
        # close session, idk if needed
        await session.close()
        
        # call make_dict() def and return the dictionary
        return self.make_dict(topic, post_headline, post_id, post_link, detailed_post_text, post_date)

    #! Get newest post of topic
    async def getTopPosts(self, topic, amount=20):
        amount = 0 if not amount else amount
        # Create session
        async with aiohttp.ClientSession() as session:
            # Call session
            async with session.get("https://orf.at/") as r:
                try:
                    # make soup of website
                    soup = BeautifulSoup(await r.text(), features="html.parser")
                    
                    # find post in soup
                    post_soup = soup.find("div", {"class": topic})  
                    posts = post_soup.find_all("article", {"class": "ticker-story"})
                    
                except Exception as e:
                    raise e
                
            post_list = []
            post_count = 0
            
            #if post exsists
            for post in posts:
                if post_count < amount:
                    # scrape post article
                    post_article = post.find("h3", {"class": "ticker-story-headline"})
                    # scrape post object
                    post_obj = post_article.find("a")
                    # scrape post headline
                    post_headline = post_obj.text.strip()
                    # scrape post post_link
                    post_link = post_obj["href"]
                    # scrape post id
                    post_id = int(post_obj["id"].replace("story", ""))
                    
                    # scrape details of post in post_soup
                    detailed_post_soup = post.find("div", {"id": f"ticker-story-text-{post_id}"})
                    # scrape detailed post object
                    detailed_post_obj = detailed_post_soup.find("p")
                    # scrape detailed post text
                    detailed_post_text = detailed_post_obj.text.strip()
                    
                    # call session for post meta data
                    async with session.get(f"https://orf.at/stories/{post_id}") as r:
                        try:
                            # make soup of website
                            soup = BeautifulSoup(await r.text(), features="html.parser")
                            # scrape meta of soup
                            post_meta = soup.find("div", {"class": "print-only"})
                            # scrape post date of meta 
                            post_date = post_meta.text.strip() # 25.02.2022 19.07
                            # convert post date to datime object
                            post_date = datetime.strptime(post_date, '%d.%m.%Y %H.%M')
                            
                        except Exception as e:
                            raise e
                    
                    post = self.make_dict(topic, post_headline, post_id, post_link, detailed_post_text, post_date)

                    post_list.append(post)
                    post_count += 1
                
            #else:
                # if no posts exsists
                #raise ValueError(f"No posts with {topic} as topic")
                
        # close session, idk if needed
        await session.close()
        
        # call make_dict() def and return the dictionary
        return post_list
