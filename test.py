from itertools import groupby
from types import new_class

from pandas.io.formats.format import Datetime64Formatter
import streamlit as st
# import matplotlib.pyplot as plt
from google.oauth2 import service_account
from datetime import datetime as dt #-> Để xử lý data dạng datetime
import gspread #-> Để update data lên Google Spreadsheet
import numpy as np
import pandas as pd #-> Để update data dạng bản
from gspread_dataframe import set_with_dataframe #-> Để update data lên Google Spreadsheet
from oauth2client.service_account import ServiceAccountCredentials #-> Để nhập Google Spreadsheet Credentials
# import seaborn as sns
import base64
# from matplotlib import animation
from io import BytesIO
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
        # syntaxs_df
        process_syntax=syntaxs_df #[~syntaxs_df["Step"].str.contains('HP', na=False)]
        # process_syntax
        sh2=gc1.open('HP - Hist').worksheet('Category')
        category=sh2.get_all_records()
        category_df=pd.DataFrame(category)

        sh4=gc1.open('Handpick - Đơn đặt hàng').worksheet('1. DON HANG')
        order=sh4.get_all_records()
        order_=pd.DataFrame(order)
        order_=order_.drop(columns={'DÒNG','NHÓM','ĐVT','QUI CÁCH','LOẠI QC','GHI CHÚ','NMSX','LOẠI HÀNG','GỖ','NỆM','TÊN HANDPICK','NGÀY LẬP','SỐ ĐƠN HÀNG',"XUẤT MỚI"},axis=0)
        # order_['NGÀY XUẤT']=order_['NGÀY XUẤT'].astype('datetime64')
        # order_['CHANGED']=order_['CHANGED'].astype('datetime64')
        order_['NGÀY XUẤT MỚI']=order_.apply(lambda x: x['CHANGED'] if x['CHANGED']!="" else x['NGÀY XUẤT'],axis=1)
 
        order_['S/L']=order_['S/L'].astype('str')
        order_['ID ORDER']=order_['ID ORDER'].astype('str')
        order_.columns=order_.columns.str.replace(" ","_")    
        order_['ID1']=order_['KHUNG']+order_['KIM_LOẠI']+order_['VENEER_-_GC_NGOÀI']
        sub_order=order_[['ID_ORDER','ID1']]
        sub_order_=sub_order.merge(category_df,how='left',on='ID1')
        sub_order_=sub_order_[['ID_ORDER','ID','Descriptions']]

        order_df=order_.merge(sub_order_,how='left',on='ID_ORDER')
        order_df=order_df[['ID_ORDER','TÊN_TTF','S/L','SƠN','NGÀY_XUẤT_MỚI','ID','Descriptions','CHANGED','ĐÓNG_GÓI']]

        order_df=order_df.rename(columns={'Descriptions':'Loại ĐH'})
        # order_df
        BB=order_df[order_df['ĐÓNG_GÓI'].str.contains("L")]
        
        sh3=gc1.open('HP - Hist').worksheet('Form')
        Form=sh3.get_all_records()
        Form_df=pd.DataFrame(Form)
        Form_df.columns=Form_df.columns.str.replace(" ","_")
        # Form_df
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
        # data_v
                # data_v4['ID_ORDER']=data_v4.astype('str')
        data_v44=data_v[['ID_ORDER','Bộ_phận','BỘ_PHẬN','Mô_Tả','Dấu_thời_gian','NHÀ_MÁY','Thao_tác_của_bạn']]
        data_v44['BỘ_PHẬN']=data_v44['BỘ_PHẬN'].astype(int)
        sh4=gc1.open('HP - Hist').worksheet('Trang tính5')
        stt=sh4.get_all_records()
        stt_df=pd.DataFrame(stt)
        stt_df.columns=stt_df.columns.str.replace(" ","_")

        data_v4=data_v44.append(stt_df)
        data_v4=data_v4.sort_values(by=['ID_ORDER','BỘ_PHẬN','Dấu_thời_gian'])
        data_v4_=data_v4[data_v4['Bộ_phận'].str.contains("D")==False]

        list_order=data_v4_['ID_ORDER'].unique().tolist()
        _list={}
        for i in list_order:
            _list[i]={}
            _list[i]['Thời_gian']=data_v4_.loc[data_v4_.ID_ORDER==i]['Dấu_thời_gian'].to_list()
            # _list[i]['Bước']=data_v4.loc[data_v4.ID_ORDER==i]['BỘ_PHẬN'].to_list()
            _list[i]['Bộ_Phận']=data_v4_.loc[data_v4_.ID_ORDER==i]['Bộ_phận'].to_list()
            _list[i]['Tình_trạng']=data_v4_.loc[data_v4_.ID_ORDER==i]['Mô_Tả'].to_list()

            _list[i]['Nhà_máy']=data_v4_.loc[data_v4_.ID_ORDER==i]['NHÀ_MÁY'].to_list()
        new_={k:{sk:sv[-1] for sk,sv in s.items() if len(sv)>0} for k,s in _list.items() }
        new_status=pd.DataFrame.from_dict(new_, orient='index').reset_index()
        # new_status['Bước']=new_status['Bước'].astype(str).astype(int)
        # new_status

        new_status=new_status.rename(columns={'index':'ID_ORDER'})

        order_df_=order_df.merge(new_status,how='left',on='ID_ORDER')

        import datetime as dt 

        order_df_f=order_df_.copy()
        order_df_f['Thời_gian']=order_df_f['Thời_gian'].astype('datetime64')
        order_df_f['Ngày_giải_quyết']= (dt.datetime.today()- order_df_f['Thời_gian']).dt.days

        D_=data_v4.loc[(data_v4['Bộ_phận'].str.contains('D')==True)].sort_values(by=['ID_ORDER','Dấu_thời_gian'])
        D_=D_.replace(np.nan," ")
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

        order_D_=order_D[['ID_ORDER','NGÀY_XUẤT_MỚI','TÊN_TTF','Tình_trạng','Bộ_Phận','S/L','Thời_gian']]
        order_tm=order_D_.copy()

        order_tm['Thời_gian']=order_tm['Thời_gian'].astype('datetime64')
        order_tm['Ngày_giải_quyết']= (dt.datetime.today()- order_tm['Thời_gian']).dt.days


        spreadsheet_key = '1DHvhU43JWaeODEUGel9JknkgVJWBen1RNtzRhViq93g' # input SPREADSHEET_KEY HERE
        # sh = gc1.open_by_key(spreadsheet_key)
        # # ACCES GOOGLE SHEET
        # sheet_index_no1 = 3

        # worksheet1 = sh.get_worksheet(sheet_index_no1)#-> 0 - first sheet, 1 - second sheet etc. 

        # set_with_dataframe(worksheet1, order_tm) #-> Upload user_df vào Sheet đầu tiên trong Spreadsheet

        return new_status,order_df_f,order_tm,BB
st.set_page_config(layout='wide')
st.markdown("<h1 style='text-align: center; color: blue;font-style:bold'>OPERATION DASHBOARD</h1>", unsafe_allow_html=True)
st.markdown("<h6 style='text-align: right; color:black;font-style: italic'> Developed by HTL</h6>", unsafe_allow_html=True)
st.markdown("")
import io

def download_link(object_to_download, download_filename, download_link_text):

    if isinstance(object_to_download,pd.DataFrame):
        # object_to_download = object_to_download.to_excel(index = False, header=True,encoding="cp1258")
            
        towrite = io.BytesIO()
        downloaded_file = object_to_download.to_excel(towrite, encoding='utf-8', index=False, header=True) # write to BytesIO buffer
        towrite.seek(0)  # reset pointer
        b64 = base64.b64encode(towrite.read()).decode() 
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="myfilename.xlsx">Bấm vào đây để tải danh sách về</a>'


def highlight(val):
    yellow = 'background-color: #ff9966' if 7<val <11  else 'background-color:#a1e2ff' if val <=2 else 'background-color: #2edaff' if 2<val<=4 else 'background-color: #99cc33' if 4<val<=7 else 'background-color: 	#ff5252' if val >11 else 'background-color: white' 
    return yellow
def color(val):
    color = 'orange' if 'Chờ' in str(val)  or 'Đợi' in str(val) else 'yellow' if 'Thiếu' in str(val) or "chưa" in str(val) else 'gray' if 'Hủy' in str(val) else 'red'  if "ngưng" in str(val) else "whitr"
    return f'background-color: {color}'

def select_col(x):
    c1 = 'background-color: yellow'
    c2 = 'color: white'
    c3=""
    #compare columns
    mask = x['CHANGED'] !="0"
    #DataFrame with same index and columns names as original filled empty strings
    df1 =  pd.DataFrame(c3, index=x.index, columns=x.columns)
    #modify values of df1 column by boolean mask
    df1.loc[mask, 'NGÀY_XUẤT_MỚI'] = c1
    df1['CHANGED'] = c2
    return df1



def main():
    username = st.sidebar.text_input("User Name") 
    password = st.sidebar.text_input("Password",type='password')
    if st.sidebar.checkbox("Login"):
        if  password==st.secrets["passwords"] and username==st.secrets['user']:
            list=created_data()
            last_status=list[0]
            order_df=list[1]
            order_df=order_df.drop(columns={'ID'})
            order_df=order_df.replace("",np.nan)
            order_df=order_df[order_df['ID_ORDER'].isnull()==False]
            order_df['S/L']=order_df['S/L'].astype(int)
            order_df=order_df.replace(np.nan,0)

            order_df['Ngày_giải_quyết']=order_df['Ngày_giải_quyết'].astype(int)

            D=list[2]
            BB=list[3]
            D=D[D['S/L'].isnull()==False]
            c1,c2,c3= st.columns((.833,.833,.833))

            with c1:
                id_or=st.text_input('Nhập SĐH',)
            # col1,col2=st.columns((2.5,2))
            list_order=[]
            or_result=0
            # with col1:
            if not id_or:
                or_result=order_df
                TM=D
            else:
                or_result=order_df.loc[order_df['ID_ORDER'].str.contains(id_or,na=False)]
                TM=D[D['ID_ORDER'].str.contains(id_or,na=False)].set_index(drop=True)
            list_order=or_result['ID_ORDER'].unique().tolist()
            or_result[['Tình_trạng','Bộ_Phận']]=or_result[['Tình_trạng','Bộ_Phận']].fillna(value='0. Chưa cập nhật')

            st.subheader('Báo cáo tổng quan')
            st.markdown('##### Đang xử lí tại các bộ phận:')
            doing=or_result[or_result['Tình_trạng'].str.contains('ngưng')==False]
            group=doing.groupby('Bộ_Phận').agg({'ID_ORDER':'count','S/L':'sum'}).reset_index()
            group
            pen=or_result[or_result['Tình_trạng'].str.contains('ngưng')==True]
            er = or_result[or_result['Tình_trạng'].str.contains('sai')==True]
            st.markdown("##### Tạm ngưng: {} mã - {} sp".format(len(pen['ID_ORDER'].tolist()),sum(pen['S/L'].astype(int)),unsafe_allow_html=True))
            # group2=doing.groupby('Bộ_Phận').agg({'ID_ORDER':'count','S/L':'sum'}).reset_index()
            st.markdown("##### Đang sai/thiếu thông tin: {} mã - {} sp".format(len(er['ID_ORDER'].tolist()),sum(er['S/L'].astype(int)),unsafe_allow_html=True))
            or_result=or_result.astype(str)
#             or_result
            
            or_result=or_result[(or_result['Bộ_Phận']!="0")&(or_result['Bộ_Phận']!="L. Hoàn thành")]
            or_result['ID_ORDER'].tolist()
            st.markdown('### DANH SÁCH CÁC ĐƠN HÀNG ĐANG CÓ: {} mã - {} sp'.format(len(or_result['ID_ORDER'].tolist()),sum(or_result['S/L'].astype(int)),unsafe_allow_html=True))
           

            or_result=or_result[['ID_ORDER','TÊN_TTF','Nhà_máy','NGÀY_XUẤT_MỚI','Bộ_Phận','Tình_trạng','Ngày_giải_quyết','S/L','SƠN','Loại ĐH','CHANGED']]
            or_result['Ngày_giải_quyết']=or_result['Ngày_giải_quyết'].astype(int)
            or_result['S/L']=or_result['S/L'].astype(int)
            or_result1=or_result.copy()
            or_result11=or_result1.style.applymap(highlight,subset=['Ngày_giải_quyết'])
            or_result111=or_result11.apply(select_col, axis=None)
            st.dataframe(or_result111.applymap(color,subset=['Tình_trạng']),height =170,width=1400)   
            st.markdown('')
            st.markdown('')

            st.markdown("#### Tình trạng thu mua: {} mã - {} sp".format(len(D['ID_ORDER'].tolist()),sum(D['S/L'].astype(int)),unsafe_allow_html=True))
            D=D.style.applymap(highlight,subset=['Ngày_giải_quyết'])
            st.dataframe(D.applymap(color,subset=['Tình_trạng']),height =170,width=1400) 
            st.markdown('')
            st. markdown('')       
            bp_df=or_result[or_result['Bộ_Phận']=='0. Chưa cập nhật']
            bp_df_=bp_df[['ID_ORDER','TÊN_TTF','NGÀY_XUẤT_MỚI','Nhà_máy','Tình_trạng','Ngày_giải_quyết','S/L','SƠN','CHANGED']].reset_index(drop=True)

            st.markdown("#### Tình trạng bao bì mới: {} mã - {} sp".format(len(BB['ID_ORDER'].tolist()),sum(BB['S/L'].astype(int)),unsafe_allow_html=True))
            # BB=BB.style.applymap(highlight,subset=['Ngày_giải_quyết'])
            # st.dataframe(BB.style.applymap(color,subset=['Tình_trạng']),height =170,width=1400) 
            BB
            st.markdown('')
            st. markdown('')       
            bp_df=or_result[or_result['Bộ_Phận']=='0. Chưa cập nhật']
            bp_df_=bp_df[['ID_ORDER','TÊN_TTF','NGÀY_XUẤT_MỚI','Nhà_máy','Tình_trạng','Ngày_giải_quyết','S/L','SƠN','CHANGED']].reset_index(drop=True)




            st.markdown("#### 0. Chưa cập nhật: {} mã - {} sp".format(len(bp_df_['ID_ORDER'].tolist()),sum(bp_df_['S/L'].astype(int)),unsafe_allow_html=True))
            bp_df_1=bp_df_.style.applymap(highlight,subset=['Ngày_giải_quyết'])
            bp_df_=bp_df_1.apply(select_col, axis=None)
            st.dataframe(bp_df_.applymap(color,subset=['Tình_trạng']),height =170,width=1400) 
            st.markdown('')
            st. markdown('')     



            r3_1,R,r3_2=st.columns((1.25,.1,1.25))
            list_1=['A. Đơn hàng','B. PKTH','G. Sơn','I. Nệm']
            list_2=['C. Phôi','E. Hàng trắng','K. QC TP']

            bp_df=or_result[or_result['Bộ_Phận']=='A. Đơn hàng']
            bp_df_=bp_df[['ID_ORDER','TÊN_TTF','Nhà_máy','NGÀY_XUẤT_MỚI','Tình_trạng','Ngày_giải_quyết','S/L','SƠN','CHANGED']].reset_index(drop=True)

            st.markdown("#### A. Đơn hàng: {} mã - {} sp".format(len(bp_df_['ID_ORDER'].tolist()),sum(bp_df_['S/L'].astype(int)),unsafe_allow_html=True))
            bp_df_1=bp_df_.style.applymap(highlight,subset=['Ngày_giải_quyết'])
            bp_df_=bp_df_1.apply(select_col, axis=None)

            st.dataframe(bp_df_.applymap(color,subset=['Tình_trạng']),height =170,width=1400) 
            st.markdown('')
            st. markdown('')                     



            bp_df=or_result[or_result['Bộ_Phận']=='B. PKTH']
            bp_df_=bp_df[['ID_ORDER','TÊN_TTF','Nhà_máy','NGÀY_XUẤT_MỚI','Tình_trạng','Ngày_giải_quyết','S/L','SƠN','CHANGED']].reset_index(drop=True)
            st.markdown("####  B. PKTH: {} mã - {} sp".format(len(bp_df_['ID_ORDER'].tolist()),sum(bp_df_['S/L'].astype(int)),unsafe_allow_html=True))
            bp_df_1=bp_df_.style.applymap(highlight,subset=['Ngày_giải_quyết'])
            bp_df_=bp_df_1.apply(select_col, axis=None)
            st.dataframe(bp_df_.applymap(color,subset=['Tình_trạng']),height =170,width=1400) 
            st.markdown('')
            st.markdown('')     

            bp_df=or_result[or_result['Bộ_Phận']=='C. Phôi']
            bp_df_=bp_df[['ID_ORDER','TÊN_TTF','Nhà_máy','NGÀY_XUẤT_MỚI','Tình_trạng','Ngày_giải_quyết','S/L','SƠN','CHANGED']].reset_index(drop=True)
            st.markdown("#### C. Phôi: {} mã - {} sp".format(len(bp_df_['ID_ORDER'].tolist()),sum(bp_df_['S/L'].astype(int)),unsafe_allow_html=True))
            bp_df_=bp_df_.style.applymap(highlight,subset=['Ngày_giải_quyết'])
            bp_df_=bp_df_.apply(select_col, axis=None)

            st.dataframe(bp_df_.applymap(color,subset=['Tình_trạng']),height =170,width=1400) 
            st.markdown('')           
            st.markdown('')                         

            bp_df=or_result[or_result['Bộ_Phận']=='E. Hàng trắng']
            bp_df_=bp_df[['ID_ORDER','TÊN_TTF','Nhà_máy','NGÀY_XUẤT_MỚI','Tình_trạng','Ngày_giải_quyết','S/L','SƠN','CHANGED']].reset_index(drop=True)
            st.markdown("#### D. Hàng trắng: {} mã - {} sp".format(len(bp_df_['ID_ORDER'].tolist()),sum(bp_df_['S/L'].astype(int)),unsafe_allow_html=True))
            bp_df_=bp_df_.style.applymap(highlight,subset=['Ngày_giải_quyết'])
            bp_df_=bp_df_.apply(select_col, axis=None)

            st.dataframe(bp_df_.applymap(color,subset=['Tình_trạng']),height =170,width=1400) 
            st.markdown('')          
            st.markdown('')     

            bp_df=or_result[or_result['Bộ_Phận']=='G. Sơn']
            bp_df_=bp_df[['ID_ORDER','TÊN_TTF','Nhà_máy','NGÀY_XUẤT_MỚI','Tình_trạng','Ngày_giải_quyết','S/L','SƠN','CHANGED']].reset_index(drop=True)
            st.markdown("#### E. Sơn: {} mã - {} sp".format(len(bp_df_['ID_ORDER'].tolist()),sum(bp_df_['S/L'].astype(int)),unsafe_allow_html=True))
            bp_df_=bp_df_.style.applymap(highlight,subset=['Ngày_giải_quyết'])
            bp_df_=bp_df_.apply(select_col, axis=None)

            st.dataframe(bp_df_.applymap(color,subset=['Tình_trạng']),height =170,width=1400) 
            st.markdown('')            
            st.markdown('')                         

            bp_df=or_result[or_result['Bộ_Phận']=='I. Nệm']
            bp_df_=bp_df[['ID_ORDER','TÊN_TTF','Nhà_máy','NGÀY_XUẤT_MỚI','Tình_trạng','Ngày_giải_quyết','S/L','SƠN','CHANGED']].reset_index(drop=True)
            st.markdown( "#### F. Nệm: {} mã - {} sp".format(len(bp_df_['ID_ORDER'].tolist()),sum(bp_df_['S/L'].astype(int)),unsafe_allow_html=True))
            bp_df_=bp_df_.style.applymap(highlight,subset=['Ngày_giải_quyết'])
            bp_df_=bp_df_.apply(select_col, axis=None)

            st.dataframe(bp_df_.applymap(color,subset=['Tình_trạng']),height =170,width=1400) 
            st.markdown('')
            st.markdown('')     

            bp_df=or_result[or_result['Bộ_Phận']=='K. QC TP']
            bp_df_=bp_df[['ID_ORDER','TÊN_TTF','Nhà_máy','NGÀY_XUẤT_MỚI','Tình_trạng','Ngày_giải_quyết','S/L','SƠN','CHANGED']].reset_index(drop=True)
            st.markdown("#### G. QC TP: {} mã - {} sp ".format(len(bp_df_['ID_ORDER'].tolist()),sum(bp_df_['S/L'].astype(int)),unsafe_allow_html=True))
            bp_df_=bp_df_.style.applymap(highlight,subset=['Ngày_giải_quyết'])
            bp_df_=bp_df_.apply(select_col, axis=None)

            st.dataframe(bp_df_.applymap(color,subset=['Tình_trạng']),height =170,width=1400) 

            bp_df=or_result[or_result['Bộ_Phận']=='L. Hoàn thành']
            bp_df_=bp_df[['ID_ORDER','TÊN_TTF','Nhà_máy','NGÀY_XUẤT_MỚI','Tình_trạng','Ngày_giải_quyết','S/L','SƠN','CHANGED']].reset_index(drop=True)
            st.markdown("#### Đơn hàng đã hoàn tất: {} mã - {} sp".format(len(bp_df_['ID_ORDER'].tolist()),sum(bp_df_['S/L'].astype(int)),unsafe_allow_html=True))
            bp_df_=bp_df_.style.applymap(highlight,subset=['Ngày_giải_quyết'])
            bp_df_=bp_df_.apply(select_col, axis=None)

            st.dataframe(bp_df_.applymap(color,subset=['Tình_trạng']),height =170,width=1400) 

            with c2:
                cho=st.selectbox('Chọn danh sách cần tải',['ĐH đang tạm ngừng','ĐH đang thiếu/sai','ĐH đang triển khai'])
            with c3:
                if cho=='ĐH đang tạm ngừng':
                    file=or_result[or_result['Tình_trạng'].str.contains('Tạm ngưng')]
                elif cho=='ĐH đang thiếu/sai':
                    file=or_result[or_result['Tình_trạng'].str.contains('thiếu/sai')]
                else:
                    file=or_result1
                st.markdown("")
                tmp_download_link = download_link(file, 'YOUR_DF.csv', 'Bấm vào đây để tải danh sách!')
                st.markdown(tmp_download_link, unsafe_allow_html=True)
        else:
            st.warning("Incorrect Username/Password")
if __name__=='__main__':
    main()
