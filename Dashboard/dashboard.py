import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from babel.numbers import format_currency
sns.set(style='dark')
st.set_option('deprecation.showPyplotGlobalUse', False)



class Visualization:
    def __init__(self, df):
        self.df = df


    
    def create_monthly_orders_df(df):
        monthly_orders_df = df.df.resample(rule='ME', on='order_approved_at').agg({
            "order_id": "nunique"
        })
        monthly_orders_df = monthly_orders_df.reset_index()
        monthly_orders_df.rename(columns={
            "order_approved_at": "date",
            "order_id": "order_count"
        }, inplace=True)
        
        return monthly_orders_df
    

    def create_yearly_orders_df(df):
        yearly_orders_df = df.df.resample(rule='YE', on='order_approved_at').agg({
            "order_id": "nunique"
        })
        yearly_orders_df.index = yearly_orders_df.index.strftime('%Y')
        yearly_orders_df = yearly_orders_df.reset_index()
        yearly_orders_df.rename(columns={
            "order_approved_at": "year",
            "order_id": "order_count"
        }, inplace=True)
        
        return yearly_orders_df


    def create_sum_order_items_df(df):
        sum_order_items_df = df.df.groupby("product_category_name_english")["product_id"].count().reset_index().sort_values(by="product_id", ascending=False)
        sum_order_items_df = sum_order_items_df.rename(columns={"product_id": "count", "product_category_name_english": "product"})
        return sum_order_items_df


    def create_byreview_df(df):
        by_review_df = df.df.groupby(by="review_score").order_id.nunique().reset_index()
        by_review_df.rename(columns={
            "order_id": "customer_count"
        }, inplace=True)
        
        return by_review_df
    

    def create_bypaymenttype_df(df):
        bypaymenttype_df = df.df.groupby(by="payment_type").order_id.nunique().reset_index()
        bypaymenttype_df.rename(columns={
            "order_id": "customer_count"
        }, inplace=True)
        
        return bypaymenttype_df
    
    def create_byseller_df(df):
        by_seller_df = df.df.groupby(by="seller_id").order_id.nunique().reset_index()
        by_seller_df.rename(columns={
            "order_id": "product_count"
        }, inplace=True)
        
        return by_seller_df
    
class Map:
    
    def __init__(self, df, plt, ccrs, st):
        self.df = df
        self.plt = plt
        self.ccrs = ccrs
        self.st = st
    
    def plot_world_map(self):
        # Membuat peta dunia dengan projeksi PlateCarree
        fig, ax = self.plt.subplots(subplot_kw={'projection': self.ccrs.PlateCarree()})

        # Plotting data
        ax.scatter(self.df["geolocation_lng"].values, self.df["geolocation_lat"].values, color='yellow', alpha=0.3, s=1, transform=self.ccrs.PlateCarree())

        # Menambahkan fitur peta
        ax.coastlines()
        ax.gridlines()

        # Menampilkan peta
        self.plt.title("World Map")
        self.st.pyplot()
        return ax 

    
    def plot_south_america_map(self):
        fig, ax = self.plt.subplots(subplot_kw={'projection': self.ccrs.PlateCarree()})
        ax.set_extent([-90, -30, -60, 15], crs=self.ccrs.PlateCarree())
        ax.scatter(self.df["geolocation_lng"].values, self.df["geolocation_lat"].values, color='blue', alpha=0.3, s=1, transform=self.ccrs.PlateCarree())

        # Menambahkan fitur peta
        ax.coastlines()
        ax.gridlines()

        # Menampilkan peta
        self.plt.title("Map of South America")
        self.st.pyplot()
        return ax 
    



geolocation_df = pd.read_csv('geolocation_dataset.csv')

all_df = pd.read_csv("data_df.csv")
datetime_columns = ["shipping_limit_date", "review_creation_date","review_answer_timestamp","order_purchase_timestamp","order_approved_at","order_delivered_carrier_date","order_delivered_customer_date","order_estimated_delivery_date"]
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)


 
for column in datetime_columns:
   all_df[column] = pd.to_datetime(all_df[column], format="%Y-%m-%d %H:%M:%S", errors='coerce')



min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()
 
with st.sidebar:

    st.title("Nurul Nyi Qoniah")
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )



main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                (all_df["order_approved_at"] <= str(end_date))]



vis = Visualization(main_df)
monthly_order_df = vis.create_monthly_orders_df()
yearly_order_df = vis.create_yearly_orders_df()
sum_order_items_df = vis.create_sum_order_items_df()
by_review_df = vis.create_byreview_df()
by_seller_df = vis.create_byseller_df()
by_payment_type_df = vis.create_bypaymenttype_df()


map = Map(geolocation_df, plt, ccrs, st)


st.header('Proyek Analisis Data E-Commerce Dashboard :sparkles:')

st.subheader('Monthly Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    year=start_date.strftime("%Y")
    monthly_orders_2018_df = monthly_order_df[monthly_order_df['date'].astype(str).str.startswith(year)]
    total_orders = monthly_orders_2018_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    st.metric("Year", value=year)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders_2018_df["date"],
    monthly_orders_2018_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)


st.subheader('Yearly Orders')
 
col1 = st.columns(1)

# Menampilkan total pesanan di kolom pertama
total_orders = yearly_order_df.order_count.sum()
st.metric("Total orders", value=total_orders)
 
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    yearly_order_df["year"],
    yearly_order_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)



st.subheader("Best and Worst Performing Product by Number of Sales")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="count", y="product", hue="product", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="count", y="product", hue="product", data=sum_order_items_df.sort_values(by="count", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)



st.subheader("Customer Demographic")
tab1, tab2 = st.tabs([ "World Geolocation", "South America Geolocation"])

with tab1:
    map.plot_world_map()

with tab2:
    map.plot_south_america_map()




st.subheader('Order Review')
 
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#72BCD4"]
sns.barplot(
    y="customer_count", 
    x="review_score",
    hue="customer_count",
    data=by_review_df,
    palette=colors,
    ax=ax
)
ax.set_title("Number of Customer by Review Score", loc="center", fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)



st.subheader('Payment Type')

by_payment_type_df = by_payment_type_df.sort_values(by="customer_count", ascending=True)
colors = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#72BCD4"]


fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(
    y="customer_count", 
    x="payment_type",
    hue="payment_type",
    data=by_payment_type_df,
    palette=colors,
    ax=ax
)
ax.set_title("Number of Customer by Payment Type", loc="center", fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)


st.subheader('Seller Order')

by_seller_df = by_seller_df.sort_values(by="product_count", ascending=False).head(5)
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]



fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(
    y="product_count", 
    x="seller_id",
    hue="seller_id",
    data=by_seller_df,
    palette=colors,
    ax=ax
)
ax.set_title("Number of Product Sold by Seller", loc="center", fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=10)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)

st.caption('Copyright (C) Nurul Nyi Qoniah')
