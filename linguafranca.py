from os import path, remove
from time import sleep
from string import punctuation

import googletrans as go
import gtts as gt
import speech_recognition as spr
from playsound import playsound

#create translate and recognize objects used on phrases
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
        print('> Mandarin Chinese\n> Traditional Taiwan')   
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
            dispLang = ' '.join([word.capitalize() for word in lang.split(' ')])
            lang = paren_langs[lang]

        #assign language code for selected language (inaccesible by gTTS dictionary, must be done through googletrans)
        if lang in gt.lang.tts_langs().values() or lang in paren_langs.values():
            lcode = go.LANGCODES[lang.lower()]

            #print the language recognized based on language codes for user input
            if lang in paren_langs.values(): print(f'You have chosen: {dispLang}.',end=' ')
            else: print(f'You have chosen: {lang}.',end=' ')
            
            #ask the user if they would like to continue with this language; continue if so and repeat prompts if not
            if input('Is this correct? "Yes" or "No": ').lower() != 'no': return lcode,lang
            else: cont = input('Try another language ("retry") or "exit"? ')

        #if language given is unrecognized, ask again or close program based on user input
        else: 
            cont = input(f'"{lang}" not recognized. Try another language ("retry") or "exit"? ')
    exit()

def translateMessage(code):
    """Take translated phrase and create an audio reading as an mp3 file

    Args:
        code (str): language code for user-specified language

    Returns:
        trans_message.text,fname (tuple): tuple containing the translated message itself
                                          and the path of the audio file the translation is saved under
    """
    fname = 'trans.mp3' #random name set for storing the audio; I preferred using it as a variable
    #if there is already a translated message being stored, delete it to create a new one
    if path.exists(fname):remove(fname)

    #get message from the user
    message = input('Enter the phrase you would like to translate: ')
    print(f'"{message}" becomes...', end=' ')

    #translate user's message (googletrans) and print it out
    trans_message = tr.translate(message,src='en',dest=code)
    print(f'"{trans_message.text}"')
    sleep(1.5) #delay so translation can be read before anything new prints out

    #use translation text to save spoken translation as mp3 (gTTS)
    taudio = gt.gTTS(text=trans_message.text, lang=lcode)
    taudio.save(fname)

    #return translation as text and audio file
    return trans_message.text,fname

def playTranslation(file):
    """play saved translation until user continues

    Args:
        file (str): path to saved translation reading mp3
    """
    #play translation until the user wants to continue
    cont = 'yes'
    while cont.lower() != 'no':
        print('Playing translation...')
        playsound(file)
        cont = input('Replay? "Yes" or "No": ')

def pronounce(message,file):
    """Plays the translated phrase, listens to the user try to repeat it,
       and tells them if they repeated it correctly or not

    Args:
        message (str): TRANSLATION of the user-given phrase
        file (str): path to the mp3 audio file of the tts translation
    """
    #record and evaluate user repeating phrase until they no longer want to try it
    cont = 'yes'
    while cont != 'no':
        #play and print the translation to the user
        print('Playing phrase...',end=' ')
        playsound(file)
        print(f'"{message}"')

        #use default microphone to listen to user
        with spr.Microphone() as source:
            print('Try to repeat!')
            speech = rc.listen(source,timeout=10,phrase_time_limit=10)
        try:
            #use google speech api to recognize language based on saved language code
            sptext = rc.recognize_google(speech,language=lcode)

            #print what was heard and respond accordingly based on whether what was heard matches the translation
            print(f'I heard: {sptext}')
            if sptext.lower() == message.lower().strip(punctuation):
                print('Great job!')
            else: print('Not quite there yet!')

        #if audio isn't discernible, give possible reasons why based on error gotten
        except spr.UnknownValueError:
            print('Utterly unintelligible! I heard nothing :(')
        except spr.RequestError:
            print(  'Either speech recognition failed, key not recognized, or there is no internet connection.\n'
                    'Try to check these areas before attempting to speak any new phrases')
        
        #ask the user if they would like to go again or continue
        cont = input('Would you like to try again? "Yes" or "No": ').lower()

def dispMenu(lang,msg):
    """display menu of options to the user (current values in program update whenever called)

    Args:
        lang (str): last language chosen by the user
        msg (str): last translation the user created

    Returns:
        menu (str): keyword given by the user based on given menu options
    """
    menu = input('\nWhat would you like to do now?\n'
        f'\t"Language": Select new language (Current language: {lang})\n'
        f'\t"Translate": Translate new phrase (Current phrase: "{msg}")\n'
        '\t"Play": Play current phrase\n'
        '\t"Pronounce": Try current phrase (Will not work if *current phrase* is not in *current language*!)\n'
        '\t"Exit": Close LinguaFranca program\n'
        'Enter the keyword of your desired action: ')
    return menu.lower()

#start of the program run
print('Hello! Welcome to LinguaFranca.')
#get first language
lcode,language = getLang()
#get first translation
translation,trfile = translateMessage(lcode)

#play translation if prompted
cont = input('Play translation? "Yes" or "No": ').lower()
if cont != 'no': playTranslation(trfile)

#attempt pronunciation if prompted
cont = input('Would you like to attempt this phrase? "Yes" or "No": ').lower()
if cont != 'no': pronounce(translation,trfile)

#continue to loop through parts of the translator until user closes it
choice = dispMenu(language,translation)
while choice != 'exit':
    if choice == 'language':
        lcode,language = getLang()
    elif choice == 'translate':
        translation,trfile = translateMessage(lcode)
    elif choice == 'play':
        playTranslation(trfile)
    elif choice == 'pronounce':
        pronounce(translation,trfile) 
    else:
        print('Option not recognized, try again.')
        sleep(1)
    #get new choice from the user
    choice = dispMenu(language,translation)
    print()
    
#say goodbye and exit program
print('Closing LinguaFranca... Goodbye!')
exit()