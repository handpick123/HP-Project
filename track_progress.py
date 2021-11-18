from itertools import groupby
import streamlit as st
from google.oauth2 import service_account
from datetime import datetime as dt #-> Để xử lý data dạng datetime
import gspread #-> Để update data lên Google Spreadsheet
import numpy as np
import pandas as pd #-> Để update data dạng bản
from gspread_dataframe import set_with_dataframe #-> Để update data lên Google Spreadsheet
from oauth2client.service_account import ServiceAccountCredentials #-> Để nhập Google Spreadsheet Credentials
# import seaborn as sns
import base64
from io import BytesIO
def created_data():
                ## Collect QR scan database from Googlesheet
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'],)
        gc1 = gspread.authorize(credentials)
        sh1 = gc1.open("HP - Hist").worksheet('Syntaxs')
        syntaxs_=sh1.get_all_records()
        syntaxs_df=pd.DataFrame(syntaxs_)
        syntaxs_df=syntaxs_df.replace("",np.nan)
        progress=syntaxs_df[(syntaxs_df['Step'].isnull()==True)&(syntaxs_df['Bộ_phận'].isnull()==False)]
        progress=progress[['Bộ_phận','Mô_Tả']]
        # prog
        sh4=gc1.open('Handpick - Đơn đặt hàng').worksheet('1. DON HANG')
        order=sh4.get_all_records()
        order_=pd.DataFrame(order)
        order_=order_.drop(columns={'KHÁCH HÀNG','NHÓM','ĐVT','QUI CÁCH','ĐÓNG GÓI','LOẠI QC','GHI CHÚ','NMSX','LOẠI HÀNG','GỖ','NỆM','TÊN HANDPICK','NGÀY LẬP','SỐ ĐƠN HÀNG'},axis=0)     

        return order_,progress


data=created_data()
progress=data[1]
order=data[0]
# progress
bp=progress['Bộ_phận'].unique().tolist()
bp_=st.multiselect('Tại bộ phận:',bp)
td_l=progress[progress['Bộ_phận'].isin(bp_)]
td_ll=td_l['Mô_Tả'].tolist()
with st.form(key="ac"):
    order_pb=order.copy()
    order_pb=order_pb[['ID ORDER','TÊN TTF','S/L','SƠN']]
    order_pb['Check']=order_pb["TÊN TTF"] +" _ "+order_pb['ID ORDER']
    id=order_pb['Check'].tolist()
    td=st.multiselect('Ở tiến độ',td_ll)

    id_sp=st.multiselect('Có các sản phẩm sau:',id)
    
    st.form_submit_button("Cập nhật")


