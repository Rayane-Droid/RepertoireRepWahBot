# Handler pour les messages texte généraux--------€€€€----------------------------------------------------
async def handle_text_messages(update: Update,context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()  # ✅ Cette ligne doit être ici !
    # Cas 1 :  où l'on attend un prix
    if "lang" not in context.user_data:
        await update.message.reply_text(
            "❗ Veuillez d'abord sélectionner une langue en cliquant sur un des boutons ci-dessous.\n\n🔧 Si vous avez besoin d'aide, consultez : https://exemple.com/aide"
        )
        keyboard = [[InlineKeyboardButton(name, callback_data=code)] for code, name in languages.items()]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🌍 Choisissez votre langue :", reply_markup=reply_markup)
        return
    # Cas 1 :  

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
#&&&&&&&&#
    # Fusionne ces deux blocs
    if context.user_data.get("awaiting_comment"):
        commentaire = text
        context.user_data["awaiting_comment"] = False
        context.user_data["commentaire"] = commentaire

        user_id = update.effective_user.id
        name = context.user_data.get("name", "")
        phone = context.user_data.get("phone_number", "")
        produit = context.user_data.get("produit_choisi", "")
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Enregistrement CSV
        with open("index.csv", mode="a", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([user_id, name, phone, produit, date, commentaire])

        await update.message.reply_text("✅ Merci pour votre commentaire !")

        keyboard = generate_menu_keyboard(context.user_data.get("lang", "fr"))
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(choixbien_texts.get(
            context.user_data["lang"], choixbien_texts["fr"]), reply_markup=reply_markup)
        return

    
#&&&&&&&&&#
# Cas où l'on attend un numéro de téléphone
    if context.user_data.get("awaiting_phone_number"):
        phone_number = update.message.text.strip()
        if phone_number.isdigit() and 8 <= len(phone_number) <= 15:
            context.user_data["phone_number"] = phone_number
            context.user_data["awaiting_phone_number"] = False

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
