import datetime
import pandas as pd
import numpy as np
from hbshare.fe.XZ import db_engine
from hbshare.fe.XZ import  functionality
import statsmodels.api as sm



localdb=db_engine.PrvFunDB().engine
hbdb=db_engine.HBDB()
util=functionality.Untils()


def get_monthly_jjnav(jjdm):

    #get the nav ret  for given jjdm and time zone(already times 100)
    sql="select jjdm,tjyf,rqzh,hb1y from st_fund.t_st_gm_yhb where jjdm ='{0}' and rq1y!=99999  "\
        .format(jjdm)
    navdf=hbdb.db2df(sql, db='funduser')

    max_yearmonth=navdf['tjyf'].max()
    min_yearmonth=navdf['tjyf'].min()

    return navdf,max_yearmonth,min_yearmonth

def get_daily_jjnav(jjdm_list,start_date=None,end_date=None):

    jjdm_con=util.list_sql_condition(jjdm_list)

    sql="select jjdm,jzrq,hbdr from st_fund.t_st_gm_rhb where jjdm in ({0}) and hbdr!=99999 and hbdr!=0  "\
        .format(jjdm_con)
    navdf=hbdb.db2df(sql, db='funduser')

    return navdf

def get_monthly_index_ret(zqdm,start_date=None,end_date=None):

    sql="select zqdm,tjyf,rqzh,hb1y from st_market.t_st_zs_yhb where zqdm='{0}' and abs(hb1y)!=99999 "\
        .format(zqdm)

    benchmark_ret=hbdb.db2df(sql, db='alluser')

    return  benchmark_ret

def bhar(arr):
        return 100*(np.power(np.cumprod((arr+100)/100).tolist()[-1],1/len(arr))-1)

def ols_for_group(arr):

    y_col=arr.columns[0]
    x_col=arr.columns.tolist()
    x_col.remove(y_col)

    result=sm.OLS(arr[y_col].values, arr[x_col].values).fit()

    # return util.my_general_linear_model_func(arr[x_col].values,
    #                                   arr[y_col].values)['x'].tolist()
    return result.params.tolist()

def get_barra_daily_ret(start_date=None,end_date=None):
    #barra return daily return
    sql='select factor_ret,factor_name,trade_date from st_ashare.r_st_barra_factor_return'
    test=hbdb.db2df(sql,db='alluser')
    factor_name_list=test['factor_name'].unique().tolist()
    factor_ret_df=pd.DataFrame()
    date_list=test['trade_date'].unique().tolist()
    date_list.sort()
    factor_ret_df['date']=date_list
    for factor in factor_name_list:
        factor_ret_df=pd.merge(factor_ret_df,test[test['factor_name']==factor][['factor_ret','trade_date']],
                               how='left',left_on='date',right_on='trade_date').drop('trade_date',axis=1)
        factor_ret_df.rename(columns={'factor_ret':factor},inplace=True)

    return factor_ret_df

def get_styleindex_ret(index_list,start_date=None,end_date=None):

    # style daily return
    style_ret=pd.DataFrame()
    for zqdm in index_list:

        #sql = "select spjg,zqmc,jyrq from st_market.t_st_zs_hqql where zqdm='{}' ".format(zqdm)
        sql= "select zqdm,jyrq,hbdr from st_market.t_st_zs_rhb where zqdm='{}' and hbdr!=0 ".format(zqdm)
        test = hbdb.db2df(sql=sql, db='alluser')
        #test['ret'] = test['spjg'].pct_change()
        test[zqdm]=test['hbdr']
        test.set_index('jyrq',inplace=True)
        style_ret=pd.concat([style_ret,test[zqdm]],axis=1)

    return style_ret

def get_jj_daily_ret(jjdm_list):

    tempdf = get_daily_jjnav(jjdm_list)
    jj_ret = pd.DataFrame()
    jj_ret['date'] = tempdf.sort_values('jzrq')['jzrq']
    for jjdm in tempdf['jjdm'].unique():
        jj_ret=pd.merge(jj_ret,tempdf[tempdf['jjdm']==jjdm][['hbdr','jzrq']],
                        how='left',left_on='date',right_on='jzrq').drop('jzrq',axis=1)
        jj_ret.rename(columns={'hbdr':jjdm},inplace=True)
        # jj_ret[jjdm]=jj_ret[jjdm]/100

    jj_ret.set_index('date',drop=True,inplace=True)

    return jj_ret

class Scenario_return:
    @staticmethod
    def get_histroy_scenario_ret():
        benchmark_ret=get_monthly_index_ret('000002')
        benchmark_ret['med']=99999
        benchmark_ret['scenario'] = ''
        for i in range(1,len(benchmark_ret)):
            benchmark_ret.loc[i,'med']=benchmark_ret.loc[0:i-1]['hb1y'].median()
            if(benchmark_ret.loc[i,'med']>=benchmark_ret.loc[i,'hb1y']):
                benchmark_ret.loc[i, 'scenario']='opt'
            else:
                benchmark_ret.loc[i, 'scenario'] = 'pes'

        return  benchmark_ret[['scenario','hb1y','tjyf','rqzh']]

    @staticmethod
    def pessimistic_ret(jjdm,benchmark_ret):

        navdf,max_yearmonth,min_yearmonth=get_monthly_jjnav(jjdm)

        navdf=pd.merge(navdf,benchmark_ret,how='left',on='tjyf')

        navdf['ext_ret']=navdf['hb1y_x']-navdf['hb1y_y']
        navdf.rename(columns={'rqzh_y':'rqzh'},inplace=True)

        #last 12 month average month return by calculating last 12 month cul ret and turn it into month return

        temp=navdf[navdf['scenario']=='pes']['ext_ret'].rolling(12).apply(bhar)
        temp=temp.to_frame('pes_ext_ret')
        navdf=pd.merge(navdf,temp,how='left',left_index=True, right_index=True)

        temp=navdf[navdf['scenario']=='opt']['ext_ret'].rolling(12).apply(bhar)
        temp=temp.to_frame('opt_ext_ret')
        navdf=pd.merge(navdf,temp,how='left',left_index=True, right_index=True)

        navdf['ext_ret'] = navdf['ext_ret'].rolling(12).apply(bhar)


        last_pes_ret=np.nan
        last_opt_ret=np.nan

        for i in range(0,len(navdf)):
            if(navdf.loc[i]['pes_ext_ret']==navdf.loc[i]['pes_ext_ret']):
                last_pes_ret=navdf.loc[i]['pes_ext_ret']

            else:
                navdf.loc[i,'pes_ext_ret']=last_pes_ret

            if(navdf.loc[i]['opt_ext_ret']==navdf.loc[i]['opt_ext_ret']):
                last_opt_ret=navdf.loc[i]['opt_ext_ret']

            else:
                navdf.loc[i,'opt_ext_ret']=last_opt_ret

        navdf=navdf[navdf['ext_ret'].notnull()]

        # for col in['ext_ret','pes_ext_ret','opt_ext_ret']:
        #     navdf[col] = (navdf[col]/100).astype(float).map("{:.2%}".format)

        return navdf[['jjdm','tjyf','rqzh','ext_ret','pes_ext_ret','opt_ext_ret']]

    @staticmethod
    def factorlize_ret(factor_name,fre='M'):

        sql="select * from scenario_ret"
        raw_df=pd.read_sql(sql,con=localdb)

        raw_df.rename(columns={'rqzh':'date'},inplace=True)
        raw_df=raw_df[raw_df[factor_name].notnull()]


        if(fre=='Q'):
            raw_df = raw_df[(raw_df['tjyf'].astype(str).str[4:6] == '03') | (raw_df['tjyf'].astype(str).str[4:6] == '06') | (
                        raw_df['tjyf'].astype(str).str[4:6] == '09') | (raw_df['tjyf'].astype(str).str[4:6] == '12')]
        elif(fre=='HA'):
            raw_df = raw_df[(raw_df['tjyf'].astype(str).str[4:6] == '06') | (raw_df['tjyf'].astype(str).str[4:6] == '12')]


        return raw_df

class Style_exp:


    def __init__(self,asofdate,fre='Q',start_date=None,end_date=None):


        self.jjdm_list=util.get_mutual_stock_funds(asofdate)

        #self.write_style_exp2DB(self.jjdm_list, fre, start_date, end_date)

        self.write_industry_exp2DB(self.jjdm_list, fre, start_date, end_date)

    @staticmethod
    def write_style_exp2DB(jjdm_list,fre,start_date=None,end_date=None):

        value_col = ['399370', '399371']
        size_col=['399314','399315','399316']
        bond_col=['CBA00301']

        #get value index ret :
        style_index_ret=get_styleindex_ret(value_col+size_col+bond_col)

        if(fre=='M'):
            def timezone_transform(olsdf):
                olsdf['yearmonth'] = [str(x)[0:6] for x in olsdf.index]
                return olsdf
        elif(fre=='Q'):
            def timezone_transform(olsdf):
                olsdf['yearmonth'] = ''
                olsdf.loc[olsdf.index.astype(str).str[4:6]<='03','yearmonth']='Q1'
                olsdf.loc[(olsdf.index.astype(str).str[4:6] <= '06')&(olsdf.index.astype(str).str[4:6] > '03'), 'yearmonth'] = 'Q2'
                olsdf.loc[(olsdf.index.astype(str).str[4:6] <= '09')&(olsdf.index.astype(str).str[4:6] > '06'), 'yearmonth'] = 'Q3'
                olsdf.loc[(olsdf.index.astype(str).str[4:6] <= '12')&(olsdf.index.astype(str).str[4:6] > '09'), 'yearmonth'] = 'Q4'
                olsdf['yearmonth']=olsdf.index.astype(str).str[0:4]+olsdf['yearmonth']

                return olsdf

        value_exp_df = pd.DataFrame()
        size_exp_df = pd.DataFrame()

        for jjdm in jjdm_list:

            #get jj nav ret
            jj_ret=get_jj_daily_ret([jjdm])

            olsdf = pd.merge(jj_ret, style_index_ret, how='inner', left_index=True, right_index=True)

            olsdf=timezone_transform(olsdf)


            tempdf=olsdf[olsdf[[jjdm]+value_col+bond_col].notnull().sum(axis=1)==(len(value_col)+2)]
            tempdf=tempdf.groupby('yearmonth')[[jjdm]+value_col+bond_col].apply(ols_for_group).to_frame('exp')
            i=0
            for col in value_col+bond_col:
                tempdf[col]=[x[i] for x in tempdf['exp']]
                i+=1
            tempdf.drop('exp',inplace=True,axis=1)
            tempdf['jjdm']=jjdm
            value_exp_df=pd.concat([value_exp_df,tempdf],axis=0)


            tempdf=olsdf[olsdf[[jjdm]+size_col+bond_col].notnull().sum(axis=1)==(len(size_col)+2)]
            tempdf=tempdf.groupby('yearmonth')[[jjdm]+size_col+bond_col].apply(ols_for_group).to_frame('exp')
            i=0
            for col in size_col+bond_col:
                tempdf[col]=[x[i] for x in tempdf['exp']]
                i+=1
            tempdf.drop('exp',inplace=True,axis=1)
            tempdf['jjdm'] = jjdm
            size_exp_df=pd.concat([size_exp_df,tempdf],axis=0)

            print('jj {} Done'.format(jjdm))

        value_exp_df=value_exp_df.reset_index().rename(columns={'yearmonth':'date'})
        size_exp_df=size_exp_df.reset_index().rename(columns={'yearmonth':'date'})

        value_exp_df['fre']=fre
        size_exp_df['fre']=fre

        value_exp_df.to_sql('nav_value_exposure',index=False,if_exists='append',con=localdb)
        size_exp_df.to_sql('nav_size_exposure', index=False, if_exists='append',con=localdb)

    @staticmethod
    def write_industry_exp2DB(jjdm_list,fre,start_date=None,end_date=None):

        industry_con=['801010','801030','801040','801050','801080','801110','801120','801130','801140','801150',
                      '801160','801170','801180','801200','801210','801230','801710','801720','801730','801740',
                      '801750','801760','801770','801780','801790','801880','801890','801950','801960','801970','801980'
]
        bond_col=['CBA00301']

        #get value index ret :
        style_index_ret=get_styleindex_ret(industry_con+bond_col)

        if(fre=='M'):
            def timezone_transform(olsdf):
                olsdf['yearmonth'] = [str(x)[0:6] for x in olsdf.index]
                return olsdf
        elif(fre=='Q'):
            def timezone_transform(olsdf):
                olsdf['yearmonth'] = ''
                olsdf.loc[olsdf.index.astype(str).str[4:6]<='03','yearmonth']='Q1'
                olsdf.loc[(olsdf.index.astype(str).str[4:6] <= '06')&(olsdf.index.astype(str).str[4:6] > '03'), 'yearmonth'] = 'Q2'
                olsdf.loc[(olsdf.index.astype(str).str[4:6] <= '09')&(olsdf.index.astype(str).str[4:6] > '06'), 'yearmonth'] = 'Q3'
                olsdf.loc[(olsdf.index.astype(str).str[4:6] <= '12')&(olsdf.index.astype(str).str[4:6] > '09'), 'yearmonth'] = 'Q4'
                olsdf['yearmonth']=olsdf.index.astype(str).str[0:4]+olsdf['yearmonth']

                return olsdf

        industry_exp_df = pd.DataFrame()

        for jjdm in jjdm_list:

            #get jj nav ret
            jj_ret=get_jj_daily_ret([jjdm])

            olsdf = pd.merge(jj_ret, style_index_ret, how='inner', left_index=True, right_index=True)

            olsdf=timezone_transform(olsdf)


            tempdf=olsdf[olsdf[[jjdm]+industry_con+bond_col].notnull().sum(axis=1)==(len(industry_con)+2)]
            tempdf=tempdf.groupby('yearmonth')[[jjdm]+industry_con+bond_col].apply(ols_for_group).to_frame('exp')
            i=0
            for col in industry_con+bond_col:
                tempdf[col]=[x[i] for x in tempdf['exp']]
                i+=1
            tempdf.drop('exp',inplace=True,axis=1)
            tempdf['jjdm']=jjdm
            industry_exp_df=pd.concat([industry_exp_df,tempdf],axis=0)

            print('jj {} Done'.format(jjdm))

        industry_exp_df=industry_exp_df.reset_index().rename(columns={'yearmonth':'date'})

        industry_exp_df['fre']=fre

        industry_exp_df.to_sql('nav_industry_exposure',index=False,if_exists='append',con=localdb)

class Style_analysis:

    def __init__(self,jjdm_list,fre,asofdate=datetime.datetime.today().strftime('%Y%m%d'),time_length=3):

        self.value_col = ['399370', '399371']
        self.size_col=['399314','399315','399316']
        self.bond_col=['CBA00301']
        self.industry_col=['801010','801030','801040','801050','801080','801110','801120','801130','801140','801150',
                  '801160','801170','801180','801200','801210','801230','801710','801720','801730','801740',
                  '801750','801760','801770','801780','801790','801880','801890','801950','801960','801970','801980']

        self.index_map=dict(zip(self.value_col+self.size_col,['成长','价值','大盘','中盘','小盘']))
        self.industry_map=dict(zip(self.industry_col,['农林牧渔(申万)','基础化工(申万)','钢铁(申万)','有色金属(申万)',
                                                      '电子(申万)','家用电器(申万)','食品饮料(申万)','纺织服饰(申万)',
                                                      '轻工制造(申万)','医药生物(申万)','公用事业(申万)','交通运输(申万)',
                                                      '房地产(申万)','商贸零售(申万)','社会服务(申万)','综合(申万)',
                                                      '建筑材料(申万)','建筑装饰(申万)','电力设备(申万)','国防军工(申万)',
                                                      '计算机(申万)','传媒(申万)','通信(申万)','银行(申万)','非银金融(申万)',
                                                      '汽车(申万)','机械设备(申万)','煤炭(申万)','石油石化(申万)','环保(申万)',
                                                      '美容护理(申万)']))

        start_year=str(int(asofdate[0:4])-3)

        if(fre=='M'):
            start_date=start_year+asofdate[4:6]
        else:
            if(asofdate[4:6]<='03'):
                Q=1
            elif(asofdate[4:6]>'03' and asofdate[4:6]<='06'):
                Q=2
            elif(asofdate[4:6]>'06' and asofdate[4:6]<='09'):
                Q=3
            elif(asofdate[4:6]>'09' and asofdate[4:6]<='12'):
                Q=4
            start_date=start_year+"Q"+str(Q)

        # self.size_exp=self.read_jj_style_exp(jjdm_list,'size',fre,start_date)
        # self.value_exp=self.read_jj_style_exp(jjdm_list,'value',fre,start_date)
        # self.industry_exp=self.read_jj_style_exp(jjdm_list,'industry',fre,start_date)
        self.val_date=self.get_jj_valuation_date(jjdm_list,asofdate)
        self.fre=fre
        self.asofdate=asofdate
        self.start_date=start_date

    @staticmethod
    def get_jj_valuation_date(jjdm_list,asofdate):

        jjdm_con=util.list_sql_condition(jjdm_list)
        #read jjjl info
        sql="select jjdm,ryxm,rydm,rzrq from st_fund.t_st_gm_jjjl where ryzt='-1' and jjdm in ({0}) "\
            .format(jjdm_con)
        jj_val_date=hbdb.db2df(sql,db='funduser')

        #for jj with multi managers,take the one with longer staying in this jj
        jj_val_date=jj_val_date.sort_values('rzrq')
        jj_val_date.drop_duplicates('jjdm', keep='first', inplace=True)

        #remove jj with manager managing no longer than 1.5years
        # last_oneandhalfyear = (datetime.datetime.strptime(asofdate, '%Y%m%d')
        #                        -datetime.timedelta(days=560)).strftime('%Y%m%d')
        # jj_val_date['rzrq']=jj_val_date['rzrq'].astype(str)
        # jj_val_date=jj_val_date[jj_val_date['rzrq']<=last_oneandhalfyear]


        return  jj_val_date[['jjdm','rzrq','rydm']]

    @staticmethod
    def read_jj_style_exp(jjdm_list,type,fre,start_date):

        jjdm_con=util.list_sql_condition(jjdm_list)
        sql="select * from nav_{0}_exposure where jjdm in ({1}) and fre='{2}' and date>='{3}'"\
            .format(type,jjdm_con,fre,start_date)
        expdf=pd.read_sql(sql,con=localdb)

        return  expdf

    @staticmethod
    def cal_style_shift_ratio(df,style_col):

        df=df.copy()
        # calculate the total change in styles
        df['change'] = df[style_col].diff().abs().sum(axis=1)
        # calculate the average style exp between two dates
        df['avg_exp'] = df[style_col].sum(axis=1).rolling(2).mean()
        # calculate shift ratio
        df['shift_ratio'] = df['change'] / df['avg_exp']

        return df['shift_ratio'].values

    def get_style_property(self,style_df,style_col,type,method='rank'):

        if(type=='industry'):
            style_map= self.industry_map
        else:
            style_map = self.index_map


        #standradlize the exp by either robustscaler or by ranking for each date
        if(method=='robust'):
            from sklearn.preprocessing import RobustScaler
            rs = RobustScaler()
            style_df[style_col]=rs.fit_transform(style_df[style_col].values)
        else:
            style_df[style_col] = style_df.groupby('date').rank(method='min')[style_col]
            style_df=pd.merge(style_df,
                              style_df.groupby('date').count()['jjdm'].to_frame('count'),
                              left_on='date',right_index=True)
            for col in style_col:
                style_df[col]=style_df[col]/style_df['count']


        asofdate=style_df['date'].max()

        style_property_df=pd.DataFrame()

        temp=style_df.groupby('jjdm').min()['date']
        new_jjdm_list=temp[temp<=self.start_date].index.tolist()

        new_jjdm_list.sort()

        style_property_df['jjdm']=new_jjdm_list

        for jjdm in new_jjdm_list:

            #check if manager changed during the time zone
            tempdf=style_df[style_df['jjdm']==jjdm]
            manager_change=str(str(self.val_date[self.val_date['jjdm']==jjdm]['rzrq'].values[0])[0:6]<=self.start_date)

            tempdf['shift_ratio']=self.cal_style_shift_ratio(tempdf,style_col)

            centralization=(tempdf[style_col].std(axis=1)/tempdf[style_col].mean(axis=1)).mean()

            style_property_df.loc[style_property_df['jjdm'] == jjdm,
                                  'shift_ratio'] = tempdf['shift_ratio'].mean()
            style_property_df.loc[style_property_df['jjdm'] == jjdm,
                                  'centralization'] = centralization

            for col in style_col:
                style_property_df.loc[style_property_df['jjdm'] == jjdm,
                                      style_map[col] + '_mean'] = tempdf[col].mean()

            style_property_df.loc[style_property_df['jjdm'] == jjdm,
                                  'manager_change'] = manager_change
        #get the style rank%
        # rank_col=style_property_df.columns.tolist()
        # rank_col.remove('jjdm')
        rank_col=['shift_ratio','centralization']
        style_property_df[[x+'_rank' for x in rank_col]]=style_property_df[rank_col].rank(method='min')/len(style_property_df)

        style_property_df['asofdate']=asofdate

        return style_property_df

    def save_style_property2localdb(self):

        # sql="select distinct asofdate from nav_style_property_value where fre='{0}' and by_manager='{1}' "\
        #     .format(self.fre,'True')
        # asofdate_list=pd.read_sql(sql,con=localdb)['asofdate'].values.tolist()

        # if(self.asofdate in asofdate_list):
        #     sql="delete from nav_style_property_value where asofdate='{0}' and fre-'{1}' and by_manager='{2}'"\
        #         .format(self.asofdate,self.fre,'True'+str(self.consistant_date))
        #     localdb.excute(sql)



        # value_df=self.get_style_property(self.read_jj_style_exp(jjdm_list,
        #                                 'value',self.fre,self.start_date)
        #                                  ,self.value_col,'value',method='rank')
        # value_df['fre']=self.fre
        # value_df.to_sql('nav_style_property_value',index=False,con=localdb,if_exists='append')
        #
        # size_df=self.get_style_property(self.read_jj_style_exp(jjdm_list,
        #                                 'size',self.fre,self.start_date)
        #                                  ,self.value_col,'size',method='rank')
        # size_df['fre'] = self.fre
        # size_df.to_sql('nav_style_property_size',index=False,con=localdb,if_exists='append')


        value_df=self.get_style_property(self.read_jj_style_exp(jjdm_list,
                                        'industry',self.fre,self.start_date)
                                         ,self.industry_col,'industry',method='rank')
        value_df['fre']=self.fre
        value_df.to_sql('nav_style_property_industry',index=False,con=localdb,if_exists='append')


if __name__ == '__main__':

    #calculate the return for different scenarios

    # stock_jjdm_list=util.get_mutual_stock_funds('20211231')
    # stock_jjdm_list.sort()
    # benchmark_ret = get_histroy_scenario_ret()
    # saved_df=pd.DataFrame()
    # for jjdm in stock_jjdm_list:
    #     scenario_ret=pessimistic_ret(jjdm,benchmark_ret)
    #     saved_df=pd.concat([saved_df,scenario_ret],axis=0)
    # saved_df.to_sql('scenario_ret',index=False,con=localdb,if_exists='append')

    #barra return daily return
    #factor_ret_df=get_barra_daily_ret()

    #write style exp into local db
    # se = Style_exp('20211231','M')
    # se = Style_exp('20211231', 'Q')

    #style exp analysis
    #

    # sql="select * from value_exposure where jjdm='002849' "
    # test=pd.read_sql(sql,con=localdb)[['399370','399371','CBA00301','date']]
    # test.set_index('date',inplace=True)
    # plot=functionality.Plot(2000,1000)
    # plot.plotly_line_style(test,'asdf')
    #

    #style property calculation
    jjdm_list=util.get_mutual_stock_funds('20211231')
    # sa=Style_analysis(jjdm_list,fre='M',time_length=3)
    # sa.save_style_property2localdb()
    #
    # sa = Style_analysis(jjdm_list, fre='Q',time_length=3)
    # sa.save_style_property2localdb()

    # sa=Style_analysis(jjdm_list,fre='M',time_length=3)
    # sa.save_style_property2localdb()

    sa=Style_analysis(jjdm_list,fre='Q',time_length=3)
    sa.save_style_property2localdb()


