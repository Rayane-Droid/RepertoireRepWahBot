import asyncio
import csv
import logging
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from telegram.error import BadRequest

from keep_alive import keep_alive, app

from Dictionnaire1 import languages, welcome_texts, who_are_you_texts, thank_you_texts, choixdproduit_text, ask_price_messages, revmenbien_texts, monnaie_texts, Popospri_texts, entrnumtel_texts, mercitel_texts, choixbien_texts, commentaires_texts, montantvalid_texts, numvalid_texts, mercicom_texts, merci_prix_texts, laisecom_texts, choixbiens_texts, paydet_texts, pascompris_texts, choixlangr_texts, choixproduit_text 
#choixlangs_texts,

from Dictionnaire2 import continue_texts, privacy_texts, commandeincon_texts, mesagevide_texts, erreurenrdone_texts, ressayer_texts
from Dictionnaire3 import description_texts
from produits import property_fields, property_details, produits_text

from fonctionne import generate_menu_keyboard

import phonenumbers
from phonenumbers import NumberParseException

import pycountry

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# 01. Start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    keyboard = [[InlineKeyboardButton(name, callback_data=code)]
                for code, name in languages.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text("👅 🌍 :", reply_markup=reply_markup)
        elif update.message:
            await update.message.reply_text("👅 🌍 :", reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
# 02. Language selection handler
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start":
        context.user_data.clear()
        keyboard = [[InlineKeyboardButton(name, callback_data=code)]
                    for code, name in languages.items()]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("👅 🌍 :", reply_markup=reply_markup)
        return

    lang_code = query.data
    context.user_data["lang"] = lang_code
    # New flag to indicate user is at description step
    context.user_data["at_description"] = True

    # Send description message with continue button
    description_msg = description_texts.get(lang_code, description_texts["fr"])

    lang = context.user_data.get("lang", "fr")
    keyboard = [
                [InlineKeyboardButton(continue_texts[lang], callback_data="continue_after_description")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await query.edit_message_text(description_msg, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in set_language handler (description message): {e}")
# 03. Handler after description to send welcome message
async def continue_after_description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_code = context.user_data.get("lang", "fr")
    welcome = welcome_texts.get(lang_code, welcome_texts["fr"])
    question = who_are_you_texts.get(lang_code, who_are_you_texts["fr"])

    # Clear description step flag
    context.user_data["at_description"] = False

    try:
        await query.edit_message_text(f"{welcome}\n\n{question}")
    except Exception as e:
        logger.error(f"Error in continue_after_description_handler: {e}")
# 04. Handle propose price button
async def handle_propose_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if context.user_data is None:
        context.user_data = {}
    lang = context.user_data.get("lang", "fr")
    context.user_data["awaiting_price_proposal"] = True
    prompt = ask_price_messages["propose_price_prompt"].get(lang, ask_price_messages["propose_price_prompt"]["fr"])

    try:
        await query.edit_message_text(prompt)
    except Exception as e:
        logger.error(f"Error in handle_propose_price handler: {e}")
# 05.
async def show_language_menu(update, context):
    keyboard = [[InlineKeyboardButton(name, callback_data=code)] for code, name in languages.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👅 🌍 :", reply_markup=reply_markup)
# 06. Text message handler with enhanced error handling and validation
async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip() if update.message and update.message.text else ""
    lang = context.user_data.get("lang", "fr")

    # Check if user is at description step, if so, redisplay description and ignore text input
    if context.user_data.get("at_description"):
        description_msg = description_texts.get(lang, description_texts["fr"])
        lang = context.user_data.get("lang", "fr")  # Défaut : français
        keyboard = [
            [InlineKeyboardButton(continue_texts[lang], callback_data="continue_after_description")]
]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(description_msg, reply_markup=reply_markup)
        return

    if not text:
        await update.message.reply_text("❗ Message vide. Veuillez entrer un texte.")
        return

    text_lower = text.lower()

    try:
        # Restart conversation
        if text_lower in ["restart", "recommencer", "/start"]:
            context.user_data.clear()
            keyboard = [[InlineKeyboardButton(name, callback_data=code)] for code, name in languages.items()]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("🔄 Conversation réinitialisée. Veuillez choisir une langue.")
            await show_language_menu(update, context)
            return

         # Language not set
        if "lang" not in context.user_data:
            keyboard = [[InlineKeyboardButton(name, callback_data=code)] for code, name in languages.items()]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "🇫🇷\n"
                "❗ Veuillez d'abord sélectionner une langue en cliquant sur un des boutons ci-dessous.\n"
                "🇬🇧\n"
                "❗ Please select a language first by clicking one of the buttons below.\n"
                "🇪🇸\n"
                "❗ Primero seleccione un idioma haciendo clic en uno de los botones a continuación.\n"
                "🇩🇪\n"
                "❗ Bitte wählen Sie zuerst eine Sprache, indem Sie auf einen der untenstehenden Buttons klicken.\n"
                "🇮🇹\n"
                "❗ Seleziona prima una lingua cliccando su uno dei pulsanti qui sotto.\n"
                "🇲🇦\n"
                "❗ يرجى أولاً اختيار لغة بالنقر على أحد الأزرار أدناه."               
            )
            await show_language_menu(update, context)
            context.user_data["menu_langue_affiche"] = True
            return

        # Awaiting proposed price
        if context.user_data.get("awaiting_price_proposal"):
            try:
                prix = float(text.replace(",", "."))
            except ValueError:
                await update.message.reply_text(montantvalid_texts.get(lang, montantvalid_texts["fr"]))
                return
            context.user_data["awaiting_price_proposal"] = False
            context.user_data["proposed_price"] = prix
            message = merci_prix_texts.get(lang, merci_prix_texts["fr"]).format(prix=prix)
            await update.message.reply_text(message)
            context.user_data["awaiting_comment"] = True
            await update.message.reply_text(laisecom_texts.get(lang, laisecom_texts["fr"]))
            return

        # Awaiting comment
        if context.user_data.get("awaiting_comment"):
            context.user_data["awaiting_comment"] = False
            context.user_data["commentaire"] = text

            user_id = update.effective_user.id
            name = context.user_data.get("name", "")
            phone = context.user_data.get("phone_number", "")
            produit = context.user_data.get("produit_choisi", "")
            prix = context.user_data.get("proposed_price", "")
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Save user data to CSV
            try:
                with open("index.csv", mode="a", encoding="utf-8", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([date, user_id, name, phone, produit, prix, text])
            except Exception as e:
                logger.error(f"Error writing to CSV: {e}")
                await update.message.reply_text("❗ Une erreur est survenue lors de l'enregistrement des données.")

            await update.message.reply_text(mercicom_texts.get(lang, mercicom_texts["fr"]))

            keyboard = generate_menu_keyboard(lang)
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(choixbien_texts.get(lang, choixbien_texts["fr"]), reply_markup=reply_markup)
            context.user_data["menu_biens_affiche"] = True
            return

        if context.user_data.get("awaiting_phone_number"):
            raw_phone = text.strip()

            try:
                phone_obj = phonenumbers.parse(raw_phone, "MA")

                if not phonenumbers.is_valid_number(phone_obj):
                    await update.message.reply_text(numvalid_texts.get(lang, numvalid_texts["fr"]))
                    return

                phone_formatted = phonenumbers.format_number(phone_obj, phonenumbers.PhoneNumberFormat.E164)
                country_code = phonenumbers.region_code_for_number(phone_obj)
                country_name = get_country_name(country_code)
                flag_emoji = get_flag_emoji(country_code)

                context.user_data["phone_number"] = phone_formatted
                context.user_data["country_code"] = country_code
                context.user_data["country_name"] = country_name
                context.user_data["awaiting_phone_number"] = False

                await update.message.reply_text(
                f"{mercitel_texts.get(lang, mercitel_texts['fr'])}\n📍 {paydet_texts.get(lang, paydet_texts['fr'])} : {flag_emoji} {country_name}"
                )

                keyboard = generate_menu_keyboard(lang)
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(choixbien_texts.get(lang, choixbien_texts["fr"]), reply_markup=reply_markup)
                context.user_data["menu_biens_affiche"] = True
                return

            except NumberParseException:
                await update.message.reply_text(numvalid_texts.get(lang, numvalid_texts["fr"]))
                return

        # Menu displayed case
        if context.user_data.get("menu_biens_affiche", False):
            await update.message.reply_text(choixbiens_texts.get(lang, choixbiens_texts["fr"]))
            keyboard = generate_menu_keyboard(lang)
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(choixbien_texts.get(lang, choixbien_texts["fr"]), reply_markup=reply_markup)
            return

        # Handling back commands
        if text_lower in ["retour", "back"]:
            if context.user_data.get("awaiting_comment"):
                context.user_data["awaiting_comment"] = False
                context.user_data["awaiting_price_proposal"] = True
                await update.message.reply_text("↩️ Retour à la proposition de prix. Entrez un montant en DH.")
                return
            elif context.user_data.get("awaiting_phone_number"):
                context.user_data["awaiting_phone_number"] = False
                await update.message.reply_text("↩️ Retour à la saisie du nom. Veuillez entrer votre nom.")
                return

        # Assume the input is user's name
        context.user_data["name"] = text
        await update.message.reply_text(f"{thank_you_texts.get(lang, thank_you_texts['fr'])} {text} !")
        await update.message.reply_text(entrnumtel_texts.get(lang, entrnumtel_texts["fr"]))
        context.user_data["awaiting_phone_number"] = True

    except Exception as e:
        logger.error(f"Error in handle_text_messages: {e}")
        await update.message.reply_text("❗ Une erreur est survenue. Veuillez réessayer.")
# 07.
def get_country_name(iso_code):
    try:
        country = pycountry.countries.get(alpha_2=iso_code)
        return country.name if country else iso_code
    except:
        return iso_code
# 08.
def get_flag_emoji(country_code):
    try:
        return ''.join(chr(0x1F1E6 + ord(c.upper()) - ord('A')) for c in country_code)
    except:
        return ''
# 09. Fallback handler for unsupported messages
async def fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "fr")  # récupérer la langue utilisateur (par défaut fr)
    message = pascompris_texts.get(lang, pascompris_texts["fr"])
    try:
        if update.message:
            await update.message.reply_text(message)
        elif update.callback_query:
            await update.callback_query.answer()  # répondre au callback pour éviter le spinner
            await update.callback_query.edit_message_text(message)
    except Exception as e:
        logger.error(f"Error in fallback_handler: {e}")
# 10. Product selection handler
async def handle_product_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product = query.data
    context.user_data["produit_choisi"] = product
    lang = context.user_data.get("lang", "fr")

    choix_text = choixdproduit_text.get(lang, choixdproduit_text["fr"])
    product_label = produits_text.get(product, {}).get(lang, product)
    details = property_details.get(product, {})

    title = details.get("📝 title", {}).get(lang, "N/A")
    description = details.get("🗒️ description", {}).get(lang, "N/A")
    address = details.get("🏠 address", {}).get(lang, "N/A")
    surface = details.get("📏 surface", {}).get(lang, "N/A")
    location = details.get("📍 Géolocalisation", {}).get(lang, "N/A")
    photo_link = details.get("📸 Photo_link", {}).get(lang, "N/A")
    video_link = details.get("🎥 video_link", {}).get(lang, "N/A")
    price = details.get("💰 price", {}).get(lang, "N/A")

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

    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        await query.edit_message_text(message)
    except Exception as e:
        logger.error(f"Error sending product details: {e}")

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"✅ {Popospri_texts.get(lang, Popospri_texts['fr'])} {monnaie_texts.get(lang, monnaie_texts['fr'])}", callback_data="propose_price")],
        [InlineKeyboardButton(revmenbien_texts.get(lang, revmenbien_texts["fr"]), callback_data="menu")]
    ])

    try:
        await query.edit_message_reply_markup(reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error setting reply markup after product selection: {e}")
# 11. Menu handler displays list of products
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "fr")
    message = choixbien_texts.get(lang, choixbien_texts["fr"])  # Utilise le bon dictionnaire
    keyboard = generate_menu_keyboard(lang)
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if update.message:
            await update.message.reply_text(message, reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in menu handler: {e}")
# 12. Handler for returning to menu
async def handle_return_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Bouton 'Revenir Au Menu' cliqué")
    query = update.callback_query
    try:
        if query:
            await query.answer()
    except BadRequest as e:
        logger.warning(f"Erreur dans query.answer() : {e}")

    await menu(update, context)
# 13. Handler for adding comment
async def handle_add_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fr")
    context.user_data["awaiting_comment"] = True

    try:
        await query.edit_message_text(commentaires_texts.get(lang, commentaires_texts["fr"]))
    except Exception as e:
        logger.error(f"Error in handle_add_comment: {e}")
# 14. Handler for unknown commands
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'fr')  # Langue par défaut : français
    msg = commandeincon_texts.get(lang, commandeincon_texts['fr'])
    await update.message.reply_text(msg)
# 15.
async def privacy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "fr")  # Langue par défaut : français
    message = privacy_texts.get(lang, privacy_texts["fr"])
    await update.message.reply_text(message)
# 16. Register handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CallbackQueryHandler(set_language, pattern="^(" + "|".join(languages.keys()) + ")$"))
app.add_handler(CallbackQueryHandler(handle_propose_price, pattern="^propose_price$"))
app.add_handler(CallbackQueryHandler(handle_return_to_menu, pattern="^menu$"))
app.add_handler(CallbackQueryHandler(handle_product_selection, pattern="^(🏡 Villa|🚗 Garage|🌳 Terrain1|🌿 Terrain2|🏞️ Terrain3)$"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))
app.add_handler(CallbackQueryHandler(start, pattern="^start$"))
app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
app.add_handler(MessageHandler(filters.ALL, fallback_handler))
app.add_handler(CallbackQueryHandler(handle_add_comment, pattern="add_comment"))
app.add_handler(CommandHandler("privacy", privacy_command))  # commande /privacy
app.add_handler(CallbackQueryHandler(continue_after_description_handler, pattern="^continue_after_description$"))
app.add_handler(CommandHandler("privacy", privacy_command))
app.add_handler(MessageHandler(filters.COMMAND, unknown_command))




# 17. Main bot entry point
if __name__ == "__main__":
    keep_alive()
    asyncio.run(app.run_polling())
