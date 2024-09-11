import os
import time
from time import sleep
from datetime import datetime 
import streamlit as st 
import random
import csv
import pandas as pd
from glob import glob

def convert_seconds_to_hhmmss(seconds):
    return time.strftime('%H:%M:%S', time.gmtime(seconds))

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    return df

def page(label, tab, testset, worker, postfix):
    num_assigns = len(testset)
    save_path = f'results/{worker}_{label}_{postfix}.csv'
    fout = open(save_path, 'a+', encoding='UTF8')
    csv_writer = csv.writer(fout)
    with tab:
        # label specific data
        log = label + 'log'
        stamp = label + 'stamp'
        elapsed_time = label + 'elapsed_time'
        date = label + 'date'
        count = label + 'count'
        text = label + 'text'
        percent = label + 'percent'

        # reset button
        st.markdown(f"***Press the '{label} Reset' button in these cases:***")
        st.markdown("***1. This is the FIRST TRIAL***")
        st.markdown("***2. If you pressed the 'F5 (refresh)' button***")
        st.markdown("***3. If you want to CLEAR DATA and RESTART***")
        st.button(f'🔄 {label} Reset 🔄', key=f'{label}_reset')
        st.divider()
        if st.session_state[f'{label}_reset']:
            fout.close()
            if os.path.exists(save_path):
                os.remove(save_path)
            if hasattr(st.session_state, log):
                del st.session_state[log]
            fout = open(save_path, 'a+', encoding='UTF8')
            csv_writer = csv.writer(fout)

        # evaluation
        if label == 'MOS':
            audio_path = label + 'audio'
            st.subheader('How natural (i.e. human-sounding) is this recording?')
            st.info('CHECK LIST: Noise, Timbre, and Sound Clarity', icon="✅")
        else:
            if label == 'SMOS':
                st.subheader('How similar is the target audio to the source audio?')
                st.info('CHECK LIST: Speaker Similarity', icon="✅")
                st.warning('IGNORE: Content Difference, Grammar, and Audio Quality', icon="⚠️")
            elif label == 'CMOS':
                st.subheader('Which of the audio has better quality?')
                st.info('CHECK LIST: Noise, Timbre, and Sound Clarity', icon="✅")

            src_audio_path = label + 'src_audio'
            tgt_audio_path = label + 'tgt_audio'

        col1, col2 = st.columns(2)
        pbar = st.progress(0, text=None)
        if not hasattr(st.session_state, log):
            st.session_state[log] = '' 
            st.session_state[stamp] = time.perf_counter()
            st.session_state[elapsed_time] = 0
            st.session_state[date] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state[count] = 0
            st.session_state[percent] = 0
            
            if label == 'MOS':
                st.session_state[audio_path] = testset['audio_url'][st.session_state[count]]
                header = ['date', 'worker', 'audio_url', 'original_text', 'score']
            elif label == 'SMOS':
                st.session_state[src_audio_path] = testset['ref_audio_url'][st.session_state[count]]
                st.session_state[tgt_audio_path] = testset['test_audio_url'][st.session_state[count]]
                header = ['date', 'worker', 'ref_audio_url', 'test_audio_url', 'original_text', 'score']
            else:
                st.session_state[src_audio_path] = testset['src_audio_url'][st.session_state[count]]
                st.session_state[tgt_audio_path] = testset['test_audio_url'][st.session_state[count]]
                header = ['date', 'worker', 'src_audio_url', 'test_audio_url', 'original_text', 'score']

            csv_writer.writerow(header)
            st.session_state[text] = testset['original_text'][st.session_state[count]]

        with col2:
            if label == 'MOS':
                st.radio(f'score', ['1 : Bad - Completely unnatural speech', 
                                    '2 : Poor - Mostly unnatural speech', 
                                    '3 : Fair - Equally natural and unnatural speech', 
                                    '4 : Good - Mostly natural speech', 
                                    '5 : Excellent - Completely natural speech'], key=f'{label}_score')
            elif label == 'SMOS':
                st.radio(f'score', ['1 : Bad - Completely dissimilar speaker', 
                                    '2 : Poor - Mostly dissimilar speaker', 
                                    '3 : Fair - Equally similar and dissimilar speaker', 
                                    '4 : Good - Mostly similar speaker', 
                                    '5 : Excellent - Completely similar speaker'], key=f'{label}_score')
            else:
                st.radio(f'score', ['-2 : Source completely Better', 
                                    '-1 : Source mostly Better', 
                                    '0 : Neutral', 
                                    '1 : Target mostly Better', 
                                    '2 : Target completely Better'], key=f'{label}_score')
            st.button('Next', key=f'{label}_submit')
        
        if st.session_state[f'{label}_submit']: 
            if st.session_state[count] < num_assigns:
                st.session_state[date] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # record
                if label == 'MOS':
                    csv_writer.writerow([st.session_state[date], 
                                        worker,
                                        st.session_state[audio_path], 
                                        st.session_state[text],
                                        st.session_state[f'{label}_score']])
                else: 
                    csv_writer.writerow([st.session_state[date], 
                                        worker,
                                        st.session_state[src_audio_path], 
                                        st.session_state[tgt_audio_path], 
                                        st.session_state[text],
                                        st.session_state[f'{label}_score']])
                st.session_state[count] += 1
            
            if st.session_state[count] < num_assigns:
                if label == 'MOS':
                    st.session_state[audio_path] = testset['audio_url'][st.session_state[count]]
                elif label == 'SMOS':
                    st.session_state[src_audio_path] = testset['ref_audio_url'][st.session_state[count]]
                    st.session_state[tgt_audio_path] = testset['test_audio_url'][st.session_state[count]]
                else:
                    st.session_state[src_audio_path] = testset['src_audio_url'][st.session_state[count]]
                    st.session_state[tgt_audio_path] = testset['test_audio_url'][st.session_state[count]]
                st.session_state[text] = testset['original_text'][st.session_state[count]]
                
                st.session_state[elapsed_time] = time.perf_counter() - st.session_state[stamp]
                st.session_state[log] = f"Completed {st.session_state[count]} out of {num_assigns} | Keep going, you're almost there! 😊 \n\n"
                st.session_state[percent] = float(st.session_state[count]/num_assigns)
                
            else:
                st.balloons()

        with col1:
            if label == 'MOS':
                st.subheader('Audio:')
                st.audio(st.session_state[audio_path], format="audio/wav")
                st.markdown(f'**Transcription**: {st.session_state[text]}')
            else:
                st.subheader('Source audio:')
                st.audio(st.session_state[src_audio_path], format="audio/wav")
                st.subheader('Target audio:')
                st.audio(st.session_state[tgt_audio_path], format="audio/wav")
                st.markdown(f'**Transcription**: {st.session_state[text]}')

        if st.session_state[count] < num_assigns:
            pbar.progress(st.session_state[percent], text=st.session_state[log])
        else:
            st.success(f'{label} test is done. \n It took a total of ({convert_seconds_to_hhmmss(st.session_state[elapsed_time])}) to assess {num_assigns} samples.\n\n' )



def log_out():
    st.session_state["logged_in"] = False
    st.success("Logged out!")
    sleep(0.5)
    st.switch_page("main.py")

def main():
    st.set_page_config(
            page_title="Audio Evaluation",
            page_icon="👋",
        )
    st.caption('Made by Changjin Han')  
    worker = st.session_state.get("name")
    if not worker: log_out()

    st.markdown(f'# Worker: :rainbow[***{worker}***]')

    labels = ['MOS', 'SMOS', 'CMOS']
    tabs = st.tabs(labels)

    css = '''
            <style>
                .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
                font-size:1.5rem;
                }
            </style>
        '''

    st.markdown(css, unsafe_allow_html=True)

    postfix = datetime.now().strftime("%Y_%m_%d")

    for label, tab in zip(labels, tabs):
        data_path = f'testset/{label}.csv'
        df = load_data(data_path)
        
        page(label, tab, df, worker, postfix)

if __name__ == '__main__':
    main()