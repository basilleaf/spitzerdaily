import os, random, csv, urllib, logging
import PIL.Image as PIL
import tweepy
from time import sleep
from resize import shrink
from secrets import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

SCREEN_NAME = 'spitzerdaily'

# file names
base_path = '/home/befoream/bots/spitzerdaily/'
tweeted_log = base_path + 'tweeted.log'
all_images_csv = base_path + 'scrapings.csv'
max_img_file_size = 3e+6  # 3 megabytes twitter limit

# twitter auth stuff
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def fetch_image(url):
    """ fetches remote image, returns full path local copy """
    local_img_file = url.split('/')[-1]
    urllib.urlretrieve(url, local_img_file)
    img_path = os.path.abspath(local_img_file)
    return img_path

# find ones we haven't tweeted yet, handle if none left
all_images = list(open(all_images_csv))  # small data
tweeted = list(open(tweeted_log))
not_yet_tweeted = [line for line in all_images if line not in tweeted]

if not not_yet_tweeted:
    # we've tweeted them all! reset the tweeted.log back to zero
    open(tweeted_log, 'w').close()
    not_yet_tweeted = all_images

# pick a random line from the not_yet_tweeted list
image_info = random.choice(not_yet_tweeted).split(',')
logger.debug(image_info)
reader = csv.reader([line])
(url, img_url, tweet) = list(reader)[0]

# download image locally
img_path = fetch_image(img_url)
if max_img_file_size < os.path.getsize(img_path):  # img file too big
    img_path = shrink(img_path, max_img_file_size)
    logger.error("image resized: %s" % img_path)

tweet_with_link = "%s %s" % (tweet, url)

# tweet!
api.update_with_media(img_path, status=tweet_with_link)
logger.info("tweeted %s" % (tweet_with_link))

# add to tweeted.log
with open(tweeted_log, 'a') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(list(image_info))

# do followbacks
followers = api.followers_ids(SCREEN_NAME)

followers = []
for block in tweepy.Cursor(api.followers_ids, SCREEN_NAME).items():
  followers += [block]

friends = []
for block in tweepy.Cursor(api.friends_ids, SCREEN_NAME).items():
  friends += [block]

to_follow = list(set(followers).difference(friends))

for f in to_follow:
    try:
        u = api.get_user(f)
        if not u.protected:  # don't try to follow private accounts
            sleep_time = random.randint(10,30)
            print "sleeping for %s" % sleep_time
            sleep(sleep_time)  # being a good twitizen

            api.create_friendship(f)
            print('followed: ' + api.get_user(f).screen_name)

    except tweepy.error.TweepError, e:
          print(e.message[0]['message'])

# unfollow unfollowers
exceptions = ['Kaleidopix','NASAspitzer']
for f in friends:
    if f not in followers:
        if api.get_user(f).screen_name not in exceptions:
            sleep_time = random.randint(1,3)
            print "sleeping for %s" % sleep_time
            sleep(sleep_time)

            print "Unfollowing {0}".format(api.get_user(f).screen_name)
            api.destroy_friendship(f)
