rm(list=ls())

library(randomForest)
library(e1071)
data <- read.csv('~/Documents/projects/bball_prj_games/UTD_2014.csv')
outcome <- read.csv('~/Documents/projects/bball_prj_games/GL2014.csv')

perf <- function(model,df){
  pred <- as.numeric(predict(model, df[cv,], type='response') > 0.5)
  actual <- df[cv,'win.numeric']
  perf <- table(pred,actual)
  
  precision <- perf['1','1']/(perf['1','1'] + perf['1','0'])
  recall <- perf['1','1']/(perf['1','1'] + perf['0','1'])
  f1 <- 2*((precision*recall)/(precision+recall))
  
  acc <- (sum(diag(perf))/sum(perf))*100
  
  # print(paste('Accuracy: ', round(acc,3), '%', sep = ''))
  # print(paste('F1-score:', round(f1,3)))
  
  perf_out <- list('acc' = acc, 'f1' = f1, 'perf' = perf)
  return(perf_out)
}

part_fit <- function(df){
  # Partition data.
  train <- sample(n, round(n*0.8))
  cv <- sample(seq(n)[-train],round(n*0.2))
  test <- seq(n)[-c(train,cv)]
  
  ## Logisitic regression model
  f <- paste('win.numeric ~ ', paste(c(hnames, anames), collapse = ' + '), sep = '')
  l <- glm(f, family = binomial(logit), data = dd[train,])
  perf(l,dd)
}

## Learning curves
lc <- function(i){
  l <- glm(f,family=binomial(logit), data = dd[train[1:i],])
  train_err <- -mean(dd[train[1:i], 'win.numeric']*log(predict(l, dd[train[1:i], ], type='response')) + (1 - dd[train[1:i],'win.numeric'])*log(1-predict(l, dd[train[1:i],], type='response')))
  cv_err <- -mean(dd[cv,'win.numeric']*log(predict(l, dd[cv,], type='response')) + (1-dd[cv,'win.numeric'])*log(1-predict(l, dd[cv,], type='response')))
  c(train_err,cv_err)
}

# hnames <- c(paste('h', seq(9), '_obp', sep=''), paste('h', seq(9), '_ops', sep=''), paste('h', seq(9), '_slg', sep=''))
# anames <- c(paste('a', seq(9), '_obp', sep=''), paste('a', seq(9), '_ops', sep=''), paste('a', seq(9), '_slg', sep=''))

hnames <- c(paste('h', seq(9), '_obp', sep=''), paste('h', seq(9), '_slg', sep=''))
anames <- c(paste('a', seq(9), '_obp', sep=''), paste('a', seq(9), '_slg', sep=''))

dd0 <- data[,c('game', hnames, anames)]
dd <- merge(dd0, outcome, by.x = 'game', by.y = 'game_id')

n <- dim(dd)[1]
train <- sample(n, round(n*0.8))
cv <- sample(seq(n)[-train],round(n*0.2))
test <- seq(n)[-c(train,cv)]

dd$win.numeric <- as.numeric(dd[,'winner'])-1 # home team win == 1

f <- as.formula(paste('win.numeric ~ ', paste(c(hnames, anames), collapse = ' + '), sep = ''))
l <- glm(f, family = binomial(logit), data = dd[train,])
summary(l)

######
## randomForest model START
######
f <- as.formula(paste('winner ~ ', paste(c(hnames, anames), collapse = ' + '), sep = ''))
rF <- randomForest(f, data = dd[train,])
pred <- predict(rF, dd[cv,], type='response')
actual <- dd[cv,'winner']
perf <- table(pred,actual)
precision <- perf['home','home']/(perf['home','home'] + perf['home','away'])
recall <- perf['home','home']/(perf['home','home'] + perf['away','home'])
f1 <- 2*((precision*recall)/(precision+recall))
acc <- (sum(diag(perf))/sum(perf))*100
print (acc)
######
## randomForest model END
######

######
## SVM START
######
f <- as.formula(paste('winner ~ ', paste(c(hnames, anames), collapse = ' + '), sep = ''))
svm <- svm(f, data = dd[train,])
pred <- predict(svm, dd[cv,], type='response')
actual <- dd[cv,'winner']
perf <- table(pred,actual)
precision <- perf['home','home']/(perf['home','home'] + perf['home','away'])
recall <- perf['home','home']/(perf['home','home'] + perf['away','home'])
f1 <- 2*((precision*recall)/(precision+recall))
acc <- (sum(diag(perf))/sum(perf))*100
print (acc)
######
## SVM END
######


performance <- lapply(seq(1000), function(i) part_fit(dd))
acc_all <- sapply(performance, with, acc)
f1_all <- sapply(performance, with, f1)

pdf('~/Documents/projects/bball_prj_games/perm_acc.pdf')
plot(acc_all, pch = 19, las = 1, bty = 'l', ylab = 'Accuracy')
abline(h = (sum(y)/length(y))*100, lwd = 3, lty = 2, col = 'gray')
title(main = 'Model performance: permutation results')
legend('topleft', lty = 2, col = 'gray', legend = 'Home WP', bty = 'n')
mtext(paste('mean: ', round(mean(acc_all),3), '%', sep = ''))
dev.off()

#######
### LEARNING CURVES
#######

## Choose min sample size based on # of predictors.
min_n <- ceiling(dim(dd)[2]/10)*10+50
n10 <- seq(min_n, length(train) ,10)

## Compute training and cross-validation errors.
out <- lapply(n10, function(i) lc(i))

## Reformat errors.
err <- cbind(unlist(data.frame(out)[1,]), unlist(data.frame(out)[2,]))
rownames(err) <- paste('N',n10,sep='')
colnames(err) <- c('train','cv')

## Plot training and cv errors.
pdf('~/Documents/projects/bball_prj_games/learning_curve.pdf')

plot(err[,'train'] ~ n10, pch=19, bty = 'l', las = 1, xlab = 'Sample size', ylab = 'Error', ylim = range(err), xlim = c(1000,2000))
points(err[,'cv'] ~ n10, pch=19, bty = 'l', las = 1, xlab = 'Sample size', ylab = 'Error',col = 'blue')
lines(n10, err[,'train'])
lines(n10, err[,'cv'], col = 'blue')
title(main = "Learning curve: Up-to-date game information predicting game outcomes.")

plot(err[,'train'] ~ n10, pch=19, bty = 'l', las = 1, xlab = 'Sample size', ylab = 'Error', ylim = range(err), xlim = c(1000,2000))
points(err[,'cv'] ~ n10, pch=19, bty = 'l', las = 1, xlab = 'Sample size', ylab = 'Error',col = 'blue')
lines(n10, err[,'train'])
lines(n10, err[,'cv'], col = 'blue')
title(main = "Learning curve: Up-to-date game information predicting game outcomes.", sub = 'Sample size: 1000-2000')

dev.off()