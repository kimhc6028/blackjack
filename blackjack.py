from __future__ import division
import numpy as np
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from matplotlib import cm
        
class Card_list:

    def __init__(self):

        cards = [i for i in range(2,11)] + [10,10,10,11]
        self.cards_list = cards * 4

class Game:

    def __init__(self):
        self.dealer = Dealer()
        self.AI_ = AI()
            
    def pop_card(self):
        return self.Deck.cards_list.pop(0)

    def shuffle_deck(self, deck):
        random.shuffle(deck)

    def give_card(self,player):

        if len(self.Deck.cards_list) == 0:
            print "No cards on deck"
            return 
        card = self.pop_card()
        #print "give {}".format(card)
        player.cards.append(card)
        player.count_sum()
        if card == 11:
            player.Ace = True

            
    def start_game(self):

        self.Deck = Card_list()
        self.shuffle_deck(self.Deck.cards_list)
        card1 = self.pop_card()
        card2 = self.pop_card()
        card3 = self.pop_card()
        card4 = self.pop_card()
        self.dealer.get_card(card3, card4)
        self.AI_.get_card(card1, card2, self.dealer.cards[0])
        

        if (self.AI_.blackjack == True) or (self.dealer.blackjack == True):
            temp = self.judge(self.AI_, self.dealer)
            #print temp


    def play(self, episode):

        score = 0
        for epi in range(episode):
            if epi % 10000 == 0:
                print("episode {} passed".format(epi))
            self.start_game()
            self.AI_.update_state()        
            #print "................."
            while True:
                #print "...................................."
                #print("    AI:{}, sum:{}".format(self.AI_.cards, self.AI_.sum_))
                #print("dealer:{}, sum:{}".format(self.dealer.cards, self.dealer.sum_))

                #self.AI_.update_agent()#########################
            
                AI_action = self.AI_.action()
                dealer_action = self.dealer.action()
                if AI_action == "hit":
                    #print "AI hit"
                    self.give_card(self.AI_)
            
                elif AI_action == "stay":
                    #print "AI stay"
                    pass
                if dealer_action == "hit":
                    #print "dealer hit"
                    self.give_card(self.dealer)
                
                elif dealer_action == "stay":
                    #print "dealer stay"
                    pass

                self.AI_.update_state()        
                #print self.AI_.state
                #print "AI card:{} dealer card:{}".format(self.AI_.cards, self.dealer.cards)

                if (AI_action == "stay") and (dealer_action == "stay"):
                    #print "stay"
                    break
                if self.AI_.sum_ > 21:
                    break
                
            
            
            reward = self.judge(self.AI_, self.dealer)
            self.AI_.end_episode(reward)
            score += reward
            
            #print temp
        score = score / episode
        print score
        self.visualize()

    def visualize(self):
        fig = plt.figure()
        ax = fig.add_subplot(211, projection="3d")
        ay = fig.add_subplot(212, projection="3d")

        xi = range(len(self.AI_.V[0]))
        yi = range(len(self.AI_.V))

        X, Y = np.meshgrid(xi, yi)
        self.AI_.V = np.divide(self.AI_.R, self.AI_.counter)
        Ace = self.AI_.V[:,:,1]
        Not_Ace = self.AI_.V[:,:,0]
        surf1 = ax.plot_surface(X, Y, Ace, rstride=1, cstride=1, cmap=cm.coolwarm,
                               linewidth=0, antialiased=False)
        ax.set_zlim3d(-1.01, 1.01)

        fig.colorbar(surf1, shrink=0.5, aspect=10)

        surf2 = ay.plot_surface(X, Y, Not_Ace, rstride=1, cstride=1, cmap=cm.coolwarm,
                               linewidth=0, antialiased=False)
        ay.set_zlim3d(-1.01, 1.01)

        fig.colorbar(surf2, shrink=0.5, aspect=10)

        #ax.plot_wireframe(X, Y, Ace, rstride=10, cstride=10)
        #ay.plot_wireframe(X, Y, Not_Ace, rstride=10, cstride=10)
        plt.show()
    def judge(self, player, dealer):
        
        if player.sum_ > 21:
            return -1 ## lose

        elif player.sum_ > dealer.sum_:
            return 1 ## win

        elif player.sum_ < dealer.sum_:
            return -1 ## lose

        elif player.sum_ == dealer.sum_:
            return 0 ##draw

        else :
            raise(TypeError)

class Player(object):

    def __init__(self):
        pass

    def get_card(self, card1, card2):

        self.blackjack = False
        self.Ace = False
        self.Ace_usable = False
        self.cards = [card1, card2]
        if 11 in self.cards:
            self.Ace = True
        self.shown_card = self.cards[0]
        self.count_sum()

        if self.sum_ == 21:
            self.blackjack = True

            
            
    def count_sum(self):

        self.sum_ = sum(self.cards)
        if self.Ace == True:
            if self.sum_ > 21:
                self.sum_ -= 10
                self.Ace_usable = False

            elif self.sum_ <= 21:
                self.Ace_usable = True


class Dealer(Player):
    
    def __init__(self):
        Player.__init__(self)

    def action(self):

        if self.sum_ <= 16:
            self.count_sum()
            return "hit"
        elif self.sum_ >= 17:
            self.count_sum()
            return "stay"
        else :
            print("Error : Dealer.rule")


        
            
class AI(Player):#monte carlo

    def __init__(self):
        Player.__init__(self)
        #self.Agent = RandomAgent()        
        #self.Agent = MonteCarloAgent()
        self.V = np.zeros((11,31,2))##dealer_card,sum,ace,reward
        self.R = np.zeros((11,31,2))
        #self.returns = [[[] for _ in range(10)
        self.loop_counter = 0        
        self.counter = np.zeros((11,31,2))

    def update_state(self):
        self.state.append((self.dealer_card, self.sum_, self.Ace_usable))
        
    def get_card(self, card1, card2, dealer_card):
        super(AI, self).get_card(card1, card2)
        self.dealer_card = dealer_card
        self.state = []
        self.loop_counter += 1

    def action(self):
        action_ = self.policy(self.sum_)
        self.count_sum()
        return action_

    def policy(self,sum_):
        ##policy
        if sum_ >= 20 :
            return "stay"

        elif sum_ < 20 :
            return "hit"

    def end_episode(self, reward):
        last=self.state.pop(-1)
        self.R[last[0] - 1][last[1]][last[2]] += reward
        self.counter[last[0] - 1][last[1]][last[2]] += 1
        CFO = reward
        for state in self.state[::-1]:
            self.R[state[0] - 1][state[1]][state[2]] += CFO
            self.counter[state[0] - 1][state[1]][state[2]] += 1
        #self.V = np.divide(self.R, self.counter)
        #self.V = self.R / self.loop_counter
        
        #self.R[self.dealer_card - 1][self.sum_][self.Ace_usable] += reward
        #self.V[self.dealer_card - 1][self.sum_][self.Ace_usable] = self.R

        
    #def update_(self):
    #self.Agent.sum_ = self.sum_
        


def main():
    game = Game()
    game.play(1000000)


if __name__ == '__main__':
    main()
    ##learning
