# -*- coding: utf-8 -*-

# ----------------- Importations des bibliothèques -----------------
import logging
import os
import asyncio
import csv
from datetime import datetime
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

# Importations des modules Telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters, Application

# ----------------- Importation des textes multilingues et données produits -----------------
from Dictionnaire import languages, welcome_texts, who_are_you_texts, choixproduit_text, thank_you_texts, produits_text, choixdproduit_text, ask_price_messages, revmenbien_texts, revmenlang_texts, monnaie_texts, Popospri_texts, etudier_texts, merci_texts, entrnumtel_texts, merciteleph_texts,  montvalid_texts, numtelvali_texts

from produits import property_fields, property_details

# ----------------- Partie Flask pour garder le bot actif (utile sur Replit) -----------------
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Le bot Telegram est actif."

def run():
    flask_app.run(host='0.0.0.0', port=8080)

def keep_alive():
    # Lancement du serveur Flask dans un thread séparé
    t = Thread(target=run)
    t.start()

# ----------------- Initialisation du bot Telegram -----------------
# Chargement des variables d'environnement depuis .env (notamment le token du bot)
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("Le token Telegram est introuvable dans le fichier .env")

# Configuration des logs pour suivre les erreurs/info
logging.basicConfig(level=logging.INFO)

# Construction de l'application Telegram avec le token
app = ApplicationBuilder().token(TOKEN).build()

# ----------------- Définition des Handlers et Fonctions principales -----------------

# Handler pour la commande /start ou le bouton "start"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Création d’un clavier avec les langues disponibles
    keyboard = [
        [InlineKeyboardButton(name, callback_data=code)]
        for code, name in languages.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Affichage selon le type de mise à jour (message ou callback)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("👅 :", reply_markup=reply_markup)
    elif update.message:
        await update.message.reply_text("👅 :", reply_markup=reply_markup)

# Handler appelé après le choix de la langue
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang_code = query.data
    context.user_data["lang"] = lang_code  # Stocke la langue choisie

    welcome = welcome_texts[lang_code]
    question = who_are_you_texts[lang_code]

    await query.edit_message_text(f"{welcome}\n\n{question}")

# Handler quand l'utilisateur clique sur "Donner un prix"
async def handle_propose_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fr")
    context.user_data["awaiting_price_proposal"] = True  # Attend une entrée texte (le prix)
    prompt = ask_price_messages["propose_price_prompt"].get(lang, ask_price_messages["propose_price_prompt"]["fr"])

    await query.edit_message_text(prompt)
    return
    
async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Cas où l'on attend un prix
    if context.user_data.get("awaiting_price_proposal"):
        try:
            prix = float(update.message.text)
            context.user_data["awaiting_price_proposal"] = False
            await update.message.reply_text(
                f"Merci pour votre proposition de {prix:.2f} DH. Nous allons l'étudier et vous contacter."
            )
        except ValueError:
            await update.message.reply_text("❗ Veuillez entrer un montant valide.")
        return

    # Cas où l'on attend un numéro de téléphone
    if context.user_data.get("awaiting_phone_number"):
        phone_number = update.message.text.strip()
        if phone_number.isdigit() and 8 <= len(phone_number) <= 15:
            context.user_data["phone_number"] = phone_number
            context.user_data["awaiting_phone_number"] = False
            await update.message.reply_text("✅ Merci, votre numéro a bien été enregistré.")

            # Affichage du menu uniquement maintenant
            lang = context.user_data.get("lang", "fr")
            keyboard = [
                [InlineKeyboardButton(produits_text["villa"][lang], callback_data="villa")],
                [InlineKeyboardButton(produits_text["garage"][lang], callback_data="garage")],
                [InlineKeyboardButton(produits_text["terrain1"][lang], callback_data="terrain1")],
                [InlineKeyboardButton(produits_text["terrain2"][lang], callback_data="terrain2")],
                [InlineKeyboardButton(produits_text["terrain3"][lang], callback_data="terrain3")],
                [InlineKeyboardButton(
                    revmenlang_texts.get(lang, revmenlang_texts["fr"]),
                    callback_data="start"
                )]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Veuillez choisir un Bien :", reply_markup=reply_markup)
        else:
            await update.message.reply_text("❗ Numéro invalide. Veuillez entrer un numéro de téléphone valide (8 à 15 chiffres).")
        return

    # Sinon, on suppose que c’est le nom de l’utilisateur
    lang = context.user_data.get("lang", "fr")
    name = update.message.text.strip()
    context.user_data["name"] = name

    thank_you = thank_you_texts.get(lang, thank_you_texts["fr"])
    await update.message.reply_text(f"{thank_you} {name} !")

    # → On demande le numéro maintenant, le menu sera affiché ensuite
    await update.message.reply_text("📞 Veuillez maintenant entrer votre numéro de téléphone :")
    context.user_data["awaiting_phone_number"] = True

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "fr")
    message = choixproduit_text.get(lang, "Veuillez choisir un Bien.")

    keyboard = [
        [InlineKeyboardButton(produits_text["villa"][lang], callback_data="villa")],
        [InlineKeyboardButton(produits_text["garage"][lang], callback_data="garage")],
        [InlineKeyboardButton(produits_text["terrain1"][lang], callback_data="terrain1")],
        [InlineKeyboardButton(produits_text["terrain2"][lang], callback_data="terrain2")],
        [InlineKeyboardButton(produits_text["terrain3"][lang], callback_data="terrain3")],
        [InlineKeyboardButton(
            revmenlang_texts.get(lang, revmenlang_texts["fr"]),
            callback_data="start"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
        
# Handler pour revenir au menu principal
async def handle_return_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Bouton 'Revenir Au Menu' cliqué")
    query = update.callback_query
    await query.answer()
    await menu(update, context)

# Handler quand l’utilisateur choisit un produit (villa, garage, terrain...)
async def handle_product_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product = query.data
    lang = context.user_data.get("lang", "fr")

    # Récupération des détails du produit
    choix_text = choixdproduit_text.get(lang, choixdproduit_text["fr"])
    product_label = produits_text.get(product, {}).get(lang, product)
    details = property_details.get(product, {})

    # Données spécifiques au bien
    title = details.get("title", {}).get(lang, "N/A")
    description = details.get("description", {}).get(lang, "N/A")
    address = details.get("address", {}).get(lang, "N/A")
    surface = details.get("surface", {}).get(lang, "N/A")
    location = details.get("location", {}).get(lang, "N/A")
    photo_link = details.get("photo_link", {}).get(lang, "N/A")
    video_link = details.get("video_link", {}).get(lang, "N/A")
    price = details.get("price", {}).get(lang, "N/A")

    # Création de la réponse
    message = (
        f"{choix_text} {product_label}.\n\n"
        f"{property_fields['📝 title'][lang]}: {title}\n"
        f"{property_fields['🗒️ description'][lang]}: {description}\n"
        f"{property_fields['🏠 address'][lang]}: {address}\n"
        f"{property_fields['📏 surface'][lang]}: {surface}\n"
        f"{property_fields['📍 Géolocalisation'][lang]}: {location}\n"
        f"{property_fields['💰 price'][lang]}: {price}\n"
        f"{property_fields['📸 Photo_link'][lang]}: {photo_link}\n"
        f"{property_fields['🎥 video_link'][lang]}: {video_link}\n"
    )

    # Affichage du message avec un petit délai
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(0)
    await query.edit_message_text(message)
    await asyncio.sleep(0)

    # Affichage des options après visualisation du produit
    reply_markup = InlineKeyboardMarkup([
        # [InlineKeyboardButton("✅ Donner un prix en : ( 🇲🇦💰 Dirham marocain ) ", callback_data="propose_price")],
        [InlineKeyboardButton(
            f"✅ {Popospri_texts.get(lang, Popospri_texts['fr'])} {monnaie_texts.get(lang, monnaie_texts['fr'])}",
            callback_data="propose_price")],
        [InlineKeyboardButton(revmenbien_texts.get(lang, revmenbien_texts["fr"]), callback_data="menu")]
    ])
    await query.edit_message_reply_markup(reply_markup=reply_markup)

# Affiche le menu des biens à tout moment

# ----------------- Enregistrement des Handlers -----------------
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CallbackQueryHandler(set_language, pattern="^(" + "|".join(languages.keys()) + ")$"))
app.add_handler(CallbackQueryHandler(handle_propose_price, pattern="^propose_price$"))
app.add_handler(CallbackQueryHandler(handle_return_to_menu, pattern="^menu$"))
app.add_handler(CallbackQueryHandler(handle_product_selection, pattern="^(villa|garage|terrain1|terrain2|terrain3)$"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))
app.add_handler(CallbackQueryHandler(start, pattern="^start$"))  # Redémarre depuis le début

# ----------------- Démarrage du Bot -----------------
if __name__ == "__main__":
    keep_alive()  # Lance Flask dans un thread pour maintenir le bot actif
    app.run_polling()  # Démarre le bot Telegram en mode polling
    
