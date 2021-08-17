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
        spreadsheet_key='1DHvhU43JWaeODEUGel9JknkgVJWBen1RNtzRhViq93g'
        #syntax_df
        sh1 = gc1.open("HP - Hist").worksheet('Syntaxs')
        syntaxs_=sh1.get_all_records()
        syntaxs_df=pd.DataFrame(syntaxs_)
        process_syntax=syntaxs_df #[~syntaxs_df["Step"].str.contains('HP', na=False)]

        # checker_syntax=syntaxs_df.loc[syntaxs_df["Step"].str.contains('HP')==True]

        sh2=gc1.open('HP - Hist').worksheet('Category')
        category=sh2.get_all_records()
        category_df=pd.DataFrame(category)


        sh3=gc1.open('HP - Hist').worksheet('Form')
        Form=sh3.get_all_records()
        Form_df=pd.DataFrame(Form)
        Form_df.columns=Form_df.columns.str.replace(" ","_")

        sh4=gc1.open('Handpick - Đơn đặt hàng').worksheet('1. DON HANG')
        order=sh4.get_all_records()
        order_df=pd.DataFrame(order)
        order_df=order_df.drop(columns={'KHÁCH HÀNG','HÌNH ẢNH','NHÓM','ĐVT','QUI CÁCH','ĐÓNG GÓI','LOẠI QC','GHI CHÚ','NMSX','LOẠI HÀNG','GỖ','SƠN','NỆM','TÊN TTF','NGÀY LẬP','SỐ ĐƠN HÀNG'},axis=0)
        order_df.columns=order_df.columns.str.replace(" ","_")       

        data=Form_df.set_index(['Dấu_thời_gian','Thao_tác_của_bạn'])
        data.columns=data.columns.str.split('-', expand=True)


        data_df=data.stack().reset_index().rename(columns={'level_2':'state'})
        data_df=data_df.replace("",np.nan)
        data_df=data_df.loc[data_df['QUÉT_MÃ_ĐHM'].isnull()==False ]
        data_v1=data_df

        data_v1[['BỘ_PHẬN', 'ID','NHÀ_MÁY']] = data_v1['Thao_tác_của_bạn'].str.split('-', 2, expand=True)
        # data_v1.head()

        data_v2=data_v1.merge(category_df,how='left',on='ID')
        data_v2=data_v2.sort_values(by=['QUÉT_MÃ_ĐHM','BỘ_PHẬN','Dấu_thời_gian'])
        data_v3=data_v2.replace("",np.nan).ffill(axis = 0).reset_index()
        data_v4=data_v3.merge(process_syntax,how='left',on='Thao_tác_của_bạn')


        # MKV_list=[1,2,3,4,5,6,7,8,9,10,11]
        # MKL_list=[1,2,3,6,5,7,8,9,10,11]
        # MKO_list=[1,2,3,6,7,8,9,10,11]
        # MVE_list=[1,2,3,6,4,7,8,9,10,11]
        # CKO_list=[1,2,3,6,7,8,9,10,11]
        # CKL_list=[1,2,3,6,5,7,8,9,10,11]
        # CVE_list=[1,2,3,6,4,7,8,9,10,11]
        # CKV_list=[1,2,3,6,4,5,7,8,9,10,11]
        # TKO_list=[1,6,7,8,9,10,11]
        # TKL_list=[1,6,5,7,8,9,10,11]
        # TVE_list=[1,6,4,7,8,9,10,11]
        # TKV_list=[1,5,4,6,7,8,9,10,11]
        # step_list=[MKO_list,MKL_list,MVE_list,MKV_list,CKO_list,CKL_list,CVE_list,CKV_list,TKO_list,TKL_list,TVE_list,TKV_list]
        # cate=['MKO','MKL','MVE','MKV','CKO','CKL','CVE','CKV','TKO','TKL','TVE','TKV']
        # dict_cate={cate[i]:step_list[i] for i in range(len(cate))}

        # def create_frame(df,id,st):
        #     id_df=df.loc[df['Order Category 4']==id]['QUÉT_MÃ_ĐHM'].unique().tolist()
        #     step=st[id]
        #     data_cate={dish:step for dish in id_df}
        #     # cate_id=pd.DataFrame.from_dict(data_cate,orient='index').reset_index()
        #     # cate_id=cate_id.rename(columns = {'index':'order_ID',0:'Step'})
        #     return data_cate

        # MKO_ID=create_frame(data_v4,cate[0],dict_cate)
        # MKL_ID=create_frame(data_v4,cate[1],dict_cate)
        # MVE_ID=create_frame(data_v4,cate[2],dict_cate)
        # MKV_ID=create_frame(data_v4,cate[3],dict_cate)
        # CKO_ID=create_frame(data_v4,cate[4],dict_cate)
        # CKL_ID=create_frame(data_v4,cate[5],dict_cate)
        # CVE_ID=create_frame(data_v4,cate[6],dict_cate)
        # CKV_ID =create_frame(data_v4,cate[7],dict_cate)
        # TKO_ID =create_frame(data_v4,cate[8],dict_cate)
        # TKL_ID =create_frame(data_v4,cate[9],dict_cate)
        # TKV_ID=create_frame(data_v4,cate[10],dict_cate)
        # data_={**MKO_ID,**MKL_ID,**MVE_ID,**MKV_ID,**CKO_ID,**CKL_ID,**CVE_ID,**CKV_ID,**TKO_ID,**TKL_ID,**TKV_ID}
        # data_step=pd.DataFrame.from_dict(data_, orient='index').reset_index()


        # dataa=pd.melt(data_step,id_vars=['index'],var_name='Step')
        # dataa['ID_ORDER']=dataa['index']
        # dataa['STEP']=dataa.value
        # dataa_df=dataa[['ID_ORDER','STEP']].loc[dataa['STEP'].isnull()==False]
        # dataa_df=dataa_df.sort_values(by=['ID_ORDER','STEP'])
        # dataa_df['STEP_IN']=dataa_df['STEP']
        # dataa_df['STEP_OT']=dataa_df['STEP'].shift(-1,axis=0)


        # data_v5=data_v4.copy()
        # data_v5=data_v5[['Dấu_thời_gian','Thao_tác_của_bạn','QUÉT_MÃ_ĐHM','BỘ_PHẬN','Order Category 4','ID']]
        # data_v5=data_v5.sort_values(by=['QUÉT_MÃ_ĐHM','BỘ_PHẬN','Dấu_thời_gian','Order Category 4'])
        # data_v5=data_v5.rename(columns={'QUÉT_MÃ_ĐHM':'ID_ORDER','BỘ_PHẬN':'STEP_IN'})
        # data_v5['STEP_IN']=data_v5['STEP_IN'].astype(str).astype(int)
        # data_v5['STEP_OT']=data_v5['STEP_IN']
        # data_v5_df=data_v5.loc[data_v5['ID']=='CF']

        # TM=data_v4.copy()
        # TM=TM[['Dấu_thời_gian','Thao_tác_của_bạn','QUÉT_MÃ_ĐHM','BỘ_PHẬN','Order Category 4','ID']]
        # TM=TM.sort_values(by=['QUÉT_MÃ_ĐHM','BỘ_PHẬN','Dấu_thời_gian','Order Category 4'])
        # TM=TM.rename(columns={'QUÉT_MÃ_ĐHM':'ID_ORDER','BỘ_PHẬN':'STEP_IN_x'})
        # TM['STEP_IN_x']=TM['STEP_IN_x'].astype(str).astype(int)
        # TM['STEP_OT_x']=TM['STEP_IN_x']
        # TMdf=TM.loc[((TM['ID']=='CF')|(TM['ID']=='QD'))&((TM['STEP_IN_x']==4)|(TM['STEP_IN_x']==5))]
        # TMdf_df=TMdf[['Dấu_thời_gian','ID_ORDER','STEP_IN_x','STEP_OT_x','ID']]

        # TM_IN=TMdf_df.loc[TMdf_df['ID']=='CF']
        # TM_OT=TMdf_df.loc[TMdf_df['ID']=='QD']
        # TM_IN=TM_IN.rename(columns={'Dấu_thời_gian':'Dấu_thời_gian_x','STEP_IN_x':'STEP'}).drop(columns={'STEP_OT_x','ID'})
        # TM_OT=TM_OT.rename(columns={'Dấu_thời_gian':'Dấu_thời_gian_y','STEP_OT_x':'STEP'}).drop(columns={'STEP_IN_x','ID'})

        # TM_df=TM_IN.merge(TM_OT,how='left',on=['ID_ORDER','STEP'])
        # TM_df=TM_df.set_index(['ID_ORDER','STEP'])


        # data_v5_df=data_v5_df.loc[(data_v5_df['STEP_IN']!=4)&(data_v5_df['STEP_IN']!=5)]
        # history=dataa_df.merge(data_v5_df,how='left',on=['ID_ORDER','STEP_IN'])
        # history['STEP_OT']=history['STEP_OT_x']
        # history_df=history.merge(data_v5_df,how='left',on=['ID_ORDER','STEP_OT'])
        # TD_df=history_df[['ID_ORDER','STEP','Dấu_thời_gian_x','Dấu_thời_gian_y']].set_index(['ID_ORDER','STEP'])

        # TD_df_f=TD_df.merge(TM_df,how='left',on=['ID_ORDER','STEP']).reset_index()
        # TD_df_f['NGÀY_NHẬN']=TD_df_f['Dấu_thời_gian_x_x'].mask(pd.isnull,TD_df_f['Dấu_thời_gian_x_y'])
        # TD_df_f['NGÀY_GIAO']=TD_df_f['Dấu_thời_gian_y_x'].mask(pd.isnull,TD_df_f['Dấu_thời_gian_y_y'])
        # TD_df_final=TD_df_f[['ID_ORDER','STEP','NGÀY_NHẬN','NGÀY_GIAO']]
        list_order=data_v4['QUÉT_MÃ_ĐHM'].unique().tolist()
        _list={}
        for i in list_order:
            _list[i]={}
            _list[i]['Thời_gian']=data_v4.loc[data_v4.QUÉT_MÃ_ĐHM==i]['Dấu_thời_gian'].to_list()
            _list[i]['Bước']=data_v4.loc[data_v4.QUÉT_MÃ_ĐHM==i]['BỘ_PHẬN'].to_list()
            _list[i]['Bộ_Phận']=data_v4.loc[data_v4.QUÉT_MÃ_ĐHM==i]['Bộ_phận'].to_list()
            _list[i]['Tình_trạng']=data_v4.loc[data_v4.QUÉT_MÃ_ĐHM==i]['Mô_Tả'].to_list()
            _list[i]['Nhóm_ĐH']=data_v4.loc[data_v4.QUÉT_MÃ_ĐHM==i]['Order Category 1'].to_list()
            _list[i]['Nhóm_ThuMua']=data_v4.loc[data_v4.QUÉT_MÃ_ĐHM==i]['Order Category 3'].to_list()
            _list[i]['Nhà_máy']=data_v4.loc[data_v4.QUÉT_MÃ_ĐHM==i]['NHÀ_MÁY'].to_list()

        # TD_df_final['NGÀY_NHẬN']=pd.to_datetime(TD_df_final['NGÀY_NHẬN'])
        # TD_df_final['NGÀY_GIAO']=pd.to_datetime(TD_df_final['NGÀY_GIAO'])

        hist_order=pd.DataFrame.from_dict(_list, orient='index').reset_index()
        new_={k:{sk:sv[-1] for sk,sv in s.items() if len(sv)>0} for k,s in _list.items() }
        new_status=pd.DataFrame.from_dict(new_, orient='index').reset_index()
        new_status=new_status.rename(columns={'index':'ID_ORDER','Bước':'STEP'})
        order_df_=order_df.merge(new_status,how='left',on='ID_ORDER')
        order_df_f=order_df_.drop(columns={'Thời_gian','STEP','NGÀY_XUẤT','Nhóm_ĐH'})
        # working_days=TD_df_final.copy()
        # working_days['NGÀY_GIẢI_QUYẾT']=working_days.apply(lambda x: len(pd.bdate_range(x['NGÀY_NHẬN'],
        #                                                                 x['NGÀY_GIAO'])) if x.notnull().all() else np.nan, axis = 1)
        # working_days['THÁNG_GIAO']=pd.DatetimeIndex(working_days['NGÀY_GIAO']).month
        # pivot=working_days[['ID_ORDER','STEP','NGÀY_GIẢI_QUYẾT','THÁNG_GIAO']]
        # pivot_df=pivot.pivot_table(index=['ID_ORDER','THÁNG_GIAO'],columns='STEP',values='NGÀY_GIẢI_QUYẾT').reset_index()
        # # pivot_df=pivot_df.apply(lambda x: x.fillna(x.mean()),axis=0)
        # pivot_df=pivot_df.fillna(pivot_df.groupby('THÁNG_GIAO').transform('mean'))
        # unpivot=pivot_df.melt(id_vars=['ID_ORDER','THÁNG_GIAO'],value_name='NGÀY_GIẢI_QUYẾT')
        # order_df_f
        return new_status,order_df_f
st.set_page_config(layout='wide')
st.markdown("<h1 style='text-align: center; color: blue;font-style:bold'>OPERATION DASHBOARD</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: right; color:black;font-style: italic'> Created by HTL</h4>", unsafe_allow_html=True)
st.markdown("")

def main():
    username = st.sidebar.text_input("User Name")
    password = st.sidebar.text_input("Password",type='password')
    if st.sidebar.checkbox("Login"):
        if password == '7611':
            list=created_data()
            last_status=list[0]
            order_df=list[1]
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
                else:
                    or_result=order_df.loc[order_df['ID_ORDER'].str.contains(id_or,na=False)]
                list_order=or_result['ID_ORDER'].unique().tolist()
                list_bp=or_result['Bộ_Phận'].unique().tolist()
                st.markdown('')
                st.write(or_result)
            
            with col2:
                    for l in list_bp:
                        st.markdown('### {}'.format(l))
                        bp_df=or_result[or_result['Bộ_Phận']==l].reset_index()
                        bp_df_=bp_df[['ID_ORDER','TÊN_HANDPICK','Tình_trạng']]
                        bp_df_
        else:
            st.warning("Incorrect Username/Password")
main()

