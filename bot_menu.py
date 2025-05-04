from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

# Messages dans différentes langues
LANG_MESSAGES = {
    'Français': "Bienvenue !\nVeuillez lire attentivement cette description.",
    'English': "Welcome!\nPlease read this description carefully.",
    'العربية': "مرحبًا بك!\nيرجى قراءة هذا الوصف بعناية.",
    'Deutsch': "Willkommen!\nBitte lesen Sie diese Beschreibung sorgfältig.",
    'Español': "¡Bienvenido!\nPor favor, lea atentamente esta descripción."
}

# Stocker les utilisateurs ayant choisi une langue
user_language_selected = set()

# Contenu des options du menu (titre, description, adresse, superficie, prix/m², lien)
MENU_OPTIONS = {
    'Option 1': {
        'title': 'Titre 1',
        'description': 'Ceci est la description détaillée de l\'option 1.',
        'address': 'Adresse de l\'option 1 : 123 Rue Exemple, Paris, France',
        'superficie': 'Superficie : 120 m²',
        'prix_per_m2': 'Prix/m² : 1500€',
        'link': 'https://exemple.com/option1'
    },
    'Option 2': {
        'title': 'Titre 2',
        'description': 'Description de l\'option 2.',
        'address': 'Adresse de l\'option 2 : 456 Avenue Exemple, Lyon, France',
        'superficie': 'Superficie : 100 m²',
        'prix_per_m2': 'Prix/m² : 1200€',
        'link': 'https://exemple.com/option2'
    },
    'Option 3': {
        'title': 'Titre 3',
        'description': 'Description de l\'option 3.',
        'address': 'Adresse de l\'option 3 : 789 Boulevard Exemple, Marseille, France',
        'superficie': 'Superficie : 80 m²',
        'prix_per_m2': 'Prix/m² : 1300€',
        'link': 'https://exemple.com/option3'
    },
    'Option 4': {
        'title': 'Titre 4',
        'description': 'Description de l\'option 4.',
        'address': 'Adresse de l\'option 4 : 1010 Route Exemple, Bordeaux, France',
        'superficie': 'Superficie : 150 m²',
        'prix_per_m2': 'Prix/m² : 1400€',
        'link': 'https://exemple.com/option4'
    },
    'Option 5': {
        'title': 'Titre 5',
        'description': 'Description de l\'option 5.',
        'address': 'Adresse de l\'option 5 : 2020 Rue Exemple, Lille, France',
        'superficie': 'Superficie : 95 m²',
        'prix_per_m2': 'Prix/m² : 1100€',
        'link': 'https://exemple.com/option5'
    },
    'Option 6': {
        'title': 'Titre 6',
        'description': 'Description de l\'option 6.',
        'address': 'Adresse de l\'option 6 : 3030 Avenue Exemple, Nantes, France',
        'superficie': 'Superficie : 105 m²',
        'prix_per_m2': 'Prix/m² : 1250€',
        'link': 'https://exemple.com/option6'
    },
    'Option 7': {
        'title': 'Titre 7',
        'description': 'Description de l\'option 7.',
        'address': 'Adresse de l\'option 7 : 4040 Boulevard Exemple, Nice, France',
        'superficie': 'Superficie : 130 m²',
        'prix_per_m2': 'Prix/m² : 1600€',
        'link': 'https://exemple.com/option7'
    }
}

# Gérer les messages reçus
def handle_message(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    user_text = update.message.text

    if user_text in LANG_MESSAGES:
        # Envoyer message de bienvenue
        context.bot.send_message(chat_id=chat_id, text=LANG_MESSAGES[user_text])

        # Ajouter utilisateur comme ayant choisi une langue
        user_language_selected.add(chat_id)

        # Afficher bouton "Continuer"
        reply_keyboard = [['Continuer']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        context.bot.send_message(chat_id=chat_id, text="Appuyez sur Continuer pour accéder au menu :", reply_markup=markup)

    elif user_text == 'Continuer' and chat_id in user_language_selected:
        # Afficher le menu à 7 choix
        menu_keyboard = [
            ['Option 1', 'Option 2', 'Option 3'],
            ['Option 4', 'Option 5'],
            ['Option 6', 'Option 7']
        ]
        markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
        context.bot.send_message(chat_id=chat_id, text="Voici le menu :", reply_markup=markup)

    elif user_text in MENU_OPTIONS:
        # Afficher le titre, description, adresse, superficie, prix/m² et lien de l'option choisie
        option = MENU_OPTIONS[user_text]
        message = f"""
**{option['title']}**

{option['description']}

**Adresse** : {option['address']}
**Superficie** : {option['superficie']}
**Prix/m²** : {option['prix_per_m2']}

👉 {option['link']}
"""
        # Ajouter bouton "Retour"
        reply_keyboard = [['Retour au menu']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        context.bot.send_message(chat_id=chat_id, text=message, reply_markup=markup)

    elif user_text == 'Retour au menu':
        # Retourner au menu principal
        menu_keyboard = [
            ['Option 1', 'Option 2', 'Option 3'],
            ['Option 4', 'Option 5'],
            ['Option 6', 'Option 7']
        ]
        markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
        context.bot.send_message(chat_id=chat_id, text="Voici le menu :", reply_markup=markup)

    else:
        # Afficher le choix de langues par défaut
        reply_keyboard = [['العربية', 'Français'], ['English', 'Deutsch'], ['Español']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        context.bot.send_message(chat_id=chat_id, text="Veuillez choisir votre langue :", reply_markup=markup)

# Démarrage du bot
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    handler = MessageHandler(Filters.text & ~Filters.command, handle_message)
    dispatcher.add_handler(handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
