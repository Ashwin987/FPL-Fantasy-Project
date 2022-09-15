library(tidyverse)
library(showtext)
library(ggtext)
data25 <- data25
library(ggplot2)
library(ggrepel)

din (data25)

str(data25)

#--------------
#code start- Interceptions 
#-----------

e <- ggplot(data25, aes(Starting.Price,Interceptions))
e + geom_text(aes(label=Starting.Price))
e + geom_text(aes(label=Starting.Price,colour=factor(Starting.Price)))

#--------------------------------------

#Without linear Regression-Interceptions
e + geom_point(aes(colour=Starting.Price))
#---------------------------------------

e + 
  geom_label_repel(data25 = subset(data25, Player == "Declan Rice"), 
                   aes(label = Player, size = NULL, color = NULL), nudge_y = 0.75,)



#--------------
#code start- Tackles Won
#-----------
e <- ggplot(data25, aes(Starting.Price,Tackles.Won))
e + geom_text(aes(label=Starting.Price))

e + geom_text(aes(label=Starting.Price,colour=factor(Starting.Price)))

e + geom_point(aes(colour=Starting.Price))

e + 
  geom_label_repel(data25 = subset(data25, Player == "Declan Rice"), 
                   aes(label = Player, size = NULL, color = NULL), nudge_y = 0.75,)


#--------------
#code start- Ball Recovery Points
#-----------
e <- ggplot(data25, aes(Starting.Price,Ball.Recovery.Points))
e + geom_text(aes(label=Starting.Price))
e + geom_text(aes(label=Starting.Price,colour=factor(Starting.Price)))

e + geom_point(aes(colour=Starting.Price))


e + 
  geom_label_repel(data25 = subset(data25, Player == "Declan Rice"), 
                   aes(label = Player, size = NULL, color = NULL), nudge_y = 0.75,)


ggplot(data25, aes(x= Starting.Price, y= Ball.Recovery.Points, colour="green", label=Player))+
  geom_point() +geom_text(hjust=0, vjust=0)
