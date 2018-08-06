# robo Telegram para geração do pedido
from pprint import pprint
import os
import logging
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, ParseMode
from telegram.ext import (Updater, CommandHandler, ConversationHandler,
    MessageHandler, Filters)
from order_class import Order

logger = logging.getLogger(__name__)

CUSTOMER, ITEM = range(2)

global UPD, ACCESS, TOKEN, PORT


def open_order(bot, update):
    try:
        user = update.message.from_user
        update.message.reply_text('Olá %s, por favor informe o cliente:' %
        user.first_name)
        return CUSTOMER
    except Exception as e:
        pprint("Método: {}-Erro: {}".format(open_order.__name__, str(e)))


def customer_name(bot, update, user_data):
    try:
        pprint(user_data)
        user_data["customer"] = update.message.text
        user_data["product"] = list()
        update.message.reply_text('O que venderemos para %s hoje?' %
        user_data["customer"])
        return ITEM
    except Exception as e:
        pprint("Método: {}-Erro: {}".format(customer_name.__name__, str(e)))


def list_products(bot, update, user_data):
    try:
        pprint(user_data)
        items = list(update.message.text.split("\n"))
        texto = "`Prod.: {}\nQtd..: {} Preço: {}`\n"
        texto = texto.format(items[0],
                             items[1].rjust(5),
                             items[2].rjust(12))
        texto += "\n\nSe houver mais produtos..."
        update.message.reply_text(texto,
        parse_mode=ParseMode.MARKDOWN)
        user_data["product"].append({"produto": items[0],
            "qtd": items[1],
            "unit": items[2]})
        return ITEM
    except Exception as e:
        pprint("Método: {}-Erro: {}".format(customer_name.__name__, str(e)))


def close_order(bot, update, user_data):
    try:
        user = update.message.from_user
        logger.info("User %s closed the conversation.", user.first_name)
        msg = "Resumo do Pedido para {}:\n"
        msg += "Items: \n"
        msg += "`Produto Qtd Item`\n"
        frmt = "`{}{}{}`\n"
        items = ""
        for p in user_data["product"]:
            items += frmt.format(p["produto"],
                p["qtd"],
                p["unit"])
        msg += items
        update.message.reply_text(msg.format(user_data["customer"]) +
        "\n\nPedido fechado!",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.MARKDOWN)
        return ConversationHandler.END
    except Exception as e:
        pprint("Método: {}-Erro: {}".format(close_order.__name__, str(e)))


if (__name__ == "__main__"):
    try:
        log_txt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logging.basicConfig(format=log_txt, level=logging.INFO)

        ACCESS = os.environ["TELEGRAM_SERVER"]
        TOKEN = os.environ["TELEGRAM_TOKEN"]
        PORT = int(os.environ.get("PORT", os.environ["TELEGRAM_PORT"]))
        UPD = Updater(TOKEN)

        dp = UPD.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('pedido', open_order)],
            states={
                CUSTOMER: [MessageHandler(Filters.text,
                customer_name,
                pass_user_data=True)],
                ITEM: [MessageHandler(Filters.text,
                list_products,
                pass_user_data=True)]
                },
            fallbacks=[CommandHandler('fechar',
            close_order,
            pass_user_data=True)]
            )

        dp.add_handler(conv_handler)

        if (ACCESS == "HEROKU"):
            HEROKU_URL = os.environ["HEROKU_URL"]
            UPD.start_webhook(listen="0.0.0.0",
                port=PORT,
                url_path=TOKEN)
            UPD.bot.set_webhook(HEROKU_URL + TOKEN)
        else:
            UPD.start_polling()

        UPD.idle()

    except Exception as e:
        pprint("Método: {}-Erro: {}".format("main", str(e)))