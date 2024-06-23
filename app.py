import streamlit as st
import requests
import json
import pandas as pd

if "df" not in st.session_state:
    st.session_state.df = None
# if "url" not in st.session_state:
#     st.session_state.url = ""

st.title('Redhat Pandas')
st.markdown("### Enter your website. We'll pentest it for you")
url = st.text_input(label="Link", placeholder="https://")


def colorCoding(row):
  if "clear" in row.security.lower():
    return ['background-color: green'] * len(row) 
  else:
    return ['background-color: red'] * len(row)

if st.session_state.df is not None:
    st.dataframe(st.session_state.df, use_container_width=True, 
                 width=1000, hide_index=True)
    


text_spinner_placeholder = st.empty()
# st.set_page_config(page_title="Redhat Panda", page_icon="🤖")

def getAuditReportForDevelopers():
    # with text_spinner_placeholder:
    #     with st.spinner("Please wait while your Tweet is being generated..."):
  print('dev', url)
  params = {'baseUrl': url}
  res = requests.get('https://jllewis11--example-linkscraper-check.modal.run/', params=params)
  print(res.status_code)

  res.encoding = 'utf-8'

  data = json.loads(res.json())
  # print(data)
  df = pd.DataFrame.from_dict(data, orient='index').reset_index()
  df.rename(columns={'index':'url', 0: 'security'}, inplace=True)
  df = df.style.apply(colorCoding, axis=1)
  st.session_state.df = df
    
def getAuditReportForUsers():
    print('users')


col1, col2 = st.columns(2)
with col1:
    st.session_state.users = not st.button(
        label="Full Report",
        type="primary",
        on_click=getAuditReportForDevelopers,
    )

with col2:
    st.session_state.users = st.button(
        label="Summary",
        type="secondary",
        on_click=getAuditReportForUsers,
    )