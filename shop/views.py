from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from . inherit import cartData
import pandas as pd
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity
import datetime
from django.conf import settings
from django.core.mail import send_mail
from statsmodels.tsa.arima.model import ARIMA
from dateutil.relativedelta import relativedelta
import csv, io
from django.shortcuts import render
from django.contrib import messages
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import  PorterStemmer 
import string
import re
import warnings
warnings.simplefilter("ignore")
import pickle


#LOAD PICKLE FILES
model = pickle.load(open(r"C:\xampp\htdocs\FakeReview\shop\templates\best_model.pkl",'rb')) 
vectorizer = pickle.load(open(r"C:\xampp\htdocs\FakeReview\shop\templates\count_vectorizer.pkl",'rb')) 

#FOR STREAMLIT
nltk.download('stopwords')

#TEXT PREPROCESSING
sw = set(stopwords.words('english'))


def index(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    #temp=[]
    #products=Product.objects.all().distinct().order_by('-date_added')
    product =  Product.objects.values_list('name', flat=True).distinct()
    products=[]

    for pp in product:
        temp=Product.objects.filter(name=pp).latest('date_added')
        products.append(temp)
    
    
    #Product.objects.filter(name=product)
    return render(request, "index.html", {'products':products, 'cartItems':cartItems})


def mail(request,items, id, mssg, ordermsg):
    subject = 'AI Online Shopping'
    message = f'Hi {request.user.customer}, \n\n {mssg} \n\n {items} \n\n {ordermsg} {id}. \n\n Regards,\nAI Online Shopping Team'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['swarajballal2425@gmail.com']
    send_mail( subject, message, email_from, recipient_list )

def cart(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    print('Cart:', cart)

    for i in cart:
        try:
            cartItems += cart[i]["quantity"]

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]["quantity"])

            order["get_cart_total"] += total
            order["get_cart_items"] += cart[i]["quantity"]

            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'image':product.image,
                },
                'quantity':cart[i]["quantity"],
                'get_total':total
            }
            items.append(item)
        except:
            pass
    return render(request, "cart.html", {'items':items, 'order':order, 'cartItems':cartItems})


def payment(request,address,city,state,zipcode,phone_number,payment):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    total = order.get_cart_total
    if request.method == "POST":
        cc_num = request.POST['cardNumber']
        shipping_adress = CheckoutDetail.objects.create(address=address, city=city, phone_number=phone_number, state=state, zipcode=zipcode, customer=request.user.customer, total_amount=total, order=order, payment=payment)
        shipping_adress.save()
        if total == order.get_cart_total:
            order.complete = True
        order.save()
        id = order.id  
        alert = True
        prod=[]
        iteml=OrderItem.objects.filter(order_id=order).values_list('product_id',flat=True)
        for pro in iteml.iterator():
            pr = Product.objects.filter(id=pro).values_list('name',flat=True).first()
            prod.append(pr)

        mail(request,prod,id,"Thank you for purchasing below items using card "+ str(cc_num),"Please note that your order id is: ")
        return render(request, "payment.html", {'alert':alert, 'id':id})
    return render(request, "payment.html")



def checkout(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    total = order.get_cart_total
    if request.method == "POST":
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        zipcode = request.POST['zipcode']
        phone_number = request.POST['phone_number']
        payment = request.POST['payment']
        if payment == "Debit Card":
            return redirect(f"/payment/{address}/{city}/{state}/{zipcode}/{phone_number}/{payment}")
        else:
            shipping_adress = CheckoutDetail.objects.create(address=address, city=city, phone_number=phone_number, state=state, zipcode=zipcode, customer=request.user.customer, total_amount=total, order=order, payment=payment)
            shipping_adress.save()
            if total == order.get_cart_total:
                order.complete = True
            order.save()
            id = order.id  
            alert = True
            prod=[]
            iteml=OrderItem.objects.filter(order_id=order).values_list('product_id',flat=True)
            for pro in iteml.iterator():
                pr = Product.objects.filter(id=pro).values_list('name',flat=True).first()
                prod.append(pr)

            mail(request,prod,id,"Thank you for purchasing below items using cod ","Please note that your order id is: ")
            return render(request, "checkout.html", {'alert':alert, 'id':id})
    return render(request, "checkout.html", {'items':items, 'order':order, 'cartItems':cartItems})




def updateItem(request):
    data = json.loads(request.body)
    productID = data['productID']
    action = data['action']

    print('Action:', action)
    print('productID:', productID)

    customer = request.user.customer
    product = Product.objects.get(id=productID)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    update_order, created = UpdateOrder.objects.get_or_create(order_id=order, desc="Your Order is Successfully Placed.")

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    elif action == 'delete':
        orderItem.quantity = 0
        OrderItem.objects.filter(id=productID).delete()

    orderItem.save()
    order.save()
    update_order.save()

    prod=[]
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    #orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    iteml=OrderItem.objects.filter(order_id=order).values_list('product_id',flat=True)

    for pro in iteml.iterator():
        pr = Product.objects.filter(id=pro).values_list('name',flat=True).first()
        prod.append(pr)


    mail(request,prod,"","You have added below items to your cart: ","")

    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was added', safe=False)

def product_price(request, prod_id):
    product = Product.objects.filter(id=prod_id).first()
    qs = Product.pdobjects.filter(name=product.name).values()
    cnt = Product.pdobjects.filter(name=product.name).count()
    if cnt > 1:
        btc = pd.DataFrame(qs.to_dataframe())
        btc.index = pd.to_datetime(btc['date_added'], format='%Y-%m-%d')
        train = btc[btc.index < pd.to_datetime("2022-01-01", format='%Y-%m-%d')]
        test = btc[btc.index > pd.to_datetime("2022-01-01", format='%Y-%m-%d')]
        # create a future date df
        ftr =  (test['date_added']+ pd.Timedelta(60, unit='days')).to_frame()
        # join the future data
        df1 = pd.concat([test, ftr], ignore_index=True)
        test = df1
        test.index = pd.to_datetime(test['date_added'], format='%Y-%m-%d')
        y = train['price']
        ARIMAmodel = ARIMA(y, order = (2, 2, 2))
        ARIMAmodel = ARIMAmodel.fit()

        y_pred = ARIMAmodel.get_forecast(len(test.index))
        y_pred_df = y_pred.conf_int(alpha = 0.05) 
        y_pred_df["Predictions"] = ARIMAmodel.predict(start = y_pred_df.index[0], end = y_pred_df.index[-1])
        y_pred_df.index = test.index
        y_pred_out = y_pred_df["Predictions"].to_frame(name=None) 
        y_pred_out=y_pred_out.dropna(subset=['Predictions'])
        result=y_pred_out.sort_values(by='date_added')
        result['date'] = result.index
        # result= result.set_index('ID').T.to_dict('list')
        
        labels = result['date'].dt.strftime('%m/%Y').tolist()
        chartLabel = product.name
        chartdata = result['Predictions'].tolist()
        result2 ={
                         "labels":labels,
                         "chartLabel":chartLabel,
                         "chartdata":chartdata,
                 }
    else:
        result2 ={
                         "labels":[],
                         "chartLabel":product.name,
                         "chartdata":[],
                 }

    
    
    return render(request, "test.html",  {'result':result2})


def product_view(request, myid):
    product = Product.objects.filter(id=myid).first()
    feature = Feature.objects.filter(product=product)
    reviews = Review.objects.filter(product=product)
    customer = request.user.customer
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    if request.method=="POST":
        content = request.POST['content']
        cleaned_review = text_preprocessing(content)
        process = vectorizer.transform([cleaned_review]).toarray()
        prediction = model.predict(process)
        p = ''.join(str(i) for i in prediction)
        review = Review(customer=customer, content=content, product=product, tag = p)
        review.save()
        return redirect(f"/product_view/{product.id}")
    return render(request, "product_view.html", {'product':product, 'cartItems':cartItems, 'feature':feature, 'reviews':reviews})

def search(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    if request.method == "POST":
        search = request.POST['search']
        products = Product.objects.filter(name__contains=search)
        return render(request, "search.html", {'search':search, 'products':products, 'cartItems':cartItems})
    else:
        return render(request, "search.html")


def change_password(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        try:
            u = User.objects.get(id=request.user.id)
            if u.check_password(current_password):
                u.set_password(new_password)
                u.save()
                alert = True
                return render(request, "change_password.html", {'alert':alert})
            else:
                currpasswrong = True
                return render(request, "change_password.html", {'currpasswrong':currpasswrong})
        except:
            pass
    return render(request, "change_password.html", {'cartItems':cartItems})

def contact(request):
    if request.method=="POST":       
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        desc = request.POST['desc']
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        alert = True
        return render(request, 'contact.html', {'alert':alert})
    return render(request, "contact.html")

def loggedin_contact(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    if request.method=="POST":       
        name = request.user
        email = request.user.email
        phone = request.user.customer.phone_number
        desc = request.POST['desc']
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        alert = True
        return render(request, 'loggedin_contact.html', {'alert':alert})
    return render(request, "loggedin_contact.html", {'cartItems':cartItems})

def tracker(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    if request.method == "POST":
        order_id = request.POST['order_id']
        order = Order.objects.filter(id=order_id).first()
        order_items = OrderItem.objects.filter(order=order)
        update_order = UpdateOrder.objects.filter(order_id=order_id)
        print(update_order)
        return render(request, "tracker.html", {'order_items':order_items, 'update_order':update_order})
    return render(request, "tracker.html", {'cartItems':cartItems})


def register(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method=="POST":   
            username = request.POST['username']
            full_name=request.POST['full_name']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            phone_number = request.POST['phone_number']
            email = request.POST['email']

            if password1 != password2:
                alert = True
                return render(request, "register.html", {'alert':alert})
            
            user = User.objects.create_user(username=username, password=password1, email=email)
            customers = Customer.objects.create(user=user, name=full_name, phone_number=phone_number, email=email, first_login= "True")
            user.save()
            customers.save()
            return redirect("/login")
    return render(request, "register.html")

def Login(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            categoryList=Product.objects.all().values_list('category', flat=True).distinct()
            u = User.objects.filter(username=username).values_list('email', flat=True).distinct()

            if user is not None:
                login(request, user)
                #customers = Customer.objects.filter(user=user).update(first_login= True)
                fir_log=Customer.objects.filter(email=u[0]).values_list('first_login', flat=True).distinct()
                if fir_log.exists() and str(fir_log[0])=="True":
                    customers = Customer.objects.filter(email=u[0]).update(first_login= "False")
                    return redirect("/preferences")
                else:
                    return redirect("/")
                #return render(request,"preferences.html",{"categoryList":categoryList})
            else:
                alert = True
                return render(request, "login.html", {"alert":alert})
    return render(request, "login.html")

def Logout(request):
    logout(request)
    alert = True
    return render(request, "index.html", {'alert':alert})
    
    
def preferences(request):
    categoryList=Product.objects.all().values_list('category', flat=True).distinct()
    if not request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method=="POST":   
            category = request.POST.getlist('category')
            for cat in category:
                prod =Product.objects.filter(category=cat).values_list('id',flat=True)
                for pr in prod:
                    pref = Preferences.objects.create(customer=request.user.customer, category=cat, product = int(pr))
                    pref.save()
            qs = Preferences.probjects.filter(customer=request.user.customer).values()
            pref_data = pd.DataFrame(qs.to_dataframe())

            pivot_df = pd.pivot_table(pref_data,index = 'customer_id',columns = 'product',values = 'category',aggfunc = 'count')
            pivot_df.reset_index(inplace=True)
            pivot_df = pivot_df.fillna(0)
            pivot_df = pivot_df.drop('customer_id', axis=1)
            co_matrix = pivot_df.T.dot(pivot_df)
            np.fill_diagonal(co_matrix.values, 0)
            cos_score_df = pd.DataFrame(cosine_similarity(co_matrix))
            cos_score_df.index = co_matrix.index
            cos_score_df.columns = np.array(co_matrix.index)
            product_recs = []
            for i in cos_score_df.index:
                product_recs.append(cos_score_df[cos_score_df.index!=i][i].sort_values(ascending = False)[0:5].index)
                
            product_recs_df = pd.DataFrame(product_recs).head(1).values.tolist()
            [product_recs_df] = product_recs_df

            
            order, created = Order.objects.get_or_create(customer=request.user.customer, complete=False)


            for i in range(0, len(product_recs_df)):
                prodd = Product.objects.get(id=int(product_recs_df[i]))
                #prodd = Product.objects.filter(id= int(product_recs_df[i])).values_list('id',flat=True)
                orderItem, created = OrderItem.objects.get_or_create(product= prodd, order= order, quantity=1)
                orderItem.save()

        
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items


            return redirect("/cart")
            #return render(request, "cart.html",{'cartItems':cartItems, 'items':items, 'order':order})
    return render(request, "preferences.html",{"categoryList":categoryList})

def product_upload(request):
    template = "product_upload.html"
     # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template)
    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')
    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=','):
        _, product_created = Product.objects.update_or_create(
            product_id = column[0],
            name=column[4][0:30],
            image=column[5],
            price=column[6],
            category=column[7]
        )
##        prod = Product.objects.get(name=column[0])
##        cust = Customer.objects.get(user=request.user)
##        _, feature_created = Feature.objects.update_or_create(
##            feature=column[8],
##            product=prod
##        )
##        _, feature_created = Review.objects.update_or_create(
##            customer=cust,
##            content=column[9],
##            product=prod
##        )
        
    context = {}
    return render(request, template, context)

def feature_upload(request):
    template = "feature_upload.html"
     # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template)
    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')
    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=','):
        prod = Product.objects.get(product_id=column[0])
        cust = Customer.objects.get(user=request.user)
        _, feature_created = Feature.objects.update_or_create(
            feature=column[8],
            product=prod
        )
        
    context = {}
    return render(request, template, context)

def text_preprocessing(text):
    removed_special_characters = re.sub("[^a-zA-Z]", " ", str(text))
    tokens = removed_special_characters.lower().split()
    
    stemmer = PorterStemmer()
    cleaned = []
    stemmed = []
    
    for token in tokens:
        if token not in sw:
            cleaned.append(token)
            
    for token in cleaned:
        token = stemmer.stem(token)
        stemmed.append(token)

    return " ".join(stemmed)

def text_classification(text):
    cleaned_review = text_preprocessing(text)
    process = vectorizer.transform([cleaned_review]).toarray()
    prediction = model.predict(process)
    p = ''.join(str(i) for i in prediction)

    if p == 'True':
        print("The review entered is Legitimate.")
    if p == 'False':
        print("The review entered is Fraudulent.")
        
def review_upload(request):
    template = "review_upload.html"
     # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template)
    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')
    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=','):
        cleaned_review = text_preprocessing(column[9])
        process = vectorizer.transform([cleaned_review]).toarray()
        prediction = model.predict(process)
        p = ''.join(str(i) for i in prediction)
        #ss=text_classification(column[9])
        prod = Product.objects.get(product_id=column[0])
        cust = Customer.objects.get(user=request.user)
        _, feature_created = Review.objects.update_or_create(
            customer=cust,
            tag=p,
            content=column[9],
            posted_by= column[12],
            posted_on= column[11],
            verified_purchase = column[10],
            votes_up = column[13],
            votes_down = column[14],
            product=prod
        )
        
    context = {}
    return render(request, template, context)


def data_prep():
    # ### Text Pre-Processing 
    # 
    # The ``review_text`` is going to be cleaned and standardized so that when implemented within the model, the model can be optimized at its best. This step takes the longest since it is in base of trial and error.
    # 
    # DONE IN THIS STAGE:
    # 1. Spelling is corrected
    # 2. tokenization,
    # 3. removing stopwords, punctuations, special charas
    # 4. lowercasing
    # 5. stemming
    # 6. removing top 3 common and rare words

    #CORRECT SPELLING
    df.review_text.apply(lambda i: ''.join(TextBlob(i).correct()))
    df['review_text'] = df['review_text'].apply(text_preprocessing)
    df['review_text'].head()
    #CHECK RARE WORDS
    r = pd.Series(' '.join(df['review_text']).split()).value_counts()[-10:]
    print("RARE WORDS:")
    print(r)
    #CHECK TOP COMMON WORDS
    words = '' 
    for i in df["review_text"]: 
        tokens = i.split()   
        words += " ".join(tokens)+" "  
    word_cloud = WordCloud(width = 700, height = 700, 
                           background_color ='white', 
                           min_font_size = 10).generate(words) 
    plt.figure(figsize = (5, 5)) 
    plt.imshow(word_cloud) 
    plt.axis("off") 
    plt.tight_layout(pad = 0) 
     
    plt.show()
    #removing common and rare words
    common = pd.Series(' '.join(df['review_text']).split()).value_counts()[:3]
    common = list(common.index)
    df['review_text'] = df['review_text'].apply(lambda i: " ".join(i for i in i.split() if i not in common))

    rare = pd.Series(' '.join(df['review_text']).split()).value_counts()[-3:]
    rare = list(rare.index)
    df['review_text'] = df['review_text'].apply(lambda i: " ".join(i for i in i.split() if i not in rare))
    #WORDCLOUD - UPDATED TOP WORDS
    words = '' 
    for i in df["review_text"]: 
        tokens = i.split()   
        words += " ".join(tokens)+" "

        
    word_cloud = WordCloud(width = 700, height = 700, background_color ='white', min_font_size = 10).generate(words) 
    plt.figure(figsize = (5, 5)) 
    plt.imshow(word_cloud) 
    plt.axis("off") 
    plt.tight_layout(pad = 0) 
      
    plt.show()
    # After removing the top 3 common word (it was removed since it would remove its meaning from the entire thing), we are left with the current top 10 words. As seen from above, we can see that the sentiment of it is quite positive, meaning that this dataset is dealing with many positive-centric reviews. The general polarity is thus, positive, and needs to be kept in mind for analysis later. It is to be noted that due to the lack of negative reviews in this case can cause for there to be discrepencies when, for instance a negative value is set to be identified as "fake" or "real", and thus can be added as a limitation to this study.
    df['review_text'].apply(word_tokenize).head()

