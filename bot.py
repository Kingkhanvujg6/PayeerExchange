from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    PicklePersistence
)
import random
import re

ADMIN_ID = 5520150248
PAYEER_ID = "P1096497903"
REVIEW_CHANNEL_ID = -1002837544941
TOKEN = "7860645618:AAEOAvgC3iA9zZQs2MfbDPCpafgM-2fIDbo"
COMMUNITY_LINK = "https://t.me/PayeerExchange2"
REVIEWS_LINK = "https://t.me/PayeerExchangeReviews2"

# Initialize persistence
persistence = PicklePersistence(filepath='user_data')
app = ApplicationBuilder().token(TOKEN).persistence(persistence).build()

main_keyboard_buttons = [
    [KeyboardButton("/start")],
    [KeyboardButton("💵 Sell"), KeyboardButton("📈 Rates")],
    [KeyboardButton("🎟️ My Tickets"), KeyboardButton("👥 Referrals")],
    [KeyboardButton("🌐 Community"), KeyboardButton("⭐ Reviews")],
    [KeyboardButton("🆘 Help")]
]
main_keyboard_markup = ReplyKeyboardMarkup(main_keyboard_buttons, resize_keyboard=True, one_time_keyboard=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Initialize all data structures if they don't exist
    if 'all_users' not in context.bot_data:
        context.bot_data['all_users'] = set()
    if 'pending_users' not in context.bot_data:
        context.bot_data['pending_users'] = {}
    if 'pending_reviews' not in context.bot_data:
        context.bot_data['pending_reviews'] = {}
    if 'user_data' not in context.bot_data:
        context.bot_data['user_data'] = {}
    if 'referral_codes' not in context.bot_data:
        context.bot_data['referral_codes'] = {}
    
    # Initialize user data if it doesn't exist or is missing the new field
    if user_id not in context.bot_data['user_data']:
        context.bot_data['user_data'][user_id] = {
            'tickets': 0,
            'referrals': 0,
            'referral_code': f"ref_{user_id}",
            'referred_by': None,
            'has_joined_community': False
        }
        context.bot_data['referral_codes'][f"ref_{user_id}"] = user_id
    else:
        # Ensure existing users have the new field
        if 'has_joined_community' not in context.bot_data['user_data'][user_id]:
            context.bot_data['user_data'][user_id]['has_joined_community'] = False
    
    # Check if user was referred
    if context.args and context.args[0].startswith('ref_'):
        referral_code = context.args[0]
        if referral_code in context.bot_data['referral_codes'] and context.bot_data['referral_codes'][referral_code] != user_id:
            referrer_id = context.bot_data['referral_codes'][referral_code]
            context.bot_data['user_data'][user_id]['referred_by'] = referrer_id
            context.bot_data['user_data'][referrer_id]['referrals'] += 1
    
    context.bot_data['all_users'].add(user_id)

    # Check if user has joined the community
    try:
        member = await context.bot.get_chat_member(chat_id="@PayeerExchange2", user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            context.bot_data['user_data'][user_id]['has_joined_community'] = True
            await update.message.reply_text("👋 Welcome! to Our Exchange Bot. Choose an option below:", reply_markup=main_keyboard_markup)
            return
    except Exception as e:
        print(f"Error checking community membership: {e}")

    # If user is not in the group or an error occurred, show the join message
    keyboard = [
        [InlineKeyboardButton("✅ Join Community", url=COMMUNITY_LINK)],
        [InlineKeyboardButton("✅ I've Joined", callback_data="check_community")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome! Please join our community first to continue:\n\n"
        f"👉 {COMMUNITY_LINK}\n\n"
        "After joining, click the button below to continue.",
        reply_markup=reply_markup
    )
    
async def check_community_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Ensure user data exists with the required field
    if user_id not in context.bot_data.get('user_data', {}):
        context.bot_data['user_data'][user_id] = {
            'tickets': 0,
            'referrals': 0,
            'referral_code': f"ref_{user_id}",
            'referred_by': None,
            'has_joined_community': False
        }
    
    try:
        # Check if user is a member of the community
        member = await context.bot.get_chat_member(chat_id="@PayeerExchange2", user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            context.bot_data['user_data'][user_id]['has_joined_community'] = True
            
            # Show main menu
            await query.edit_message_text("✅ Thanks for joining! Choose an option below:")
            await context.bot.send_message(
                chat_id=user_id,
                text="Main Menu:",
                reply_markup=main_keyboard_markup
            )
        else:
            await query.answer("Please join the community first.", show_alert=True)
    except Exception as e:
        print(f"Error checking community membership: {e}")
        await query.answer("Error verifying your membership. Please try again.", show_alert=True)

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # Check if user has joined community
    if user_id not in context.bot_data.get('user_data', {}) or not context.bot_data['user_data'][user_id].get('has_joined_community', False):
        await update.message.reply_text("Please join our community first using /start", reply_markup=ReplyKeyboardRemove())
        return

    if text == "💵 Sell":
        keyboard = [
            [InlineKeyboardButton("💵 Sell Dollar", callback_data="sell_dollar")],
            [InlineKeyboardButton("💶 Sell Ruble", callback_data="sell_ruble")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Choose a currency to sell:", reply_markup=reply_markup)
    
    elif text == "📈 Rates":
        await update.message.reply_text(
            "📊 Current Rates:\n\n"
            "1 USD = 255 PKR\n"
            "1 RUB = 2.8 PKR\n"
            "Minimum: 1 USD or 100 RUB"
        )
    
    elif text == "🎟️ My Tickets":
        ticket_count = context.bot_data['user_data'][user_id]['tickets']
        await update.message.reply_text(f"🎟️ You have {ticket_count} tickets")
        
    elif text == "👥 Referrals":
        user_data = context.bot_data['user_data'][user_id]
        referral_count = user_data['referrals']
        ticket_count = user_data['tickets']
        referral_link = f"https://t.me/{(await context.bot.get_me()).username}?start={user_data['referral_code']}"
        
        message = (
            f"👥 Your Referrals:\n\n"
            f"• Total Referrals: {referral_count}\n"
            f"• Tickets Earned: {ticket_count}\n\n"
            f"Share your referral link:\n{referral_link}"
        )
        await update.message.reply_text(message)
    
    elif text == "🌐 Community":
        await update.message.reply_text(f"Join our community: {COMMUNITY_LINK}")

    elif text == "⭐ Reviews":
        await update.message.reply_text(f"Read reviews from other users: {REVIEWS_LINK}")
        
    elif text == "🆘 Help":
        await update.message.reply_text(
            "🆘 Help Guide:\n\n"
            "1. Tap on 'Sell Dollar' or 'Sell Ruble'\n"
            "2. Send Payeer to the ID\n"
            "3. Send screenshot with details\n"
            "4. Wait for review (24 hrs to 48 hrs max)\n\n"
            "🎟️ Ticket System:\n"
            "- Refer friends using your referral link\n"
            "- Earn 1 ticket for every $1 your referrals sell\n"
            "- More tickets = higher chance to win prizes!"
        )
    elif text is not None and context.user_data.get("awaiting_review"):
        context.user_data["awaiting_review"] = False
        review_text = update.message.text
        user = update.message.from_user
        
        context.bot_data['pending_reviews'][user.id] = review_text

        await update.message.reply_text("✅ Thanks for your feedback — we really appreciate your review!")

        buttons = [
            [
                InlineKeyboardButton("✅ Approve Review", callback_data=f"approve_review_{user.id}"),
                InlineKeyboardButton("❌ Reject Review", callback_data=f"reject_review_{user.id}")
            ]
        ]
        username = f"@{user.username}" if user.username else f"User ID: {user.id}"
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 New Review from {username}:\n\n{review_text}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 This command is only for admins.")
        return
    
    # Ensure all data structures exist before counting
    all_users = context.bot_data.get('all_users', set())
    pending_users = context.bot_data.get('pending_users', {})
    pending_reviews = context.bot_data.get('pending_reviews', {})
    
    stats_msg = (
        f"📊 Bot Statistics:\n\n"
        f"• Total Users: {len(all_users)}\n"
        f"• Pending Payments: {len(pending_users)}\n"
        f"• Pending Reviews: {len(pending_reviews)}"
    )
    await update.message.reply_text(stats_msg)

async def top_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 This command is only for admins.")
        return

    user_data = context.bot_data.get('user_data', {})
    
    # Sort users by tickets in descending order
    sorted_users = sorted(user_data.items(), key=lambda item: item[1]['tickets'], reverse=True)
    
    if not sorted_users or sorted_users[0][1]['tickets'] == 0:
        await update.message.reply_text("No users have tickets yet.")
        return

    message = "🏆 Top Users by Tickets:\n\n"
    for i, (user_id, data) in enumerate(sorted_users[:10]):  # Show top 10 users
        try:
            user = await context.bot.get_chat(user_id)
            username = user.username or user.first_name
            message += f"{i+1}. {username} - {data['tickets']} tickets\n"
        except Exception:
            # Handle cases where user details can't be fetched
            message += f"{i+1}. User ID: {user_id} - {data['tickets']} tickets\n"
    
    await update.message.reply_text(message)

async def broadcast_text_usage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 This command is only for admins.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /broadcast Your message here\n\nOr send a photo/video with /broadcast in the caption.")
        return
    
    message_text = " ".join(context.args)
    total = 0
    failed = 0
    
    # Get all users from persistent storage
    all_users = list(context.bot_data.get('all_users', set()))
    
    for user_id in all_users:
        try:
            await context.bot.send_message(chat_id=user_id, text=f"📢 Announcement:\n\n{message_text}")
            total += 1
        except Exception as e:
            print(f"Failed to send to {user_id}: {e}")
            failed += 1
            # Remove inactive users
            context.bot_data['all_users'].discard(user_id)
    
    await update.message.reply_text(f"📢 Broadcast Results:\n• Sent: {total}\n• Failed: {failed}")

async def broadcast_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 This command is only for admins.")
        return

    message = update.effective_message
    caption = message.caption if message.caption else ""
    
    if not caption.startswith('/broadcast'):
        return

    # Remove the command from the caption
    caption_text = caption.replace('/broadcast', '').strip()

    total = 0
    failed = 0
    all_users = list(context.bot_data.get('all_users', set()))

    for user_id in all_users:
        try:
            if message.photo:
                await context.bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=caption_text)
            elif message.video:
                await context.bot.send_video(chat_id=user_id, video=message.video.file_id, caption=caption_text)
            total += 1
        except Exception as e:
            print(f"Failed to send to {user_id}: {e}")
            failed += 1
            context.bot_data['all_users'].discard(user_id)

    await update.message.reply_text(f"📢 Media Broadcast Results:\n• Sent: {total}\n• Failed: {failed}")

async def pick_winner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 This command is only for admins.")
        return
    
    # Get all users with tickets
    users_with_tickets = []
    for user_id, user_data in context.bot_data.get('user_data', {}).items():
        if user_data['tickets'] > 0:
            users_with_tickets.append((user_id, user_data['tickets']))
    
    if not users_with_tickets:
        await update.message.reply_text("No users with tickets found.")
        return
    
    # Create weighted list for random selection
    weighted_list = []
    for user_id, tickets in users_with_tickets:
        weighted_list.extend([user_id] * tickets)
    
    # Pick a random winner
    winner_id = random.choice(weighted_list)
    
    # Reset all tickets to zero
    for user_id in context.bot_data.get('user_data', {}):
        context.bot_data['user_data'][user_id]['tickets'] = 0
    
    try:
        winner_user = await context.bot.get_chat(winner_id)
        winner_name = winner_user.username or winner_user.first_name or "Unknown"
        await update.message.reply_text(f"🎉 Winner selected: @{winner_name} (ID: {winner_id})")
        
        # Notify the winner
        await context.bot.send_message(
            chat_id=winner_id,
            text="🎉 Congratulations! You've won the referral contest!"
        )
    except Exception as e:
        await update.message.reply_text(f"Winner ID: {winner_id}, but couldn't fetch details: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    
    if query.data == "sell_dollar":
        # Check if user has joined community
        if user_id not in context.bot_data.get('user_data', {}) or not context.bot_data['user_data'][user_id].get('has_joined_community', False):
            await query.answer("Please join our community first using /start", show_alert=True)
            return
            
        context.user_data['selling_currency'] = 'usd'
        await query.edit_message_text(
            f"💵 Send your Payeer USD to this ID: `{PAYEER_ID}`\n\n"
            "Then send a screenshot with caption:\n"
            "`Name: Account Name`\n"
            "`Amount: $X USD`\n"
            "`Payment Method: Easypaisa or JazzCash`\n"
            "`Number: 0300*******`",
            parse_mode="Markdown"
        )
    elif query.data == "sell_ruble":
        # Check if user has joined community
        if user_id not in context.bot_data.get('user_data', {}) or not context.bot_data['user_data'][user_id].get('has_joined_community', False):
            await query.answer("Please join our community first using /start", show_alert=True)
            return
            
        context.user_data['selling_currency'] = 'rub'
        await query.edit_message_text(
            f"💶 Send your Payeer RUB to this ID: `{PAYEER_ID}`\n\n"
            "Then send a screenshot with caption:\n"
            "`Name: Account Name`\n"
            "`Amount: X RUB`\n"
            "`Payment Method: Easypaisa or JazzCash`\n"
            "`Number: 0300*******`",
            parse_mode="Markdown"
        )

async def handle_payment_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check if user has joined community
    if user_id not in context.bot_data.get('user_data', {}) or not context.bot_data['user_data'][user_id].get('has_joined_community', False):
        await update.message.reply_text("Please join our community first using /start")
        return
        
    message = update.message
    if not message.photo or not message.caption:
        await message.reply_text("⚠️ Please send a payment screenshot with all required details in the caption.")
        return

    caption = message.caption
    
    # Regex to extract amount and currency from the caption
    match = re.search(r'Amount:\s*[\$]?\s*(\d+(?:\.\d+)?)\s*(?:(USD|usd|\$|dollars)|(RUB|руб|ruble|Ruble))?', caption, re.IGNORECASE)

    if not match:
        await message.reply_text(
            "⚠️ **Wrong format!** Please use the correct format:\n\n"
            "`Name: Account Name`\n"
            "`Amount: $X` or `Amount: X RUB`\n"
            "`Payment Method: Easypaisa or JazzCash`\n"
            "`Number: 0300*******`",
            parse_mode="Markdown"
        )
        return

    amount_str = match.group(1)
    currency_from_caption = match.group(2) or match.group(3)
    
    # Now check if the currency from the caption matches the one stored in user_data
    stored_currency = context.user_data.get('selling_currency')

    # If the user has not selected a currency from the inline buttons, or if the caption currency doesn't match the selection, reject it.
    if not stored_currency:
        await message.reply_text("❌ Please select a currency to sell using the inline buttons first.")
        return
    
    if stored_currency == 'usd' and not (currency_from_caption and re.search(r'(USD|usd|\$|dollars)', currency_from_caption, re.IGNORECASE)):
        await message.reply_text("❌ You selected **Dollar** but the caption does not mention USD. Please try again with the correct caption format.")
        return
        
    if stored_currency == 'rub' and not (currency_from_caption and re.search(r'(RUB|руб|ruble)', currency_from_caption, re.IGNORECASE)):
        await message.reply_text("❌ You selected **Rubble** but the caption does not mention RUB. Please try again with the correct caption format.")
        return

    context.bot_data['pending_users'][user_id] = {
        'message_id': message.message_id,
        'caption': caption,
        'currency': stored_currency
    }

    buttons = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    username = f"@{message.from_user.username}" if message.from_user.username else f"User ID: {user_id}"
    admin_caption = f"📥 Payment Request from {username}\n"
    admin_caption += f"\n{caption}"

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=admin_caption,
        reply_markup=reply_markup
    )
    
    await message.reply_text("✅ Payment received and under review. Please wait for confirmation.")

async def admin_inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("approve_"):
        _, user_id_str = data.split('_')
        user_id = int(user_id_str)
        
        # Check if user is in pending list
        if user_id not in context.bot_data.get('pending_users', {}):
            await query.edit_message_caption(caption="Error: Payment details not found.")
            return

        # Get currency from pending data
        pending_data = context.bot_data['pending_users'][user_id]
        caption = pending_data['caption']
        currency = pending_data['currency']
        
        amount_match = re.search(r'Amount:\s*[\$]?\s*(\d+(?:\.\d+)?)', caption, re.IGNORECASE)
        amount = 0
        
        if amount_match:
            amount_value = float(amount_match.group(1))
            if currency == 'usd':
                amount = int(amount_value)
            elif currency == 'rub':
                amount = int(amount_value / 100)
        
        # Check if user was referred and award tickets to referrer
        if user_id in context.bot_data.get('user_data', {}) and context.bot_data['user_data'][user_id].get('referred_by'):
            referrer_id = context.bot_data['user_data'][user_id]['referred_by']
            if referrer_id in context.bot_data.get('user_data', {}):
                context.bot_data['user_data'][referrer_id]['tickets'] += amount
                
                # Notify referrer
                try:
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text=f"🎉 Your referral sold — You earned {amount} ticket(s) 🎟️. Total: {context.bot_data['user_data'][referrer_id]['tickets']} tickets."
                    )
                except:
                    pass  # Silently fail if we can't notify the referrer

        await context.bot.send_message(chat_id=user_id, text="🎉 Payment confirmed and processed successfully!")
        
        review_buttons = [[InlineKeyboardButton("✍️ Must Give a Review", callback_data=f"review_{user_id}")]]
        await context.bot.send_message(
            chat_id=user_id, 
            text="Tap below If you've used the bot and found it helpful, please leave a review. Your feedback means a lot to us and helps us improve even more:", 
            reply_markup=InlineKeyboardMarkup(review_buttons)
        )
        
        # Remove from pending after approval
        del context.bot_data['pending_users'][user_id]
        if 'selling_currency' in context.user_data:
            del context.user_data['selling_currency']
        
        await query.edit_message_caption(caption="✅ Payment Approved")

    elif data.startswith("reject_"):
        _, user_id_str = data.split('_')
        user_id = int(user_id_str)

        # Remove from pending after rejection
        if user_id in context.bot_data['pending_users']:
            del context.bot_data['pending_users'][user_id]
        if 'selling_currency' in context.user_data:
            del context.user_data['selling_currency']
        
        await context.bot.send_message(
            chat_id=user_id, 
            text="❌ Payment rejected. Please ensure:\n\n"
                 "1. All details are correct\n"
                 "2. Screenshot is clear\n"
                 "3. Amount matches your transfer\n"
                 "Resend with correct information and try Again, or contact support for assistance at payeerexchange2@gmail.com. We typically respond within 24 to 48 hours"
        )
        
        await query.edit_message_caption(caption="❌ Payment Rejected")

async def collect_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["awaiting_review"] = True
    await query.edit_message_text("📝 Please write your review and send it as a text message:")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_review"):
        context.user_data["awaiting_review"] = False
        review_text = update.message.text
        user = update.message.from_user
        
        context.bot_data['pending_reviews'][user.id] = review_text

        await update.message.reply_text("✅ Thanks for your feedback — we really appreciate your review!")

        buttons = [
            [
                InlineKeyboardButton("✅ Approve Review", callback_data=f"approve_review_{user.id}"),
                InlineKeyboardButton("❌ Reject Review", callback_data=f"reject_review_{user.id}")
            ]
        ]
        username = f"@{user.username}" if user.username else f"User ID: {user.id}"
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 New Review from {username}:\n\n{review_text}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

async def handle_review_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("approve_review_") or data.startswith("reject_review_"):
        action, _, user_id = data.partition("review_")
        user_id = int(user_id)

        if user_id in context.bot_data['pending_reviews']:
            review_text = context.bot_data['pending_reviews'].pop(user_id)
            if action == "approve_":
                await context.bot.send_message(
                    chat_id=REVIEW_CHANNEL_ID,
                    text=f"🌟 User Review:\n\n{review_text}"
                )
                await query.edit_message_text("✅ Review published successfully!")
            else:
                await query.edit_message_text("❌ Review rejected.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

if __name__ == "__main__":
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast_text_usage))
    app.add_handler(CommandHandler("pick_winner", pick_winner))
    app.add_handler(CommandHandler("top_users", top_users))
    
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(sell_dollar|sell_ruble|check_community)$"))
    app.add_handler(CallbackQueryHandler(admin_inline_handler, pattern="^(approve_|reject_)[0-9]+$"))
    app.add_handler(CallbackQueryHandler(collect_review, pattern="^review_[0-9]+$"))
    app.add_handler(CallbackQueryHandler(handle_review_approval, pattern="^(approve_review_|reject_review_)[0-9]+$"))
    
    # Message handlers
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_main_menu))
    app.add_handler(MessageHandler(filters.PHOTO & filters.CAPTION & filters.User(ADMIN_ID), broadcast_media))
    app.add_handler(MessageHandler(filters.VIDEO & filters.CAPTION & filters.User(ADMIN_ID), broadcast_media))
    app.add_handler(MessageHandler(filters.PHOTO & filters.CAPTION, handle_payment_details))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    print("🤖 Bot is running with Referral + Ticket System...")
    app.run_polling()
