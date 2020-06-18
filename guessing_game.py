import sqlite3
from collections import namedtuple
import csv
import time
import random
import sys
import re

connection = sqlite3.connect("./players.db")
connection = sqlite3.connect("./words.db")
cursor = connection.cursor()
Player = namedtuple("Player", "first_name last_name score played_game win lose")
Word = namedtuple("Word", "word hint")

words_and_hints = []
with open("words.csv", "r") as words:
    reader = csv.reader(words)
    Words = namedtuple("Words", "word hint")
    next(reader)
    for row in reader:
        row = [column.strip().replace('"', "") for column in row]
        current_word_and_hint = Words(*row)
        words_and_hints.append(current_word_and_hint)

correct_letters = []
incorrect_letters = []
words_from_file = []
hints_from_file = []

def set_up_players_table():
    #cursor.execute("DROP TABLE IF EXISTS players")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            first_name TEXT,
            last_name TEXT,
            score INTEGER,
            played_game INTEGER,
            win INTEGER,
            lose INTEGER,
            UNIQUE (first_name, last_name) ON CONFLICT ROLLBACK
        )
    """)
    connection.commit()
    
def set_up_words_table():
    #cursor.execute("DROP TABLE IF EXISTS words")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS words (
            word TEXT,
            hint TEXT
        )
    """)
    connection.commit()
    
def insert_player(first_name, last_name, score, played_game, win, lose):
    sql = """
        INSERT OR REPLACE INTO players (first_name, last_name, score, played_game, win, lose)
        VALUES ("{}", "{}", {}, {}, {}, {})
        """.format(first_name, last_name, score, played_game, win, lose)
    cursor.execute(sql)
    connection.commit()
    time.sleep(1)
    
def insert_word(word, hint):
    sql = """
        INSERT OR REPLACE INTO words (word, hint)
        VALUES ('{}', '{}')
    """.format(word, hint)
    cursor.execute(sql)
    connection.commit()
    
def insert_everything_from_file():
    for word_and_hint in words_and_hints:
        words_from_file.append(word_and_hint.word)
        hints_from_file.append(word_and_hint.hint)
        insert_word(word_and_hint.word, word_and_hint.hint)
    
def get_all_players():
    sql = "SELECT * FROM players"
    rows= cursor.execute(sql)
    players = rows.fetchall()
    if len(players) == 0:
        print("\nThere isn't anyone.")
        time.sleep(1)
    else:
        return [Player(*player)for player in players]
    
def get_all_words():
    sql = "SELECT * FROM words"
    rows = cursor.execute(sql)
    words = rows.fetchall()
    return [Word(*word) for word in words]

def show_words():
    words = get_all_words()
    if words is not None:
        for word in words:
            print("\nWord: {}, Hint: {}".format(word.word, word.hint))

def search_for_player(first_name, last_name):
    sql = "SELECT * FROM players WHERE first_name == '{}' AND last_name == '{}'".format(first_name, last_name)
    row = cursor.execute(sql)
    player = row.fetchone()
    if player is None:
        time.sleep(1)
        print("\nThere is no player with a name like that.")
        time.sleep(1)
        return None
    else:
        time.sleep(1)
        return Player(*player)
    
def delete_player(first_name, last_name):
    sql = "DELETE FROM players WHERE first_name == '{}' AND last_name == '{}'".format(first_name, last_name)
    cursor.execute(sql)
    connection.commit()
    
def update_player_name(new_first_name, new_last_name, first_name, last_name):
    sql = "UPDATE players SET first_name = '{}', last_name = '{}' WHERE first_name == '{}' AND last_name == '{}'".format(new_first_name, new_last_name, first_name, last_name)
    cursor.execute(sql)
    connection.commit()

def update_score_negative(last_name):
    sql = "UPDATE players SET score = score - 2, lose = lose + 1 WHERE last_name == '{}'".format(last_name)
    cursor.execute(sql)
    connection.commit()
    
def update_score_positive(last_name, lives):
    sql = "UPDATE players SET score = score + (10 - {}), win = win + 1 WHERE last_name == '{}'".format(lives, last_name)
    cursor.execute(sql)
    connection.commit()
    
def update_played_game(last_name):
    sql = "UPDATE players SET played_game = played_game + 1 WHERE last_name == '{}'".format(last_name)
    cursor.execute(sql)
    connection.commit()
    
def get_random_word():
    elements = get_all_words()
    words = []
    for element in elements:
        words.append(element)
    word = random.choice(words)
    return word

def start_the_game(random_word):
    new_word = random_word.word
    for letter in new_word:
           new_word = new_word.replace(letter, " _ ")
    return new_word

def statistics_global():
    number_of_players = 0
    scores = 0
    number_of_played_games = 0
    wins = 0
    loses = 0
    every_player = get_all_players()
    if every_player is not None:
        
        for player in every_player:

            if player.played_game > 0 :
                number_of_players += 1
                scores += player.score
                number_of_played_games += player.played_game
                wins += player.win
                loses += player.lose
                average_score = scores / number_of_played_games
                if wins == 0:
                    average_percent = 100 - (loses * 100 / number_of_played_games)
                elif wins != 0:
                    average_percent = wins * 100 / number_of_played_games
        
                print("""
Number of player(s): {}, Played game(s): {}, Score(s): {}, Wins: {}, Loses: {}.
On average players got {} points for each game and they were successful {}% of the time.
    """.format(number_of_players, number_of_played_games, scores, wins, loses, round(average_score,2), round(average_percent,2)))
                time.sleep(2)
            else:
                print("\nSorry, it seems nobody has played a game yet.")
                time.sleep(1)   
        
    elif every_player is None:
        #time.sleep(1)
        print("\nSorry, it seems there isn't anyone in the database.")
        time.sleep(1)
        return None
    
def statistics_personal(first_name, last_name):
    players = get_all_players()
    players_wins = 0
    players_loses = 0
    players_games = 0
    if players is not None:
        for another_player in players:
            if another_player.played_game > 0:
                players_wins += another_player.win
                players_loses += another_player.lose
                players_games += another_player.played_game
                if players_wins == 0:
                    another_player_average_percent = 100 - (players_loses * 100 / players_games)
                elif players_wins != 0:
                    another_player_average_percent = players_wins * 100 / players_games
            else:
                print("\nSorry, something went wrong here, let's try it again.")
                time.sleep(1)
    elif players is None:
        #time.sleep(1)
        print("\nSorry, it seems there isn't anyone in the database.")
        time.sleep(1)
        return None
    
    player = search_for_player(first_name, last_name)
    if player is not None:
        score = player.score
        played_games = player.played_game
        win = player.win
        lose = player.lose
        if played_games > 0:
            if win == 0:
                average_percent = 100 - (lose * 100 / played_games)
            elif win != 0:
                average_percent = win * 100 / played_games
            print("""
Until now {} got {} point(s) after {} game(s), {} won {} time(s) and lost {} time(s).
It means {} was successful {}% of the time.
    """.format(first_name, score, played_games, first_name, win, lose, first_name, round(average_percent,2)))
            time.sleep(1)
            if another_player_average_percent > average_percent:
                print("On average players won {}% of the time, so {} is a bit under the average. Keep practising!\n".format(round(another_player_average_percent,2), first_name))
                time.sleep(1)
            elif another_player_average_percent < average_percent:
                print("On average players won {}% of the time, so {} is a bit better than the average. Good game!\n".format(round(another_player_average_percent,2), first_name))
                time.sleep(1)
            elif another_player_average_percent == average_percent:
                print("On average players won {}% of the time, so {} is an average player. Keep practising!\n".format(round(another_player_average_percent,2), first_name))
                time.sleep(1)
        elif played_games == 0:
            print("\nSorry, it seems {} hasn't played a game yet.".format(first_name))
            time.sleep(2)
    elif player is None:
        #time.sleep(1)
        print("\nSorry, it seems there isn't anyone in the database.")
        time.sleep(1)
        return None

def restart():
    return None

def exit():
    sys.exit()
    
def multiplayer_game(lives):
    list_of_players = []
    all_players = get_all_players()
    for player in all_players:
        list_of_players.extend([player.first_name, player.last_name])
    time.sleep(1)
    print("\nIf you'd like to quit from this mode, just type 'exit' now or after your name and the game will restart.")
    time.sleep(1)
    number_of_players = input("\nHow many players do we have? ")
    if number_of_players == "exit":
        time.sleep(1)
        print("\nBetter luck next time!")
        time.sleep(2)
        return None
    if not re.match('^[1-9]$', number_of_players):
        time.sleep(1)
        print("\nPlease use only numbers in the correct range (1 - maximum number of players in the database) as an answer for this question! Let's try it again.")
        time.sleep(2)
    else:   
        time.sleep(1)
        if int(number_of_players) <= len(all_players):
            rounds = 0
            while rounds < int(number_of_players):
                print("\nHere is the " + str(rounds+1) + ". round.\n")
                time.sleep(1)
                first_name = input("Your first name: ")
                last_name = input("Your last name: ")
                if first_name in list_of_players and last_name in list_of_players:
                    play_the_game(lives, first_name, last_name)
                    rounds += 1
                    time.sleep(2)
                    for f_name in list_of_players:
                        if f_name == first_name:
                            list_of_players.remove(f_name)
                    for l_name in list_of_players:
                        if l_name == last_name:
                            list_of_players.remove(l_name)
                    print(list_of_players)
                else:
                    time.sleep(1)
                    print("\nSomething went wrong. Maybe you have had your turn before during this game or the name wasn't correct. Let's try it again.")
                    time.sleep(2)
            print("\nHope you guys had a good time!")
            time.sleep(1)
        elif int(number_of_players) > len(all_players):
            print("""
Sorry, it looks like we haven't got enough player in the database.
Please add the missing players to it first, so all of you can get access to the game.""")

def play_the_game(lives, first_name, last_name):
    
    player = search_for_player(first_name, last_name)
    if player is None or first_name != player.first_name or last_name != player.last_name:
        print("\nTry to add a new player first. You need an existing player in order to get access to the game.")
        time.sleep(1)
        return None

    word = get_random_word()
    list_of_letters = list(word.word)
    start_the_game(word)
    output = start_the_game(word).replace(" ", "")
    separator_empty = ""
    separator_space = " "
    separator_comma = ", "
    visible_output = list(output)
    print("\nThe word you need to figure out: ", start_the_game(word))
    time.sleep(1)
    print("\nHint: " + word.hint)
    time.sleep(1)
    
    while lives > 0:
        
        print("""\n
                    (If you know the final answer, please type 'ready'.
                    But you only have one shot. If your are wrong, you lost.
                    Also if you would like to quit, just type 'exit' and the game will restart.)""")
        
        guess = input("\nYour guess (a single character between a-z): ")
        
        if guess == "ready":
            time.sleep(1)
            final_guess = input("\nSo, what is your final guess? ")
            
            if final_guess == word.word:
                time.sleep(1)
                print("\nCongratulations! You just won the game!\n")
                update_score_positive(last_name, lives)
                update_played_game(last_name)
                player = search_for_player(first_name, last_name)
                print(first_name + ", you have " + str(player.score) + " point(s) and you played " + str(player.played_game) + " game(s).")
                time.sleep(1)
                correct_letters.clear()
                return None
            
            elif final_guess != word.word:
                time.sleep(1)
                print("\nSorry, you are wrong, the game is over.\n")
                time.sleep(1)
                print("You think it'd be great to know the solution, right? Well, I won't tell you.\n")
                time.sleep(1)
                update_score_negative(last_name)
                update_played_game(last_name)
                player = search_for_player(first_name, last_name)
                print(first_name + ", you have " + str(player.score) + " point(s) and you played " + str(player.played_game) + " game(s).")
                time.sleep(1)
                correct_letters.clear()
                return None
            
        elif guess == "exit":
            time.sleep(1)
            final_decision = input("\nAre you sure? If you leave now, all of your results during ths round will be lost. Maybe the next word will be harder. (yes/no): ")
            if final_decision == "yes":
                time.sleep(1)
                print("\nBetter luck next time!")
                correct_letters.clear()
                incorrect_letters.clear()
                time.sleep(1)
                return None
            elif final_decision == "no":
                time.sleep(1)
                print("\nYou got me, that was funny. Don't do it again.")
                time.sleep(1)
        
        elif len(guess) > 1 and guess != "exit" and guess != "ready" or re.match("[0-9]", guess):
            time.sleep(1)
            print("\nPlease use only the allowed characters or words. Let's try it again.")
            time.sleep(1)
        
        elif guess in list_of_letters:
            
            index_of_letter = []
            
            for letter in re.finditer(guess, word.word):
                index_of_letter.append(letter.start())
                
            for num in index_of_letter:
                visible_output[num] = guess
                
            if guess not in correct_letters:
                time.sleep(1)
                correct_letters.append(guess)
                print("\nGreat! You found a(n) " + "'" + guess + "'" + ". Keep going! \n")
                time.sleep(1)
                print("You still have " + str(lives) + " lives.")
                time.sleep(1)
                
            else:
                time.sleep(1)
                print("\nYou already found that letter! Try another one.")
                time.sleep(1)
                
        elif guess not in list_of_letters:
            time.sleep(1)
            lives -= 1
            incorrect_letters.append(guess)
            print("\nSorry, that letter is not what you are looking for.")
            time.sleep(1)
            print("\nYou can only make " + str(lives) + " more mistake(s).")
            time.sleep(1)
            
        print("\nThe word you need to figure out: " + separator_space.join(visible_output))
        print("\nHint: " + word.hint)
        print("\nYour correct guesses: " + separator_comma.join(correct_letters))
        print("Your incorrect guesses: " + separator_comma.join(incorrect_letters) + "\n")
        time.sleep(1)
        
        
        if separator_empty.join(visible_output) == word.word:
            time.sleep(1)
            print("\nCongratulations! You just won the game!\n")
            update_score_positive(last_name, lives)
            update_played_game(last_name)
            player = search_for_player(first_name, last_name)
            print(first_name + ", you have " + str(player.score) + " point(s) and you played " + str(player.played_game) + " game(s).")
            time.sleep(1)
            correct_letters.clear()
            incorrect_letters.clear()
            return None
            
    if lives == 0:
        print("\nSorry, the game is over.")
        time.sleep(1)
        update_score_negative(last_name)
        update_played_game(last_name)
        player = search_for_player(first_name, last_name)
        print("\n", first_name + ", you have " + str(player.score) + " point(s) and you played " + str(player.played_game) + " game(s).")
        time.sleep(1)
        correct_letters.clear()
        incorrect_letters.clear()
        return None

set_up_players_table()
set_up_words_table()  
insert_everything_from_file()

while True:
    print("""
        Welcome to my barchoba! Thank you for playing with my game, have fun and good luck!

        Please select an option:
        
        1. Add new player
        2. Update player name
        3. Show all players
        4. Show all words and hints
        5. Check player stats
        6. Delete player
        7. Start a new game
        8. Statistics
        9. Exit
    """)
    
    choice = input()
    
    if not re.match("[1-9]", choice):
        time.sleep(1)
        print("Please use only numbers 1-9! Let's try it again.")
        time.sleep(2)
        
    if choice == "1":
        time.sleep(1)
        first_name = input("First name: ")
        last_name = input("Last name: ")
        insert_player(first_name, last_name, 0, 0, 0, 0)
        
        print("\nNew player has been added!")
        new_player = search_for_player(first_name, last_name)
        print("Name: {} {}, Score: {}, Played games: {}, Win: {}, Lose: {}".format(*new_player))
        time.sleep(1)
        
    elif choice == "2":
        first_name = input("Your old first name: ")
        new_first_name = input("Your new first name: ")
        last_name = input("\nYour old last name: ")
        new_last_name = input("Your new last name: ")
        player = search_for_player(first_name, last_name)
        time.sleep(1)
        if player is not None:
            update_player_name(new_first_name, new_last_name, first_name, last_name)
            print("\nPlayer has been updated!")
            time.sleep(1)
        else:
            print("\nYou can only modify existing players. Let's try it again.")
            time.sleep(2)
        
    elif choice == "3":
        time.sleep(1)
        players = get_all_players()
        if players is not None:
            for player in players:
                print("Name: {} {}, Score: {}, Played games: {}, Win: {}, Lose: {}".format(*player))
                time.sleep(1)
                
    elif choice == "4":
        time.sleep(1)
        show_words()
        time.sleep(2)
    
    elif choice == "5":
        time.sleep(1)
        first_name = input("Please type the first name of the player you are looking for: ")
        last_name = input("Please type the last name of the player you are looking for: ")
        player = search_for_player(first_name, last_name)
        time.sleep(1)
        if player is not None:
            print("\nName: {} {}, Score: {}, Played games: {}, Win: {}, Lose: {}".format(*player))
            time.sleep(1)
        else:
            print("\nTry again, please.")
            time.sleep(2)
            
    elif choice == "6":
        time.sleep(1)
        first_name = input("First name of the player you'd like to delete: ")
        last_name = input("Last name of the player you'd like to delete: ")
        player = search_for_player(first_name, last_name)
        if player is not None:
            time.sleep(1)
            final_decision = input("\nAre you sure? If you delete this player all of her/his points will be lost. Forever. (yes/no): ")
            time.sleep(1)
            if final_decision == "yes":
                delete_player(first_name, last_name)
                print("\nYou successfully deleted this player: " + first_name + " " + last_name)
                time.sleep(1)
            elif final_decision == "no":
                print("\nAlrighty then! You almost scared me.")
                time.sleep(1)
            else:
                time.sleep(1)
                print("\nYour answer should be 'yes' or 'no'. Let's try it again.")
                time.sleep(2)
        
    elif choice == "7":
        time.sleep(1)
        print("""
            Please choose one:
            
            1. Single player, against me, the computer
            2. Multiplayer, against your friend / the love of your life
        """)
        
        type_of_game = input()
        
        if not re.match("[1,2]", type_of_game):
            time.sleep(1)
            print("\nPlease use only 1 or 2 as an answer! Let's try it again.")
            time.sleep(2)
        
        if type_of_game == "1":
            time.sleep(1)
            print("""
                Alrighty then. So you are against me.
                I won't get any points, because I'm already a winner: you are playing with my game.
                You need to have an avatar for getting access to the game.
                If you don't have any, you can go back to the main menu by choosing the right option.
                If you do, we can start having fun.
                Which level would you like to try?
                (You can get more points, if you play on harder levels.)
                
                1. Easy-peasy (Even a monkey could do it)
                2. Medium (Boring, but you need to think a bit)
                3. Hard (It's kinda challenging)
                4. Mithril (hard as hell, you won't survive it)
                
                5. Return to the main menu
            """)
            
            level = input()
            
            if not re.match("[1-5]", level):
                time.sleep(1)
                print("\nPlease use only numbers 1-5! Let's try it again.")
                time.sleep(2)
            
            if level == "1":
                time.sleep(1)
                print("\nOn this level you have 8 lives.\n")
                time.sleep(1)
                first_name = input("Your first name: ")
                last_name = input("Your last name: ")
                time.sleep(1)
                play_the_game(8, first_name, last_name)
                time.sleep(1)
                
            elif level == "2":
                time.sleep(1)
                print("\nOn this level you have 6 lives.\n")
                time.sleep(1)
                first_name = input("Your first name: ")
                last_name = input("Your last name: ")
                time.sleep(1)
                play_the_game(6, first_name, last_name)
                time.sleep(1)
                
            elif level == "3":
                time.sleep(1)
                print("\nOn this level you have 4 lives.\n")
                time.sleep(1)
                first_name = input("Your first name: ")
                last_name = input("Your last name: ")
                time.sleep(1)
                play_the_game(4, first_name, last_name)
                time.sleep(1)
                
            elif level == "4":
                time.sleep(1)
                print("\nOn this level you have 2 lives.\n")
                time.sleep(1)
                first_name = input("Your first name: ")
                last_name = input("Your last name: ")
                time.sleep(1)
                play_the_game(2, first_name, last_name)
                time.sleep(1)
                
            elif level == "5":
                restart()
                time.sleep(1)
                
        elif type_of_game == "2":
            time.sleep(1)
            print("""
                Alrighty then. So you are playing against your friend.
                Both of you need to have an avatar for getting access to the game.
                If you don't have any, you can go back to the main menu by choosing the right option.
                If both of you do, we can start having fun.
                Which level would you like to try?
                (You can get more points, if you play on harder levels.)
                
                1. Easy-peasy (Even a monkey could do it)
                2. Medium (Boring, but you need to think a bit)
                3. Hard (It's kinda challenging)
                4. Mithril (hard as hell, you won't survive it)
                
                5. Return to the main menu
            """)
            
            level = input()
    
            if not re.match("[1-5]", level):
                time.sleep(1)
                print("\nPlease use only numbers 1-5! Let's try it again.")
                time.sleep(2)
            
            if level == "1":
                time.sleep(1)
                print("\nOn this level all of you have 8 lives.")
                multiplayer_game(8)
                time.sleep(2)
                
            elif level == "2":
                time.sleep(1)
                print("\nOn this level all of you have 6 lives.")
                multiplayer_game(6)
                time.sleep(2)
                
            elif level == "3":
                time.sleep(1)
                print("\nOn this level all of you have 4 lives.")
                multiplayer_game(4)
                time.sleep(2)
                
            elif level == "4":
                time.sleep(1)
                print("\nOn this level all of you have 2 lives.")
                multiplayer_game(2)
                time.sleep(2)
                
            elif level == "5":
                restart()
                time.sleep(1)
                
    elif choice == "8":
        time.sleep(1)
        print("""
            Which statistics would you like to see?
            
            1. General statistics
            2. Personal statistics
        """)
        
        stat = input()
        
        if not re.match("[1,2]", stat):
                time.sleep(1)
                print("\nPlease use only 1 or 2 as an answer for this question! Let's try it again.")
                time.sleep(2)
                
        if stat == "1":
            time.sleep(1)
            print("\nAlright, so here is every information you can find about the players' results.")
            time.sleep(1)
            statistics_global()
            time.sleep(2)
            
        if stat == "2":
            time.sleep(1)
            first_name = input("First name of the player you'd like to know a bit more: ")
            last_name = input("Last name of the player you'd like to know a bit more: ")
            time.sleep(1)
            print("\nAlright, so here is everything you can find about {}'s results.".format(first_name))
            time.sleep(1)
            statistics_personal(first_name, last_name)
            time.sleep(2)
            
    elif choice == "9":
        time.sleep(1)
        final_decision = input("Are you sure? (yes/no): ")
        time.sleep(1)
        if final_decision == "yes":
            print("\nHope you had a good time here, see you later!")
            time.sleep(2)
            exit()
        elif final_decision == "no":
            print("\nIt's not funny, don't try to scare me ever again.")
            time.sleep(2)
        else:
            time.sleep(1)
            print("\nYour answer should be 'yes' or 'no'. Let's try it again.")
            time.sleep(2)
        