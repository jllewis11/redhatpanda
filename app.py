import os

import streamlit as st

import requests
import json
import pandas as pd

from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))

def ask_openai(text):
  prompt = f"If the evaluation report I give you declares the response data to be clear or secure, say 0. If it is a potential risk, say 2. If it is a risk, say 1. Here's the report: {text}"
  response = client.chat.completions.create(
    model="gpt-4o",  # You can use other models like "gpt-3.5-turbo"
    messages=[
      {"role": "system", "content": "You are evaluating whether a report says a system is secure or not"},
      {"role": "user", "content": prompt}
    ],
    max_tokens=150  # Adjust the response length as needed
  )
  return response.choices[0].message.content

def summarize_report():
  # if st.session_state.df is None:
  getAuditReportForDevelopers()
  
  prompt = f"Summarize the potential and current security risks. Here's the report: {st.session_state.raw}"
  response = client.chat.completions.create(
    model="gpt-4o",  # You can use other models like "gpt-3.5-turbo"
    messages=[
      {"role": "system", "content": "You are evaluating whether a report says a system is secure or not"},
      {"role": "user", "content": prompt}
    ],
    max_tokens=150  # Adjust the response length as needed
  )
  print(response.choices[0].message)
  st.session_state.summary = response.choices[0].message.content

t = 'The response data contains sensitive information that poses a security risk. The data includes an API key for Segment.io, which should not be exposed publicly. This could potentially allow unauthorized access to the Segment.io account and its associated data. Additionally, the response includes details about the project and its integrations, which could also be considered sensitive information. Therefore, I cannot say "clear" in this case.'
# print(ask_openai("clear") is '0')

if "df" not in st.session_state:
  st.session_state.df = None
if "summary" not in st.session_state:
   st.session_state.summary = ""
if "raw" not in st.session_state:
   st.session_state.raw = ""
# if "url" not in st.session_state:
#     st.session_state.url = ""

st.title('Redhat Pandas')
st.markdown("### Enter your website. We'll pentest it for you")
url = st.text_input(label="Link", placeholder="https://")


def colorCoding(row):
  # value = True if "clear" in row.security.lower() else False #
  value = ask_openai(row.security)
  if value == "0":
    return ['background-color: green'] * len(row) 
  elif value == "2":
    return ['background-color: yellow'] * len(row) 
  else:
    return ['background-color: red'] * len(row)

if st.session_state.df is not None:
    st.dataframe(st.session_state.df, use_container_width=True, 
                 width=1000, hide_index=True)
    
if st.session_state.summary != "":
  st.markdown("### Summary")
  # st.text_area(st.session_state.summary)
  st.markdown(f"""<span style="word-wrap: break-word;">{st.session_state.summary}</span>""", unsafe_allow_html=True)

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
  st.session_state.raw = df['security'].apply(lambda x: ' '.join(x.split())).tolist()
  df = df.style.apply(colorCoding, axis=1)
  st.session_state.df = df
  # df.to_csv('out.csv', index=False)
    
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
        on_click=summarize_report,
    )