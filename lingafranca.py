import googletrans as go
import gtts as gt
from playsound import playsound
import speech_recognition as spr
import os
from string import punctuation

tr = go.Translator()
rc = spr.Recognizer()

def printLangs(lang):
    """Print all languages available for the program to use (based on )
    """
    while lang == 'List languages':
        print('Printing all accepted languages...')
        for language in gt.lang.tts_langs().values():
            if language.lower() in go.LANGCODES:print('>',language)
        print('>Mandarin Chinese\n>Traditional Taiwan (type: Chinese (Traditional))')   
        print('End of languages.\n')
        lang = input('Enter the name of the language you want to learn: ').capitalize()
    return lang

def getLang():
    cont = 1
    while cont:
        paren_langs = {'Mandarin chinese':'Chinese (simplified)','Traditional taiwan':'Chinese (traditional)','Burmese':'Myanmar (burmese)'}
        print('To get a list of all accepted languages, type "list languages"')
        lang = input('Enter the name of the language you want to learn: ').capitalize()

        #print all languages
        if lang == 'List languages':
            lang = printLangs(lang)

        #reassign certain names that don't transfer perfectly between language lists
        if lang in paren_langs:
            lang = paren_langs[lang]

        #assign language code for selected language (inaccesible by gTTS dictionary, must be done through googletranslate)
        if lang in gt.lang.tts_langs().values() or lang in paren_langs.values():
            lcode = go.LANGCODES[lang.lower()]
            if int(input(f'You have chosen: {lang}. Is this correct?\nYes(1) or No(0): ')): return lcode,lang
            else:
                cont = int(input('Try another language (1) or exit(0)? '))

        else: 
            cont = int(input(f'"{lang}" not recognized. Try another language (1) or exit(0)? '))
    exit()

def translateMessage(code):
    fname = 'trans.mp3'
    if os.path.exists(fname):os.remove(fname)
    #translating message
    message = input('Enter the phrase you would like to translate: ')
    trans_message = tr.translate(message,src='en',dest=code)
    print(f'{message} becomes: {trans_message.text}')

    #use translation text to save spoken translation as mp3
    taudio = gt.gTTS(text=trans_message.text, lang=lcode)
    taudio.save(fname)

    return trans_message.text,fname

def playTranslation(file):
    #play translation until the user wants to continue
    cont = 1
    while cont:
        print('Playing translation...')
        playsound(file)
        cont = int(input('Replay? Yes(1) or No(0): '))

def pronounce(message,file):
    #record and evaluate user repeating phrase until they no longer want to try it
    cont = 1
    while cont:
        print('Playing phrase...')
        playsound(file)
        print(f'"{message}"')
        with spr.Microphone() as source:
            print('Try to repeat!')
            speech = rc.listen(source)
        try:
            sptext = rc.recognize_google(speech,language=lcode)
            print(f'I heard: {sptext}')
            if sptext == message.capitalize().strip(punctuation):
                print('Great job!')
            else: print('Not quite there yet!')
        except spr.UnknownValueError:
            print('Utterly unintelligible! I heard nothing :(')
        except spr.RequestError:
            print(  'Either speech recognition failed, key not recognized, or there is no internet connection.\n'
                    'Try to check these areas before attempting to speak any new phrases')
        cont = int(input('Would you like to try again? Yes(1) or No(0) '))

def dispMenu(lang,msg):
    menu = ('\nWhat would you like to do now?\n'
        f'\t1: Select new language (Current language: {lang})\n'
        f'\t2: Translate new phrase (Current phrase: "{msg}")\n'
        '\t3: Play current phrase\n'
        '\t4: Try current phrase (Will not work if *current phrase* is not in *current language*!)\n'
        '\t0: Exit\n'
        'Enter the number of your desired action: ')
    return int(input(menu))

    

print('Hello! Welcome to this LingaFranca!\n')
#get language on startup
lcode,language = getLang()
#get first translation
translation,trfile = translateMessage(lcode)

cont = int(input('Play translation? Yes(1) or No(0): '))
if cont: playTranslation(trfile)

cont = int(input('Would you like to attempt this phrase? Yes(1) or No(0): '))
if cont: pronounce(translation,trfile)

#continue to loop through steps of the translator until user closes it
choice = dispMenu(language,translation)
while choice:
    if choice == 1:
        lcode,language = getLang()
    elif choice == 2:
        translation,trfile = translateMessage(lcode)
    elif choice == 3:
        playTranslation(trfile)
    elif choice == 4:
        pronounce(translation,trfile)        
    choice = dispMenu(language,translation)
    print()
print('Closing LingaFranca... Goodbye!')

exit()
