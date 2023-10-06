import datetime 
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import logging
import glob 
import shutil 
import os 
import requests 

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(funcName)s:%(levelname)s:%(message)s')
logger = logging.getLogger("spark_structured_streaming")

start_date = datetime.datetime(2023, 10, 5, 0, 0)

default_args = {
    'owner': 'airflow',
    'start_date': start_date,
    'retries': 1,
    'retry_delay': datetime.timedelta(seconds=5)
}

UPLOAD_QUEUE = '/Users/kaleb/Documents/gitRepos/Projects/Hdtgm_webserver/_setup/audio_files'

def copy_sample_episodes():
    base_dir = '/Users/kaleb/Documents/HDTGM Episodes/'
    all_files = glob.glob(base_dir+'*')
    n_to_transfer = min(5, len(all_files))
    n_transferred = 0
    for i in range(n_to_transfer):
        logging.info(f"Moving {all_files[i]}")
        shutil.copyfile(all_files[i], '/'.join([UPLOAD_QUEUE, all_files[i].split('/')[-1]]))
        n_transferred += 1
    
    # all_files = glob.glob(UPLOAD_QUEUE+'/*')
    # fnames = [f.split('/')[-1] for f in all_files]
    # post_files = [('upload_file', open(os.path.join(UPLOAD_QUEUE, f),'rb')) for f in fnames]
    # logging.info('Sending post request')
    # res = requests.post('http://192.168.132.58:5000/episode_upload', files=post_files)
    
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
    post_files = [('upload_file', open(os.path.join(UPLOAD_QUEUE, f),'rb')) for f in fnames]
    res = requests.post('http://192.168.132.109:5000/episode_upload', files=post_files)
    return fnames 

def cleanup(new_files):
    for f in new_files:
        print(f"Would remove {os.path.join(UPLOAD_QUEUE, f)}")
        # os.remove(os.path.join(UPLOAD_QUEUE, f))

with DAG('episode_upload_dag', default_args=default_args, 
schedule_interval='0 1 * * *', catchup=False) as dag:

    sampling_task = PythonOperator(
        task_id='sample_episodes',
        python_callable=copy_sample_episodes,
        dag=dag,
    )
    
    upload_task = PythonOperator(
        task_id='upload_task',
        python_callable=upload_new_episodes,
        trigger_rule='none_failed',
        dag=dag,
    )

    sampling_task >> upload_task
