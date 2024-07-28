import os
import pandas as pd
import asyncio
import yfinance as yf
from dotenv import load_dotenv
from telegram import Update 
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import signal

# Load environment variables from .env file
load_dotenv(dotenv_path="config.env")

# Load secrets 
TOKEN = os.getenv('TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME')

# Ensure an event loop is available
try:
    loop = asyncio.get_running_loop()
except RuntimeError:  # no event loop currently running
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Function to handle shutdown signals
def shutdown():
    for task in asyncio.all_tasks(loop):
        task.cancel()
    loop.stop()

# Register signal handlers
signal.signal(signal.SIGINT, lambda s, f: shutdown())
signal.signal(signal.SIGTERM, lambda s, f: shutdown())

# Dummy HTTP Server for Health Check
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'OK')

def run_http_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    httpd.serve_forever()

# Start the dummy HTTP server in a separate thread
http_thread = threading.Thread(target=run_http_server)
http_thread.daemon = True
http_thread.start()


# ------------------------------------------------------------------------------------------#
# Commands
# ------------------------------------------------------------------------------------------#

# Start command to send a welcome message
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Thank you for chatting with me! I am an origami that changes imperial units to metric units! :)')

# Help command to provide a list of available commands
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('''
                                    
          The following commands are available:
                                    
          /start -> Welcome Message
          /help -> This message
          /feet -> Convert feet to cm
          /inches -> Convert inches to cm
          /miles -> Convert miles to km
          /pounds -> Convert pounds to kg and g
          /founce -> Convert fluid ounce to L and mL
          /ounce -> Convert ounce to kg and g
          /cup -> Convert cup to mL
          /gallon -> Convert gallon to L
          /fahrenheit -> Convert Fahrenheit to Celcius
                                    ''')


# Command functions to provide a brief message about the conversions they handle
async def feet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I can count feets to centimetres!')

async def inches_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I can change inches to centimetres!')

async def miles_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I can change miles to kilometres!')

async def pounds_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I can convert pounds to kilograms and grams.')

async def founce_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I can convert fluid ounce to liters and milliliters.')

async def ounce_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I can convert ounce to kilograms and grams.')

async def cup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I can convert cup to milliliters.')

async def gallon_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I can convert gallon(s) to liters.')

async def fahrenheit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I can convert Fahrenheit to Celcius.')

# async def currencies_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text('I can fetch Malaysian Ringgit, U.S Dollars, Japan Yen, HK Dollars, and Australian Dollars relative to 1 SG Dollar.')

# Currency Command Handler
async def currencies_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    currencies = get_currencies()
    if isinstance(currencies, str):
        await update.message.reply_text(currencies)
    else:
        result_message = "Currency Information:\n\n" + '\n'.join(currencies)
        await update.message.reply_text(result_message)

# ------------------------------------------------------------------------------------------#
# Responses
# ------------------------------------------------------------------------------------------#

# Function to handle simple text responses
def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hey There fellow dinosaur!'
    
    if 'how are you' in processed:
        return 'I am good! How are you?'
    
    return 'I do not understand what you wrote...'

# Fetch currency data from yfinance
def get_currencies():
    try :
        currencies = ['SGDMYR=X', 'SGDUSD=X', 'SGDJPY=X', 'SGDHKD=X', 'SGDAUD=X'] # MYR, USD, JPY, HKD, AUD
        data = yf.download(tickers= currencies, period = '1d')

        latest_currency_data = data['Close'].iloc[-1]
        myr = latest_currency_data['SGDMYR=X'].round(3)
        usd = latest_currency_data['SGDUSD=X'].round(3)
        jpy = latest_currency_data['SGDJPY=X'].round(3)
        hkd = latest_currency_data['SGDHKD=X'].round(3)
        aud = latest_currency_data['SGDAUD=X'].round(3)

        myr_string = f'1 SGD is equal to {myr} RM.'
        usd_string = f'1 SGD is equal to {usd} USD.'
        jpy_string = f'1 SGD is equal to {jpy} YEN.'
        hkd_string = f'1 SGD is equal to {hkd} HKD.'
        aud_string = f'1 SGD is equal to {aud} AUD.'

        return [myr_string, usd_string, jpy_string, hkd_string, aud_string]
    except ValueError:
        return('Please enter a valid number.')

async def currencies_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Call the get_currencies function to obtain the currency information
    currency_info = get_currencies()

    # Prepare the result message
    result_message = 'Currency Information:\n\n' + '\n'.join(currency_info)

    # Send the result back to the user
    await update.message.reply_text(result_message)

# ------------------------------------------------------------------------------------------#
# Conversion Functions
# ------------------------------------------------------------------------------------------#

# Conversion of feet to cm
def feet_to_cm(feet):
    try:
        feet = float(feet)
        if feet >= 0:
            cm = feet * 30.48
            return (f'{feet} feet is approximately {cm:.2f} centimetres.')
        else:
            return 'Please enter a non-negative number of feet.'
    except ValueError:
        return 'Invalid input. Please enter a valid number of feet.'

async def feet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        # Extract the user's input from the command message
        text = update.message.text.split(' ',1)[1] # split by space to remove the /feet command

        # Attempt to convert feet to centimetres
        result = feet_to_cm(text)

        # Send the result back to the user
        await update.message.reply_text(result)

    except IndexError:
        # Handle the case where the user did not input after the /feet command
        await update.message.reply_text('Please provide the number of feet to convert to centimetres.')

# conversion of inches to cm
def inches_to_cm(inch):
    try:
        inch = float(inch)
        if inch >= 0:
            cm = inch * 2.54
            return (f'{inch} inches is approximately {cm} centimetres.')
        else:
            return (f'Please enter a non-negative number of inches.')
        
    except ValueError:
        return 'Invalid input. Please enter a valid number of inches.'

async def inches_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        # Extract the user's input from the command message
        text = update.message.text.split(' ',1)[1] # split by space to remove the /inches command

        # Attempt to convert inches to centimetres
        result = inches_to_cm(text)

        # Send the result back to the user
        await update.message.reply_text(result)

    except IndexError:
        # Handle the case where the user did not input after the /inches command
        await update.message.reply_text('Please provide the number of inches to convert to centimetres.')



# conversion of miles to km
def miles_to_km(miles):
    try:
        miles = float(miles)
        if miles >= 0:
            km = miles * 1.609344
            return(f'{miles} miles is approximately {km} kilometres.')
        else:
            return ('Please enter a non-negative number of miles.')
    except ValueError:
        return 'Invalid input. Please enter a valid number of miles.'
    
async def miles_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    try:
        # Extract the user's input from the command message
        text = update.message.text.split(' ',1)[1] # split by space to remove the /miles command

        # Attempt to convert miles to kilometres
        result = miles_to_km(text)

        # Send the result back to the user
        await update.message.reply_text(result)

    except:
        # Handle the case where the user did not input after the /miles command
        await update.message.reply_text('Please provide the number of miles to convert to kilometres.')

# Conversion of pounds to kg
def pounds_to_kg(pounds):
    try:
        pounds = float(pounds)
        if pounds >= 0:
            kg = pounds * 0.453592
            grams = kg * 1000
            return(f'{pounds} pounds is approximately {kg} kg or {grams} g.')
        else:
            return ('Please enter a non-negative number of pounds.')
    except ValueError:
        return 'Invalid input. Please enter a valid number of pounds.'
    
async def pounds_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        # Extract the user's input from the command message
        text = update.message.text.split(' ',1)[1] # split by space to remove the /pounds command

        # Attempt to convert pounds to kg and g
        result = pounds_to_kg(text)

        # Send the result back to the user
        await update.message.reply_text(result)
    
    except:
        # Handle the case where the user did not input after the /pounds command
        await update.message.reply_text('Please provide the number of pounds to convert to kilograms and grams.')

# Conversion of FLUID OUNCE to milliliters
def f_ounce_to_ml(founce):
    try:
        founce = float(founce)
        if founce >= 0:
            ml = founce * 29.5735
            liter = founce / 1000
            return(f'{founce} fluid ounce(fl.oz) is approximately {liter:.3f} L or {ml:.3f} mL.')
        else:
            return('Please enter a non-negative number of fluid ounce.')
    except ValueError:
        return 'Invalid input. Please enter a valid number of fluid ounce.'

async def founce_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try: 
        # Extract the users input from the command message
        text = update.message.text.split(' ', 1)[1] # split by space to remove the /founce command

        # Attempt to convert fluid ounce to milliters or liters
        result = f_ounce_to_ml(text)

        # Send the result back to the user
        await update.message.reply_text(result)

    except:
        # Handle the case where the user did not input after the /founce command
        await update.message.reply_text('Please provide the number of fluid ounces to convert to liters and milliliters.')

# Conversion of Ounce to grams
def ounce_to_g(ounce):
    try:
        ounce = float(ounce)
        if ounce >= 0:
            grams = ounce * 28.3495
            kilograms = ounce / 35.274

            return(f'{ounce} ounce (oz) is approximately {kilograms:.3f} kg or {grams} g.')
        else:
            return('Please enter a non-negative numbers.')
    except ValueError:
        return 'Invalid input, Please enter a valid number of ounce.'

async def ounce_command(update:Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        # Extract the users input from the command message
        text = update.message.text.split(' ',1)[1] # Split the message and remove /ounce command

        # Attempt to convert ounce to grams
        result = ounce_to_g(text)

        # Send result back to user
        await update.message.reply_text(result)

    except:
        # handle the case where the user did not input after the /ounce command
        await update.message.reply_text('Please provide the number of ounces to convert to kilograms and grams.')
    
# Conversion of cup to milliliters
def cup_to_ml(cup):
    try:
        cup = float(cup)
        if cup >= 0:
            ml = cup * 236.588
            return(f'{cup} cup(s) is approximately {ml} mL.')
        else:
            return('Please enter a non-negative number.')
    except ValueError:
        return 'Invalid input. Please enter a valid number of cup(s).'
    
async def cup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        # Extract the users input from the command message
        text = update.message.text.split(' ',1)[1] # Split the message and remove the /cup command

        # Attempt to convert cup to mL
        result = cup_to_ml(text)

        # Send result back to the user
        await update.message.reply_text(result)
    
    except:
        # Handle the case where the user did not input after the /cup command
        await update.message.reply_text('Please provide the number of cups to convert to milliliters.')

# Conversion of gallon to liters
def gallon_to_l(gallon):
    try:
        gallon = float(gallon)
        if gallon >= 0:
            liters = gallon * 3.78541
            return(f'{gallon} gallon(s) is approximately {liters:.3f} L.')
        else:
            return('Please enter a non-negative numbers.')
    except ValueError:
        return 'Invalid input. Please enter a valid number of gallon(s).'

async def gallon_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        # Extract the users input from the command message
        text = update.message.text.split(' ',1)[1] # Split the message and remove the /gallon command

        # Attempt to convert gallon to liters
        result = gallon_to_l(text)

        # Send results back to the user
        await update.message.reply_text(result)

    except:
        # Handle the case where the user did not input after the /gallon command
        await update.message.reply_text('Please provide the number of gallon(s) to convert to liters')

# Conversion of Fahrenheit to Celcius
def fahrenheit_to_celcius(fahrenheit):
    try:
        fahrenheit = float(fahrenheit)
        celcius = (fahrenheit-32) * 5/9
        return (f'{fahrenheit}°F is approximately {celcius}°C.')
    except ValueError:
        return('Please enter a valid number.')

async def fahrenheit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    try:
        # Extract the users input from the command message
        text = update.message.text.split(' ',1)[1] # Split the message and remove the /fahrenheit command

        # Attempt to convert fahrenheit to celcius
        result = fahrenheit_to_celcius(text)

        # Send results back to the user
        await update.message.reply_text(result)

    except:
        # Handle the case where the user did not input the /fahrenheit command
        await update.message.reply_text('Please provide the temperature in Fahrenheit to convert to Celcius.')
        





# ------------------------------------------------------------------------------------------#
# Handlers
# ------------------------------------------------------------------------------------------#

# Handle incoming messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
    
    print('Bot', response)
    await update.message.reply_text(response)




# Handle errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

# ------------------------------------------------------------------------------------------#
# Main
# ------------------------------------------------------------------------------------------#

if __name__ == '__main__':
    print('starting bot...')

    # Ensure an event loop is available in the Streamlit environment
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # create the application and set up handlers   
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('feet', feet_command))
    app.add_handler(CommandHandler('inches', inches_command))
    app.add_handler(CommandHandler('miles', miles_command))
    app.add_handler(CommandHandler('pounds', pounds_command))
    app.add_handler(CommandHandler('founce', founce_command))
    app.add_handler(CommandHandler('ounce', ounce_command))
    app.add_handler(CommandHandler('cup', cup_command))
    app.add_handler(CommandHandler('gallon', gallon_command))
    app.add_handler(CommandHandler('fahrenheit', fahrenheit_command))
    app.add_handler(CommandHandler('currencies', currencies_command))


    # Messages
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Error
    app.add_error_handler(error)

    loop.run_until_complete(app.initialize())
    loop.create_task(app.start())
    loop.run_forever()

    # Polls the bot
    print('polling...')
    app.run_polling(poll_interval=3)