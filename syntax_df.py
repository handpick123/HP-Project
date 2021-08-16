import pandas as pd
def abc():
    print(5)
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
# def create_df(df):
#     MKO_ID=create_frame(df,cate[0],dict_cate)
#     MKL_ID=create_frame(df,cate[1],dict_cate)
#     MVE_ID=create_frame(df,cate[2],dict_cate)
#     MKV_ID=create_frame(df,cate[3],dict_cate)
#     CKO_ID=create_frame(df,cate[4],dict_cate)
#     CKL_ID=create_frame(df,cate[5],dict_cate)
#     CVE_ID=create_frame(df,cate[6],dict_cate)
#     CKV_ID =create_frame(df,cate[7],dict_cate)
#     TKO_ID =create_frame(df,cate[8],dict_cate)
#     TKL_ID =create_frame(df,cate[9],dict_cate)
#     TKV_ID=create_frame(df,cate[10],dict_cate)
#     data_={**MKO_ID,**MKL_ID,**MVE_ID,**MKV_ID,**CKO_ID,**CKL_ID,**CVE_ID,**CKV_ID,**TKO_ID,**TKL_ID,**TKV_ID}
#     data_step=pd.DataFrame.from_dict(data_, orient='index').reset_index()
#     return data_step