import streamlit as st
from google.oauth2 import service_account
from datetime import datetime as dt #-> Để xử lý data dạng datetime
import gspread #-> Để update data lên Google Spreadsheet
import numpy as np
import pandas as pd #-> Để update data dạng bản
from oauth2client.service_account import ServiceAccountCredentials #-> Để nhập Google Spreadsheet Credentials
import seaborn as sns
def created_data():
                ## Collect QR scan database from Googlesheet
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'],)
        gc1 = gspread.authorize(credentials)
        spreadsheet_key = '1VakpJ7a7o1Eosyh-wto80X0TrkTYSxfaEwNoza3KlLw' # input SPREADSHEET_KEY HERE

        #syntax_df
        sh1 = gc1.open("HP - Hist").worksheet('Syntaxs')
        syntaxs_=sh1.get_all_records()
        syntaxs_df=pd.DataFrame(syntaxs_)
        process_syntax=syntaxs_df #[~syntaxs_df["Step"].str.contains('HP', na=False)]

        sh2=gc1.open('HP - Hist').worksheet('Category')
        category=sh2.get_all_records()
        category_df=pd.DataFrame(category)
        sh4=gc1.open('Handpick - Đơn đặt hàng').worksheet('1. DON HANG')
        order=sh4.get_all_records()
        order_=pd.DataFrame(order)
        order_=order_.drop(columns={'KHÁCH HÀNG','NHÓM','ĐVT','QUI CÁCH','ĐÓNG GÓI','LOẠI QC','GHI CHÚ','NMSX','LOẠI HÀNG','GỖ','SƠN','NỆM','TÊN TTF','NGÀY LẬP','SỐ ĐƠN HÀNG'},axis=0)
        order_['S/L']=order_['S/L'].astype('str')
        order_['ID ORDER']=order_['ID ORDER'].astype('str')
        order_.columns=order_.columns.str.replace(" ","_")    
        order_['Order Category 3']=order_['KHUNG']+order_['KIM_LOẠI']+order_['VENEER']
        sub_order=order_[['ID_ORDER','Order Category 3']]
        sub_order_=sub_order.merge(category_df,how='left',on='Order Category 3')
        sub_order_=sub_order_[['ID_ORDER','ID','Descriptions']]
        order_df=order_.merge(sub_order_,how='left',on='ID_ORDER')
        order_df=order_df[['ID_ORDER','TÊN_HANDPICK','S/L','NGÀY_XUẤT','ID','Descriptions']]


        sh3=gc1.open('HP - Hist').worksheet('Form')
        Form=sh3.get_all_records()
        Form_df=pd.DataFrame(Form)
        Form_df.columns=Form_df.columns.str.replace(" ","_")

        data=Form_df.set_index(['Dấu_thời_gian','Thao_tác_của_bạn'])
        data.columns=data.columns.str.split('-', expand=True)

        data_df=data.stack().reset_index().rename(columns={'level_2':'state'})
        data_df=data_df.replace("",np.nan)
        data_df=data_df.loc[data_df['QUÉT_MÃ_ĐHM'].isnull()==False ]

        data_v1=data_df.copy()
        data_v1[['BỘ_PHẬN', 'ID','NHÀ_MÁY']] = data_v1['Thao_tác_của_bạn'].str.split('-', 2, expand=True)
        data_v1=data_v1.rename(columns={'QUÉT_MÃ_ĐHM':'ID_ORDER'})

        data_v2=data_v1.merge(sub_order_,on='ID_ORDER',how='left')
        data_v2=data_v2.sort_values(by=['ID_ORDER','BỘ_PHẬN','Dấu_thời_gian'])
        data_v3=data_v2.replace("",np.nan).ffill(axis = 0).reset_index()
        data_v=data_v3.merge(process_syntax,how='left',on='Thao_tác_của_bạn')
        data_v4=data_v[data_v['Bộ_phận'].str.contains('D')==False]
        # data_v4['ID_ORDER']=data_v4.astype('str')

        list_order=data_v4['ID_ORDER'].unique().tolist()
        _list={}
        for i in list_order:
            _list[i]={}
            _list[i]['Thời_gian']=data_v4.loc[data_v4.ID_ORDER==i]['Dấu_thời_gian'].to_list()
            _list[i]['Bước']=data_v4.loc[data_v4.ID_ORDER==i]['BỘ_PHẬN'].to_list()
            _list[i]['Bộ_Phận']=data_v4.loc[data_v4.ID_ORDER==i]['Bộ_phận'].to_list()
            _list[i]['Tình_trạng']=data_v4.loc[data_v4.ID_ORDER==i]['Mô_Tả'].to_list()
            # _list[i]['Nhóm_ĐH']=data_v4.loc[data_v4.ID_ORDER==i]['Order Category 1'].to_list()
            _list[i]['Nhóm_ThuMua']=data_v4.loc[data_v4.ID_ORDER==i]['Descriptions'].to_list()
            _list[i]['Nhà_máy']=data_v4.loc[data_v4.ID_ORDER==i]['NHÀ_MÁY'].to_list()

        new_={k:{sk:sv[-1] for sk,sv in s.items() if len(sv)>0} for k,s in _list.items() }
        new_status=pd.DataFrame.from_dict(new_, orient='index').reset_index()
        new_status['Bước']=new_status['Bước'].astype(str).astype(int)

        new_={k:{sk:sv[-1] for sk,sv in s.items() if len(sv)>0} for k,s in _list.items() }
        new_status=pd.DataFrame.from_dict(new_, orient='index').reset_index()
        new_status=new_status.rename(columns={'index':'ID_ORDER','Bước':'STEP'})
        order_df_=order_df.merge(new_status,how='left',on='ID_ORDER')
        order_df_f=order_df_.drop(columns={'Thời_gian','STEP','NGÀY_XUẤT'})
        D_=data_v.loc[data_v['Bộ_phận'].str.contains('D')==True]
        tm_order=D_['ID_ORDER'].unique().tolist()
        tm_list={}
        for j in tm_order:
            tm_list[j]={}
            tm_list[j]['Thời_gian']=D_.loc[D_.ID_ORDER==j]['Dấu_thời_gian'].to_list()
            tm_list[j]['Bộ_Phận']=D_.loc[D_.ID_ORDER==j]['Bộ_phận'].to_list()
            tm_list[j]['Tình_trạng']=D_.loc[D_.ID_ORDER==j]['Mô_Tả'].to_list()     

        tm_df={k2:{sk2:sv2[-1] for sk2,sv2 in s2.items() if len(sv2)>0} for k2,s2 in tm_list.items() }
        tm_df_=pd.DataFrame.from_dict(tm_df, orient='index').reset_index()
        tm_df_=tm_df_.rename(columns={'index':'ID_ORDER','Bước':'STEP'})
        order_D=tm_df_.merge(order_df,how='left',on='ID_ORDER')
        order_D_=order_D[['ID_ORDER','TÊN_HANDPICK','Tình_trạng']]
        return new_status,order_df_f,order_D_
st.set_page_config(layout='wide')
st.markdown("<h1 style='text-align: center; color: blue;font-style:bold'>OPERATION DASHBOARD</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: right; color:black;font-style: italic'> Created by HTL</h4>", unsafe_allow_html=True)
st.markdown("")
# def color_survived(val):
#     color = 'red' if val==0 else 'yellow' if val==1 else 'green'
#     return f'background-color: {color}'
def color_survived(s):        
    if s.str.contains('đợi')== True:
        return 'background-color: green'
    elif s.str.contains('ngưng')== rue:
        return 'background-color: red'
def main():
    username = st.sidebar.text_input("User Name")
    password = st.sidebar.text_input("Password",type='password')
    if st.sidebar.checkbox("Login"):
        if password == '7611':
            list=created_data()
            last_status=list[0]
            order_df=list[1]
            order_df=order_df.drop(columns={'ID','Descriptions'})

            st.dataframe(order_df.style.applymap(color_survived, subset=['Tình_trạng']))

#             st.dataframe(order_df.style.applymap(styler, subset=['Tình trạng']))

            D=list[2]
            c1_1,c1_2=st.columns((2.5,2))
            c1,c2,c3 = st.columns((1.125,1.125,1.75))
            with c1_2:
                st.markdown('### B. TIẾN ĐỘ CHUNG')
            with c1_1:
                st.markdown('### A. TIẾN ĐỘ ĐƠN HÀNG')
            with c1:
                id_or=st.text_input('Nhập SĐH',)
            col1,col2=st.columns((2.5,2))
            list_order=[]
            or_result=0
            with col1:
                if not id_or:
                    or_result=order_df
                    TM=D
                else:
                    or_result=order_df.loc[order_df['ID_ORDER'].str.contains(id_or,na=False)]
                    TM=D[D['ID_ORDER'].str.contains(id_or,na=False)]
                list_order=or_result['ID_ORDER'].unique().tolist()
                or_result[['Tình_trạng','Bộ_Phận']]=or_result[['Tình_trạng','Bộ_Phận']].fillna(value='0. Chưa cập nhật')
                list_bp=sorted(or_result['Bộ_Phận'].unique().tolist())
                st.markdown('')
                st.write(or_result)
            r3_1,r3_2,r3_3,r3_4=st.columns((1.25,1.25,1,1))
            for l in range(0,round(len(list_bp)/2)):
                with r3_1:
                    st.markdown("<h4 style='text-align: left; color: blue;font-style:bold'>{}</h1>".format(list_bp[l]),unsafe_allow_html=True)
                    st.markdown('')
                    bp_df=or_result[or_result['Bộ_Phận']==list_bp[l]].reset_index()
                    bp_df_=bp_df[['ID_ORDER','TÊN_HANDPICK','Tình_trạng']]
                    bp_df_
                    st.markdown("<h4 style='text-align: left; color: blue;font-style:bold'>D. Thu mua</h1>",unsafe_allow_html=True)
                    D
            for m in range(round(len(list_bp)/2),len(list_bp)):
                with r3_2:
                    st.markdown("<h4 style='text-align: left; color: blue;font-style:bold'>{}</h1>".format(list_bp[m]),unsafe_allow_html=True)
                    st.markdown('')
                    bp_df=or_result[or_result['Bộ_Phận']==list_bp[m]].reset_index()
                    bp_df_=bp_df[['ID_ORDER','TÊN_HANDPICK','Tình_trạng']]
                    bp_df_
        else:
            st.warning("Incorrect Username/Password")
if __name__=='__main__':
    main()
