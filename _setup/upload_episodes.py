import logging
import glob 
import shutil 
import os 
import requests 

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(funcName)s:%(levelname)s:%(message)s')
logger = logging.getLogger("spark_structured_streaming")

UPLOAD_QUEUE = '/Users/kaleb/Documents/gitRepos/Projects/Hdtgm_webserver/_setup/audio_files'

def copy_sample_episodes():
    base_dir = '/Users/kaleb/Documents/HDTGM Episodes/'
    all_files = glob.glob(base_dir+'*')
    n_to_transfer = min(5, len(all_files))
    n_transferred = 0
    for i in range(n_to_transfer):
        logging.info(f"Moving {all_files[i]}")
        shutil.move(all_files[i], '/'.join([UPLOAD_QUEUE, all_files[i].split('/')[-1]]))
        n_transferred += 1
    
    return n_transferred

def upload_new_episodes():
    """
    Checks for new episodes to upload to the server
    """
    # uploader = EpisodeUploader(source_folder=UPLOAD_QUEUE)
    # new_files = uploader.get_new_episodes()
    # res = uploader.send_requests(new_files)
    # if res.status_code == 200:
    #     uploader.cleanup()

    all_files = glob.glob(UPLOAD_QUEUE+'/*')
    fnames = [f.split('/')[-1] for f in all_files]
    logging.info(f"Found {fnames} to post")
    post_files = [('file', open(os.path.join(UPLOAD_QUEUE, f),'rb')) for f in fnames]
    logging.info(f'About to post {post_files}')
    res = requests.post('http://192.168.132.58:5000/episode_upload', files=post_files)
    if res.status_code == 200:
        cleanup(fnames)
    return res 

def cleanup(new_files):
    for f in new_files:
        # print(f"Would remove {os.path.join(UPLOAD_QUEUE, f)}")
        os.remove(os.path.join(UPLOAD_QUEUE, f))

def main():
    n_transferred = copy_sample_episodes()
    upload_new_episodes()
    import datetime
    with open('/Users/kaleb/Documents/gitRepos/Projects/Hdtgm_webserver/test_txt.txt', 'r+') as f:
        f.write(f'Finished transferring {n_transferred} new episodes at {datetime.datetime.now()}')

if __name__ == '__main__':
    main()
