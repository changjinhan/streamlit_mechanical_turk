from time import sleep
import streamlit as st 

def log_in():
    st.session_state["logged_in"] = True
    st.success("Logged in!")
    sleep(0.5)
    st.switch_page("pages/audio_evaluation.py")


if __name__ == '__main__':
    if not st.session_state.get("logged_in", False):
        st.set_page_config(
            page_title="SMT",
            page_icon="👋",
        )
        st.title('Streamlit Mechanical Turk (SMT)')
        st.caption('Made by Changjin Han')

        # start = None
        # visible = True if start else False
        worker_info = st.form('Worker Info')
        name = worker_info.text_input('Type your name:')
        st.session_state['name'] = name
        start = worker_info.form_submit_button('Start!')
        if start: log_in()
    