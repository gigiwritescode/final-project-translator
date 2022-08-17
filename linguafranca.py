import googletrans as go
import gtts as gt
from playsound import playsound
import speech_recognition as spr
from time import sleep
from os import path, remove
from string import punctuation

tr = go.Translator()
rc = spr.Recognizer()

def printLangs(lang):
    """ Print all languages available for the program to use
        (based on google tts language availability, since there are fewer languages).

    Args:
        lang (str): name of the language the user types in.
                    if 'list languages' is typed, the program cycles.

    Returns:
        lang (str): if user types anything besides 'list languages' the phrase they typed is returned.
    """
    #every time list languages is typed in, program comes back to this command
    #this repeats until a new entry is given, and returns if it is entered again
    while lang == 'List languages':
        print('Printing all accepted languages...')

        #prints every language from gTTS that is also accepted by googletrans
        for language in gt.lang.tts_langs().values(): 
            if language.lower() in go.LANGCODES:print('>',language)

        #language codes between gTTS and googletrans are the same for "Mandarin Chinese" and "Traditional Taiwan" Chinese
        #but the terms used for the languages are different, so they are added to the list separately
        print('>Mandarin Chinese\n>Traditional Taiwan')   
        print('End of languages.\n')

        #request language again
        lang = input('Enter the name of the language you want to learn: ').capitalize()
    return lang

def getLang():
    """Get the language the user wants to learn as both the name of the language and its language code in googletrans

    Returns:
        lcode,lang (tuple): tuple containing the language code and name of the user-specified language
    """
    #continue until the user inputs a language they want to use or exits
    cont = 'Yes'
    while cont.lower() != 'exit':

        #dictionary for the values that do not translate perfectly between language lists
        paren_langs = {'Mandarin chinese':'Chinese (simplified)','Traditional taiwan':'Chinese (traditional)','Burmese':'Myanmar (burmese)'}
        
        #get language name from the user
        lang = input('Enter the name of the language you want to learn.\n'
                     '(to get a list of all accepted languages, type "list languages")\n').capitalize()

        #print all languages if prompted
        if lang == 'List languages':
            lang = printLangs(lang)

        #reassign certain names that don't transfer perfectly between language lists
        if lang in paren_langs:
            lang = paren_langs[lang]

        #assign language code for selected language (inaccesible by gTTS dictionary, must be done through googletrans)
        if lang in gt.lang.tts_langs().values() or lang in paren_langs.values():
            lcode = go.LANGCODES[lang.lower()]

            #ask the user if they would like to continue with this language; continue if so and repeat prompts if not
            if input(f'You have chosen: {lang}. Is this correct? ("Yes" or "No"): ').lower() != 'no': return lcode,lang
            else:
                cont = input('Try another language ("retry") or "exit"? ')

        #if language given is unrecognized, ask again or close program based on user input
        else: 
            cont = input(f'"{lang}" not recognized. Try another language ("retry") or "exit"? ')
    exit()

def translateMessage(code):
    fname = 'trans.mp3'
    if path.exists(fname):remove(fname)
    #translating message
    message = input('Enter the phrase you would like to translate: ')
    print(f'"{message}" becomes...', end=' ')
    trans_message = tr.translate(message,src='en',dest=code)
    print(f'"{trans_message.text}"')

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
            if sptext.lower() == message.lower().strip(punctuation):
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

    

print('Hello! Welcome to LinguaFranca.')
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
    sleep(1.5) 
    choice = dispMenu(language,translation)
    print()

print('Closing LinguaFranca... Goodbye!')
exit()
