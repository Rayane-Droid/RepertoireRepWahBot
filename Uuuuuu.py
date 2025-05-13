# ----------------- Importations des bibliothèques -----------------

import logging
import os
import asyncio
from flask import Flask
from threading import Thread
from dotenv import load\_dotenv

import csv
from datetime import datetime

# Importations des modules Telegram

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from telegram.error import BadRequest

# ----------------- Importation des textes multilingues et données produits -----------------

from Dictionnaire import languages, welcome\_texts, who\_are\_you\_texts, choixproduit\_text, thank\_you\_texts, choixdproduit\_text, ask\_price\_messages, revmenbien\_texts, revmenlang\_texts, monnaie\_texts, Popospri\_texts, entrnumtel\_texts, mercitel\_texts, choixbien\_texts, commentaires\_texts

from produits import property\_fields, property\_details, produits\_text

# ----------------- Partie Flask pour garder le bot actif (utile sur Replit) -----------------

flask\_app = Flask('')

@flask\_app.route('/')
def home():
return "Le bot Telegram est actif."

def run():
flask\_app.run(host='0.0.0.0', port=8080)

def keep\_alive():
\# Lancement du serveur Flask dans un thread séparé
t = Thread(target=run)
t.start()

# ----------------- Initialisation du bot Telegram ---------------------------------------------------

# Chargement des variables d'environnement depuis .env (notamment le token du bot)

load\_dotenv()
TOKEN = os.getenv("BOT\_TOKEN")

if not TOKEN:
raise ValueError("Le token Telegram est introuvable dans le fichier .env")

# Configuration des logs pour suivre les erreurs/info ------------------------------------------------

logging.basicConfig(level=logging.INFO)

# Construction de l'application Telegram avec le token -----------------------------------------------

app = ApplicationBuilder().token(TOKEN).build()

# ----------------- Définition des Handlers et Fonctions principales ---------------------------------

# Handler pour la commande /start ou le bouton "start"------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT\_TYPE):
\# Création d’un clavier avec les langues disponibles
keyboard = \[\[InlineKeyboardButton(name, callback\_data=code)]
for code, name in languages.items()]
reply\_markup = InlineKeyboardMarkup(keyboard)

```
# Affichage selon le type de mise à jour (message ou callback)
if update.callback_query:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "👅 :", reply_markup=reply_markup)
elif update.message:
    await update.message.reply_text("👅 :", reply_markup=reply_markup)
```

# Handler appelé après le choix de la langue----------------------------------------------------------

async def set\_language(update: Update, context: ContextTypes.DEFAULT\_TYPE):
query = update.callback\_query
await query.answer()

```
lang_code = query.data
context.user_data["lang"] = lang_code  # Stocke la langue choisie

welcome = welcome_texts[lang_code]
question = who_are_you_texts[lang_code]

await query.edit_message_text(f"{welcome}\n\n{question}")
```

# Handler quand l'utilisateur clique sur "Donner un prix"---------------------------------------------

async def handle\_propose\_price(update: Update, context: ContextTypes.DEFAULT\_TYPE):
query = update.callback\_query
await query.answer()
\#1#
if context.user\_data is None:
context.user\_data = {}
lang = context.user\_data.get("lang", "fr")
context.user\_data\[
"awaiting\_price\_proposal"] = True  # Attend une entrée texte (le prix)
prompt = ask\_price\_messages\["propose\_price\_prompt"].get(
lang, ask\_price\_messages\["propose\_price\_prompt"]\["fr"])

```
await query.edit_message_text(prompt)
return
```

# Handler pour les messages texte généraux--------€€€€----------------------------------------------------

async def handle\_text\_messages(update: Update,context: ContextTypes.DEFAULT\_TYPE):
text = update.message.text.strip()  # ✅ Cette ligne doit être ici !
\# Cas 1 :  où l'on attend un prix
if "lang" not in context.user\_data:
await update.message.reply\_text(
"❗ Veuillez d'abord sélectionner une langue en cliquant sur un des boutons ci-dessous.\n\n🔧 Si vous avez besoin d'aide, consultez : [https://exemple.com/aide](https://exemple.com/aide)"
)
keyboard = \[\[InlineKeyboardButton(name, callback\_data=code)] for code, name in languages.items()]
reply\_markup = InlineKeyboardMarkup(keyboard)
await update.message.reply\_text("🌍 Choisissez votre langue :", reply\_markup=reply\_markup)
return
\# Cas 1 :

```
if context.user_data.get("awaiting_price_proposal"):
    try:
        prix = float(update.message.text.replace(
            ",", ".").strip())  # Gère les virgules aussi
        context.user_data["awaiting_price_proposal"] = False
        context.user_data["proposed_price"] = prix

        await update.message.reply_text(
            f"✅ Merci pour votre proposition de {prix:.2f} DH. Nous allons l'étudier et vous contacter."
        )

        user_id = update.effective_user.id
        name = context.user_data.get("name", "")
        phone = context.user_data.get("phone_number", "")
        produit = context.user_data.get("produit_choisi", "")

        enregistrer_donnees(user_id, name, phone, produit, prix)

        # Demander un commentaire
        context.user_data["awaiting_comment"] = True
        await update.message.reply_text(
            "📝 Souhaitez-vous laisser un commentaire concernant votre proposition ?"
        )

    except ValueError:
        await update.message.reply_text(
            "❗ Veuillez entrer un montant valide.")
    return

# Cas où l'on attend un commentaire
if context.user_data.get("awaiting_comment"):
    commentaire = text
    context.user_data["awaiting_comment"] = False
    context.user_data["commentaire"] = commentaire

    await update.message.reply_text("✅ Merci pour votre commentaire !")

    # Maintenant on affiche le menu des biens
    lang = context.user_data.get("lang", "fr")
    keyboard = generate_menu_keyboard(lang)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(choixbien_texts.get(
        lang, choixbien_texts["fr"]),
                                    reply_markup=reply_markup)
    return
```

\#€€€€€\_\_\_\_\_#
\#context.user\_data\["awaiting\_bien\_selection"] = True  # On attend un clic sur un bien
\# Cas où l'on attend un numéro de téléphone
if context.user\_data.get("awaiting\_phone\_number"):
phone\_number = update.message.text.strip()
if phone\_number.isdigit() and 8 <= len(phone\_number) <= 15:
context.user\_data\["phone\_number"] = phone\_number
context.user\_data\["awaiting\_phone\_number"] = False

```
        lang = context.user_data.get("lang", "fr")
        await update.message.reply_text(
            mercitel_texts.get(lang, mercitel_texts["fr"]))

        # Affichage du menu uniquement maintenant
        keyboard = generate_menu_keyboard(lang)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(choixbien_texts.get(
            lang, choixbien_texts["fr"]),
                                        reply_markup=reply_markup)

    else:
        await update.message.reply_text(
            "❗ Numéro invalide. Veuillez entrer un numéro de téléphone valide (8 à 15 chiffres)."
        )
    return

# Cas où on attend un commentaire
if context.user_data.get("awaiting_comment"):
    comment = update.message.text.strip()
    context.user_data["awaiting_comment"] = False

    user_id = update.effective_user.id
    name = context.user_data.get("name", "")
    phone = context.user_data.get("phone_number", "")
    produit = context.user_data.get("produit_choisi", "")
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Enregistrer dans un fichier CSV
    with open("index.csv", mode="a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([user_id, name, phone, produit, date, comment])

    await update.message.reply_text("✅ Merci pour votre commentaire !")

    # Retour au menu
    keyboard = [[InlineKeyboardButton("⬅️", callback_data="menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Retour au menu principal",
                                    reply_markup=reply_markup)


# Sinon, on suppose que c’est le nom de l’utilisateur
name = update.message.text.strip()
context.user_data["name"] = name
lang = context.user_data.get("lang", "fr")

thank_you = thank_you_texts.get(lang, thank_you_texts["fr"])
await update.message.reply_text(f"{thank_you} {name} !")

# Demander le numéro de téléphone après avoir reçu le nom
await update.message.reply_text(
    entrnumtel_texts.get(lang, entrnumtel_texts["fr"]))
context.user_data["awaiting_phone_number"] = True
return
```

async def fallback\_handler(update: Update, context: ContextTypes.DEFAULT\_TYPE):
await update.message.reply\_text(
"Je n'ai pas compris ce message. Utilisez /menu pour revenir au menu principal."
)

# ----------------- Enregistrement des Handlers -----------------

app.add\_handler(CommandHandler("start", start))

# Handler quand l’utilisateur choisit un produit (villa, garage, terrain...)

async def handle\_product\_selection(update: Update, context: ContextTypes.DEFAULT\_TYPE):
query = update.callback\_query
await query.answer()
product = query.data
context.user\_data\["produit\_choisi"] = product
lang = context.user\_data.get("lang", "fr")

```
# Récupération des détails du produit
choix_text = choixdproduit_text.get(lang, choixdproduit_text["fr"])
product_label = produits_text.get(product, {}).get(lang, product)
details = property_details.get(product, {})

# Données spécifiques au bien
title = details.get("📝 title", {}).get(lang, "N/A")
description = details.get("🗒️ description", {}).get(lang, "N/A")
address = details.get("🏠 address", {}).get(lang, "N/A")
surface = details.get("📏 surface", {}).get(lang, "N/A")
location = details.get("📍 Géolocalisation", {}).get(lang, "N/A")
photo_link = details.get("📸 Photo_link", {}).get(lang, "N/A")
video_link = details.get("🎥 video_link", {}).get(lang, "N/A")
price = details.get("💰 price", {}).get(lang, "N/A")

# Création de la réponse message
message = (
    f"{choix_text} {product_label}.\n\n"
    f"{property_fields.get('📝 title', {}).get(lang, 'N/A')}: {title}\n"
    f"{property_fields.get('🗒️ description', {}).get(lang, 'N/A')}: {description}\n"
    f"{property_fields.get('🏠 address', {}).get(lang, 'N/A')}: {address}\n"
    f"{property_fields.get('📏 surface', {}).get(lang, 'N/A')}: {surface}\n"
    f"{property_fields.get('📍 Géolocalisation', {}).get(lang, 'N/A')}: {location}\n"
    f"{property_fields.get('💰 price', {}).get(lang, 'N/A')}: {price}\n"
    f"{property_fields.get('📸 Photo_link', {}).get(lang, 'N/A')}: {photo_link}\n"
    f"{property_fields.get('🎥 video_link', {}).get(lang, 'N/A')}: {video_link}"
)

# Affichage du message avec un petit délai
await context.bot.send_chat_action(chat_id=update.effective_chat.id,
                                   action=ChatAction.TYPING)
await query.edit_message_text(message)

# Affichage des options après visualisation du produit
reply_markup = InlineKeyboardMarkup([
    # [InlineKeyboardButton("Donner un prix en : ( 🇲🇦💰 Dirham marocain ) ", callback_data="propose_price")],
    [
        InlineKeyboardButton(
            f"✅ {Popospri_texts.get(lang, Popospri_texts['fr'])} {monnaie_texts.get(lang, monnaie_texts['fr'])}",
            callback_data="propose_price")
    ],
    [
        InlineKeyboardButton(revmenbien_texts.get(lang,
                                                  revmenbien_texts["fr"]),
                             callback_data="menu")
    ]
])
await query.edit_message_reply_markup(reply_markup=reply_markup)
```

# Affiche le menu des biens à tout moment

async def menu(update: Update, context: ContextTypes.DEFAULT\_TYPE):
lang = context.user\_data.get("lang", "fr")

```
message = choixproduit_text.get(lang, "Veuillez choisir un Bien.")

keyboard = generate_menu_keyboard(lang)
reply_markup = InlineKeyboardMarkup(keyboard)

if update.message:
    await update.message.reply_text(message, reply_markup=reply_markup)
elif update.callback_query:
    await update.callback_query.edit_message_text(
        message, reply_markup=reply_markup)
```

async def handle\_return\_to\_menu(update: Update, context: ContextTypes.DEFAULT\_TYPE):
print("Bouton 'Revenir Au Menu' cliqué")
query = update.callback\_query

```
if query:
    try:
        await query.answer(
        )  # Ne doit pas dépasser 10 secondes après l'appui
    except BadRequest as e:
        print(f"Erreur dans query.answer(): {e}"
              )  # Eviter un crash silencieux

await menu(update, context)
```

# Handler pour "Ajouter un commentaire"

async def handle\_add\_comment(update: Update, context: ContextTypes.DEFAULT\_TYPE):
query = update.callback\_query
await query.answer()

```
lang = context.user_data.get("lang", "fr")
context.user_data[
    "awaiting_comment"] = True  # Active l'attente du commentaire

await query.edit_message_text(
    commentaires_texts.get(lang, commentaires_texts["fr"]))
```

def enregistrer\_donnees(user\_id, name, phone, produit, prix):
with open("index.csv", mode="a", newline='', encoding="utf-8") as file:
writer = csv.writer(file)
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
writer.writerow(\[now, user\_id, name, phone, produit, prix])

def generate\_menu\_keyboard(lang):
return \[\[
InlineKeyboardButton(produits\_text\["🏡 Villa"]\[lang],
callback\_data="🏡 Villa")
],
\[
InlineKeyboardButton(produits\_text\["🚗 Garage"]\[lang],
callback\_data="🚗 Garage")
],
\[
InlineKeyboardButton(produits\_text\["🌳 Terrain1"]\[lang],
callback\_data="🌳 Terrain1")
],
\[
InlineKeyboardButton(produits\_text\["🌿 Terrain2"]\[lang],
callback\_data="🌿 Terrain2")
],
\[
InlineKeyboardButton(produits\_text\["🏞️ Terrain3"]\[lang],
callback\_data="🏞️ Terrain3")
],
\[
InlineKeyboardButton(revmenlang\_texts.get(
lang, revmenlang\_texts\["fr"]),
callback\_data="start")
]]

app.add\_handler(CommandHandler("menu", menu))
app.add\_handler(CallbackQueryHandler(set\_language, pattern="^(" + "|".join(languages.keys()) + ")\$"))
app.add\_handler(CallbackQueryHandler(handle\_propose\_price, pattern="^propose\_price\$"))
app.add\_handler(CallbackQueryHandler(handle\_return\_to\_menu, pattern="^menu\$"))
app.add\_handler(CallbackQueryHandler(handle\_product\_selection, pattern="^(🏡 Villa|🚗 Garage|🌳 Terrain1|🌿 Terrain2|🏞️ Terrain3)\$"))
app.add\_handler(MessageHandler(filters.TEXT & \~filters.COMMAND, handle\_text\_messages))
app.add\_handler(CallbackQueryHandler(start, pattern="^start\$"))  # Redémarre depuis le début
app.add\_handler(MessageHandler(filters.ALL, fallback\_handler))
app.add\_handler(CallbackQueryHandler(handle\_add\_comment, pattern="add\_comment"))

# ----------------- Démarrage du Bot -----------------

if **name** == "**main**":
keep\_alive()  # Lance Flask dans un thread pour maintenir le bot actif
app.run\_polling()  # Démarre le bot Telegram en mode polling

