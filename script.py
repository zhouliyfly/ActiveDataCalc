import pandas as pd
import os

import warnings
warnings.filterwarnings('ignore')

def get_file_names(path = './data'):

    path = './data'

    path_files = []
    file_names = []
    
    if os.path.exists(path) == False:
        print ("Error: 没有找到data文件夹")
    else:
        for name in os.listdir(path):
            if os.path.splitext(name)[1] == '.xls' or os.path.splitext(name)[1] == '.xlsx':
                s = path + '/' + name
                path_files.append(s)
                file_names.append(name)
    
        if len(file_names) == 0:
            print ("Error: 没有找到Excel文件")
        
    return path_files, file_names

def check_integrity(file_names):
    #print(file_names)
    
    status = True
    names = dict()
    
    if len(file_names) == 0:
        status = False
        return status, names
    
    filename1 = None
    filename2 = None
    filename3 = None
    
    if '订单表.xlsx' in file_names:
        filename1 = '订单表.xlsx'
    elif '订单表.xls' in file_names:
        filename1 = '订单表.xls'
    else:
        pass
    names['dingdan'] = filename1
    
    if filename1 == None:
        print ("Error: 没有找到订单表")
        status = False
        return status, names
    
    if '特价表.xlsx' in file_names:
        filename2 = '特价表.xlsx'
    elif '特价表.xls' in file_names:
        filename2 = '特价表.xls'
    else:
        pass
    
    names['tejia'] = filename2
        
    if '满减表.xlsx' in file_names:
        filename3 = '满减表.xlsx'
    elif '满减表.xls' in file_names:
        filename3 = '满减表.xls'
    else:
        pass
    
    names['manjian'] = filename3
    
    if filename2 == None and filename3 == None:
        print ("Error: 没有找到特价表或满减表")
        status = False
        return status, names
    
    status = True
    return status, names

def tejia(table_dingdan, table_tejia):
    
    df_activity = table_tejia[[u'编码',u'药帮忙价',u'活动价']]
    df_order = table_dingdan[[u'订单编号',u'下单时间',u'商品编号', u'商品价格', u'商品数量']]
    df_merge = pd.merge(df_order, df_activity, left_on = u'商品编号', right_on = u'编码')
    df_mer_activity = df_merge[df_merge[u'商品价格'] == df_merge[u'活动价']]
    df_tmp = df_mer_activity.loc[:,[u'订单编号', u'商品编号',u'药帮忙价']]
    df_activityorder = pd.merge(table_dingdan, df_tmp, on=[u'订单编号', u'商品编号'])
    df_activityorder['费用'] = (df_activityorder['药帮忙价']-df_activityorder['商品价格']) \
          * df_activityorder['商品数量']
    writer = pd.ExcelWriter('特价活动表.xlsx')
    df_activityorder.to_excel(writer,u'活动订单表')
    writer.save()
    
def manjian(table_dingdan, table_manjian):
    
    df_order = table_dingdan[[u'订单编号',u'下单时间',u'商品编号', u'商品价格', u'商品数量']]
    df_order[u'下单时间'] = pd.to_datetime(df_order[u'下单时间'])
    df_activity = table_manjian[[u'开始时间',u'结束时间',u'编码',u'数量',u'满减']]
    df_activity[u'开始时间'] = pd.to_datetime(df_activity[u'开始时间'])
    df_activity[u'结束时间'] = pd.to_datetime(df_activity[u'结束时间'])

    df_merge = pd.merge(df_order, df_activity, left_on = u'商品编号', right_on = u'编码')
    df_mer_time = df_merge[(df_merge[u'下单时间'] >= df_merge[u'开始时间']) &(df_merge[u'下单时间'] <= df_merge[u'结束时间'])]
    df_salessum = pd.merge(table_dingdan, df_mer_time, on=[u'订单编号', u'商品编号'])
    df_mer_activity = df_mer_time[df_mer_time[u'商品数量'] >= df_mer_time[u'数量']]
    df_tmp = df_mer_activity.loc[:,[u'订单编号', u'商品编号', u'数量',u'满减']]
    df_activityorder = pd.merge(table_dingdan, df_tmp, on=[u'订单编号', u'商品编号'])
    df_activityorder['费用'] = (df_activityorder['商品数量']/df_activityorder['数量'])//1 \
          * df_activityorder['满减']
    writer = pd.ExcelWriter('满减活动表.xlsx')
    df_activityorder.to_excel(writer,u'活动订单表')
    df_salessum.to_excel(writer,u'总销量订单表')
    writer.save()

def read_table_and_cacl(table_names, path):
    tablename_dingdan = path + '/' + table_names['dingdan']
    print("读取订单表...")
    df_dingdan = pd.read_excel(tablename_dingdan)
    print("订单表读取成功")
    if len(df_dingdan) == 0:
        print('订单表异常')
        return

    if table_names['manjian'] != None:
        tablename_manjian = path + '/' + table_names['manjian']
        print("读取满减表...")
        df_manjian = pd.read_excel(tablename_manjian)
        print("满减表读取成功")
        if len(df_manjian) == 0:
            print('满减表异常')
        else:
            manjian(df_dingdan, df_manjian)
            print("已成功生成满减活动表!")
    
    if table_names['tejia'] != None:
        tablename_tejia = path + '/' + table_names['tejia']
        print("读取特价表...")
        df_tejia = pd.read_excel(tablename_tejia)
        print("特价表读取成功")
        if len(df_tejia) == 0:
            print('特价表异常')
        else:
            tejia(df_dingdan, df_tejia)
            print("已成功生成特价活动表")  

def main():
    path = './data'
    path_files, file_names = get_file_names(path)
    status, names = check_integrity(file_names)
    #print(names)

    if status == False:
        return
    
    read_table_and_cacl(names, path)
    
if __name__ == "__main__":
    main()