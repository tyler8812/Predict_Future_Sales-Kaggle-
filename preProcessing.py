import calendar
from sklearn.preprocessing import LabelEncoder
from itertools import product
import numpy as np
import pandas as pd
test = pd.read_csv(
    './competitive-data-science-predict-future-sales/test.csv')
sales = pd.read_csv(
    './competitive-data-science-predict-future-sales/sales_train.csv')
shops = pd.read_csv(
    './competitive-data-science-predict-future-sales/shops.csv')
items = pd.read_csv(
    './competitive-data-science-predict-future-sales/items.csv')
item_cats = pd.read_csv(
    './competitive-data-science-predict-future-sales/item_categories.csv')
train = sales[(sales.item_price < 100000) & (sales.item_price > 0)]
train = train[sales.item_cnt_day < 1001]

train.loc[train.shop_id == 0, 'shop_id'] = 57
test.loc[test.shop_id == 0, 'shop_id'] = 57

train.loc[train.shop_id == 1, 'shop_id'] = 58
test.loc[test.shop_id == 1, 'shop_id'] = 58

train.loc[train.shop_id == 40, 'shop_id'] = 39
test.loc[test.shop_id == 40, 'shop_id'] = 39

# group block num   AZQS
index_cols = ['shop_id', 'item_id', 'date_block_num']

df = []
for block_num in train['date_block_num'].unique():
    cur_shops = train.loc[sales['date_block_num']
                          == block_num, 'shop_id'].unique()
    cur_items = train.loc[sales['date_block_num']
                          == block_num, 'item_id'].unique()
    df.append(
        np.array(list(product(*[cur_shops, cur_items, [block_num]])), dtype='int32'))

df = pd.DataFrame(np.vstack(df), columns=index_cols, dtype=np.int32)

# Add month sales
group = train.groupby(['date_block_num', 'shop_id', 'item_id']).agg(
    {'item_cnt_day': ['sum']})
group.columns = ['item_cnt_month']
group.reset_index(inplace=True)

df = pd.merge(df, group, on=index_cols, how='left')
df['item_cnt_month'] = (df['item_cnt_month']
                        .fillna(0)
                        .clip(0, 20)
                        .astype(np.float16))

# test dataset
test['date_block_num'] = 34
test['date_block_num'] = test['date_block_num'].astype(np.int8)
test['shop_id'] = test['shop_id'].astype(np.int8)
test['item_id'] = test['item_id'].astype(np.int16)
test = test.drop(columns=['ID'])
df = pd.concat([df, test], ignore_index=True, sort=False, keys=index_cols)
df.fillna(0, inplace=True)


# add city code feature
shops['city'] = shops['shop_name'].apply(lambda x: x.split()[0].lower())
shops.loc[shops.city == '!якутск', 'city'] = 'якутск'
shops['city_code'] = LabelEncoder().fit_transform(shops['city'])

coords = dict()
coords['якутск'] = (62.028098, 129.732555, 4)
coords['адыгея'] = (44.609764, 40.100516, 3)
coords['балашиха'] = (55.8094500, 37.9580600, 1)
coords['волжский'] = (53.4305800, 50.1190000, 3)
coords['вологда'] = (59.2239000, 39.8839800, 2)
coords['воронеж'] = (51.6720400, 39.1843000, 3)
coords['выездная'] = (0, 0, 0)
coords['жуковский'] = (55.5952800, 38.1202800, 1)
coords['интернет-магазин'] = (0, 0, 0)
coords['казань'] = (55.7887400, 49.1221400, 4)
coords['калуга'] = (54.5293000, 36.2754200, 4)
coords['коломна'] = (55.0794400, 38.7783300, 4)
coords['красноярск'] = (56.0183900, 92.8671700, 4)
coords['курск'] = (51.7373300, 36.1873500, 3)
coords['москва'] = (55.7522200, 37.6155600, 1)
coords['мытищи'] = (55.9116300, 37.7307600, 1)
coords['н.новгород'] = (56.3286700, 44.0020500, 4)
coords['новосибирск'] = (55.0415000, 82.9346000, 4)
coords['омск'] = (54.9924400, 73.3685900, 4)
coords['ростовнадону'] = (47.2313500, 39.7232800, 3)
coords['спб'] = (59.9386300, 30.3141300, 2)
coords['самара'] = (53.2000700, 50.1500000, 4)
coords['сергиев'] = (56.3000000, 38.1333300, 4)
coords['сургут'] = (61.2500000, 73.4166700, 4)
coords['томск'] = (56.4977100, 84.9743700, 4)
coords['тюмень'] = (57.1522200, 65.5272200, 4)
coords['уфа'] = (54.7430600, 55.9677900, 4)
coords['химки'] = (55.8970400, 37.4296900, 1)
coords['цифровой'] = (0, 0, 0)
coords['чехов'] = (55.1477000, 37.4772800, 4)
coords['ярославль'] = (57.6298700, 39.8736800, 2)

shops['city_coord_1'] = shops['city'].apply(lambda x: coords[x][0])
shops['city_coord_2'] = shops['city'].apply(lambda x: coords[x][1])
shops['country_part'] = shops['city'].apply(lambda x: coords[x][2])

shops = shops[['shop_id', 'city_code',
               'city_coord_1', 'city_coord_2', 'country_part']]
df = pd.merge(df, shops, on=['shop_id'], how='left')
# add item category feature
map_dict = {
    'Чистые носители (штучные)': 'Чистые носители',
    'Чистые носители (шпиль)': 'Чистые носители',
    'PC ': 'Аксессуары',
    'Служебные': 'Служебные '
}

items = pd.merge(items, item_cats, on='item_category_id')

items['item_category'] = items['item_category_name'].apply(
    lambda x: x.split('-')[0])
items['item_category'] = items['item_category'].apply(
    lambda x: map_dict[x] if x in map_dict.keys() else x)
items['item_category_common'] = LabelEncoder(
).fit_transform(items['item_category'])

items['item_category_code'] = LabelEncoder(
).fit_transform(items['item_category_name'])
items = items[['item_id', 'item_category_common', 'item_category_code']]
df = pd.merge(df, items, on=['item_id'], how='left')
# add weekend feature


def count_days(date_block_num):
    year = 2013 + date_block_num // 12
    month = 1 + date_block_num % 12
    weeknd_count = len(
        [1 for i in calendar.monthcalendar(year, month) if i[6] != 0])
    days_in_month = calendar.monthrange(year, month)[1]
    return weeknd_count, days_in_month, month


map_dict = {i: count_days(i) for i in range(35)}

df['weeknd_count'] = df['date_block_num'].apply(lambda x: map_dict[x][0])
df['days_in_month'] = df['date_block_num'].apply(lambda x: map_dict[x][1])
# add interaction feature
# item first appears in which block
first_item_block = df.groupby(
    ['item_id'])['date_block_num'].min().reset_index()
first_item_block['item_first_interaction'] = 1

# items, shop first appear in which block
first_shop_item_buy_block = df[df['date_block_num'] > 0].groupby(
    ['shop_id', 'item_id'])['date_block_num'].min().reset_index()
first_shop_item_buy_block['first_date_block_num'] = first_shop_item_buy_block['date_block_num']

df = pd.merge(df, first_item_block[['item_id', 'date_block_num', 'item_first_interaction']], on=[
              'item_id', 'date_block_num'], how='left')
df = pd.merge(df, first_shop_item_buy_block[[
              'item_id', 'shop_id', 'first_date_block_num']], on=['item_id', 'shop_id'], how='left')

# item was sold before this block
df['first_date_block_num'].fillna(100, inplace=True)
df['shop_item_sold_before'] = (
    df['first_date_block_num'] < df['date_block_num']).astype('int8')
df.drop(['first_date_block_num'], axis=1, inplace=True)

df['item_first_interaction'].fillna(0, inplace=True)
df['shop_item_sold_before'].fillna(0, inplace=True)

df['item_first_interaction'] = df['item_first_interaction'].astype('int8')
df['shop_item_sold_before'] = df['shop_item_sold_before'].astype('int8')

#  add lag feature


def lag_feature(df, lags, col):
    tmp = df[['date_block_num', 'shop_id', 'item_id', col]]
    for i in lags:
        shifted = tmp.copy()
        shifted.columns = ['date_block_num',
                           'shop_id', 'item_id', col+'_lag_'+str(i)]
        shifted['date_block_num'] += i
        df = pd.merge(df, shifted, on=[
                      'date_block_num', 'shop_id', 'item_id'], how='left')
        df[col+'_lag_'+str(i)] = df[col+'_lag_'+str(i)].astype('float16')
    return df


# Add sales lags for last 3 months
df = lag_feature(df, [1, 2, 3], 'item_cnt_month')
# Add avg shop/item price
index_cols = ['shop_id', 'item_id', 'date_block_num']
group = train.groupby(index_cols)['item_price'].mean().reset_index().rename(
    columns={"item_price": "avg_shop_price"}, errors="raise")

df = pd.merge(df, group, on=index_cols, how='left')

df['avg_shop_price'] = (df['avg_shop_price']
                        .fillna(0)
                        .astype(np.float16))

index_cols = ['item_id', 'date_block_num']
group = train.groupby(['date_block_num', 'item_id'])['item_price'].mean(
).reset_index().rename(columns={"item_price": "avg_item_price"}, errors="raise")


df = pd.merge(df, group, on=index_cols, how='left')
df['avg_item_price'] = (df['avg_item_price']
                        .fillna(0)
                        .astype(np.float16))

df['item_shop_price_avg'] = (
    df['avg_shop_price'] - df['avg_item_price']) / df['avg_item_price']
df['item_shop_price_avg'].fillna(0, inplace=True)

df = lag_feature(df, [1, 2, 3], 'item_shop_price_avg')
df.drop(['avg_shop_price', 'avg_item_price',
        'item_shop_price_avg'], axis=1, inplace=True)
# Add target encoding for items for last 3 months
item_id_target_mean = df.groupby(['date_block_num', 'item_id'])['item_cnt_month'].mean(
).reset_index().rename(columns={"item_cnt_month": "item_target_enc"}, errors="raise")
df = pd.merge(df, item_id_target_mean, on=[
              'date_block_num', 'item_id'], how='left')

df['item_target_enc'] = (df['item_target_enc']
                         .fillna(0)
                         .astype(np.float16))

df = lag_feature(df, [1, 2, 3], 'item_target_enc')
df.drop(['item_target_enc'], axis=1, inplace=True)
# Add target encoding for item/city for last 3 months
item_id_target_mean = df.groupby(['date_block_num', 'item_id', 'city_code'])['item_cnt_month'].mean().reset_index().rename(columns={
    "item_cnt_month": "item_loc_target_enc"}, errors="raise")
df = pd.merge(df, item_id_target_mean, on=[
              'date_block_num', 'item_id', 'city_code'], how='left')

df['item_loc_target_enc'] = (df['item_loc_target_enc']
                             .fillna(0)
                             .astype(np.float16))

df = lag_feature(df, [1, 2, 3], 'item_loc_target_enc')
df.drop(['item_loc_target_enc'], axis=1, inplace=True)
# Add target encoding for item/shop for last 3 months
item_id_target_mean = df.groupby(['date_block_num', 'item_id', 'shop_id'])['item_cnt_month'].mean().reset_index().rename(columns={
    "item_cnt_month": "item_shop_target_enc"}, errors="raise")

df = pd.merge(df, item_id_target_mean, on=[
              'date_block_num', 'item_id', 'shop_id'], how='left')

df['item_shop_target_enc'] = (df['item_shop_target_enc']
                              .fillna(0)
                              .astype(np.float16))

df = lag_feature(df, [1, 2, 3], 'item_shop_target_enc')
df.drop(['item_shop_target_enc'], axis=1, inplace=True)
# For new items add avg category sales for last 3 months
item_id_target_mean = df[df['item_first_interaction'] == 1].groupby(['date_block_num', 'item_category_code'])['item_cnt_month'].mean().reset_index().rename(columns={
    "item_cnt_month": "new_item_cat_avg"}, errors="raise")

df = pd.merge(df, item_id_target_mean, on=[
              'date_block_num', 'item_category_code'], how='left')

df['new_item_cat_avg'] = (df['new_item_cat_avg']
                          .fillna(0)
                          .astype(np.float16))

df = lag_feature(df, [1, 2, 3], 'new_item_cat_avg')
df.drop(['new_item_cat_avg'], axis=1, inplace=True)
# For new items add avg category sales in a separate store for last 3 months
item_id_target_mean = df[df['item_first_interaction'] == 1].groupby(['date_block_num', 'item_category_code', 'shop_id'])['item_cnt_month'].mean().reset_index().rename(columns={
    "item_cnt_month": "new_item_shop_cat_avg"}, errors="raise")

df = pd.merge(df, item_id_target_mean, on=[
              'date_block_num', 'item_category_code', 'shop_id'], how='left')

df['new_item_shop_cat_avg'] = (df['new_item_shop_cat_avg']
                               .fillna(0)
                               .astype(np.float16))

df = lag_feature(df, [1, 2, 3], 'new_item_shop_cat_avg')
df.drop(['new_item_shop_cat_avg'], axis=1, inplace=True)
# Add sales for the last three months for similar item (item with id = item_id - 1;
# kinda tricky feature, but increased the metric significantly)


def lag_feature_adv(df, lags, col):
    tmp = df[['date_block_num', 'shop_id', 'item_id', col]]
    for i in lags:
        shifted = tmp.copy()
        shifted.columns = ['date_block_num', 'shop_id',
                           'item_id', col+'_lag_'+str(i)+'_adv']
        shifted['date_block_num'] += i
        shifted['item_id'] -= 1
        df = pd.merge(df, shifted, on=[
                      'date_block_num', 'shop_id', 'item_id'], how='left')
        df[col+'_lag_'+str(i)+'_adv'] = df[col+'_lag_' +
                                           str(i)+'_adv'].astype('float16')
    return df


df = lag_feature_adv(df, [1, 2, 3], 'item_cnt_month')
# Add sales for the last three months for similar item (item with id = item_id - 1;
# kinda tricky feature, but increased the metric significantly)


def lag_feature_adv2(df, lags, col):
    tmp = df[['date_block_num', 'shop_id', 'item_id', col]]
    for i in lags:
        shifted = tmp.copy()
        shifted.columns = ['date_block_num', 'shop_id',
                           'item_id', col+'_lag_'+str(i)+'_adv2']
        shifted['date_block_num'] += i
        shifted['item_id'] += 1
        df = pd.merge(df, shifted, on=[
                      'date_block_num', 'shop_id', 'item_id'], how='left')
        df[col+'_lag_'+str(i)+'_adv2'] = df[col+'_lag_' +
                                            str(i)+'_adv2'].astype('float16')
    return df


df = lag_feature_adv2(df, [1, 2, 3], 'item_cnt_month')
df.fillna(0, inplace=True)
df = df[(df['date_block_num'] > 2)]
df = df[(df['shop_id'] != 9)]
df = df[(df['shop_id'] != 20)]
df.to_pickle('temp.pkl')
