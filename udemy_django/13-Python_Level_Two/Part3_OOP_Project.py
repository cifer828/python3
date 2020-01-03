#####################################
### WELCOME TO YOUR OOP PROJECT #####
#####################################
import random
# For this project you will be using OOP to create a card game. This card game will
# be the card game "War" for two players, you and the computer. If you don't know
# how to play "War" here are the basic rules:
#
# The deck is divided evenly, with each player receiving 26 cards, dealt one at a time,
# face down. Anyone may deal first. Each player places his stack of cards face down,
# in front of him.
#
# The Play:
#
# Each player turns up a card at the same time and the player with the higher card
# takes both cards and puts them, face down, on the bottom of his stack.
#
# If the cards are the same rank, it is War. Each player turns up three cards face
# down and one card face up. The player with the higher cards takes both piles
# (six cards). If the turned-up cards are again the same rank, each player places
# another card face down and turns another card face up. The player with the
# higher card takes all 10 cards, and so on.
#
# There are some more variations on this but we will keep it simple for now.
# Ignore "double" wars
#
# https://en.wikipedia.org/wiki/War_(card_game)

from random import shuffle

# Two useful variables for creating Cards.
SUITE = 'H D S C'.split()
RANKS = '2 3 4 5 6 7 8 9 10 J Q K A'.split()


class Deck:
    """
    This is the Deck Class. This object will create a deck of cards to initiate
    play. You can then use this Deck list of cards to split in half and give to
    the players. It will use SUITE and RANKS to create the deck. It should also
    have a method for splitting/cutting the deck in half and Shuffling the deck.
    """
    def __init__(self):
        self.deck = [(s, r) for r in RANKS for s in SUITE]

    def shuffling(self):
        print("shuffling cards")
        random.shuffle(self.deck)

    def splitting(self):
        print("splitting cards")
        return self.deck[:26], self.deck[26:]


class Hand:
    """
    This is the Hand class. Each player has a Hand, and can add or remove
    cards from that hand. There should be an add and remove card method here.
    """
    def __init__(self, cards):
        self.cards = cards

    def __len__(self):
        return len(self.cards)

    def append_card(self, cards):
        self.cards += cards

    def pop(self):
        return self.cards.pop(0)


class Player:
    """
    This is the Player class, which takes in a name and an instance of a Hand
    class object. The Payer can then play cards and check if they still have cards.
    """
    def __init__(self, name, hand):
        self.name = name
        self.hand = hand

    def __len__(self):
        return len(self.hand)

    def show_a_card(self):
        card = self.hand.pop()
        print("Player {} shows {} ".format(self.name, card))
        return card

    def put_down_cards(self, num):
        cards = [self.hand.pop() for _ in range(num)]
        print("Player {} turns down {} cards".format(self.name, num))
        return cards

    def lose(self, need_cards=1):
        if len(self.hand) < need_cards:
            print("Player {} doesn't have {} cards left".format(self.name, need_cards))
        return len(self.hand) < need_cards

    def get_cards(self, cards):
        self.hand.append_card(cards)


def convert_rand(rank):
    if rank == 'J':
        return 11
    if rank == 'Q':
        return 12
    if rank == 'K':
        return 13
    if rank == 'A':
        return 14
    return int(rank)


def compare_one_card(player_a, player_b, pool):
    a_card = player_a.show_a_card()
    b_card = player_b.show_a_card()
    pool += [a_card, b_card]
    if convert_rand(a_card[1]) > convert_rand(b_card[1]):
        return player_a
    elif convert_rand(a_card[1]) < convert_rand(b_card[1]):
        return player_b
    else:
        return None


def check_winner(player_a, player_b, left_num):
    if player_a.lose(left_num):
        print("{} wins".format(player_b.name))
        return True
    if player_b.lose(left_num):
        print("{} win".format(player_a.name))
        return True
    return False

######################
#### GAME PLAY #######
######################


print("Welcome to War, let's begin...")

# Use the 3 classes along with some logic to play a game of war!
deck = Deck()
deck.shuffling()
hand1, hand2 = deck.splitting()
me = Player("me", Hand(hand1))
ai = Player("ai", Hand(hand2))

i = 0

while True:
    print("------Round {}: {} has {} cards, {} has {} cards--------".format(i, me.name, len(me), ai.name, len(ai)))
    i += 1
    if check_winner(me, ai, 1):
        break

    left_cards = []
    winner = compare_one_card(me, ai, left_cards)

    # tie
    while winner is None:
        if check_winner(me, ai, 4):
            break

        # each player put 3 cards down
        left_cards += me.put_down_cards(3) + ai.put_down_cards(3)
        winner = compare_one_card(me, ai, left_cards)

        # # tie again
        # if winner is None:
        #     if check_winner(me, ai, 4):
        #         break
        #     left_cards += me.put_down_cards(1) + ai.put_down_cards(1)
        #     winner = compare_one_card(me, ai, left_cards)
    if winner is None:
        break
    winner.get_cards(left_cards)









