
import logging
import os

from Dictionnaire import languages, welcome_texts, who_are_you_texts, thank_you_texts

from flask import Flask
from threading import Thread

flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Le bot Telegram est actif."

def run():
    flask_app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()


from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Charger les variables d’environnement
load_dotenv()

# Récupérer le token depuis .env
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("Le token Telegram est introuvable dans le fichier .env")

logging.basicConfig(level=logging.INFO)
app = ApplicationBuilder().token(TOKEN).build()


languages = {
    "fr": "Français",
    "en": "English",
    "es": "Español",
    "de": "Deutsch",
    "ar": "العربية"
}

welcome_texts = {
    "fr": "Bienvenue !",
    "en": "Welcome!",
    "es": "¡Bienvenido!",
    "de": "Willkommen!",
    "ar": "مرحبا بك!"
}

who_are_you_texts = {
    "fr": "Veuillez entrer votre nom ou celui de votre société :",
    "en": "Please enter your name or company name:",
    "es": "Introduzca su nombre o el de su empresa:",
    "de": "Bitte geben Sie Ihren Namen oder Firmennamen ein:",
    "ar": "يرجى إدخال اسمك أو اسم شركتك:"
}

thank_you_texts = {
    "fr": "Merci pour votre visite !",
    "en": "Thank you for visiting!",
    "es": "¡Gracias por su visita!",
    "de": "Danke für Ihren Besuch!",
    "ar": "شكراً لزيارتك!"
}

products = {
    "villa": {
        "title": "Villa",
        "description": "Une belle villa spacieuse.",
        "surface": "300 m²",
        "address": "123 Rue de la Mer",
        "location": "Ville A",
        "photo_link": "https://link_to_photo_villa.com",
        "video_link": "https://link_to_video_villa.com",
        "price": "500,000€"
    },
    "garage": {
        "title": "Garage",
        "description": "Un garage spacieux pour 2 voitures.",
        "surface": "50 m²",
        "address": "456 Rue du Garage",
        "location": "Ville B",
        "photo_link": "https://link_to_photo_garage.com",
        "video_link": "https://link_to_video_garage.com",
        "price": "30,000€"
    },
    "terrain1": {
        "title": "Terrain 1",
        "description": "Terrain à bâtir dans un quartier calme.",
        "surface": "1000 m²",
        "address": "789 Rue du Terrain",
        "location": "Ville C",
        "photo_link": "https://link_to_photo_terrain1.com",
        "video_link": "https://link_to_video_terrain1.com",
        "price": "150,000€"
    },
    "terrain2": {
        "title": "Terrain 2",
        "description": "Grand terrain avec vue sur la montagne.",
        "surface": "1500 m²",
        "address": "101 Rue Montagne",
        "location": "Ville D",
        "photo_link": "https://link_to_photo_terrain2.com",
        "video_link": "https://link_to_video_terrain2.com",
        "price": "200,000€"
    },
    "terrain3": {
        "title": "Terrain 3",
        "description": "Terrain idéal pour un projet commercial.",
        "surface": "2000 m²",
        "address": "202 Rue Commerciale",
        "location": "Ville E",
        "photo_link": "https://link_to_photo_terrain3.com",
        "video_link": "https://link_to_video_terrain3.com",
        "price": "250,000€"
    }
}

# 1. /start : Choix de la langue
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton(name, callback_data=f"lang_{code}")] for code, name in languages.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Bienvenue! Choisissez une langue / Choose a language", reply_markup=reply_markup)

# 2. Callback langue choisie
async def language_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    lang_code = query.data.split("_")[1]
    context.user_data["language"] = lang_code
    await query.answer()
    await query.edit_message_text(welcome_texts[lang_code])
    await query.message.reply_text(who_are_you_texts[lang_code])

# 3. Récupération du nom
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get("awaiting_price"):
        await receive_price(update, context)
    elif "user_name" not in context.user_data:
        await receive_name(update, context)
    else:
        await update.message.reply_text("Revenir Au Menu Principale. /start")


# 4. Afficher la liste des produits
async def view_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Villa", callback_data="product_villa"),
         InlineKeyboardButton("Garage", callback_data="product_garage")],
        [InlineKeyboardButton("Terrain 1", callback_data="product_terrain1"),
         InlineKeyboardButton("Terrain 2", callback_data="product_terrain2")],
        [InlineKeyboardButton("Terrain 3", callback_data="product_terrain3")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Choisissez un produit :", reply_markup=reply_markup)

# 5. Détails d’un produit
async def show_product_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    product_key = query.data.split("_")[1]
    product = products.get(product_key)

    if product:
        context.user_data["selected_product"] = product_key  # Stocker le produit choisi
        details = (
            f"🏠 *{product['title']}*\n\n"
            f"*Description:* {product['description']}\n"
            f"*Superficie:* {product['surface']}\n"
            f"*Adresse:* {product['address']}\n"
            f"*Localisation:* {product['location']}\n"
            f"*Prix:* {product['price']}\n\n"
            f"[📷 Voir la photo]({product['photo_link']}) | [🎥 Voir la vidéo]({product['video_link']})"
        )
        await query.answer()
        await query.edit_message_text(details, parse_mode="Markdown", disable_web_page_preview=False)

        # Boutons : retour + proposer un prix
        keyboard = [
            [InlineKeyboardButton("⬅️ Retour", callback_data="view_products")],
            [InlineKeyboardButton("💰 Proposer un prix", callback_data="propose_price")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Que souhaitez-vous faire ?", reply_markup=reply_markup)

# 6. Proposition du client
async def propose_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("language", "fr")

    messages = {
        "fr": "Veuillez entrer votre prix proposé pour ce bien (€) :",
        "en": "Please enter your proposed price for this property (€):",
        "es": "Por favor ingrese su precio propuesto para esta propiedad (€):",
        "de": "Bitte geben Sie Ihren vorgeschlagenen Preis für diese Immobilie ein (€):",
        "ar": "يرجى إدخال السعر الذي تقترحه لهذا العقار (€):"
    }

    await query.message.reply_text(messages[lang])
    context.user_data["awaiting_price"] = True  # On attend le prix de l'utilisateur

# 7. Réception du prix proposé
async def receive_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get("awaiting_price"):
        proposed_price = update.message.text.strip()
        lang = context.user_data.get("language", "fr")
        product_key = context.user_data.get("selected_product", "inconnu")
        user_name = context.user_data.get("user_name", "utilisateur")

        # Tu peux enregistrer ce prix dans une base de données ici si nécessaire

        confirmations = {
            "fr": f"Merci {user_name}, vous avez proposé {proposed_price}€ pour le bien '{products[product_key]['title']}'. Nous vous contacterons bientôt.",
            "en": f"Thank you {user_name}, you proposed {proposed_price}€ for the property '{products[product_key]['title']}'. We will contact you soon.",
            "es": f"Gracias {user_name}, propuso {proposed_price}€ para la propiedad '{products[product_key]['title']}'. Nos pondremos en contacto con usted pronto.",
            "de": f"Vielen Dank {user_name}, Sie haben {proposed_price}€ für die Immobilie '{products[product_key]['title']}' vorgeschlagen. Wir werden Sie bald kontaktieren.",
            "ar": f"شكراً {user_name}، لقد اقترحت {proposed_price}€ للعقار '{products[product_key]['title']}'. سنتواصل معك قريباً."
        }

        await update.message.reply_text(confirmations[lang])
        context.user_data["awaiting_price"] = False  # Réinitialiser l'état
    else:
        # Si l'utilisateur envoie un message sans que le bot attende un prix
        await update.message.reply_text("Veuillez commencer avec /start ou sélectionner une option.")

# 8. Réception du nom de l'utilisateur
async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.message.text.strip()
    context.user_data["user_name"] = user_name
    lang = context.user_data.get("language", "fr")

    await update.message.reply_text(f"{thank_you_texts[lang]} {user_name} 🙏")

    # Affiche les produits disponibles
    keyboard = [
        [InlineKeyboardButton("Voir les produits disponibles", callback_data="view_products")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Cliquez ci-dessous pour voir nos biens disponibles :", reply_markup=reply_markup)


# Enregistre les gestionnaires
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(language_choice, pattern="^lang_"))
app.add_handler(CallbackQueryHandler(view_products, pattern="^view_products$"))
app.add_handler(CallbackQueryHandler(show_product_details, pattern="^product_"))
app.add_handler(CallbackQueryHandler(propose_price, pattern="^propose_price$"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_price))

# Lancement de l'application
if __name__ == "__main__":
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(language_choice, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(view_products, pattern="^view_products$"))
    app.add_handler(CallbackQueryHandler(show_product_details, pattern="^product_"))
    app.add_handler(CallbackQueryHandler(propose_price, pattern="^propose_price$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot is running...")
    keep_alive()
    app.run_polling()
