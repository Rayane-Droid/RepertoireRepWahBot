
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "TON_TOKEN_ICI"  # Remplace par ton token

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
    "fr": "Vous êtes qui ? Veuillez entrer votre nom ou celui de votre société :",
    "en": "Who are you? Please enter your name or company name:",
    "es": "¿Quién eres? Introduzca su nombre o el de su empresa:",
    "de": "Wer sind Sie? Bitte geben Sie Ihren Namen oder Firmennamen ein:",
    "ar": "من أنت؟ يرجى إدخال اسمك أو اسم شركتك:"
}

thank_you_texts = {
    "fr": "Merci pour votre visite !",
    "en": "Thank you for visiting!",
    "es": "¡Gracias por su visita!",
    "de": "Danke für Ihren Besuch!",
    "ar": "شكراً لزيارتك!"
}

descriptions = {
    "fr": "Veuillez lire attentivement cette description : nous mettons ces produits en vente. Bonne continuation.",
    "en": "Please read this description carefully: we are offering these products for sale. Best of luck.",
    "es": "Lea atentamente esta descripción: ponemos estos productos a la venta. Buena suerte.",
    "de": "Bitte lesen Sie diese Beschreibung sorgfältig: Wir bieten diese Produkte zum Verkauf an. Viel Erfolg.",
    "ar": "يرجى قراءة هذا الوصف بعناية: نحن نعرض هذه المنتجات للبيع. بالتوفيق."
}

# Dictionnaire pour les produits avec leurs détails
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

# Fonction pour envoyer le message de bienvenue et proposer un choix de langue
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton(languages["fr"], callback_data="lang_fr"),
         InlineKeyboardButton(languages["en"], callback_data="lang_en"),
         InlineKeyboardButton(languages["es"], callback_data="lang_es"),
         InlineKeyboardButton(languages["de"], callback_data="lang_de"),
         InlineKeyboardButton(languages["ar"], callback_data="lang_ar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Bienvenue! Choisissez une langue / Choose a language", reply_markup=reply_markup)

# Fonction pour gérer le choix de la langue
async def language_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    language = query.data.split("_")[1]
    
    # Envoyer le message de bienvenue
    await query.answer()
    await query.edit_message_text(welcome_texts[language])

    # Demander le nom ou le nom de la société
    await query.message.reply_text(who_are_you_texts[language])

    # Enregistrer la langue choisie dans le contexte de l'utilisateur
    context.user_data["language"] = language

    # Ajouter un bouton "continuer"
    keyboard = [[InlineKeyboardButton("Continuer", callback_data="continue")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Veuillez entrer votre nom ou le nom de votre société.", reply_markup=reply_markup)

# Fonction pour continuer après avoir entré le nom ou la société
async def continue_after_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    language = context.user_data.get("language", "fr")

    # Demander à l'utilisateur de visiter
    await query.answer()
    await query.edit_message_text(thank_you_texts[language])

    # Ajouter un bouton "continuer"
    keyboard = [[InlineKeyboardButton("Continuer", callback_data="view_products")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Merci pour votre visite !", reply_markup=reply_markup)

# Fonction pour afficher les produits
async def view_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    language = context.user_data.get("language", "fr")

    # Menu des produits
    keyboard = [
        [InlineKeyboardButton("Villa", callback_data="product_villa"),
         InlineKeyboardButton("Garage", callback_data="product_garage")],
        [InlineKeyboardButton("Terrain 1", callback_data="product_terrain1"),
         InlineKeyboardButton("Terrain 2", callback_data="product_terrain2")],
        [InlineKeyboardButton("Terrain 3", callback_data="product_terrain3")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.answer()
    await query.edit_message_text("Choisissez un produit / Choose a product", reply_markup=reply_markup)

# Fonction pour afficher les détails du produit
async def show_product_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    product_key = query.data.split("_")[1]
    product = products.get(product_key)

    if product:
        # Afficher les détails du produit
        product_details = f"""
        Titre: {product['title']}
        Description: {product['description']}
        Superficie: {product['surface']}
        Adresse: {product['address']}
        Localisation: {product['location']}
        Photos: {product['photo_link']}
        Vidéo: {product['video_link']}
        Prix: {product['price']}
        """

        await query.answer()
        await query.edit_message_text(product_details)

        # Ajouter le bouton "Retour"
        keyboard = [[InlineKeyboardButton("Retour", callback_data="view_products")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Retour au menu des produits", reply_markup=reply_markup)

# Fonction pour proposer un prix
async def propose_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    language = context.user_data.get("language", "fr")

    # Proposer un prix
    await query.answer()
    await query.edit_message_text("Voulez-vous proposer un prix ?")

    # Ajouter un bouton pour soumettre un prix
    keyboard = [[InlineKeyboardButton("Proposer un prix", callback_data="submit_price")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Cliquez pour proposer un prix", reply_markup=reply_markup)

# Ajouter les gestionnaires de commandes
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(language_choice, pattern="^lang_"))
app.add_handler(CallbackQueryHandler(continue_after_name, pattern="^continue$"))
app.add_handler(CallbackQueryHandler(view_products, pattern="^view_products$"))
app.add_handler(CallbackQueryHandler(show_product_details, pattern="^product_"))
app.add_handler(CallbackQueryHandler(propose_price, pattern="^submit_price$"))

if __name__ == "__main__":
    app.run_polling()
