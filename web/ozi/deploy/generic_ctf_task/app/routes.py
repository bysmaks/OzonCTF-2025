from flask import Blueprint, render_template, request, redirect, url_for, current_app
import random
import os
from .models import products, cart
from .ban_words import forbidden_words

main = Blueprint('main', __name__)

@main.route('/')
def index():
    for product in products:
        product['discount'] = random.choice([5, 10, 15, 20, 25, 30])
    return render_template('index.html', products=products)

@main.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        product['views'] = product.get('views', 0) + 1
    return render_template('product.html', product=product)


@main.route('/cart')
def show_cart():
    total_cost = calculate_cart_total(cart)
    return render_template('cart.html', cart=cart, total_cost=total_cost)

@main.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = next((item for item in products if item['id'] == product_id), None)
    if product:
        cart.append(product)
    return redirect(url_for('main.show_cart'))

def calculate_cart_total(cart):
    expression = " + ".join([str(item['price']) for item in cart])

    try:
        if any(word in expression for word in forbidden_words):
            return 'no info'
        total_cost = eval(expression)
    except Exception:
        total_cost = 0
    return total_cost



@main.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    global cart
    cart = [item for item in cart if item['id'] != product_id]
    return redirect(url_for('main.show_cart'))

@main.route('/chat')
def chat():
    response = random.choice([ 
        "Привет! Какой товар вас интересует?",
        "Этот товар - отличный выбор!",
        "Вы хотите добавить его в корзину?",
        "У нас сегодня действует скидка!",
        "Не забудьте посмотреть другие товары."
    ])
    return {'response': response}

@main.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        image = request.files['image']
        
        if image:
            image_filename = image.filename
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename))
        else:
            image_filename = 'default.png'
        
        new_id = max([p['id'] for p in products], default=0) + 1
        products.append({'id': new_id, 'name': name, 'price': price, 'description': description, 'image': image_filename, 'views': 0})
        
        return redirect(url_for('main.index'))
    
    return render_template('add_product.html')
